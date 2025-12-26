"""
Finalization Service for Farm Audit Management System.

This service manages audit finalization, transitioning audits from REVIEWED to FINALIZED
status and preventing any modifications after finalization.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.exceptions import ValidationError, PermissionError
from app.models.audit import Audit
from app.models.enums import AuditStatus

logger = get_logger(__name__)


class FinalizationService:
    """
    Service for managing audit finalization.
    
    Handles the finalization process which:
    1. Transitions audit status from REVIEWED to FINALIZED
    2. Captures finalized_at timestamp and finalized_by user
    3. Makes audit immutable (prevents further modifications)
    """

    def __init__(self, db: Session):
        self.db = db

    def finalize_audit(
        self,
        audit_id: UUID,
        user_id: UUID
    ) -> Audit:
        """
        Finalize an audit.
        
        Transitions audit from REVIEWED to FINALIZED status, captures finalization
        metadata, and makes the audit immutable.
        
        Args:
            audit_id: UUID of the audit to finalize
            user_id: ID of the user performing finalization
            
        Returns:
            Finalized audit
            
        Raises:
            ValidationError: If audit not found or not in REVIEWED status
        """
        logger.info(
            "Finalizing audit",
            extra={
                "audit_id": str(audit_id),
                "user_id": str(user_id)
            }
        )

        # Get audit
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise ValidationError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND",
                details={"audit_id": str(audit_id)}
            )

        # Validate current status
        if audit.status != AuditStatus.REVIEWED:
            raise ValidationError(
                message=f"Cannot finalize audit with status {audit.status.value}. Audit must be in REVIEWED status.",
                error_code="INVALID_STATUS_FOR_FINALIZATION",
                details={
                    "current_status": audit.status.value,
                    "required_status": AuditStatus.REVIEWED.value
                }
            )

        # Check if already finalized (defensive check)
        if audit.finalized_at is not None:
            raise ValidationError(
                message="Audit is already finalized",
                error_code="AUDIT_ALREADY_FINALIZED",
                details={
                    "audit_id": str(audit_id),
                    "finalized_at": audit.finalized_at.isoformat(),
                    "finalized_by": str(audit.finalized_by)
                }
            )

        # Transition to FINALIZED status
        audit.status = AuditStatus.FINALIZED
        audit.finalized_at = datetime.utcnow()
        audit.finalized_by = user_id

        self.db.commit()
        self.db.refresh(audit)

        logger.info(
            "Audit finalized successfully",
            extra={
                "audit_id": str(audit_id),
                "finalized_by": str(user_id),
                "finalized_at": audit.finalized_at.isoformat()
            }
        )

        return audit

    def is_audit_finalized(self, audit_id: UUID) -> bool:
        """
        Check if an audit is finalized.
        
        Args:
            audit_id: UUID of the audit
            
        Returns:
            True if audit is finalized or shared, False otherwise
        """
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            return False

        return audit.status in [AuditStatus.FINALIZED, AuditStatus.SHARED]

    def validate_modification_allowed(self, audit_id: UUID) -> None:
        """
        Validate that modifications are allowed on an audit.
        
        Raises ValidationError if audit is finalized or shared.
        
        Args:
            audit_id: UUID of the audit
            
        Raises:
            ValidationError: If audit is finalized or shared
        """
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise ValidationError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND",
                details={"audit_id": str(audit_id)}
            )

        if audit.status in [AuditStatus.FINALIZED, AuditStatus.SHARED]:
            raise ValidationError(
                message=f"Cannot modify audit with status {audit.status.value}. Finalized and shared audits are immutable.",
                error_code="AUDIT_IMMUTABLE",
                details={
                    "audit_id": str(audit_id),
                    "status": audit.status.value,
                    "finalized_at": audit.finalized_at.isoformat() if audit.finalized_at else None,
                    "finalized_by": str(audit.finalized_by) if audit.finalized_by else None
                }
            )

    def get_finalization_info(self, audit_id: UUID) -> Optional[dict]:
        """
        Get finalization information for an audit.
        
        Args:
            audit_id: UUID of the audit
            
        Returns:
            Dictionary with finalization info, or None if not finalized
        """
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit or not audit.finalized_at:
            return None

        return {
            "finalized_at": audit.finalized_at.isoformat(),
            "finalized_by": str(audit.finalized_by) if audit.finalized_by else None,
            "status": audit.status.value
        }
