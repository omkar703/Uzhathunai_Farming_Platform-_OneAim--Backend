"""
Report Service for Farm Audit Management System.

This service generates audit reports with selected content including:
- Audit details, template info, and crop info
- Only flagged responses and photos
- All issues categorized by severity
- All recommendations from schedule_change_log
- Multilingual support using parameter snapshots

Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError
from app.models.audit import (
    Audit, AuditResponse, AuditResponsePhoto, AuditReview, 
    AuditReviewPhoto, AuditIssue, AuditParameterInstance
)
from app.models.schedule import ScheduleChangeLog
from app.models.crop import Crop
from app.models.plot import Plot
from app.models.farm import Farm
from app.models.organization import Organization
from app.models.template import Template
from app.models.enums import IssueSeverity

logger = get_logger(__name__)


class ReportService:
    """
    Service for generating audit reports.
    
    Generates comprehensive audit reports with flagged content,
    issues, and recommendations. Supports multilingual report generation
    using parameter snapshots.
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_report(
        self,
        audit_id: UUID,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive audit report.
        
        Includes:
        - Audit details (audit number, name, date, status)
        - Template information
        - Crop and organization information
        - Only flagged responses (is_flagged_for_report = true)
        - Only flagged photos (is_flagged_for_report = true)
        - All issues categorized by severity
        - All recommendations from schedule_change_log
        - Uses parameter_snapshot for display text
        - Supports multilingual content
        
        Args:
            audit_id: UUID of the audit
            language: Language code for report (en, ta, ml)
            
        Returns:
            Dictionary containing complete report data
            
        Raises:
            NotFoundError: If audit not found
            ValidationError: If language not supported
            
        Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7
        """
        logger.info(
            "Generating audit report",
            extra={
                "audit_id": str(audit_id),
                "language": language
            }
        )

        # Validate language
        supported_languages = ["en", "ta", "ml"]
        if language not in supported_languages:
            raise ValidationError(
                message=f"Language '{language}' not supported",
                error_code="UNSUPPORTED_LANGUAGE",
                details={
                    "language": language,
                    "supported_languages": supported_languages
                }
            )

        # Get audit
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND",
                details={"audit_id": str(audit_id)}
            )

        # Get basic report details and stats from AuditService
        from app.services.audit_service import AuditService
        audit_service = AuditService(self.db)
        base_data = audit_service.get_audit_report(audit_id)

        # Flatten issues from dictionary to list
        issues_dict = self._get_issues_by_severity(audit)
        flattened_issues = []
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            flattened_issues.extend(issues_dict.get(severity, []))

        # Build report matching AuditReportResponse schema
        report = {
            "audit": self._get_audit_details(audit, language),
            "stats": base_data["stats"],
            "issues": flattened_issues,
            "recommendations": self._get_recommendations(audit),
            # Metadata and Enriched Content
            "template_info": self._get_template_info(audit, language),
            "crop_info": self._get_crop_info(audit),
            "organization_info": self._get_organization_info(audit),
            "flagged_responses": self._get_flagged_responses(audit, language),
            "flagged_photos": self._get_flagged_photos(audit),
            "generated_at": audit.created_at.isoformat() if audit.created_at else None,
            "language": language
        }

        logger.info(
            "Audit report generated and standardized",
            extra={
                "audit_id": str(audit_id),
                "language": language,
                "flagged_responses_count": len(report["flagged_responses"]),
                "flagged_photos_count": len(report["flagged_photos"]),
                "issues_count": len(report["issues"]),
                "recommendations_count": len(report["recommendations"])
            }
        )

        return report


    def _get_audit_details(self, audit: Audit, language: str) -> Dict[str, Any]:
        """Get audit details."""
        return {
            "id": audit.id,
            "audit_number": audit.audit_number,
            "name": audit.name,
            "audit_date": audit.audit_date,
            "status": audit.status,
            "created_at": audit.created_at,
            "updated_at": audit.updated_at,
            "finalized_at": audit.finalized_at,
            "shared_at": audit.shared_at,
            "fsp_organization_id": audit.fsp_organization_id,
            "farming_organization_id": audit.farming_organization_id,
            "crop_id": audit.crop_id,
            "template_id": audit.template_id,
            "created_by": audit.created_by
        }

    def _get_template_info(self, audit: Audit, language: str) -> Dict[str, Any]:
        """Get template information from snapshot."""
        template_snapshot = audit.template_snapshot or {}
        
        # Get template name from snapshot translations
        translations = template_snapshot.get("translations", {})
        template_name = translations.get(language, {}).get("name", "")
        if not template_name and translations:
            # Fallback to English if language not available
            template_name = translations.get("en", {}).get("name", "")
        
        return {
            "template_id": str(audit.template_id),
            "template_code": template_snapshot.get("code", ""),
            "template_name": template_name,
            "template_version": template_snapshot.get("version", 1),
            "crop_type_id": template_snapshot.get("crop_type_id")
        }

    def _get_crop_info(self, audit: Audit) -> Dict[str, Any]:
        """Get crop information."""
        crop = self.db.query(Crop).filter(Crop.id == audit.crop_id).first()
        if not crop:
            return {}
        
        variety_name = None
        if crop.crop_variety:
            # Try to get English translation or any available
            trans = next((t for t in crop.crop_variety.translations if t.language_code == "en"), None)
            if not trans and crop.crop_variety.translations:
                trans = crop.crop_variety.translations[0]
            variety_name = trans.name if trans else None

        return {
            "crop_id": str(crop.id),
            "crop_name": crop.name,
            "variety": variety_name,
            "planting_date": crop.planted_date.isoformat() if crop.planted_date else None,
            "expected_harvest_date": crop.completed_date.isoformat() if crop.completed_date else None
        }


    def _get_organization_info(self, audit: Audit) -> Dict[str, Any]:
        """Get FSP and farming organization information."""
        fsp_org = self.db.query(Organization).filter(
            Organization.id == audit.fsp_organization_id
        ).first()
        
        farming_org = self.db.query(Organization).filter(
            Organization.id == audit.farming_organization_id
        ).first()
        
        return {
            "fsp_organization": {
                "id": str(fsp_org.id) if fsp_org else None,
                "name": fsp_org.name if fsp_org else None
            },
            "farming_organization": {
                "id": str(farming_org.id) if farming_org else None,
                "name": farming_org.name if farming_org else None,
                "district": farming_org.district if farming_org else None
            }
        }

    def _get_flagged_responses(self, audit: Audit, language: str) -> List[Dict[str, Any]]:
        """
        Get only flagged responses (is_flagged_for_report = true).
        
        Uses parameter_snapshot for display text.
        
        Requirements: 18.2, 18.6
        """
        # Get all responses with reviews that are flagged
        flagged_responses = []
        
        responses = self.db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit.id
        ).all()
        
        for response in responses:
            # Check if response has a review that is flagged
            review = self.db.query(AuditReview).filter(
                AuditReview.audit_response_id == response.id,
                AuditReview.is_flagged_for_report == True
            ).first()
            
            if review:
                # Get parameter instance for snapshot
                param_instance = self.db.query(AuditParameterInstance).filter(
                    AuditParameterInstance.id == response.audit_parameter_instance_id
                ).first()
                
                if param_instance:
                    parameter_snapshot = param_instance.parameter_snapshot
                    
                    # Get parameter name from snapshot
                    param_translations = parameter_snapshot.get("translations", {})
                    param_name = param_translations.get(language, {}).get("name", "")
                    if not param_name and param_translations:
                        param_name = param_translations.get("en", {}).get("name", "")
                    
                    # Get response value (use review value if available, otherwise original)
                    response_value = self._format_response_value(
                        review if review else response,
                        parameter_snapshot,
                        language
                    )
                    
                    flagged_responses.append({
                        "id": response.id,
                        "audit_id": response.audit_id,
                        "audit_parameter_instance_id": response.audit_parameter_instance_id,
                        "parameter_name": param_name,
                        "parameter_code": parameter_snapshot.get("code", ""),
                        "parameter_type": parameter_snapshot.get("parameter_type", ""),
                        "response_value": response_value,
                        "notes": response.notes,
                        "created_at": response.created_at,
                        "updated_at": response.updated_at,
                        "created_by": response.created_by
                    })
        
        return flagged_responses

    def _format_response_value(
        self,
        response_or_review: Any,
        parameter_snapshot: Dict[str, Any],
        language: str
    ) -> str:
        """Format response value based on parameter type."""
        param_type = parameter_snapshot.get("parameter_type", "")
        
        if param_type == "TEXT":
            return response_or_review.response_text or ""
        
        elif param_type == "NUMERIC":
            if response_or_review.response_numeric is not None:
                unit = parameter_snapshot.get("parameter_metadata", {}).get("unit", "")
                return f"{response_or_review.response_numeric} {unit}".strip()
            return ""
        
        elif param_type == "DATE":
            if response_or_review.response_date:
                return response_or_review.response_date.isoformat()
            return ""
        
        elif param_type in ["SINGLE_SELECT", "MULTI_SELECT"]:
            # Handle naming mismatch between AuditResponse and AuditReview
            option_ids = getattr(response_or_review, "response_option_ids", None) or \
                         getattr(response_or_review, "response_options", None)
            
            if option_ids:
                # Get option display text from snapshot
                options = parameter_snapshot.get("options", [])
                option_texts = []
                
                for option_id in option_ids:
                    for option in options:
                        if option.get("option_id") == str(option_id):
                            option_translations = option.get("translations", {})
                            option_text = option_translations.get(language, "")
                            if not option_text and option_translations:
                                option_text = option_translations.get("en", "")
                            if option_text:
                                option_texts.append(option_text)
                            break
                
                return ", ".join(option_texts)
            return ""

        
        return ""

    def _get_flagged_photos(self, audit: Audit) -> List[Dict[str, Any]]:
        """
        Get only flagged photos (is_flagged_for_report = true).
        
        Requirements: 18.3
        """
        flagged_photos = []
        
        # Get all photos for this audit
        photos = self.db.query(AuditResponsePhoto).filter(
            AuditResponsePhoto.audit_id == audit.id
        ).all()

        
        for photo in photos:
            # Check if photo has a review that is flagged
            review_photo = self.db.query(AuditReviewPhoto).filter(
                AuditReviewPhoto.audit_response_photo_id == photo.id,
                AuditReviewPhoto.is_flagged_for_report == True
            ).first()
            
            if review_photo:
                flagged_photos.append({
                    "id": photo.id,
                    "audit_id": photo.audit_id,
                    "audit_response_id": photo.audit_response_id,
                    "file_url": photo.file_url,
                    "file_key": photo.file_key,
                    "caption": review_photo.caption or photo.caption,
                    "uploaded_at": photo.uploaded_at,
                    "uploaded_by": photo.uploaded_by
                })
        
        return flagged_photos

    def _get_issues_by_severity(self, audit: Audit) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all issues categorized by severity.
        
        Requirements: 18.4
        """
        issues = self.db.query(AuditIssue).filter(
            AuditIssue.audit_id == audit.id
        ).all()
        
        # Categorize by severity
        issues_by_severity = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }
        
        for issue in issues:
            issue_data = {
                "id": issue.id,
                "audit_id": issue.audit_id,
                "title": issue.title,
                "description": issue.description,
                "severity": issue.severity,
                "created_at": issue.created_at,
                "created_by": issue.created_by
            }
            
            issues_by_severity[issue.severity.value].append(issue_data)
        
        return issues_by_severity

    def _get_recommendations(self, audit: Audit) -> List[Dict[str, Any]]:
        """
        Get all recommendations from schedule_change_log.
        
        Requirements: 18.5
        """
        recommendations = self.db.query(ScheduleChangeLog).filter(
            and_(
                ScheduleChangeLog.trigger_type == "AUDIT",
                ScheduleChangeLog.trigger_reference_id == audit.id
            )
        ).all()
        
        recommendation_list = []
        for rec in recommendations:
            # Extract basic info from task_details_after if available
            title = rec.change_type
            description = rec.change_description
            
            recommendation_list.append({
                "id": rec.id,
                "schedule_id": rec.schedule_id,
                "change_type": rec.change_type,
                "task_id": rec.task_id,
                "task_details_before": rec.task_details_before,
                "task_details_after": rec.task_details_after,
                "change_description": rec.change_description,
                "is_applied": rec.is_applied,
                "applied_at": rec.applied_at,
                "applied_by": rec.applied_by,
                "created_at": rec.created_at,
                "created_by": rec.created_by
            })
        
        return recommendation_list


