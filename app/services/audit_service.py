"""
Audit Service for Farm Audit Management System.

This service manages audit creation, lifecycle, and operations.
Handles audit creation with snapshot generation, audit number generation,
and farming organization derivation from crops.
"""

from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError, ConflictError
from app.models.audit import Audit, AuditParameterInstance
from app.models.template import Template, TemplateSection, TemplateParameter
from app.models.crop import Crop
from app.models.plot import Plot
from app.models.farm import Farm
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import AuditStatus, SyncStatus
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
        audit_date: Optional[date] = None
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
            status=AuditStatus.DRAFT,
            template_snapshot=template_snapshot,
            audit_date=audit_date,
            sync_status=SyncStatus.SYNCED,
            created_by=user_id
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
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND",
                details={"audit_id": str(audit_id)}
            )
        return audit

    def get_audits(
        self,
        fsp_organization_id: Optional[UUID] = None,
        farming_organization_id: Optional[UUID] = None,
        crop_id: Optional[UUID] = None,
        status: Optional[AuditStatus] = None,
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
            page: Page number (1-indexed)
            limit: Items per page
            
        Returns:
            Tuple of (audits list, total count)
        """
        query = self.db.query(Audit)

        # Apply filters
        if fsp_organization_id:
            query = query.filter(Audit.fsp_organization_id == fsp_organization_id)
        if farming_organization_id:
            query = query.filter(Audit.farming_organization_id == farming_organization_id)
        if crop_id:
            query = query.filter(Audit.crop_id == crop_id)
        if status:
            query = query.filter(Audit.status == status)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * limit
        audits = query.order_by(Audit.created_at.desc()).offset(offset).limit(limit).all()

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
            sections_map[section_id].append({
                "instance_id": str(instance.id),
                "parameter_id": str(instance.parameter_id),
                "is_required": instance.is_required,
                "sort_order": instance.sort_order,
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
