"""
LLM Provider Factory & Configuration Module

Provides a unified factory function `get_llm()` to initialize LLM clients
(e.g., Groq, Azure OpenAI) based on application settings and environment variables.
"""

import logging
from typing import Optional, Any
from langchain_core.language_models.chat_models import BaseChatModel
from config.settings import get_settings

logger = logging.getLogger(__name__)


def get_llm(
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    streaming: bool = False,
    provider: Optional[str] = None,
    **kwargs: Any,
) -> BaseChatModel:
    """
    Factory function to initialize and return a LangChain Chat Model based on configuration.

    Args:
        temperature: Controls randomness in generation (0.0 for deterministic RAG answers).
        max_tokens: Optional limit on output response length.
        streaming: Enable token streaming if supported.
        provider: Override LLM provider ("groq", "azure", "azure_openai"). If None, uses settings.LLM_PROVIDER.
        **kwargs: Additional parameters passed to the model constructor.

    Returns:
        BaseChatModel: An initialized LangChain chat model instance.

    Raises:
        ValueError: If provider is unsupported or required API credentials/endpoints are missing.
    """
    settings = get_settings()
    target_provider = (provider or settings.LLM_PROVIDER).lower().strip()

    logger.info(f"Initializing LLM provider: {target_provider}")

    if target_provider == "groq":
        api_key = settings.GROQ_API_KEY
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError(
                "GROQ_API_KEY is not set or contains placeholder value. "
                "Please configure a valid GROQ_API_KEY in your .env file."
            )
        
        try:
            from langchain_groq import ChatGroq
        except ImportError as e:
            raise ImportError(
                "langchain-groq package is required for Groq provider. "
                "Please install it using 'pip install langchain-groq'."
            ) from e

        llm_kwargs = {
            "groq_api_key": api_key,
            "model_name": settings.GROQ_MODEL,
            "temperature": temperature,
            "streaming": streaming,
            **kwargs,
        }
        if max_tokens is not None:
            llm_kwargs["max_tokens"] = max_tokens

        return ChatGroq(**llm_kwargs)

    elif target_provider in ("azure", "azure_openai"):
        api_key = settings.AZURE_OPENAI_API_KEY
        endpoint = settings.AZURE_OPENAI_ENDPOINT
        deployment = settings.AZURE_OPENAI_DEPLOYMENT_NAME

        if not api_key or not endpoint or not deployment:
            raise ValueError(
                "Azure OpenAI configuration incomplete. Ensure AZURE_OPENAI_API_KEY, "
                "AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME are set in .env."
            )

        try:
            from langchain_community.chat_models import AzureChatOpenAI
        except ImportError:
            try:
                from langchain_openai import AzureChatOpenAI
            except ImportError as e:
                raise ImportError(
                    "langchain-community or langchain-openai package is required for Azure OpenAI provider."
                ) from e

        llm_kwargs = {
            "azure_api_key": api_key,
            "azure_endpoint": endpoint,
            "azure_deployment": deployment,
            "temperature": temperature,
            "streaming": streaming,
            **kwargs,
        }
        if max_tokens is not None:
            llm_kwargs["max_tokens"] = max_tokens

        return AzureChatOpenAI(**llm_kwargs)

    else:
        supported = ["groq", "azure", "azure_openai"]
        raise ValueError(
            f"Unsupported LLM provider '{target_provider}'. Supported providers are: {supported}"
        )
