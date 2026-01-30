"""
Workflow Service for Farm Audit Management System.

This service manages audit status transitions and validates workflow rules.
Ensures audits follow the proper lifecycle: DRAFT → IN_PROGRESS → SUBMITTED → REVIEWED → FINALIZED → SHARED
"""

from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.core.logging import get_logger
from app.core.exceptions import ValidationError, PermissionError
from app.models.audit import Audit, AuditParameterInstance, AuditResponse, AuditResponsePhoto
from app.models.enums import AuditStatus

logger = get_logger(__name__)


class WorkflowService:
    """
    Service for managing audit workflow and status transitions.
    
    Handles status transitions with validation of workflow rules,
    required responses, and photo requirements.
    """

    # Define valid status transitions
    VALID_TRANSITIONS = {
        AuditStatus.PENDING: [AuditStatus.IN_PROGRESS, AuditStatus.SUBMITTED, AuditStatus.COMPLETED],
        AuditStatus.DRAFT: [AuditStatus.PENDING, AuditStatus.IN_PROGRESS, AuditStatus.COMPLETED],
        AuditStatus.IN_PROGRESS: [AuditStatus.DRAFT, AuditStatus.COMPLETED, AuditStatus.SUBMITTED, AuditStatus.SUBMITTED_FOR_REVIEW],
        AuditStatus.COMPLETED: [AuditStatus.IN_PROGRESS, AuditStatus.SUBMITTED_TO_FARMER, AuditStatus.SUBMITTED, AuditStatus.SUBMITTED_FOR_REVIEW],
        AuditStatus.SUBMITTED: [AuditStatus.IN_PROGRESS, AuditStatus.REVIEWED, AuditStatus.SUBMITTED_FOR_REVIEW, AuditStatus.COMPLETED],
        AuditStatus.SUBMITTED_FOR_REVIEW: [AuditStatus.IN_PROGRESS, AuditStatus.IN_ANALYSIS, AuditStatus.REVIEWED, AuditStatus.COMPLETED],
        AuditStatus.IN_ANALYSIS: [AuditStatus.SUBMITTED_FOR_REVIEW, AuditStatus.REVIEWED, AuditStatus.FINALIZED],
        AuditStatus.REVIEWED: [AuditStatus.SUBMITTED, AuditStatus.SUBMITTED_FOR_REVIEW, AuditStatus.FINALIZED, AuditStatus.COMPLETED],
        AuditStatus.FINALIZED: [AuditStatus.SHARED, AuditStatus.SUBMITTED_TO_FARMER],
        AuditStatus.SHARED: [],  # Terminal state
        AuditStatus.SUBMITTED_TO_FARMER: []  # Terminal
    }

    def __init__(self, db: Session):
        self.db = db

    def transition_status(
        self,
        audit_id: UUID,
        to_status: AuditStatus,
        user_id: UUID
    ) -> Audit:
        """
        Transition audit to a new status with validation.
        
        Validates:
        1. Status transition is valid (follows workflow rules)
        2. Required responses are complete (for SUBMITTED status)
        3. Photo requirements are met (for SUBMITTED status)
        
        Args:
            audit_id: UUID of the audit
            to_status: Target status
            user_id: ID of the user performing the transition
            
        Returns:
            Updated audit
            
        Raises:
            ValidationError: If transition is invalid or validation fails
        """
        logger.info(
            "Transitioning audit status",
            extra={
                "audit_id": str(audit_id),
                "to_status": to_status.value,
                "user_id": str(user_id)
            }
        )

        # Get audit with explicit lock to prevent race conditions
        audit = self.db.query(Audit).with_for_update().filter(Audit.id == audit_id).first()
        if not audit:
            raise ValidationError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND",
                details={"audit_id": str(audit_id)}
            )

        current_status = audit.status
        print(f"DEBUG: Current status: {current_status}", flush=True)

        # Validate transition is allowed
        allowed_transitions = self.VALID_TRANSITIONS.get(current_status, [])
        print(f"DEBUG: Allowed transitions: {allowed_transitions}", flush=True)
        
        if to_status not in allowed_transitions:
            logger.error(
                f"DEBUGGING_ERROR: Invalid transition",
                extra={
                    "current": current_status.value,
                    "target": to_status.value,
                    "allowed": [s.value for s in allowed_transitions]
                }
            )
            print(f"DEBUG: Transition denied!", flush=True)
            raise ValidationError(
                message=f"Invalid status transition from {current_status.value} to {to_status.value}",
                error_code="INVALID_STATUS_TRANSITION",
                details={
                    "current_status": current_status.value,
                    "requested_status": to_status.value,
                    "valid_transitions": [s.value for s in self.VALID_TRANSITIONS.get(current_status, [])]
                }
            )

        # Validate requirements for SUBMITTED patterns and COMPLETED
        print(f"DEBUG: Checking validation requirements for {to_status}", flush=True)
        if to_status in [AuditStatus.SUBMITTED, AuditStatus.SUBMITTED_FOR_REVIEW, AuditStatus.COMPLETED, AuditStatus.SUBMITTED_TO_FARMER]:
            print("DEBUG: calling _validate_submission_requirements", flush=True)
            self._validate_submission_requirements(audit)
        else:
             print("DEBUG: skipping _validate_submission_requirements", flush=True)
        
        # Update status

        # Update status
        audit.status = to_status
        self.db.commit()
        self.db.refresh(audit)

        logger.info(
            "Audit status transitioned successfully",
            extra={
                "audit_id": str(audit_id),
                "from_status": current_status.value,
                "to_status": to_status.value
            }
        )

        return audit

    def _validate_submission_requirements(self, audit: Audit) -> None:
        """
        Validate audit meets requirements for submission.
        
        Checks:
        1. All required parameters have responses
        2. Photo requirements are met for all parameters
        
        Optimized to use bulk fetching to avoid N+1 queries.
        
        Args:
            audit: Audit instance
            
        Raises:
            ValidationError: If validation fails
        """
        logger.info(
            "Validating submission requirements",
            extra={"audit_id": str(audit.id)}
        )
        print("DEBUG: Inside _validate_submission_requirements", flush=True)

        # Get all parameter instances
        instances = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.audit_id == audit.id
        ).all()

        # Bulk fetch all responses
        responses = self.db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit.id
        ).all()
        response_map = {r.audit_parameter_instance_id: r for r in responses}

        # Bulk fetch photo counts
        photo_counts = self.db.query(
            AuditResponsePhoto.audit_response_id,
            func.count(AuditResponsePhoto.id)
        ).filter(
            AuditResponsePhoto.audit_id == audit.id,
            AuditResponsePhoto.audit_response_id.isnot(None)
        ).group_by(AuditResponsePhoto.audit_response_id).all()
        
        photo_count_map = {r[0]: r[1] for r in photo_counts}

        missing_required = []
        photo_violations = []

        for instance in instances:
            # Check required parameters have responses
            response = response_map.get(instance.id)

            if instance.is_required:
                if not response or not self._has_valid_response(response):
                    # Get parameter name from snapshot
                    param_name = self._get_parameter_name(instance)
                    missing_required.append(param_name)
                    continue

            # Check photo requirements
            if response:
                photo_count = photo_count_map.get(response.id, 0)
                photo_validation = self._validate_photo_requirements(instance, photo_count)
                if not photo_validation["valid"]:
                    param_name = self._get_parameter_name(instance)
                    photo_violations.append({
                        "parameter": param_name,
                        "error": photo_validation["error"]
                    })

        # Raise validation error if any issues found
        if missing_required or photo_violations:
            error_details = {}
            if missing_required:
                error_details["missing_required_responses"] = missing_required
            if photo_violations:
                error_details["photo_requirement_violations"] = photo_violations
            
            logger.error(
                f"DEBUGGING_ERROR: Validation failed",
                extra={
                    "missing": missing_required,
                    "photo_violations": photo_violations,
                    "audit_id": str(audit.id)
                }
            )

            raise ValidationError(
                message="Audit does not meet submission requirements",
                error_code="SUBMISSION_REQUIREMENTS_NOT_MET",
                details=error_details
            )

        logger.info(
            "Submission requirements validated successfully",
            extra={"audit_id": str(audit.id)}
        )

    def _has_valid_response(self, response: AuditResponse) -> bool:
        """
        Check if response has a valid value.
        
        Args:
            response: AuditResponse instance
            
        Returns:
            True if response has a value, False otherwise
        """
        return (
            response.response_text is not None or
            response.response_numeric is not None or
            response.response_date is not None or
            (response.response_options is not None and len(response.response_options) > 0)
        )

    def _validate_photo_requirements(
        self,
        instance: AuditParameterInstance,
        photo_count: int
    ) -> Dict[str, any]:
        """
        Validate photo requirements for a parameter.
        
        Args:
            instance: AuditParameterInstance
            photo_count: Number of photos uploaded for this response
            
        Returns:
            Dictionary with 'valid' boolean and optional 'error' message
        """
        # Get photo requirements from parameter snapshot
        snapshot = instance.parameter_snapshot
        if not snapshot:
            return {"valid": True}

        metadata = snapshot.get("parameter_metadata") or {}
        min_photos = metadata.get("min_photos", 0)
        max_photos = metadata.get("max_photos", 999)

        # Validate min photos
        if photo_count < min_photos:
            return {
                "valid": False,
                "error": f"Minimum {min_photos} photos required, but only {photo_count} provided"
            }

        # Validate max photos
        if photo_count > max_photos:
            return {
                "valid": False,
                "error": f"Maximum {max_photos} photos allowed, but {photo_count} provided"
            }

        return {"valid": True}

    def _get_parameter_name(self, instance: AuditParameterInstance) -> str:
        """
        Get parameter name from snapshot.
        
        Args:
            instance: AuditParameterInstance
            
        Returns:
            Parameter name (English translation)
        """
        snapshot = instance.parameter_snapshot
        if not snapshot:
            return f"Parameter {instance.parameter_id}"

        translations = snapshot.get("translations", {})
        en_translation = translations.get("en", {})
        return en_translation.get("name", f"Parameter {instance.parameter_id}")

    def validate_submission_readiness(self, audit_id: UUID) -> Dict[str, any]:
        """
        Check if audit is ready for submission without transitioning.
        
        Returns validation results including any issues that would prevent submission.
        
        Args:
            audit_id: UUID of the audit
            
        Returns:
            Dictionary with validation results
        """
        logger.info(
            "Checking submission readiness",
            extra={"audit_id": str(audit_id)}
        )

        # Get audit
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            return {
                "ready": False,
                "error": "Audit not found"
            }

        # Check current status allows submission
        if audit.status not in [AuditStatus.DRAFT, AuditStatus.PENDING, AuditStatus.IN_PROGRESS]:
            return {
                "ready": False,
                "error": f"Cannot submit audit with status {audit.status.value}"
            }

        # Get all parameter instances
        instances = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.audit_id == audit.id
        ).all()

        missing_required = []
        photo_violations = []

        for instance in instances:
            # Check required parameters
            if instance.is_required:
                response = self.db.query(AuditResponse).filter(
                    AuditResponse.audit_parameter_instance_id == instance.id
                ).first()

                if not response or not self._has_valid_response(response):
                    param_name = self._get_parameter_name(instance)
                    missing_required.append(param_name)
                    continue

            # Check photo requirements
            response = self.db.query(AuditResponse).filter(
                AuditResponse.audit_parameter_instance_id == instance.id
            ).first()

            if response:
                photo_validation = self._validate_photo_requirements(instance, response)
                if not photo_validation["valid"]:
                    param_name = self._get_parameter_name(instance)
                    photo_violations.append({
                        "parameter": param_name,
                        "error": photo_validation["error"]
                    })

        # Build result
        ready = len(missing_required) == 0 and len(photo_violations) == 0

        result = {
            "ready": ready,
            "current_status": audit.status.value
        }

        if missing_required:
            result["missing_required_responses"] = missing_required

        if photo_violations:
            result["photo_requirement_violations"] = photo_violations

        logger.info(
            "Submission readiness checked",
            extra={
                "audit_id": str(audit_id),
                "ready": ready
            }
        )

        return result
