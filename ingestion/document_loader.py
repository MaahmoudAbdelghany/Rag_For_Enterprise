"""
Multi-Format Document Loader (Step 1.1)

Unified document loading module that converts PDF, DOCX, Markdown, XLSX, CSV,
and TXT files into LangChain Document objects with RBAC metadata tags.

Primary engine: Docling (IBM) — handles PDF, DOCX, Markdown, XLSX, CSV, and
other formats through a single DocumentConverter API.
Fallback: pandas for CSV/Excel when Docling is unavailable or fails.

Each loaded document is tagged with:
  - source: absolute path to the original file
  - filename: basename of the file
  - file_type: extension (pdf, docx, md, xlsx, csv, txt)
  - department: inferred from parent directory name (validated against RBAC)
  - sensitivity: default "internal" (overridden later by metadata extraction)
"""

import logging
import os
from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported file extensions
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".xlsx", ".csv", ".txt"}

# Valid departments from RBAC config (avoids circular import at module level)
VALID_DEPARTMENTS = {"finance", "hr", "marketing", "engineering", "general"}

# Default sensitivity level assigned at load time
DEFAULT_SENSITIVITY = "internal"


# ---------------------------------------------------------------------------
# Department inference
# ---------------------------------------------------------------------------
def infer_department(file_path: str) -> str:
    """
    Infer the department from the file's parent directory name.

    The project convention stores raw documents under:
        ingestion/data/raw/{department}/filename.ext

    If the parent directory matches a known department, that value is used.
    Otherwise, defaults to "general".
    """
    parent_dir = Path(file_path).parent.name.lower()
    if parent_dir in VALID_DEPARTMENTS:
        return parent_dir
    logger.warning(
        f"Could not infer department from path '{file_path}'. "
        f"Parent directory '{parent_dir}' is not a valid department. "
        f"Defaulting to 'general'."
    )
    return "general"


# ---------------------------------------------------------------------------
# Base metadata builder
# ---------------------------------------------------------------------------
def _build_base_metadata(file_path: str) -> dict:
    """
    Build the base metadata dictionary attached to every loaded Document.
    """
    abs_path = str(Path(file_path).resolve())
    filename = Path(file_path).name
    extension = Path(file_path).suffix.lower().lstrip(".")

    return {
        "source": abs_path,
        "filename": filename,
        "file_type": extension,
        "department": infer_department(file_path),
        "sensitivity": DEFAULT_SENSITIVITY,
    }


# ---------------------------------------------------------------------------
# Docling-based loader (primary)
# ---------------------------------------------------------------------------
def _load_with_docling(file_path: str, metadata: dict) -> List[Document]:
    """
    Use Docling's DocumentConverter to parse a file into Markdown, then wrap
    the output as a single LangChain Document.

    Docling handles: PDF, DOCX, PPTX, HTML, Markdown, XLSX, CSV, images.
    We export to Markdown because it preserves structure (headings, tables)
    in a format that downstream chunkers can split effectively.
    """
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(file_path)
    markdown_content = result.document.export_to_markdown()

    if not markdown_content or not markdown_content.strip():
        logger.warning(f"Docling returned empty content for '{file_path}'.")
        return []

    doc = Document(page_content=markdown_content, metadata=metadata.copy())
    logger.info(
        f"Docling loaded '{metadata['filename']}' — "
        f"{len(markdown_content):,} chars"
    )
    return [doc]


# ---------------------------------------------------------------------------
# Pandas-based fallback for CSV / Excel
# ---------------------------------------------------------------------------
def _load_tabular_with_pandas(file_path: str, metadata: dict) -> List[Document]:
    """
    Fallback loader for CSV and XLSX files using pandas.
    Converts each sheet (or the single CSV) into a Markdown table representation
    so downstream chunkers receive structured, readable text.
    """
    import pandas as pd

    ext = metadata["file_type"]
    documents: List[Document] = []

    try:
        if ext == "csv":
            df = pd.read_csv(file_path)
            md_table = df.to_markdown(index=False)
            sheet_meta = {**metadata, "sheet_name": "default"}
            documents.append(Document(page_content=md_table, metadata=sheet_meta))
            logger.info(
                f"Pandas loaded CSV '{metadata['filename']}' — "
                f"{len(df)} rows, {len(df.columns)} columns"
            )

        elif ext == "xlsx":
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                md_table = df.to_markdown(index=False)
                sheet_meta = {**metadata, "sheet_name": sheet_name}
                documents.append(
                    Document(page_content=md_table, metadata=sheet_meta)
                )
            logger.info(
                f"Pandas loaded XLSX '{metadata['filename']}' — "
                f"{len(xls.sheet_names)} sheet(s)"
            )
        else:
            raise ValueError(f"Unsupported tabular format: .{ext}")

    except Exception as e:
        logger.error(f"Pandas failed to load '{file_path}': {e}")
        raise

    return documents


# ---------------------------------------------------------------------------
# Plain-text fallback
# ---------------------------------------------------------------------------
def _load_plain_text(file_path: str, metadata: dict) -> List[Document]:
    """
    Simple UTF-8 text reader. Used as a last-resort fallback for .txt and .md
    files if Docling is not available.
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = Path(file_path).read_text(encoding="latin-1")

    if not content.strip():
        logger.warning(f"Empty file: '{file_path}'")
        return []

    doc = Document(page_content=content, metadata=metadata.copy())
    logger.info(
        f"Plain-text loaded '{metadata['filename']}' — {len(content):,} chars"
    )
    return [doc]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def load_document(file_path: str) -> List[Document]:
    """
    Load a single document from disk and return LangChain Document(s) with
    RBAC metadata.

    Strategy:
      1. Validate that the file exists and has a supported extension.
      2. Try Docling (primary engine) for all supported formats.
      3. If Docling is unavailable or fails:
         - CSV / XLSX → pandas fallback
         - TXT / MD   → plain-text fallback
      4. Attach department + sensitivity metadata to every Document.

    Args:
        file_path: Path to the document file.

    Returns:
        A list of LangChain Document objects (usually one per file, or one per
        Excel sheet for XLSX).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file extension is not supported.
    """
    path = Path(file_path).resolve()

    # Validate existence
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Validate extension
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    # Build base metadata
    metadata = _build_base_metadata(str(path))

    # --- Attempt Docling first ---
    try:
        docs = _load_with_docling(str(path), metadata)
        if docs:
            return docs
        logger.warning(
            f"Docling returned empty for '{path.name}', trying fallback."
        )
    except ImportError:
        logger.info(
            "Docling is not installed. Using fallback loaders. "
            "Install with: pip install docling"
        )
    except Exception as e:
        logger.warning(
            f"Docling failed for '{path.name}': {e}. Trying fallback."
        )

    # --- Fallback loaders ---
    file_type = metadata["file_type"]

    if file_type in ("csv", "xlsx"):
        return _load_tabular_with_pandas(str(path), metadata)
    elif file_type in ("txt", "md"):
        return _load_plain_text(str(path), metadata)
    else:
        # PDF / DOCX without Docling — cannot proceed
        raise RuntimeError(
            f"Cannot load '{path.name}' (type: .{file_type}) without Docling. "
            f"Please install docling: pip install docling"
        )


def load_directory(
    directory_path: str,
    recursive: bool = True,
) -> List[Document]:
    """
    Scan a directory for supported files and load all of them.

    Args:
        directory_path: Path to the directory to scan.
        recursive: If True, scan subdirectories recursively.

    Returns:
        A flat list of LangChain Document objects from all loaded files.
    """
    dir_path = Path(directory_path).resolve()
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")

    all_documents: List[Document] = []
    pattern = "**/*" if recursive else "*"

    files_found = sorted(
        f for f in dir_path.glob(pattern)
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    logger.info(
        f"Found {len(files_found)} supported file(s) in '{dir_path}'"
    )

    for file in files_found:
        try:
            docs = load_document(str(file))
            all_documents.extend(docs)
        except Exception as e:
            logger.error(f"Failed to load '{file.name}': {e}")
            continue

    logger.info(
        f"Loaded {len(all_documents)} document(s) total from '{dir_path}'"
    )
    return all_documents
