"""
Response Service for Farm Audit Management System in Uzhathunai v2.0.

Handles audit response submission and validation against parameter snapshots.
Validates responses for TEXT, NUMERIC, DATE, SINGLE_SELECT, and MULTI_SELECT parameter types.
"""
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date

from app.models.audit import AuditResponse, AuditParameterInstance, Audit
from app.schemas.audit import ResponseSubmit, ResponseUpdate
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ValidationResult:
    """Result of validation operation"""
    def __init__(self, valid: bool, error: Optional[str] = None):
        self.valid = valid
        self.error = error


class ResponseService:
    """Service for managing audit responses with validation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    def submit_response(
        self,
        audit_id: UUID,
        data: ResponseSubmit,
        user_id: UUID
    ) -> AuditResponse:
        """
        Submit a response to an audit parameter.
        
        Validates the response against the parameter snapshot to ensure:
        - Correct parameter type
        - Valid numeric ranges
        - Valid option selections
        - Photo requirements (checked separately)
        
        Args:
            audit_id: UUID of the audit
            data: Response submission data
            user_id: UUID of the user submitting the response
            
        Returns:
            Created AuditResponse
            
        Raises:
            NotFoundError: If audit or parameter instance not found
            ValidationError: If response validation fails
            PermissionError: If audit is finalized or shared
        """
        # Get audit
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND",
                details={"audit_id": str(audit_id)}
            )
        
        # Check audit status - cannot modify finalized or shared audits
        if audit.status in ['FINALIZED', 'SHARED']:
            raise PermissionError(
                message=f"Cannot submit responses to {audit.status.lower()} audit",
                error_code="AUDIT_IMMUTABLE",
                details={"audit_id": str(audit_id), "status": audit.status}
            )
        
        # Get parameter instance
        param_instance = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.id == data.audit_parameter_instance_id,
            AuditParameterInstance.audit_id == audit_id
        ).first()
        
        if not param_instance:
            raise NotFoundError(
                message=f"Parameter instance {data.audit_parameter_instance_id} not found in audit {audit_id}",
                error_code="PARAMETER_INSTANCE_NOT_FOUND",
                details={
                    "audit_id": str(audit_id),
                    "parameter_instance_id": str(data.audit_parameter_instance_id)
                }
            )
        
        # Validate response against parameter snapshot
        validation_result = self._validate_response(data, param_instance.parameter_snapshot)
        if not validation_result.valid:
            raise ValidationError(
                message=validation_result.error,
                error_code="RESPONSE_VALIDATION_FAILED",
                details={
                    "audit_id": str(audit_id),
                    "parameter_instance_id": str(data.audit_parameter_instance_id)
                }
            )
        
        # Check if response already exists
        existing_response = self.db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit_id,
            AuditResponse.audit_parameter_instance_id == data.audit_parameter_instance_id
        ).first()
        
        if existing_response:
            # Update existing response
            existing_response.response_text = data.response_text
            existing_response.response_numeric = Decimal(str(data.response_numeric)) if data.response_numeric is not None else None
            existing_response.response_date = data.response_date
            existing_response.response_options = data.response_options
            existing_response.notes = data.notes
            
            self.db.commit()
            self.db.refresh(existing_response)
            
            self.logger.info(
                "Audit response updated",
                extra={
                    "response_id": str(existing_response.id),
                    "audit_id": str(audit_id),
                    "parameter_instance_id": str(data.audit_parameter_instance_id),
                    "user_id": str(user_id),
                    "action": "update"
                }
            )
            
            return existing_response
        
        # Create new response
        response = AuditResponse(
            audit_id=audit_id,
            audit_parameter_instance_id=data.audit_parameter_instance_id,
            response_text=data.response_text,
            response_numeric=Decimal(str(data.response_numeric)) if data.response_numeric is not None else None,
            response_date=data.response_date,
            response_options=data.response_options,
            notes=data.notes,
            created_by=user_id
        )
        
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        
        self.logger.info(
            "Audit response created",
            extra={
                "response_id": str(response.id),
                "audit_id": str(audit_id),
                "parameter_instance_id": str(data.audit_parameter_instance_id),
                "user_id": str(user_id),
                "action": "create"
            }
        )
        
        return response
    
    def update_response(
        self,
        audit_id: UUID,
        response_id: UUID,
        data: ResponseUpdate,
        user_id: UUID
    ) -> AuditResponse:
        """
        Update an existing audit response.
        
        Args:
            audit_id: UUID of the audit
            response_id: UUID of the response to update
            data: Response update data
            user_id: UUID of the user updating the response
            
        Returns:
            Updated AuditResponse
            
        Raises:
            NotFoundError: If response not found
            ValidationError: If response validation fails
            PermissionError: If audit is finalized or shared
        """
        # Get response
        response = self.db.query(AuditResponse).filter(
            AuditResponse.id == response_id,
            AuditResponse.audit_id == audit_id
        ).first()
        
        if not response:
            raise NotFoundError(
                message=f"Response {response_id} not found in audit {audit_id}",
                error_code="RESPONSE_NOT_FOUND",
                details={"audit_id": str(audit_id), "response_id": str(response_id)}
            )
        
        # Check audit status
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if audit.status in ['FINALIZED', 'SHARED']:
            raise PermissionError(
                message=f"Cannot update responses in {audit.status.lower()} audit",
                error_code="AUDIT_IMMUTABLE",
                details={"audit_id": str(audit_id), "status": audit.status}
            )
        
        # Get parameter instance for validation
        param_instance = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.id == response.audit_parameter_instance_id
        ).first()
        
        # Create validation data
        validation_data = ResponseSubmit(
            audit_parameter_instance_id=response.audit_parameter_instance_id,
            response_text=data.response_text,
            response_numeric=data.response_numeric,
            response_date=data.response_date,
            response_options=data.response_options,
            notes=data.notes
        )
        
        # Validate response
        validation_result = self._validate_response(validation_data, param_instance.parameter_snapshot)
        if not validation_result.valid:
            raise ValidationError(
                message=validation_result.error,
                error_code="RESPONSE_VALIDATION_FAILED",
                details={"response_id": str(response_id)}
            )
        
        # Update response
        if data.response_text is not None:
            response.response_text = data.response_text
        if data.response_numeric is not None:
            response.response_numeric = Decimal(str(data.response_numeric))
        if data.response_date is not None:
            response.response_date = data.response_date
        if data.response_options is not None:
            response.response_options = data.response_options
        if data.notes is not None:
            response.notes = data.notes
        
        self.db.commit()
        self.db.refresh(response)
        
        self.logger.info(
            "Audit response updated",
            extra={
                "response_id": str(response_id),
                "audit_id": str(audit_id),
                "user_id": str(user_id),
                "action": "update"
            }
        )
        
        return response
    
    def get_audit_responses(
        self,
        audit_id: UUID
    ) -> List[AuditResponse]:
        """
        Get all responses for an audit.
        
        Args:
            audit_id: UUID of the audit
            
        Returns:
            List of AuditResponse objects
        """
        responses = self.db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit_id
        ).order_by(AuditResponse.created_at).all()
        
        return responses
    
    def _validate_response(
        self,
        response: ResponseSubmit,
        snapshot: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate response against parameter snapshot.
        
        Validates:
        - TEXT: No specific validation beyond required check
        - NUMERIC: Min/max value validation
        - DATE: Valid date format
        - SINGLE_SELECT: Exactly one option, valid option ID
        - MULTI_SELECT: Valid option IDs
        
        Args:
            response: Response data to validate
            snapshot: Parameter snapshot with configuration
            
        Returns:
            ValidationResult with valid flag and error message
        """
        param_type = snapshot.get('parameter_type')
        metadata = snapshot.get('parameter_metadata', {})
        
        # TEXT validation
        if param_type == 'TEXT':
            # No specific validation beyond required check (handled elsewhere)
            if response.response_text is None:
                return ValidationResult(False, "Text response is required")
            return ValidationResult(True)
        
        # NUMERIC validation
        elif param_type == 'NUMERIC':
            if response.response_numeric is None:
                return ValidationResult(False, "Numeric response is required")
            
            min_value = metadata.get('min_value')
            max_value = metadata.get('max_value')
            
            if min_value is not None and response.response_numeric < min_value:
                return ValidationResult(False, f"Value must be at least {min_value}")
            
            if max_value is not None and response.response_numeric > max_value:
                return ValidationResult(False, f"Value must be at most {max_value}")
            
            return ValidationResult(True)
        
        # DATE validation
        elif param_type == 'DATE':
            if response.response_date is None:
                return ValidationResult(False, "Date response is required")
            
            # Date format validation is handled by Pydantic
            return ValidationResult(True)
        
        # SINGLE_SELECT validation
        elif param_type == 'SINGLE_SELECT':
            if not response.response_options:
                return ValidationResult(False, "Must select exactly one option")
            
            if len(response.response_options) != 1:
                return ValidationResult(False, "Must select exactly one option")
            
            # Validate option ID exists in snapshot
            valid_option_ids = [UUID(opt['option_id']) for opt in snapshot.get('options', [])]
            if response.response_options[0] not in valid_option_ids:
                return ValidationResult(False, "Invalid option selected")
            
            return ValidationResult(True)
        
        # MULTI_SELECT validation
        elif param_type == 'MULTI_SELECT':
            if not response.response_options:
                return ValidationResult(False, "Must select at least one option")
            
            # Validate all option IDs exist in snapshot
            valid_option_ids = [UUID(opt['option_id']) for opt in snapshot.get('options', [])]
            for opt_id in response.response_options:
                if opt_id not in valid_option_ids:
                    return ValidationResult(False, f"Invalid option: {opt_id}")
            
            return ValidationResult(True)
        
        # Unknown parameter type
        return ValidationResult(False, f"Unknown parameter type: {param_type}")

