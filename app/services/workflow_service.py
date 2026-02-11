"""
Workflow Service for Farm Audit Management System.

This service manages audit status transitions and validates workflow rules.
Ensures audits follow the proper lifecycle: DRAFT → IN_PROGRESS → SUBMITTED → REVIEWED → FINALIZED → SHARED
"""

from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime
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
        AuditStatus.DRAFT: [AuditStatus.PENDING, AuditStatus.IN_PROGRESS, AuditStatus.COMPLETED, AuditStatus.SUBMITTED, AuditStatus.SUBMITTED_FOR_REVIEW],
        AuditStatus.IN_PROGRESS: [AuditStatus.DRAFT, AuditStatus.COMPLETED, AuditStatus.SUBMITTED, AuditStatus.SUBMITTED_FOR_REVIEW],
        AuditStatus.COMPLETED: [AuditStatus.IN_PROGRESS, AuditStatus.SUBMITTED_TO_FARMER, AuditStatus.SUBMITTED, AuditStatus.SUBMITTED_FOR_REVIEW],
        AuditStatus.SUBMITTED: [AuditStatus.IN_PROGRESS, AuditStatus.REVIEWED, AuditStatus.SUBMITTED_FOR_REVIEW, AuditStatus.COMPLETED, AuditStatus.FINALIZED],
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
        """
        import time
        start_time = time.time()
        
        logger.info(
            "Transitioning audit status - START",
            extra={
                "audit_id": str(audit_id),
                "to_status": to_status.value,
                "user_id": str(user_id)
            }
        )
        print(f"DEBUG: [Transition] START - Audit {audit_id} to {to_status.value}", flush=True)

        try:
            # Acquire lock and fetch audit
            lock_start = time.time()
            print(f"DEBUG: [Transition] Acquiring database lock for audit {audit_id}", flush=True)
            audit = self.db.query(Audit).with_for_update().filter(Audit.id == audit_id).first()
            lock_duration = time.time() - lock_start
            print(f"DEBUG: [Transition] Lock acquired in {lock_duration:.3f}s", flush=True)
            
            if not audit:
                logger.error(f"Audit {audit_id} not found")
                raise ValidationError(
                    message=f"Audit {audit_id} not found",
                    error_code="AUDIT_NOT_FOUND",
                    details={"audit_id": str(audit_id)}
                )

            current_status = audit.status
            print(f"DEBUG: [Transition] Current status: {current_status.value}", flush=True)

            # Validate transition is allowed
            allowed_transitions = self.VALID_TRANSITIONS.get(current_status, [])
            if to_status not in allowed_transitions:
                logger.error(
                    f"Invalid transition from {current_status.value} to {to_status.value}",
                    extra={"allowed": [s.value for s in allowed_transitions]}
                )
                raise ValidationError(
                    message=f"Invalid status transition from {current_status.value} to {to_status.value}",
                    error_code="INVALID_STATUS_TRANSITION",
                    details={
                        "current_status": current_status.value,
                        "requested_status": to_status.value,
                        "valid_transitions": [s.value for s in self.VALID_TRANSITIONS.get(current_status, [])]
                    }
                )

            # Validate requirements for submission-like statuses
            if to_status in [AuditStatus.SUBMITTED, AuditStatus.SUBMITTED_FOR_REVIEW, AuditStatus.COMPLETED, AuditStatus.SUBMITTED_TO_FARMER]:
                print(f"DEBUG: [Transition] Validating submission requirements", flush=True)
                validation_start = time.time()
                self._validate_submission_requirements(audit)
                validation_duration = time.time() - validation_start
                print(f"DEBUG: [Transition] Validation completed in {validation_duration:.3f}s", flush=True)
            
            # Update status
            print(f"DEBUG: [Transition] Updating status to {to_status.value}", flush=True)
            audit.status = to_status
            
            # If finalizing, capture metadata
            if to_status == AuditStatus.FINALIZED:
                print(f"DEBUG: [Transition] Setting finalization metadata", flush=True)
                if not audit.finalized_at:
                    audit.finalized_at = datetime.utcnow()
                if not audit.finalized_by:
                    audit.finalized_by = user_id
            
            # Commit transaction
            print(f"DEBUG: [Transition] Committing transaction", flush=True)
            commit_start = time.time()
            self.db.commit()
            commit_duration = time.time() - commit_start
            print(f"DEBUG: [Transition] Commit completed in {commit_duration:.3f}s", flush=True)
            
            # Refresh audit
            print(f"DEBUG: [Transition] Refreshing audit object", flush=True)
            self.db.refresh(audit)

            total_duration = time.time() - start_time
            logger.info(
                "Audit status transitioned successfully",
                extra={
                    "audit_id": str(audit_id),
                    "from_status": current_status.value,
                    "to_status": to_status.value,
                    "duration_seconds": total_duration,
                    "lock_duration": lock_duration,
                    "commit_duration": commit_duration
                }
            )
            print(f"DEBUG: [Transition] SUCCESS - Total duration: {total_duration:.3f}s", flush=True)

            return audit
            
        except Exception as e:
            error_duration = time.time() - start_time
            logger.error(
                f"Error during status transition: {str(e)}",
                extra={
                    "audit_id": str(audit_id),
                    "to_status": to_status.value,
                    "error_type": type(e).__name__,
                    "duration_seconds": error_duration
                },
                exc_info=True
            )
            print(f"DEBUG: [Transition] ERROR after {error_duration:.3f}s: {type(e).__name__}: {str(e)}", flush=True)
            self.db.rollback()
            raise

    def _validate_submission_requirements(self, audit: Audit) -> None:
        """
        Validate audit meets requirements for submission.
        """
        logger.info(
            "Validating submission requirements",
            extra={"audit_id": str(audit.id)}
        )

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
            response = response_map.get(instance.id)

            if instance.is_required:
                if not response or not self._has_valid_response(response):
                    param_name = self._get_parameter_name(instance)
                    missing_required.append(param_name)
                    continue

            if response:
                photo_count = photo_count_map.get(response.id, 0)
                photo_validation = self._validate_photo_requirements(instance, photo_count)
                if not photo_validation["valid"]:
                    param_name = self._get_parameter_name(instance)
                    photo_violations.append({
                        "parameter": param_name,
                        "error": photo_validation["error"]
                    })

        if missing_required or photo_violations:
            error_details = {}
            error_summary = []
            
            if missing_required:
                error_details["missing_required_responses"] = missing_required
                error_summary.append(f"Missing: {', '.join(missing_required)}")
            if photo_violations:
                error_details["photo_requirement_violations"] = photo_violations
                error_summary.append(f"Photo issues: {len(photo_violations)}")
            
            summary_str = f" ({'; '.join(error_summary)})" if error_summary else ""
            
            raise ValidationError(
                message=f"Audit does not meet submission requirements{summary_str}",
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
        """
        snapshot = instance.parameter_snapshot
        if not snapshot:
            return {"valid": True}

        metadata = snapshot.get("parameter_metadata") or {}
        min_photos = metadata.get("min_photos", 0)
        max_photos = metadata.get("max_photos", 999)

        if photo_count < min_photos:
            return {
                "valid": False,
                "error": f"Minimum {min_photos} photos required, but only {photo_count} provided"
            }

        if photo_count > max_photos:
            return {
                "valid": False,
                "error": f"Maximum {max_photos} photos allowed, but {photo_count} provided"
            }

        return {"valid": True}

    def _get_parameter_name(self, instance: AuditParameterInstance) -> str:
        """
        Get parameter name from snapshot.
        """
        snapshot = instance.parameter_snapshot
        if not snapshot:
            return f"Parameter {instance.parameter_id}"

        translations = snapshot.get("translations", {})
        en_translation = translations.get("en", {})
        name = en_translation.get("name")
        
        if name:
            return name
            
        # Fallback to live parameter data
        if instance.parameter and instance.parameter.translations:
            for t in instance.parameter.translations:
                if t.language_code == "en":
                    return t.name
                    
        return f"Parameter {instance.parameter_id}"

    def validate_submission_readiness(self, audit_id: UUID) -> Dict[str, any]:
        """
        Check if audit is ready for submission without transitioning.
        """
        logger.info(
            "Checking submission readiness",
            extra={"audit_id": str(audit_id)}
        )

        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            return {"ready": False, "error": "Audit not found"}

        if audit.status not in [AuditStatus.DRAFT, AuditStatus.PENDING, AuditStatus.IN_PROGRESS]:
            return {"ready": False, "error": f"Cannot submit audit with status {audit.status.value}"}

        instances = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.audit_id == audit.id
        ).all()

        missing_required = []
        photo_violations = []

        for instance in instances:
            response = self.db.query(AuditResponse).filter(
                AuditResponse.audit_parameter_instance_id == instance.id
            ).first()

            if instance.is_required:
                if not response or not self._has_valid_response(response):
                    param_name = self._get_parameter_name(instance)
                    missing_required.append(param_name)
                    continue

            if response:
                # Fixed type mismatch here: pass count, not response object
                photo_count = self.db.query(func.count(AuditResponsePhoto.id)).filter(
                    AuditResponsePhoto.audit_response_id == response.id
                ).scalar() or 0
                
                photo_validation = self._validate_photo_requirements(instance, photo_count)
                if not photo_validation["valid"]:
                    param_name = self._get_parameter_name(instance)
                    photo_violations.append({
                        "parameter": param_name,
                        "error": photo_validation["error"]
                    })

        ready = len(missing_required) == 0 and len(photo_violations) == 0
        result = {"ready": ready, "current_status": audit.status.value}
        if missing_required:
            result["missing_required_responses"] = missing_required
        if photo_violations:
            result["photo_requirement_violations"] = photo_violations

        return result
