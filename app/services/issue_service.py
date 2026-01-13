"""
Issue Service for Farm Audit Management System in Uzhathunai v2.0.

Handles creation and management of audit issues with severity categorization.
Issues can be created during SUBMITTED, REVIEWED, and FINALIZED audit statuses.

Requirements: 13.1, 13.2, 13.3, 13.4
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.audit import AuditIssue, Audit
from app.models.enums import IssueSeverity, AuditStatus
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.core.logging import get_logger

logger = get_logger(__name__)


class IssueService:
    """Service for managing audit issues."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_issue(
        self,
        audit_id: UUID,
        title: str,
        description: Optional[str],
        severity: IssueSeverity,
        user_id: UUID
    ) -> AuditIssue:
        """
        Create an audit issue.
        
        Validates that the audit exists and is in an appropriate status
        (SUBMITTED, REVIEWED, or FINALIZED).
        
        Args:
            audit_id: ID of the audit
            title: Issue title (required)
            description: Issue description (optional)
            severity: Issue severity level
            user_id: ID of the user creating the issue
            
        Returns:
            Created AuditIssue
            
        Raises:
            NotFoundError: If audit not found
            ValidationError: If audit status is invalid for issue creation
            
        Requirements: 13.1, 13.2, 13.3
        """
        # Validate audit exists
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND",
                details={"audit_id": str(audit_id)}
            )
        
        # Validate audit status
        valid_statuses = [AuditStatus.SUBMITTED, AuditStatus.REVIEWED, AuditStatus.FINALIZED]
        if audit.status not in valid_statuses:
            raise ValidationError(
                message=f"Issues can only be created for audits in SUBMITTED, REVIEWED, or FINALIZED status. Current status: {audit.status}",
                error_code="INVALID_AUDIT_STATUS",
                details={
                    "audit_id": str(audit_id),
                    "current_status": audit.status.value,
                    "valid_statuses": [s.value for s in valid_statuses]
                }
            )
        
        # Validate title
        if not title or not title.strip():
            raise ValidationError(
                message="Issue title is required",
                error_code="TITLE_REQUIRED",
                details={"field": "title"}
            )
        
        # Create issue
        issue = AuditIssue(
            audit_id=audit_id,
            title=title.strip(),
            description=description.strip() if description else None,
            severity=severity,
            created_by=user_id
        )
        
        self.db.add(issue)
        self.db.commit()
        self.db.refresh(issue)
        
        logger.info(
            "Audit issue created",
            extra={
                "issue_id": str(issue.id),
                "audit_id": str(audit_id),
                "severity": severity.value,
                "user_id": str(user_id),
                "action": "create_issue"
            }
        )
        
        return issue
    
    def get_issue(self, issue_id: UUID) -> AuditIssue:
        """
        Get an audit issue by ID.
        
        Args:
            issue_id: ID of the issue
            
        Returns:
            AuditIssue
            
        Raises:
            NotFoundError: If issue not found
        """
        issue = self.db.query(AuditIssue).filter(AuditIssue.id == issue_id).first()
        if not issue:
            raise NotFoundError(
                message=f"Issue {issue_id} not found",
                error_code="ISSUE_NOT_FOUND",
                details={"issue_id": str(issue_id)}
            )
        return issue
    
    def get_audit_issues(
        self,
        audit_id: UUID,
        severity: Optional[IssueSeverity] = None
    ) -> List[AuditIssue]:
        """
        Get all issues for an audit, optionally filtered by severity.
        
        Args:
            audit_id: ID of the audit
            severity: Optional severity filter
            
        Returns:
            List of AuditIssue
            
        Requirements: 13.1
        """
        query = self.db.query(AuditIssue).filter(AuditIssue.audit_id == audit_id)
        
        if severity:
            query = query.filter(AuditIssue.severity == severity)
        
        # Order by severity (CRITICAL first) and creation time
        severity_order = {
            IssueSeverity.CRITICAL: 0,
            IssueSeverity.HIGH: 1,
            IssueSeverity.MEDIUM: 2,
            IssueSeverity.LOW: 3
        }
        
        issues = query.all()
        issues.sort(key=lambda x: (severity_order.get(x.severity, 999), x.created_at))
        
        return issues
    
    def update_issue(
        self,
        issue_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        severity: Optional[IssueSeverity] = None
    ) -> AuditIssue:
        """
        Update an audit issue.
        
        Args:
            issue_id: ID of the issue
            title: New title (optional)
            description: New description (optional)
            severity: New severity (optional)
            
        Returns:
            Updated AuditIssue
            
        Raises:
            NotFoundError: If issue not found
            ValidationError: If validation fails
        """
        issue = self.get_issue(issue_id)
        
        # Update fields if provided
        if title is not None:
            if not title.strip():
                raise ValidationError(
                    message="Issue title cannot be empty",
                    error_code="TITLE_REQUIRED",
                    details={"field": "title"}
                )
            issue.title = title.strip()
        
        if description is not None:
            issue.description = description.strip() if description else None
        
        if severity is not None:
            issue.severity = severity
        
        self.db.commit()
        self.db.refresh(issue)
        
        logger.info(
            "Audit issue updated",
            extra={
                "issue_id": str(issue_id),
                "audit_id": str(issue.audit_id),
                "action": "update_issue"
            }
        )
        
        return issue
    
    def delete_issue(self, issue_id: UUID) -> None:
        """
        Delete an audit issue.
        
        Args:
            issue_id: ID of the issue
            
        Raises:
            NotFoundError: If issue not found
        """
        issue = self.get_issue(issue_id)
        
        audit_id = issue.audit_id
        
        self.db.delete(issue)
        self.db.commit()
        
        logger.info(
            "Audit issue deleted",
            extra={
                "issue_id": str(issue_id),
                "audit_id": str(audit_id),
                "action": "delete_issue"
            }
        )
