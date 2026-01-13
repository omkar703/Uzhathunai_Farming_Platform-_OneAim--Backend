"""
Sharing Service for Farm Audit Management System.

This service manages audit sharing, transitioning audits from FINALIZED to SHARED
status and making them read-only for all parties.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.exceptions import ValidationError
from app.models.audit import Audit
from app.models.enums import AuditStatus

logger = get_logger(__name__)


class SharingService:
    """
    Service for managing audit sharing.
    
    Handles the sharing process which:
    1. Transitions audit status from FINALIZED to SHARED
    2. Captures shared_at timestamp
    3. Makes audit read-only for all parties (FSP and farming organizations)
    """

    def __init__(self, db: Session):
        self.db = db

    def share_audit(
        self,
        audit_id: UUID,
        user_id: UUID
    ) -> Audit:
        """
        Share a finalized audit with the farming organization.
        
        Transitions audit from FINALIZED to SHARED status, captures sharing
        timestamp, and makes the audit read-only for all parties.
        
        Args:
            audit_id: UUID of the audit to share
            user_id: ID of the user performing the sharing
            
        Returns:
            Shared audit
            
        Raises:
            ValidationError: If audit not found or not in FINALIZED status
        """
        logger.info(
            "Sharing audit",
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
        if audit.status != AuditStatus.FINALIZED:
            raise ValidationError(
                message=f"Cannot share audit with status {audit.status.value}. Audit must be in FINALIZED status.",
                error_code="INVALID_STATUS_FOR_SHARING",
                details={
                    "current_status": audit.status.value,
                    "required_status": AuditStatus.FINALIZED.value
                }
            )

        # Check if already shared (defensive check)
        if audit.shared_at is not None:
            raise ValidationError(
                message="Audit is already shared",
                error_code="AUDIT_ALREADY_SHARED",
                details={
                    "audit_id": str(audit_id),
                    "shared_at": audit.shared_at.isoformat()
                }
            )

        # Transition to SHARED status
        audit.status = AuditStatus.SHARED
        audit.shared_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(audit)

        logger.info(
            "Audit shared successfully",
            extra={
                "audit_id": str(audit_id),
                "shared_at": audit.shared_at.isoformat(),
                "farming_organization_id": str(audit.farming_organization_id)
            }
        )

        return audit

    def is_audit_shared(self, audit_id: UUID) -> bool:
        """
        Check if an audit is shared.
        
        Args:
            audit_id: UUID of the audit
            
        Returns:
            True if audit is shared, False otherwise
        """
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            return False

        return audit.status == AuditStatus.SHARED

    def validate_read_only(self, audit_id: UUID) -> None:
        """
        Validate that an audit is read-only (shared).
        
        Raises ValidationError if audit is not shared.
        
        Args:
            audit_id: UUID of the audit
            
        Raises:
            ValidationError: If audit is not shared
        """
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise ValidationError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND",
                details={"audit_id": str(audit_id)}
            )

        if audit.status != AuditStatus.SHARED:
            raise ValidationError(
                message=f"Audit is not shared. Current status: {audit.status.value}",
                error_code="AUDIT_NOT_SHARED",
                details={
                    "audit_id": str(audit_id),
                    "status": audit.status.value
                }
            )

    def get_sharing_info(self, audit_id: UUID) -> Optional[dict]:
        """
        Get sharing information for an audit.
        
        Args:
            audit_id: UUID of the audit
            
        Returns:
            Dictionary with sharing info, or None if not shared
        """
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit or not audit.shared_at:
            return None

        return {
            "shared_at": audit.shared_at.isoformat(),
            "status": audit.status.value,
            "farming_organization_id": str(audit.farming_organization_id),
            "fsp_organization_id": str(audit.fsp_organization_id)
        }
