"""Pydantic schemas for Uzhathunai v2.0"""

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    UserLogout,
    UserUpdate,
    ChangePassword,
    TokenResponse,
    AuthResponse,
)
from app.schemas.user import UserResponse
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    FSPServiceListingCreate,
)
from app.schemas.member import (
    MemberResponse,
    MemberRoleAssignment,
    UpdateMemberRolesRequest,
    UpdateMemberStatusRequest,
    MemberRoleResponse,
)
from app.schemas.invitation import (
    InviteMemberRequest,
    InvitationResponse,
    AcceptInvitationResponse,
    RejectInvitationResponse,
)
from app.schemas.rbac import (
    RoleResponse,
    PermissionResponse,
    RolePermissionResponse,
    CreateOrgRolePermissionOverrideRequest,
    OrgRolePermissionOverrideResponse,
    PermissionCheckRequest,
    PermissionCheckResponse,
)
from app.schemas.fsp_service import (
    MasterServiceResponse,
    MasterServiceTranslationResponse,
    FSPServiceListingResponse,
    FSPServiceListingUpdate,
)
from app.schemas.measurement_unit import (
    MeasurementUnitResponse,
    MeasurementUnitTranslationResponse,
    ConvertQuantityRequest,
    ConvertQuantityResponse,
)
from app.schemas.crop_data import (
    CropCategoryResponse,
    CropCategoryTranslationResponse,
    CropTypeResponse,
    CropTypeTranslationResponse,
    CropVarietyResponse,
    CropVarietyTranslationResponse,
    VarietyMetadata,
)
from app.schemas.input_item import (
    InputItemCategoryCreate,
    InputItemCategoryUpdate,
    InputItemCategoryResponse,
    InputItemCategoryTranslationResponse,
    InputItemCreate,
    InputItemUpdate,
    InputItemResponse,
    InputItemTranslationResponse,
    ItemMetadata,
)
from app.schemas.finance_category import (
    FinanceCategoryCreate,
    FinanceCategoryUpdate,
    FinanceCategoryResponse,
    FinanceCategoryTranslationResponse,
)
from app.schemas.reference_data import (
    TaskResponse,
    TaskTranslationResponse,
    ReferenceDataTypeResponse,
    ReferenceDataResponse,
    ReferenceDataTranslationResponse,
    ReferenceMetadata,
)
from app.schemas.farm import (
    FarmCreate,
    FarmUpdate,
    FarmResponse,
    FarmSupervisorResponse,
    FarmAttributes,
    GeoJSONPoint,
    GeoJSONPolygon,
)
from app.schemas.plot import (
    PlotCreate,
    PlotUpdate,
    PlotResponse,
    PlotAttributes,
)
from app.schemas.crop import (
    CropCreate,
    CropUpdate,
    CropResponse,
    UpdateLifecycleRequest,
    CropYieldCreate,
    CropYieldUpdate,
    CropYieldResponse,
    YieldComparisonResponse,
    CropPhotoUpload,
    CropPhotoResponse,
)

__all__ = [
    # Auth schemas
    "UserRegister",
    "UserLogin",
    "TokenRefresh",
    "UserLogout",
    "UserUpdate",
    "ChangePassword",
    "TokenResponse",
    "AuthResponse",
    "UserResponse",
    # Organization schemas
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    "FSPServiceListingCreate",
    # Member schemas
    "MemberResponse",
    "MemberRoleAssignment",
    "UpdateMemberRolesRequest",
    "UpdateMemberStatusRequest",
    "MemberRoleResponse",
    # Invitation schemas
    "InviteMemberRequest",
    "InvitationResponse",
    "AcceptInvitationResponse",
    "RejectInvitationResponse",
    # RBAC schemas
    "RoleResponse",
    "PermissionResponse",
    "RolePermissionResponse",
    "CreateOrgRolePermissionOverrideRequest",
    "OrgRolePermissionOverrideResponse",
    "PermissionCheckRequest",
    "PermissionCheckResponse",
    # FSP Service schemas
    "MasterServiceResponse",
    "MasterServiceTranslationResponse",
    "FSPServiceListingResponse",
    "FSPServiceListingUpdate",
    # Measurement Unit schemas
    "MeasurementUnitResponse",
    "MeasurementUnitTranslationResponse",
    "ConvertQuantityRequest",
    "ConvertQuantityResponse",
    # Crop Data schemas
    "CropCategoryResponse",
    "CropCategoryTranslationResponse",
    "CropTypeResponse",
    "CropTypeTranslationResponse",
    "CropVarietyResponse",
    "CropVarietyTranslationResponse",
    "VarietyMetadata",
    # Input Item schemas
    "InputItemCategoryCreate",
    "InputItemCategoryUpdate",
    "InputItemCategoryResponse",
    "InputItemCategoryTranslationResponse",
    "InputItemCreate",
    "InputItemUpdate",
    "InputItemResponse",
    "InputItemTranslationResponse",
    "ItemMetadata",
    # Finance Category schemas
    "FinanceCategoryCreate",
    "FinanceCategoryUpdate",
    "FinanceCategoryResponse",
    "FinanceCategoryTranslationResponse",
    # Reference Data schemas
    "TaskResponse",
    "TaskTranslationResponse",
    "ReferenceDataTypeResponse",
    "ReferenceDataResponse",
    "ReferenceDataTranslationResponse",
    "ReferenceMetadata",
    # Farm schemas
    "FarmCreate",
    "FarmUpdate",
    "FarmResponse",
    "FarmSupervisorResponse",
    "FarmAttributes",
    "GeoJSONPoint",
    "GeoJSONPolygon",
    # Plot schemas
    "PlotCreate",
    "PlotUpdate",
    "PlotResponse",
    "PlotAttributes",
    # Crop schemas
    "CropCreate",
    "CropUpdate",
    "CropResponse",
    "UpdateLifecycleRequest",
    "CropYieldCreate",
    "CropYieldUpdate",
    "CropYieldResponse",
    "YieldComparisonResponse",
    "CropPhotoUpload",
    "CropPhotoResponse",
]
