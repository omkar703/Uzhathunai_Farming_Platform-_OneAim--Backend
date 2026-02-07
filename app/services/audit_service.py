"""
Audit Service for Farm Audit Management System.

This service manages audit creation, lifecycle, and operations.
Handles audit creation with snapshot generation, audit number generation,
and farming organization derivation from crops.
"""

from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from sqlalchemy.orm import joinedload

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError, ConflictError
from app.models.audit import Audit, AuditParameterInstance, AuditIssue, AuditResponse, AuditRecommendation, AuditReview, AuditResponsePhoto
from app.models.schedule import ScheduleChangeLog
from app.models.template import Template, TemplateSection, TemplateParameter
from app.models.crop import Crop
from app.models.plot import Plot
from app.models.farm import Farm
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import AuditStatus, SyncStatus, ScheduleChangeTrigger
from app.services.snapshot_service import SnapshotService

logger = get_logger(__name__)


class AuditService:
    """
    Service for managing audits and audit lifecycle.
    
    Handles audit creation with snapshot generation, audit number generation,
    farming organization derivation, and audit lifecycle management.
    """

    def __init__(self, db: Session):
        self.db = db
        self.snapshot_service = SnapshotService(db)

    def create_audit(
        self,
        template_id: UUID,
        crop_id: UUID,
        fsp_organization_id: UUID,
        name: str,
        user_id: UUID,
        work_order_id: Optional[UUID] = None,
        audit_date: Optional[date] = None,
        assigned_to: Optional[UUID] = None
    ) -> Audit:
        """
        Create a new audit from a template for a specific crop.
        
        This method:
        1. Validates template and crop exist
        2. Derives farming_organization_id from crop
        3. Generates unique audit_number (AUD-YYYY-NNNN)
        4. Creates template snapshot
        5. Creates audit record
        6. Creates audit_parameter_instances with parameter snapshots
        7. Initializes sync_status as 'synced'
        
        Args:
            template_id: UUID of the template to use
            crop_id: UUID of the crop being audited
            fsp_organization_id: UUID of the FSP organization conducting the audit
            name: Name for the audit
            user_id: ID of the user creating the audit
            work_order_id: Optional work order ID
            audit_date: Optional audit date (defaults to today)
            
        Returns:
            Created audit with parameter instances
            
        Raises:
            NotFoundError: If template or crop not found
            ValidationError: If crop's organization cannot be determined
        """
        logger.info(
            "Creating audit",
            extra={
                "template_id": str(template_id),
                "crop_id": str(crop_id),
                "fsp_organization_id": str(fsp_organization_id),
                "user_id": str(user_id)
            }
        )

        # Validate template exists
        template = self.db.query(Template).filter(Template.id == template_id).first()
        if not template:
            raise NotFoundError(
                message=f"Template {template_id} not found",
                error_code="TEMPLATE_NOT_FOUND",
                details={"template_id": str(template_id)}
            )

        # Validate crop exists
        crop = self.db.query(Crop).filter(Crop.id == crop_id).first()
        if not crop:
            raise NotFoundError(
                message=f"Crop {crop_id} not found",
                error_code="CROP_NOT_FOUND",
                details={"crop_id": str(crop_id)}
            )

        # Derive farming_organization_id from crop
        # Hierarchy: Crop → Plot → Farm → Organization
        farming_organization_id = self._derive_farming_organization(crop)

        # Generate unique audit number
        audit_number = self._generate_audit_number()

        # Create template snapshot
        template_snapshot = self.snapshot_service.create_template_snapshot(template_id)

        # Set audit date
        if audit_date is None:
            audit_date = date.today()

        # Create audit
        audit = Audit(
            fsp_organization_id=fsp_organization_id,
            farming_organization_id=farming_organization_id,
            work_order_id=work_order_id,
            crop_id=crop_id,
            template_id=template_id,
            audit_number=audit_number,
            name=name,
            status=AuditStatus.PENDING if assigned_to else AuditStatus.DRAFT,
            template_snapshot=template_snapshot,
            audit_date=audit_date,
            sync_status=SyncStatus.PENDING_SYNC,
            created_by=user_id,
            assigned_to_user_id=assigned_to
        )

        self.db.add(audit)
        self.db.flush()

        # Create audit_parameter_instances
        self._create_parameter_instances(audit, template_snapshot, user_id)

        self.db.commit()
        self.db.refresh(audit)

        logger.info(
            "Audit created successfully",
            extra={
                "audit_id": str(audit.id),
                "audit_number": audit_number,
                "farming_organization_id": str(farming_organization_id),
                "parameter_instances_count": len(audit.parameter_instances)
            }
        )

        return audit

    def _derive_farming_organization(self, crop: Crop) -> UUID:
        """
        Derive farming organization ID from crop.
        
        Follows hierarchy: Crop → Plot → Farm → Organization
        
        Args:
            crop: Crop instance
            
        Returns:
            UUID of the farming organization
            
        Raises:
            ValidationError: If organization cannot be determined
        """
        # Get plot
        plot = self.db.query(Plot).filter(Plot.id == crop.plot_id).first()
        if not plot:
            raise ValidationError(
                message=f"Plot not found for crop {crop.id}",
                error_code="PLOT_NOT_FOUND",
                details={"crop_id": str(crop.id), "plot_id": str(crop.plot_id)}
            )

        # Get farm
        farm = self.db.query(Farm).filter(Farm.id == plot.farm_id).first()
        if not farm:
            raise ValidationError(
                message=f"Farm not found for plot {plot.id}",
                error_code="FARM_NOT_FOUND",
                details={"plot_id": str(plot.id), "farm_id": str(plot.farm_id)}
            )

        # Get organization
        organization = self.db.query(Organization).filter(
            Organization.id == farm.organization_id
        ).first()
        if not organization:
            raise ValidationError(
                message=f"Organization not found for farm {farm.id}",
                error_code="ORGANIZATION_NOT_FOUND",
                details={"farm_id": str(farm.id), "organization_id": str(farm.organization_id)}
            )

        logger.info(
            "Farming organization derived",
            extra={
                "crop_id": str(crop.id),
                "plot_id": str(plot.id),
                "farm_id": str(farm.id),
                "organization_id": str(organization.id)
            }
        )

        return organization.id

    def _generate_audit_number(self) -> str:
        """
        Generate unique audit number in format AUD-YYYY-NNNN.
        
        NNNN is a sequential number within the year, zero-padded to 4 digits.
        
        Returns:
            Unique audit number string
        """
        current_year = datetime.now().year

        # Get the count of audits created this year
        count = self.db.query(func.count(Audit.id)).filter(
            extract('year', Audit.created_at) == current_year
        ).scalar()

        # Generate next number (count + 1)
        next_number = (count or 0) + 1

        # Format as AUD-YYYY-NNNN
        audit_number = f"AUD-{current_year}-{next_number:04d}"

        # Check if number already exists (race condition protection)
        existing = self.db.query(Audit).filter(
            Audit.audit_number == audit_number
        ).first()

        if existing:
            # If exists, try next number
            next_number += 1
            audit_number = f"AUD-{current_year}-{next_number:04d}"

        logger.info(
            "Audit number generated",
            extra={"audit_number": audit_number, "year": current_year}
        )

        return audit_number

    def _create_parameter_instances(
        self,
        audit: Audit,
        template_snapshot: Dict[str, Any],
        user_id: UUID
    ) -> None:
        """
        Create audit_parameter_instances from template snapshot.
        
        Creates an instance for each parameter in the template with a complete
        parameter snapshot.
        
        Args:
            audit: Audit instance
            template_snapshot: Complete template snapshot
            user_id: ID of the user creating the audit
        """
        logger.info(
            "Creating parameter instances",
            extra={"audit_id": str(audit.id)}
        )

        instance_count = 0

        for section in template_snapshot.get("sections", []):
            section_id = UUID(section["section_id"])

            # Get template_section_id
            template_section = self.db.query(TemplateSection).filter(
                and_(
                    TemplateSection.template_id == audit.template_id,
                    TemplateSection.section_id == section_id
                )
            ).first()

            if not template_section:
                logger.warning(
                    "Template section not found",
                    extra={
                        "template_id": str(audit.template_id),
                        "section_id": str(section_id)
                    }
                )
                continue

            for parameter in section.get("parameters", []):
                parameter_id = UUID(parameter["parameter_id"])
                parameter_snapshot = parameter["parameter_snapshot"]

                # Create audit parameter instance
                instance = AuditParameterInstance(
                    audit_id=audit.id,
                    template_section_id=template_section.id,
                    parameter_id=parameter_id,
                    sort_order=parameter["sort_order"],
                    is_required=parameter["is_required"],
                    parameter_snapshot=parameter_snapshot,
                    created_by=user_id
                )

                self.db.add(instance)
                instance_count += 1

        logger.info(
            "Parameter instances created",
            extra={
                "audit_id": str(audit.id),
                "instance_count": instance_count
            }
        )

    def get_audit(self, audit_id: UUID) -> Audit:
        """
        Get audit by ID.
        
        Args:
            audit_id: UUID of the audit
            
        Returns:
            Audit instance
            
        Raises:
            NotFoundError: If audit not found
        """
        audit = self.db.query(Audit).options(
            joinedload(Audit.assigned_to),
            joinedload(Audit.analyst),
            joinedload(Audit.fsp_organization)
        ).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND",
                details={"audit_id": str(audit_id)}
            )
        
        # Calculate and attach progress
        audit.progress = self._calculate_progress(audit_id)
        
        return audit

    def assign_audit(
        self,
        audit_id: UUID,
        assigned_to: Optional[UUID] = None,
        analyst_id: Optional[UUID] = None,
        user_id: UUID = None
    ) -> Audit:
        """
        Assign an audit to a field officer or analyst.
        
        Args:
            audit_id: UUID of the audit
            assigned_to: UUID of the field officer (optional)
            analyst_id: UUID of the analyst (optional)
            user_id: ID of the user performing the assignment
            
        Returns:
            Updated audit
        """
        audit = self.get_audit(audit_id)
        
        # Update assignments if provided
        if assigned_to is not None:
            # Verify user exists (optional, but good practice)
            # For now assuming integrity constraint handles it or we trust input
            audit.assigned_to_user_id = assigned_to
            
            # If assigning to FO and status is DRAFT, move to PENDING
            if audit.status == AuditStatus.DRAFT:
                audit.status = AuditStatus.PENDING
                
        if analyst_id is not None:
            audit.analyst_user_id = analyst_id
            
            # If assigning to Analyst and status is SUBMITTED, move to IN_ANALYSIS?
            # Or SUBMITTED_FOR_REVIEW?
            # Let's keep it simple for now, simple assignment shouldn't auto-transition unlikely states
            # unless specific workflow.
            if audit.status == AuditStatus.SUBMITTED:
                 audit.status = AuditStatus.IN_ANALYSIS

        audit.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(audit)
        
        logger.info(
            "Audit assigned",
            extra={
                "audit_id": str(audit.id),
                "assigned_to": str(assigned_to) if assigned_to else None,
                "analyst_id": str(analyst_id) if analyst_id else None,
                "user_id": str(user_id)
            }
        )
        
        return audit

    def _calculate_progress(self, audit_id: UUID) -> float:
        """
        Calculate audit completion progress.
        
        Progress is defined as the percentage of mandatory parameters that have responses.
        If no mandatory parameters exist, uses total parameters.
        """
        # Get all instances
        instances = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.audit_id == audit_id
        ).all()
        
        if not instances:
            return 0.0
            
        # Get response count
        response_count = self.db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit_id
        ).count()
        
        # Simple progress: responses / total instances
        # A more sophisticated version would only count mandatory or specific types
        # but this matches the "answered / total" logic requested.
        progress = (response_count / len(instances)) * 100.0
        return round(min(progress, 100.0), 1)

    def delete_audit(
        self,
        audit_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete an audit.
        
        Args:
            audit_id: UUID of the audit
            user_id: ID of the user requesting deletion
            
        Raises:
            NotFoundError: If audit not found
        """
        audit = self.get_audit(audit_id)
        
        logger.info(
            "Deleting audit",
            extra={
                "audit_id": str(audit_id),
                "user_id": str(user_id)
            }
        )
        
        self.db.delete(audit)
        self.db.commit()

    def get_audits(
        self,
        fsp_organization_id: Optional[UUID] = None,
        farming_organization_id: Optional[UUID] = None,
        crop_id: Optional[UUID] = None,
        status: Optional[AuditStatus] = None,
        assigned_to_user_id: Optional[UUID] = None,
        created_by_user_id: Optional[UUID] = None,
        analyst_user_id: Optional[UUID] = None,
        work_order_id: Optional[UUID] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Audit], int]:
        """
        Get audits with filtering and pagination.
        
        Args:
            fsp_organization_id: Filter by FSP organization
            farming_organization_id: Filter by farming organization
            crop_id: Filter by crop
            status: Filter by status
            assigned_to_user_id: Filter by assigned user
            created_by_user_id: Filter by creator
            page: Page number (1-indexed)
            limit: Items per page
            
        Returns:
            Tuple of (audits list, total count)
        """
        logger.info(f"DEBUG: [S1] Entering get_audits. farming_org_id={farming_organization_id}")
        query = self.db.query(Audit)
        
        # DEBUG: Dump all audits in DB to see what org IDs they have
        all_audits = self.db.query(Audit).limit(10).all()
        print(f"!!! DEBUG: Total audits in DB (limit 10): {len(all_audits)}", flush=True)
        for idx, a in enumerate(all_audits):
            print(f"!!! DEBUG: Audit[{idx}]: id={a.id}, farming_org={a.farming_organization_id}, status={a.status}", flush=True)

        # DEBUG: System-wide check
        all_count = self.db.query(func.count(Audit.id)).scalar()
        logger.info(f"DEBUG: [S2] Total audits in DB (any org): {all_count}")
        if all_count > 0:
            sample = self.db.query(Audit).limit(3).all()
            for s in sample:
                logger.info(f"DEBUG: [S3] Sample Audit: id={s.id}, farming_org={s.farming_organization_id}, status={s.status}")

        # Apply filters
        if fsp_organization_id:
            query = query.filter(Audit.fsp_organization_id == fsp_organization_id)
        if farming_organization_id:
            # DEBUG: print statements bypass logging config
            print(f"!!! DEBUG: [S1] Entering get_audits for org: {farming_organization_id}", flush=True)
            temp_all = self.db.query(Audit).filter(Audit.farming_organization_id == farming_organization_id).all()
            print(f"!!! DEBUG: [S2] Total audits for org {farming_organization_id} (ignoring status): {len(temp_all)}", flush=True)
            for a in temp_all:
                print(f"!!! DEBUG: [S3] Audit {a.id} status: {a.status}", flush=True)
                
            # BROAD FILTER: Show all audits for farmer during debugging
            query = query.filter(Audit.farming_organization_id == farming_organization_id)
        if crop_id:
            query = query.filter(Audit.crop_id == crop_id)
        if status:
            query = query.filter(Audit.status == status)
        if assigned_to_user_id:
            query = query.filter(Audit.assigned_to_user_id == assigned_to_user_id)
        if created_by_user_id:
            query = query.filter(Audit.created_by == created_by_user_id)
        if analyst_user_id:
            query = query.filter(Audit.analyst_user_id == analyst_user_id)
        if work_order_id:
            query = query.filter(Audit.work_order_id == work_order_id)
        
        # Eager load relationships for list view
        query = query.options(
            joinedload(Audit.assigned_to),
            joinedload(Audit.analyst),
            joinedload(Audit.fsp_organization)
        )

        # Get total count
        total = query.count()
        logger.info(f"DEBUG: get_audits called with farming_org_id={farming_organization_id}, fsp_org_id={fsp_organization_id}, status={status}")
        logger.info(f"DEBUG: Found {total} audits matching criteria")

        # Apply pagination
        offset = (page - 1) * limit
        audits = query.order_by(Audit.created_at.desc()).offset(offset).limit(limit).all()

        # Calculate progress for each audit
        for audit in audits:
            audit.progress = self._calculate_progress(audit.id)

        return audits, total

    def get_audit_structure(self, audit_id: UUID) -> Dict[str, Any]:
        """
        Get audit structure with sections and parameters from snapshots.
        
        Returns the complete audit structure including template snapshot
        and parameter instances with their snapshots.
        
        Args:
            audit_id: UUID of the audit
            
        Returns:
            Dictionary containing audit structure
            
        Raises:
            NotFoundError: If audit not found
        """
        audit = self.get_audit(audit_id)

        # Get parameter instances
        instances = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.audit_id == audit_id
        ).order_by(AuditParameterInstance.sort_order).all()

        # Build structure from template snapshot
        structure = {
            "audit_id": str(audit.id),
            "audit_number": audit.audit_number,
            "name": audit.name,
            "status": audit.status.value,
            "template_snapshot": audit.template_snapshot,
            "sections": []
        }

        # Group instances by section
        sections_map = {}
        for instance in instances:
            section_id = str(instance.template_section_id)
            if section_id not in sections_map:
                sections_map[section_id] = []
            # Extract name from snapshot
            name = None
            snapshot = instance.parameter_snapshot
            if snapshot and "translations" in snapshot:
                translations = snapshot["translations"]
                if "en" in translations:
                    name = translations["en"].get("name")
                elif translations:
                    # Fallback to first available
                    first_lang = next(iter(translations))
                    name = translations[first_lang].get("name")
            
            sections_map[section_id].append({
                "instance_id": str(instance.id),
                "parameter_id": str(instance.parameter_id),
                "is_required": instance.is_required,
                "sort_order": instance.sort_order,
                "name": name,
                "parameter_snapshot": instance.parameter_snapshot
            })

        # Build sections from template snapshot
        if audit.template_snapshot:
            for section in audit.template_snapshot.get("sections", []):
                section_id = section.get("section_id")
                # Find template_section_id for this section
                template_section = self.db.query(TemplateSection).filter(
                    and_(
                        TemplateSection.template_id == audit.template_id,
                        TemplateSection.section_id == UUID(section_id)
                    )
                ).first()

                if template_section:
                    section_data = {
                        "section_id": section_id,
                        "code": section.get("code"),
                        "translations": section.get("translations", {}),
                        "parameters": sections_map.get(str(template_section.id), [])
                    }
                    structure["sections"].append(section_data)

        return structure

    def get_audit_report(self, audit_id: UUID) -> Dict[str, Any]:
        """
        Get comprehensive audit report with stats.
        
        Args:
            audit_id: UUID of the audit
            
        Returns:
            Dictionary matching AuditReportResponse schema
        """
        # Get audit with related data
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND",
                details={"audit_id": str(audit_id)}
            )

        # Get instances and responses
        instances = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.audit_id == audit_id
        ).all()
        
        responses = self.db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit_id
        ).all()
        
        # Create map of instance_id -> response
        response_map = {r.audit_parameter_instance_id: r for r in responses}
        
        # Calculate stats
        total_mandatory = 0
        answered_mandatory = 0
        total_optional = 0
        answered_optional = 0
        
        for instance in instances:
            has_response = False
            response = response_map.get(instance.id)
            if response:
                # Check if response is "valid" / non-empty
                has_response = (
                    response.response_text is not None or
                    response.response_numeric is not None or
                    response.response_date is not None or
                    (response.response_options is not None and len(response.response_options) > 0)
                )
            
            if instance.is_required:
                total_mandatory += 1
                if has_response:
                    answered_mandatory += 1
            else:
                total_optional += 1
                if has_response:
                    answered_optional += 1
                    
        # Calculate compliance score (percentage of mandatory answered)
        compliance_score = 0.0
        if total_mandatory > 0:
            compliance_score = (answered_mandatory / total_mandatory) * 100.0
        elif total_optional > 0:
            # If no mandatory, base on optional? Or 100?
            # Let's say 100 if no mandatory requirements exists and audit is done?
            # For now, 0 if nothing to do, or 100?
            compliance_score = 100.0
            
        # Get issues
        issues = self.db.query(AuditIssue).filter(
            AuditIssue.audit_id == audit_id
        ).all()
        
        issues_stats = {}
        for issue in issues:
            severity = issue.severity.value if issue.severity else "UNKNOWN"
            issues_stats[severity] = issues_stats.get(severity, 0) + 1
            
        # Get recommendations (ScheduleChangeLog linked to this audit)
        schedule_recommendations = self.db.query(ScheduleChangeLog).filter(
            and_(
                ScheduleChangeLog.trigger_type == ScheduleChangeTrigger.AUDIT,
                ScheduleChangeLog.trigger_reference_id == audit_id
            )
        ).all()

        # Get standalone recommendations
        standalone_recommendations = self.db.query(AuditRecommendation).filter(
            AuditRecommendation.audit_id == audit_id
        ).all()

        # Get flagged reviews (responses)
        flagged_reviews = self.db.query(AuditReview).options(
            joinedload(AuditReview.audit_response)
        ).filter(
            AuditReview.is_flagged_for_report == True,
            AuditReview.audit_response.has(AuditResponse.audit_id == audit_id)
        ).all()

        flagged_responses_data = []
        for review in flagged_reviews:
            resp = review.audit_response
            param_instance = self.db.query(AuditParameterInstance).filter(
                AuditParameterInstance.id == resp.audit_parameter_instance_id
            ).first()
            
            param_name = "Unknown Parameter"
            param_type = "TEXT"
            options = []
            if param_instance and param_instance.parameter_snapshot:
                snapshot = param_instance.parameter_snapshot
                param_type = snapshot.get("parameter_type", "TEXT")
                options = snapshot.get("options", [])
                translations = snapshot.get('translations', {})
                if 'en' in translations:
                    param_name = translations['en'].get('name')
                elif translations:
                    first = next(iter(translations))
                    param_name = translations[first].get('name')

            def format_val(r_obj, p_type, opts, fallback_obj=None):
                if not r_obj and not fallback_obj: return "N/A"
                
                def get_v(attr):
                    v = getattr(r_obj, attr, None) if r_obj else None
                    if v is None and fallback_obj:
                        v = getattr(fallback_obj, attr, None)
                    return v

                if p_type == "TEXT": 
                    return get_v("response_text") or "N/A"
                if p_type == "NUMERIC": 
                    v = get_v("response_numeric")
                    return str(v) if v is not None else "N/A"
                if p_type == "DATE": 
                    v = get_v("response_date")
                    return str(v) if v is not None else "N/A"
                if p_type in ["SINGLE_SELECT", "MULTI_SELECT"]:
                    # Handle naming mismatch
                    ids = getattr(r_obj, "response_option_ids", None) if r_obj else None
                    if ids is None:
                        ids = getattr(r_obj, "response_options", None) if r_obj else None
                    if ids is None and fallback_obj:
                        ids = getattr(fallback_obj, "response_options", None)
                        
                    if ids:
                        labels = []
                        for opt_id in ids:
                            opt_def = next((o for o in opts if o.get("option_id") == str(opt_id)), None)
                            if opt_def:
                                o_trans = opt_def.get("translations", {})
                                labels.append(o_trans.get("en") or next(iter(o_trans.values())) if o_trans else str(opt_id))
                        return ", ".join(labels) if labels else "N/A"
                return "N/A"

            flagged_responses_data.append({
                "parameter_name": param_name,
                "original_response": format_val(resp, param_type, options),
                "reviewed_response": format_val(review, param_type, options, fallback_obj=resp),
                "is_flagged": True
            })

        # Get flagged photos
        flagged_photos = self.db.query(AuditResponsePhoto).filter(
            AuditResponsePhoto.audit_id == audit_id,
            AuditResponsePhoto.is_flagged_for_report == True
        ).all()
        
        flagged_photos_data = []
        for photo in flagged_photos:
            flagged_photos_data.append({
                "file_url": photo.file_url,
                "caption": photo.caption,
                "response_id": str(photo.audit_response_id) if photo.audit_response_id else None
            })
        
        return {
            "audit": audit,
            "stats": {
                "compliance_score": round(compliance_score, 1),
                "total_mandatory": total_mandatory,
                "answered_mandatory": answered_mandatory,
                "total_optional": total_optional,
                "answered_optional": answered_optional,
                "issues_by_severity": issues_stats
            },
            "issues": issues,
            "schedule_recommendations": schedule_recommendations,
            "standalone_recommendations": standalone_recommendations,
            "flagged_responses": flagged_responses_data,
            "flagged_photos": flagged_photos_data
        }
