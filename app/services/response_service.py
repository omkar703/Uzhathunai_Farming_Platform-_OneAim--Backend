"""
Response Service for Farm Audit Management System in Uzhathunai v2.0.

Handles audit response submission and validation against parameter snapshots.
Validates responses for TEXT, NUMERIC, DATE, SINGLE_SELECT, and MULTI_SELECT parameter types.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date, datetime
import uuid

from app.models.audit import AuditResponse, AuditParameterInstance, Audit, AuditResponsePhoto
from app.models.enums import PhotoSourceType, AuditStatus
from app.schemas.audit import ResponseSubmit, ResponseUpdate, ResponseBulkSubmit
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
        """
        self._check_audit_status(audit_id)
        response = self._process_response_internal(audit_id, data, user_id)
        self.db.commit()
        self.db.refresh(response)
        return response

    def submit_bulk_responses(
        self,
        audit_id: UUID,
        data: ResponseBulkSubmit,
        user_id: UUID
    ) -> List[AuditResponse]:
        """
        Submit multiple responses for an audit in a single transaction.
        """
        self._check_audit_status(audit_id)
        
        if not data.responses:
            return []
            
        print(f"DEBUG: [ResponseService] Bulk Submit: Processing {len(data.responses)} items for audit {audit_id}", flush=True)

        # 1. Collect all parameter instance IDs
        param_instance_ids = [r.audit_parameter_instance_id for r in data.responses]
        
        # 2. Bulk fetch parameter instances
        param_instances = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.id.in_(param_instance_ids),
            AuditParameterInstance.audit_id == audit_id
        ).all()
        param_instance_map = {p.id: p for p in param_instances}
        
        # Verify all instances exist
        found_ids = set(param_instance_map.keys())
        missing_ids = set(param_instance_ids) - found_ids
        if missing_ids:
            missing_id = list(missing_ids)[0]
            raise NotFoundError(message=f"Parameter instance {missing_id} not found", error_code="PARAMETER_NOT_FOUND")
            
        # 3. Bulk fetch existing responses
        existing_responses = self.db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit_id,
            AuditResponse.audit_parameter_instance_id.in_(param_instance_ids)
        ).all()
        existing_response_map = {r.audit_parameter_instance_id: r for r in existing_responses}
        
        # 4. Process responses
        new_responses_data = []
        update_responses_data = []
        response_ids_to_return = []
        evidence_processing_queue = []
        timestamp = datetime.now()
        
        for response_data in data.responses:
            param_instance = param_instance_map[response_data.audit_parameter_instance_id]
            
            print(f"DEBUG: [ResponseService] Process item: text={response_data.response_text}, num={response_data.response_numeric}", flush=True)

            # Validate
            validation_result = self._validate_response(response_data, param_instance.parameter_snapshot)
            if not validation_result.valid:
                raise ValidationError(message=validation_result.error, error_code="VALIDATION_ERROR")
                
            existing_response = existing_response_map.get(response_data.audit_parameter_instance_id)
            
            if existing_response:
                update_data = {
                    "id": existing_response.id,
                    "response_text": response_data.response_text,
                    "response_numeric": Decimal(str(response_data.response_numeric)) if response_data.response_numeric is not None else None,
                    "response_date": response_data.response_date,
                    "response_options": response_data.response_options,
                    "notes": response_data.notes,
                    "updated_at": timestamp
                }
                update_responses_data.append(update_data)
                response_ids_to_return.append(existing_response.id)
                if response_data.evidence_urls:
                    evidence_processing_queue.append((existing_response.id, response_data.evidence_urls))
            else:
                new_id = uuid.uuid4()
                insert_data = {
                    "id": new_id,
                    "audit_id": audit_id,
                    "audit_parameter_instance_id": response_data.audit_parameter_instance_id,
                    "response_text": response_data.response_text,
                    "response_numeric": Decimal(str(response_data.response_numeric)) if response_data.response_numeric is not None else None,
                    "response_date": response_data.response_date,
                    "response_options": response_data.response_options,
                    "notes": response_data.notes,
                    "created_by": user_id,
                    "created_at": timestamp,
                    "updated_at": timestamp
                }
                new_responses_data.append(insert_data)
                response_ids_to_return.append(new_id)
                if response_data.evidence_urls:
                    evidence_processing_queue.append((new_id, response_data.evidence_urls))
            
            # Map boolean to text if needed
            if response_data.response_boolean is not None:
                # We do this check loosely, or we could check param type if we had efficient access
                # For bulk, let's just assume if boolean is provided, we store in text as fallback
                if insert_data.get("response_text") is None:
                    insert_data["response_text"] = "true" if response_data.response_boolean else "false"
                    print(f"DEBUG: [ResponseService] Mapped boolean {response_data.response_boolean} to text {insert_data['response_text']}", flush=True)
        
        # 5. Bulk writes
        if new_responses_data:
            self.db.bulk_insert_mappings(AuditResponse, new_responses_data)
        if update_responses_data:
            self.db.bulk_update_mappings(AuditResponse, update_responses_data)
            
        # 6. Process evidence URLs
        for resp_id, urls in evidence_processing_queue:
            self._process_evidence_urls(audit_id, resp_id, urls, user_id)
            
        self.db.commit()
        
        return self.db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit_id,
            AuditResponse.id.in_(response_ids_to_return)
        ).all()

    def _check_audit_status(self, audit_id: UUID) -> Audit:
        """Helper to validate audit existence and status"""
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(message=f"Audit {audit_id} not found", error_code="AUDIT_NOT_FOUND")
        
        # Only block if finalized or shared
        if audit.status in [AuditStatus.FINALIZED, AuditStatus.SHARED]:
            raise PermissionError(message=f"Cannot submit responses to {audit.status.lower()} audit", error_code="AUDIT_LOCKED")
        return audit

    def _process_response_internal(
        self,
        audit_id: UUID,
        data: ResponseSubmit,
        user_id: UUID
    ) -> AuditResponse:
        """Internal method to process a single response submission without committing."""
        param_instance = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.id == data.audit_parameter_instance_id,
            AuditParameterInstance.audit_id == audit_id
        ).first()
        
        if not param_instance:
            raise NotFoundError(message="Parameter instance not found", error_code="PARAMETER_NOT_FOUND")
        
        validation_result = self._validate_response(data, param_instance.parameter_snapshot)
        if not validation_result.valid:
            raise ValidationError(message=validation_result.error, error_code="VALIDATION_ERROR")
        
        existing_response = self.db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit_id,
            AuditResponse.audit_parameter_instance_id == data.audit_parameter_instance_id
        ).first()
        
        if existing_response:
            existing_response.response_text = data.response_text
            existing_response.response_numeric = Decimal(str(data.response_numeric)) if data.response_numeric is not None else None
            existing_response.response_date = data.response_date
            existing_response.response_options = data.response_options
            existing_response.notes = data.notes
            if data.evidence_urls:
                self._process_evidence_urls(audit_id, existing_response.id, data.evidence_urls, user_id)
            return existing_response
        
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
        # WORKAROUND: Map boolean to text since column missing
        if data.response_boolean is not None and not response.response_text:
             response.response_text = "true" if data.response_boolean else "false"
             
        self.db.add(response)
        self.db.flush()
        if data.evidence_urls:
            self._process_evidence_urls(audit_id, response.id, data.evidence_urls, user_id)
        return response
    
    def update_response(
        self,
        audit_id: UUID,
        response_id: UUID,
        data: ResponseUpdate,
        user_id: UUID
    ) -> AuditResponse:
        """Update an existing audit response."""
        response = self.db.query(AuditResponse).filter(
            AuditResponse.id == response_id,
            AuditResponse.audit_id == audit_id
        ).first()
        
        if not response:
            raise NotFoundError(message="Response not found", error_code="RESPONSE_NOT_FOUND")
        
        self._check_audit_status(audit_id)
        
        param_instance = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.id == response.audit_parameter_instance_id
        ).first()
        
        validation_data = ResponseSubmit(
            audit_parameter_instance_id=response.audit_parameter_instance_id,
            response_text=data.response_text,
            response_numeric=data.response_numeric,
            response_date=data.response_date,
            response_options=data.response_options,
            notes=data.notes
        )
        
        validation_result = self._validate_response(validation_data, param_instance.parameter_snapshot)
        if not validation_result.valid:
            raise ValidationError(message=validation_result.error, error_code="VALIDATION_ERROR")
        
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

        # WORKAROUND: Map boolean to text since column missing
        if data.response_boolean is not None:
            response.response_text = "true" if data.response_boolean else "false"

        if data.evidence_urls:
             self._process_evidence_urls(audit_id, response.id, data.evidence_urls, user_id)

        self.db.commit()
        self.db.refresh(response)
        return response
    
    def get_audit_responses(
        self,
        audit_id: UUID,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Get all responses for an audit with hydrated metadata and review overrides."""
        # Join with AuditReview to get overrides
        from app.models.audit import AuditReview
        
        results = self.db.query(
            AuditResponse, AuditParameterInstance, AuditReview
        ).join(
            AuditParameterInstance, 
            AuditResponse.audit_parameter_instance_id == AuditParameterInstance.id
        ).outerjoin(
            AuditReview,
            AuditResponse.id == AuditReview.audit_response_id
        ).filter(
            AuditResponse.audit_id == audit_id
        ).order_by(AuditResponse.created_at).all()
        
        photos = self.db.query(AuditResponsePhoto).filter(
            AuditResponsePhoto.audit_id == audit_id,
            AuditResponsePhoto.audit_response_id.isnot(None)
        ).all()
        
        # Map photos to response IDs
        photos_by_response = {}
        for photo in photos:
            if photo.audit_response_id not in photos_by_response:
                photos_by_response[photo.audit_response_id] = []
            
            url = photo.file_url
            if url and url.startswith("uploads/"):
                url = f"/{url}"
            photos_by_response[photo.audit_response_id].append(url)
            
        hydrated_responses = []
        
        for response, param_instance, review in results:
            snapshot = param_instance.parameter_snapshot or {}
            param_type = snapshot.get("parameter_type")
            
            translations = snapshot.get("translations", {})
            param_name = translations.get(language, {}).get("name", "")
            if not param_name and translations:
                param_name = translations.get("en", {}).get("name", "")
                
            # PRIORITIZE REVIEW OVERRIDES
            # Check review fields. AuditReview fields are response_text, response_numeric, response_date, response_option_ids
            res_text = response.response_text
            res_numeric = response.response_numeric
            res_date = response.response_date
            res_options = response.response_options
            
            if review:
                if review.response_text is not None:
                    res_text = review.response_text
                if review.response_numeric is not None:
                    res_numeric = review.response_numeric
                if review.response_date is not None:
                    res_date = review.response_date
                if review.response_option_ids is not None:
                    res_options = review.response_option_ids
                # Map boolean override from text if type matches
                if param_type == 'BOOLEAN' and review.response_text:
                    res_boolean = review.response_text.lower() == 'true'

            option_labels = []
            if param_type in ["SINGLE_SELECT", "MULTI_SELECT"] and res_options:
                options = snapshot.get("options", [])
                for opt_id in res_options:
                    option_def = next((o for o in options if o.get("option_id") == str(opt_id)), None)
                    if option_def:
                        opt_trans = option_def.get("translations", {})
                        label = opt_trans.get(language, "")
                        if not label:
                            label = opt_trans.get("en", "")
                        if label:
                            option_labels.append(label)
            
            response_dict = {
                "id": response.id,
                "audit_id": response.audit_id,
                "audit_parameter_instance_id": response.audit_parameter_instance_id,
                "parameter_name": param_name,
                "parameter_type": param_type,
                "parameter_code": snapshot.get("code"),
                "response_text": res_text,
                "response_numeric": res_numeric,
                "response_date": res_date,
                "response_boolean": (res_text.lower() == 'true') if param_type == 'BOOLEAN' and res_text else None, 
                "response_options": res_options,
                "response_option_labels": option_labels if option_labels else None,
                "notes": response.notes,
                "evidence_urls": photos_by_response.get(response.id, []),
                "created_at": response.created_at,
                "updated_at": response.updated_at,
                "created_by": response.created_by,
                "is_flagged_for_report": review.is_flagged_for_report if review else False
            }
            hydrated_responses.append(response_dict)
        
        return hydrated_responses
    
    def _process_evidence_urls(self, audit_id: UUID, response_id: UUID, urls: List[str], user_id: UUID):
        """Link evidence photos to response."""
        for url in urls:
            existing_photo = self.db.query(AuditResponsePhoto).filter(
                AuditResponsePhoto.audit_id == audit_id,
                AuditResponsePhoto.file_url == url,
                AuditResponsePhoto.audit_response_id.is_(None)
            ).first()
            
            if existing_photo:
                existing_photo.audit_response_id = response_id
            else:
                already_linked = self.db.query(AuditResponsePhoto).filter(
                    AuditResponsePhoto.audit_response_id == response_id,
                    AuditResponsePhoto.file_url == url
                ).first()
                if not already_linked:
                    photo = AuditResponsePhoto(
                        audit_id=audit_id,
                        audit_response_id=response_id,
                        file_url=url,
                        uploaded_by=user_id
                    )
                    self.db.add(photo)
    
    def _validate_response(
        self,
        response: ResponseSubmit,
        snapshot: Dict[str, Any]
    ) -> ValidationResult:
        """Validate response against parameter snapshot."""
        param_type = snapshot.get('parameter_type')
        metadata = snapshot.get('parameter_metadata', {})
        
        if param_type == 'TEXT':
            return ValidationResult(True)
        
        elif param_type == 'NUMERIC':
            if response.response_numeric is not None:
                min_value = metadata.get('min_value')
                max_value = metadata.get('max_value')
                if min_value is not None and response.response_numeric < min_value:
                    return ValidationResult(False, f"Value must be at least {min_value}")
                if max_value is not None and response.response_numeric > max_value:
                    return ValidationResult(False, f"Value must be at most {max_value}")
            return ValidationResult(True)
        
        elif param_type == 'DATE':
            return ValidationResult(True)
        
        elif param_type == 'SINGLE_SELECT':
            if response.response_options and len(response.response_options) != 1:
                return ValidationResult(False, "Must select exactly one option")
            if response.response_options:
                options = snapshot.get('options', [])
                valid_option_ids = [UUID(opt['option_id']) for opt in options]
                if response.response_options[0] not in valid_option_ids:
                    return ValidationResult(False, "Invalid option selected")
            return ValidationResult(True)
        
        elif param_type == 'MULTI_SELECT':
            if response.response_options:
                options = snapshot.get('options', [])
                valid_option_ids = [UUID(opt['option_id']) for opt in options]
                for opt_id in response.response_options:
                    if opt_id not in valid_option_ids:
                        return ValidationResult(False, f"Invalid option: {opt_id}")
            return ValidationResult(True)
        
        elif param_type == 'BOOLEAN':
            return ValidationResult(True)
            
        elif param_type == 'PHOTO':
            return ValidationResult(True)
        
        return ValidationResult(False, f"Unknown parameter type: {param_type}")
