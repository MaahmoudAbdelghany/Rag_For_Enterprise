"""
Role-Based Access Control (RBAC) Configuration & Policy Engine

Defines roles, departments, sensitivity levels, permission matrix,
and Qdrant vector database filter generation for Level 2 database-level enforcement.
"""

from enum import Enum
from typing import List, Dict, Set, Optional, Any
from pydantic import BaseModel
from qdrant_client.http import models as qdrant_models


class SensitivityLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


# Rank sensitivity levels for hierarchy checking
SENSITIVITY_RANK: Dict[SensitivityLevel, int] = {
    SensitivityLevel.PUBLIC: 1,
    SensitivityLevel.INTERNAL: 2,
    SensitivityLevel.CONFIDENTIAL: 3,
    SensitivityLevel.RESTRICTED: 4,
}


class Department(str, Enum):
    FINANCE = "finance"
    HR = "hr"
    MARKETING = "marketing"
    ENGINEERING = "engineering"
    GENERAL = "general"


class UserRole(str, Enum):
    FINANCE_TEAM = "finance_team"
    HR_TEAM = "hr_team"
    MARKETING_TEAM = "marketing_team"
    ENGINEERING_TEAM = "engineering_team"
    C_LEVEL = "c_level"


class RolePermission(BaseModel):
    role: UserRole
    allowed_departments: Set[str]
    max_sensitivity: SensitivityLevel


# Enterprise RBAC Access Matrix Definition
RBAC_MATRIX: Dict[UserRole, RolePermission] = {
    UserRole.FINANCE_TEAM: RolePermission(
        role=UserRole.FINANCE_TEAM,
        allowed_departments={Department.FINANCE.value, Department.GENERAL.value},
        max_sensitivity=SensitivityLevel.CONFIDENTIAL,
    ),
    UserRole.HR_TEAM: RolePermission(
        role=UserRole.HR_TEAM,
        allowed_departments={Department.HR.value, Department.GENERAL.value},
        max_sensitivity=SensitivityLevel.CONFIDENTIAL,
    ),
    UserRole.MARKETING_TEAM: RolePermission(
        role=UserRole.MARKETING_TEAM,
        allowed_departments={Department.MARKETING.value, Department.GENERAL.value},
        max_sensitivity=SensitivityLevel.CONFIDENTIAL,
    ),
    UserRole.ENGINEERING_TEAM: RolePermission(
        role=UserRole.ENGINEERING_TEAM,
        allowed_departments={Department.ENGINEERING.value, Department.GENERAL.value},
        max_sensitivity=SensitivityLevel.CONFIDENTIAL,
    ),
    UserRole.C_LEVEL: RolePermission(
        role=UserRole.C_LEVEL,
        allowed_departments={
            Department.FINANCE.value,
            Department.HR.value,
            Department.MARKETING.value,
            Department.ENGINEERING.value,
            Department.GENERAL.value,
        },
        max_sensitivity=SensitivityLevel.RESTRICTED,
    ),
}


def get_role_permission(role: str) -> RolePermission:
    """
    Retrieve permissions for a given role name.
    Raises ValueError if role is invalid.
    """
    try:
        user_role = UserRole(role.lower())
        return RBAC_MATRIX[user_role]
    except ValueError:
        raise ValueError(f"Invalid role '{role}'. Valid roles: {[r.value for r in UserRole]}")


def is_access_allowed(
    user_role: str,
    target_department: str,
    target_sensitivity: str = SensitivityLevel.INTERNAL.value,
) -> bool:
    """
    Check if a given role is authorized to access a document with target department and sensitivity level.
    """
    try:
        permission = get_role_permission(user_role)
    except ValueError:
        return False

    # Check department match
    if target_department.lower() not in permission.allowed_departments:
        return False

    # Check sensitivity level ceiling
    doc_sensitivity = SensitivityLevel(target_sensitivity.lower())
    user_max_sensitivity = permission.max_sensitivity

    return SENSITIVITY_RANK[doc_sensitivity] <= SENSITIVITY_RANK[user_max_sensitivity]


def get_allowed_sensitivity_levels(max_sensitivity: SensitivityLevel) -> List[str]:
    """
    Get a list of all sensitivity levels up to and including the max_sensitivity level.
    """
    max_rank = SENSITIVITY_RANK[max_sensitivity]
    return [
        level.value
        for level, rank in SENSITIVITY_RANK.items()
        if rank <= max_rank
    ]


def build_qdrant_rbac_filter(user_role: str) -> qdrant_models.Filter:
    """
    Construct a Qdrant database payload filter enforcing RBAC level-2 retrieval security.
    Filtering occurs AT THE DATABASE LEVEL before vector similarity search.
    """
    permission = get_role_permission(user_role)
    allowed_depts = list(permission.allowed_departments)
    allowed_sensitivities = get_allowed_sensitivity_levels(permission.max_sensitivity)

    qdrant_filter = qdrant_models.Filter(
        must=[
            qdrant_models.FieldCondition(
                key="department",
                match=qdrant_models.MatchAny(any=allowed_depts),
            ),
            qdrant_models.FieldCondition(
                key="sensitivity",
                match=qdrant_models.MatchAny(any=allowed_sensitivities),
            ),
        ]
    )
    return qdrant_filter
