"""
Snapshot Service for Farm Audit Management System.

This service creates immutable snapshots of templates and parameters at audit creation time.
Snapshots capture complete configuration including options, validation rules, and translations.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ServiceError
from app.models.parameter import Parameter, ParameterTranslation, ParameterOptionSetMap
from app.models.option_set import OptionSet, Option, OptionTranslation
from app.models.template import Template, TemplateTranslation, TemplateSection, TemplateParameter
from app.models.section import Section, SectionTranslation

logger = get_logger(__name__)


class SnapshotService:
    """
    Service for creating immutable snapshots of templates and parameters.
    
    Snapshots ensure audit data remains consistent even if templates or parameters
    are modified after audit creation.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_parameter_snapshot(self, parameter_id: UUID) -> Dict[str, Any]:
        """
        Create immutable parameter snapshot.
        
        Captures complete parameter configuration including:
        - Parameter metadata (type, validation rules, photo requirements)
        - Option set and options (if applicable)
        - All multilingual translations
        
        Args:
            parameter_id: UUID of the parameter
            
        Returns:
            Dictionary containing complete parameter snapshot
            
        Raises:
            NotFoundError: If parameter not found
        """
        logger.info(
            "Creating parameter snapshot",
            extra={"parameter_id": str(parameter_id)}
        )

        # Get parameter
        parameter = self.db.query(Parameter).filter(Parameter.id == parameter_id).first()
        if not parameter:
            raise NotFoundError(
                message=f"Parameter {parameter_id} not found",
                error_code="PARAMETER_NOT_FOUND",
                details={"parameter_id": str(parameter_id)}
            )

        # Build snapshot
        snapshot = {
            "parameter_id": str(parameter.id),
            "code": parameter.code,
            "parameter_type": parameter.parameter_type.value,
            "parameter_metadata": parameter.parameter_metadata or {},
            "option_set_id": None,
            "options": [],
            "translations": {},
            "snapshot_date": datetime.utcnow().isoformat()
        }

        # Get translations
        translations = self.db.query(ParameterTranslation).filter(
            ParameterTranslation.parameter_id == parameter_id
        ).all()

        for trans in translations:
            snapshot["translations"][trans.language_code] = {
                "name": trans.name,
                "description": trans.description,
                "help_text": trans.help_text
            }

        # Get option set and options (for SINGLE_SELECT and MULTI_SELECT)
        if parameter.parameter_type.value in ['SINGLE_SELECT', 'MULTI_SELECT']:
            option_set_map = self.db.query(ParameterOptionSetMap).filter(
                ParameterOptionSetMap.parameter_id == parameter_id
            ).first()

            if option_set_map:
                option_set = self.db.query(OptionSet).filter(
                    OptionSet.id == option_set_map.option_set_id
                ).first()

                if option_set:
                    snapshot["option_set_id"] = str(option_set.id)

                    # Get options
                    options = self.db.query(Option).filter(
                        Option.option_set_id == option_set.id,
                        Option.is_active == True
                    ).order_by(Option.sort_order).all()

                    for option in options:
                        option_data = {
                            "option_id": str(option.id),
                            "code": option.code,
                            "sort_order": option.sort_order,
                            "translations": {}
                        }

                        # Get option translations
                        option_translations = self.db.query(OptionTranslation).filter(
                            OptionTranslation.option_id == option.id
                        ).all()

                        for opt_trans in option_translations:
                            option_data["translations"][opt_trans.language_code] = opt_trans.display_text

                        snapshot["options"].append(option_data)

        logger.info(
            "Parameter snapshot created",
            extra={
                "parameter_id": str(parameter_id),
                "parameter_type": parameter.parameter_type.value,
                "has_options": len(snapshot["options"]) > 0
            }
        )

        return snapshot

    def create_template_snapshot(self, template_id: UUID) -> Dict[str, Any]:
        """
        Create immutable template snapshot.
        
        Captures complete template structure including:
        - Template metadata (code, version, crop type)
        - All sections with their parameters
        - All multilingual translations
        - Parameter snapshots for each parameter
        
        Args:
            template_id: UUID of the template
            
        Returns:
            Dictionary containing complete template snapshot
            
        Raises:
            NotFoundError: If template not found
        """
        logger.info(
            "Creating template snapshot",
            extra={"template_id": str(template_id)}
        )

        # Get template
        template = self.db.query(Template).filter(Template.id == template_id).first()
        if not template:
            raise NotFoundError(
                message=f"Template {template_id} not found",
                error_code="TEMPLATE_NOT_FOUND",
                details={"template_id": str(template_id)}
            )

        # Build snapshot
        snapshot = {
            "template_id": str(template.id),
            "code": template.code,
            "version": template.version,
            "crop_type_id": str(template.crop_type_id) if template.crop_type_id else None,
            "translations": {},
            "sections": [],
            "snapshot_date": datetime.utcnow().isoformat()
        }

        # Get template translations
        template_translations = self.db.query(TemplateTranslation).filter(
            TemplateTranslation.template_id == template_id
        ).all()

        for trans in template_translations:
            snapshot["translations"][trans.language_code] = {
                "name": trans.name,
                "description": trans.description
            }

        # Get template sections
        template_sections = self.db.query(TemplateSection).filter(
            TemplateSection.template_id == template_id
        ).order_by(TemplateSection.sort_order).all()

        for template_section in template_sections:
            # Get section details
            section = self.db.query(Section).filter(
                Section.id == template_section.section_id
            ).first()

            if not section:
                continue

            section_data = {
                "section_id": str(section.id),
                "code": section.code,
                "sort_order": template_section.sort_order,
                "translations": {},
                "parameters": []
            }

            # Get section translations
            section_translations = self.db.query(SectionTranslation).filter(
                SectionTranslation.section_id == section.id
            ).all()

            for sec_trans in section_translations:
                section_data["translations"][sec_trans.language_code] = {
                    "name": sec_trans.name,
                    "description": sec_trans.description
                }

            # Get template parameters for this section
            template_parameters = self.db.query(TemplateParameter).filter(
                TemplateParameter.template_section_id == template_section.id
            ).order_by(TemplateParameter.sort_order).all()

            for template_param in template_parameters:
                # Create parameter snapshot
                param_snapshot = self.create_parameter_snapshot(template_param.parameter_id)

                parameter_data = {
                    "parameter_id": str(template_param.parameter_id),
                    "is_required": template_param.is_required,
                    "sort_order": template_param.sort_order,
                    "parameter_snapshot": param_snapshot
                }

                section_data["parameters"].append(parameter_data)

            snapshot["sections"].append(section_data)

        logger.info(
            "Template snapshot created",
            extra={
                "template_id": str(template_id),
                "sections_count": len(snapshot["sections"]),
                "total_parameters": sum(len(s["parameters"]) for s in snapshot["sections"])
            }
        )

        return snapshot

    def validate_snapshot_integrity(self, snapshot: Dict[str, Any]) -> bool:
        """
        Validate snapshot integrity.
        
        Ensures snapshot contains all required fields and is properly structured.
        
        Args:
            snapshot: Snapshot dictionary to validate
            
        Returns:
            True if snapshot is valid, False otherwise
        """
        try:
            # Check required fields for parameter snapshot
            if "parameter_id" in snapshot:
                required_fields = ["parameter_id", "code", "parameter_type", "translations"]
                for field in required_fields:
                    if field not in snapshot:
                        logger.warning(
                            "Parameter snapshot missing required field",
                            extra={"field": field}
                        )
                        return False

            # Check required fields for template snapshot
            elif "template_id" in snapshot:
                required_fields = ["template_id", "code", "version", "sections"]
                for field in required_fields:
                    if field not in snapshot:
                        logger.warning(
                            "Template snapshot missing required field",
                            extra={"field": field}
                        )
                        return False

            return True

        except Exception as e:
            logger.error(
                "Snapshot validation failed",
                extra={"error": str(e)},
                exc_info=True
            )
            return False

    def get_option_display_text(
        self,
        snapshot: Dict[str, Any],
        option_id: UUID,
        language: str = "en"
    ) -> Optional[str]:
        """
        Get option display text from snapshot.
        
        Args:
            snapshot: Parameter snapshot containing options
            option_id: UUID of the option
            language: Language code (default: "en")
            
        Returns:
            Display text for the option in specified language, or None if not found
        """
        if "options" not in snapshot:
            return None

        for option in snapshot["options"]:
            if option.get("option_id") == str(option_id):
                translations = option.get("translations", {})
                return translations.get(language, translations.get("en"))

        return None
