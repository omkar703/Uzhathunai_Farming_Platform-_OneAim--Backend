"""
Enum classes for Uzhathunai v2.0 Organizations & RBAC module.

All enums match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from enum import Enum as PyEnum


class OrganizationType(str, PyEnum):
    """Organization type enum - matches DDL line 10"""
    FARMING = "FARMING"
    FSP = "FSP"


class OrganizationStatus(str, PyEnum):
    """Organization status enum - matches DDL line 11"""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class MemberStatus(str, PyEnum):
    """Member status enum - matches DDL line 13"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class InvitationStatus(str, PyEnum):
    """Invitation status enum - matches DDL line 21"""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ServiceStatus(str, PyEnum):
    """Service status enum - matches DDL line 14"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class UserRoleScope(str, PyEnum):
    """User role scope enum - matches DDL line 12"""
    SYSTEM = "SYSTEM"
    ORGANIZATION = "ORGANIZATION"


class PermissionEffect(str, PyEnum):
    """Permission effect enum - matches DDL line 24"""
    ALLOW = "ALLOW"
    DENY = "DENY"


class MeasurementUnitCategory(str, PyEnum):
    """Measurement unit category enum - matches DDL line 27"""
    AREA = "AREA"
    VOLUME = "VOLUME"
    WEIGHT = "WEIGHT"
    LENGTH = "LENGTH"
    COUNT = "COUNT"


class CropLifecycle(str, PyEnum):
    """Crop lifecycle enum - matches DDL line 16"""
    PLANNED = "PLANNED"
    PLANTED = "PLANTED"
    TRANSPLANTED = "TRANSPLANTED"
    PRODUCTION = "PRODUCTION"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"
    CLOSED = "CLOSED"


class TransactionType(str, PyEnum):
    """Transaction type enum - matches DDL line 23"""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class TaskCategory(str, PyEnum):
    """Task category enum - matches DDL line 28"""
    FARMING = "FARMING"
    FSP_CONSULTANCY = "FSP_CONSULTANCY"


class WorkOrderStatus(str, PyEnum):
    """Work order status enum - matches DDL line 18"""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class WorkOrderScopeType(str, PyEnum):
    """Work order scope type enum - matches DDL line 19"""
    ORGANIZATION = "ORGANIZATION"
    FARM = "FARM"
    PLOT = "PLOT"
    CROP = "CROP"


class TaskStatus(str, PyEnum):
    """Task status enum - matches DDL line 15"""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"


class ScheduleChangeTrigger(str, PyEnum):
    """Schedule change trigger enum - matches DDL line 22"""
    MANUAL = "MANUAL"
    QUERY = "QUERY"
    AUDIT = "AUDIT"


class QueryStatus(str, PyEnum):
    """Query status enum - matches DDL line 20"""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_CLARIFICATION = "PENDING_CLARIFICATION"
    RESOLVED = "RESOLVED"
    REOPEN = "REOPEN"
    CLOSED = "CLOSED"


class AuditStatus(str, PyEnum):
    """Audit status enum - matches DDL line 26"""
    PENDING = "PENDING"
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    SUBMITTED_TO_FARMER = "SUBMITTED_TO_FARMER"
    SUBMITTED_FOR_REVIEW = "SUBMITTED_FOR_REVIEW"
    IN_ANALYSIS = "IN_ANALYSIS"
    REVIEWED = "REVIEWED"
    FINALIZED = "FINALIZED"
    SHARED = "SHARED"


class SyncStatus(str, PyEnum):
    """Sync status enum for offline operations - matches 003_audit_module_changes.sql"""
    PENDING_SYNC = "pending_sync"
    SYNCED = "synced"
    SYNC_FAILED = "sync_failed"


class IssueSeverity(str, PyEnum):
    """Issue severity enum - matches 003_audit_module_changes.sql"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PhotoSourceType(str, PyEnum):
    """Photo source type enum - tracks origin of the photo"""
    LIVE_CAPTURE = "LIVE_CAPTURE"
    MANUAL_UPLOAD = "MANUAL_UPLOAD"


class ChatContextType(str, PyEnum):
    """Chat context type enum - matches 008_chat_module.sql"""
    WORK_ORDER = "WORK_ORDER"
    ORGANIZATION = "ORGANIZATION"
    SUPPORT = "SUPPORT"


class MessageType(str, PyEnum):
    """Message type enum - matches 008_chat_module.sql"""
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    FILE = "FILE"
    SYSTEM = "SYSTEM"


class InputItemType(str, PyEnum):
    """Input item type enum - critical for icons/filtering"""
    FERTILIZER = "FERTILIZER"
    PESTICIDE = "PESTICIDE"
    OTHER = "OTHER"
