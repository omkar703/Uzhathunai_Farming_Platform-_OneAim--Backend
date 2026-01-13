"""SQLAlchemy models for Uzhathunai v2.0"""

from app.models.user import User, RefreshToken
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    InvitationStatus,
    ServiceStatus,
    UserRoleScope,
    PermissionEffect,
    MeasurementUnitCategory,
    CropLifecycle,
    TransactionType,
    TaskCategory,
    WorkOrderStatus,
    WorkOrderScopeType,
    TaskStatus,
    ScheduleChangeTrigger,
    QueryStatus,
    AuditStatus,
    SyncStatus
)
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.invitation import OrgMemberInvitation
from app.models.fsp_service import MasterService, MasterServiceTranslation, FSPServiceListing, FSPApprovalDocument
from app.models.rbac import Role, Permission, RolePermission, OrgRolePermissionOverride
from app.models.subscription import SubscriptionPlan
from app.models.measurement_unit import MeasurementUnit, MeasurementUnitTranslation
from app.models.crop_data import (
    CropCategory,
    CropCategoryTranslation,
    CropType,
    CropTypeTranslation,
    CropVariety,
    CropVarietyTranslation
)
from app.models.input_item import (
    InputItemCategory,
    InputItemCategoryTranslation,
    InputItem,
    InputItemTranslation
)
from app.models.finance_category import FinanceCategory, FinanceCategoryTranslation
from app.models.reference_data import (
    Task,
    TaskTranslation,
    ReferenceDataType,
    ReferenceData,
    ReferenceDataTranslation
)
from app.models.farm import (
    Farm,
    FarmSupervisor,
    FarmWaterSource,
    FarmSoilType,
    FarmIrrigationMode
)
from app.models.plot import (
    Plot,
    PlotWaterSource,
    PlotSoilType,
    PlotIrrigationMode
)
from app.models.crop import (
    Crop,
    CropLifecyclePhoto,
    CropYield,
    CropYieldPhoto
)
from app.models.work_order import WorkOrder, WorkOrderScope
from app.models.schedule_template import ScheduleTemplate, ScheduleTemplateTask, ScheduleTemplateTranslation
from app.models.schedule import Schedule, ScheduleTask, TaskActual, TaskPhoto, ScheduleChangeLog
from app.models.query import Query, QueryResponse, QueryPhoto
from app.models.option_set import OptionSet, Option, OptionTranslation
from app.models.parameter import Parameter, ParameterTranslation, ParameterOptionSetMap, ParameterType
from app.models.section import Section, SectionTranslation
from app.models.template import Template, TemplateTranslation, TemplateSection, TemplateParameter
from app.models.audit import Audit, AuditParameterInstance

__all__ = [
    # User models
    "User",
    "RefreshToken",
    # Enums
    "OrganizationType",
    "OrganizationStatus",
    "MemberStatus",
    "InvitationStatus",
    "ServiceStatus",
    "UserRoleScope",
    "PermissionEffect",
    "MeasurementUnitCategory",
    "CropLifecycle",
    "TransactionType",
    "TaskCategory",
    "WorkOrderStatus",
    "WorkOrderScopeType",
    "TaskStatus",
    "ScheduleChangeTrigger",
    "QueryStatus",
    "AuditStatus",
    "SyncStatus",
    # Organization models
    "Organization",
    "OrgMember",
    "OrgMemberRole",
    # Invitation models
    "OrgMemberInvitation",
    # FSP Service models
    "MasterService",
    "MasterServiceTranslation",
    "FSPServiceListing",
    "FSPApprovalDocument",
    # RBAC models
    "Role",
    "Permission",
    "RolePermission",
    "OrgRolePermissionOverride",
    # Subscription models
    "SubscriptionPlan",
    # Measurement Unit models
    "MeasurementUnit",
    "MeasurementUnitTranslation",
    # Crop Data models
    "CropCategory",
    "CropCategoryTranslation",
    "CropType",
    "CropTypeTranslation",
    "CropVariety",
    "CropVarietyTranslation",
    # Input Item models
    "InputItemCategory",
    "InputItemCategoryTranslation",
    "InputItem",
    "InputItemTranslation",
    # Finance Category models
    "FinanceCategory",
    "FinanceCategoryTranslation",
    # Reference Data models
    "Task",
    "TaskTranslation",
    "ReferenceDataType",
    "ReferenceData",
    "ReferenceDataTranslation",
    # Farm models
    "Farm",
    "FarmSupervisor",
    "FarmWaterSource",
    "FarmSoilType",
    "FarmIrrigationMode",
    # Plot models
    "Plot",
    "PlotWaterSource",
    "PlotSoilType",
    "PlotIrrigationMode",
    # Crop models
    "Crop",
    "CropLifecyclePhoto",
    "CropYield",
    "CropYieldPhoto",
    # Work Order models
    "WorkOrder",
    "WorkOrderScope",
    # Schedule Template models
    "ScheduleTemplate",
    "ScheduleTemplateTask",
    "ScheduleTemplateTranslation",
    # Schedule models
    "Schedule",
    "ScheduleTask",
    "TaskActual",
    "TaskPhoto",
    "ScheduleChangeLog",
    # Query models
    "Query",
    "QueryResponse",
    "QueryPhoto",
    # Option Set models
    "OptionSet",
    "Option",
    "OptionTranslation",
    # Parameter models
    "Parameter",
    "ParameterTranslation",
    "ParameterOptionSetMap",
    "ParameterType",
    # Section models
    "Section",
    "SectionTranslation",
    # Template models
    "Template",
    "TemplateTranslation",
    "TemplateSection",
    "TemplateParameter",
    # Audit models
    "Audit",
    "AuditParameterInstance",
]
