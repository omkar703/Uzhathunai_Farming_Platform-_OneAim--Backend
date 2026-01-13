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

        # Build report
        report = {
            "audit_details": self._get_audit_details(audit, language),
            "template_info": self._get_template_info(audit, language),
            "crop_info": self._get_crop_info(audit),
            "organization_info": self._get_organization_info(audit),
            "flagged_responses": self._get_flagged_responses(audit, language),
            "flagged_photos": self._get_flagged_photos(audit),
            "issues": self._get_issues_by_severity(audit),
            "recommendations": self._get_recommendations(audit),
            "generated_at": audit.created_at.isoformat() if audit.created_at else None,
            "language": language
        }

        logger.info(
            "Audit report generated",
            extra={
                "audit_id": str(audit_id),
                "language": language,
                "flagged_responses_count": len(report["flagged_responses"]),
                "flagged_photos_count": len(report["flagged_photos"]),
                "issues_count": sum(len(issues) for issues in report["issues"].values()),
                "recommendations_count": len(report["recommendations"])
            }
        )

        return report

    def _get_audit_details(self, audit: Audit, language: str) -> Dict[str, Any]:
        """Get audit details."""
        return {
            "audit_id": str(audit.id),
            "audit_number": audit.audit_number,
            "name": audit.name,
            "audit_date": audit.audit_date.isoformat() if audit.audit_date else None,
            "status": audit.status.value,
            "created_at": audit.created_at.isoformat() if audit.created_at else None,
            "finalized_at": audit.finalized_at.isoformat() if audit.finalized_at else None,
            "shared_at": audit.shared_at.isoformat() if audit.shared_at else None
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
        
        return {
            "crop_id": str(crop.id),
            "crop_name": crop.name,
            "variety": crop.variety,
            "planting_date": crop.planting_date.isoformat() if crop.planting_date else None,
            "expected_harvest_date": crop.expected_harvest_date.isoformat() if crop.expected_harvest_date else None
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
                        "response_id": str(response.id),
                        "parameter_name": param_name,
                        "parameter_code": parameter_snapshot.get("code", ""),
                        "parameter_type": parameter_snapshot.get("parameter_type", ""),
                        "response_value": response_value,
                        "notes": response.notes,
                        "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
                        "reviewed_by": str(review.reviewed_by) if review.reviewed_by else None
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
            if response_or_review.response_option_ids:
                # Get option display text from snapshot
                options = parameter_snapshot.get("options", [])
                option_texts = []
                
                for option_id in response_or_review.response_option_ids:
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
        
        # Get all responses for this audit
        responses = self.db.query(AuditResponse).filter(
            AuditResponse.audit_id == audit.id
        ).all()
        
        response_ids = [r.id for r in responses]
        
        # Get all photos for these responses
        photos = self.db.query(AuditResponsePhoto).filter(
            AuditResponsePhoto.audit_response_id.in_(response_ids)
        ).all()
        
        for photo in photos:
            # Check if photo has a review that is flagged
            review_photo = self.db.query(AuditReviewPhoto).filter(
                AuditReviewPhoto.audit_response_photo_id == photo.id,
                AuditReviewPhoto.is_flagged_for_report == True
            ).first()
            
            if review_photo:
                flagged_photos.append({
                    "photo_id": str(photo.id),
                    "file_url": photo.file_url,
                    "file_key": photo.file_key,
                    "caption": review_photo.caption or photo.caption,
                    "uploaded_at": photo.uploaded_at.isoformat() if photo.uploaded_at else None,
                    "reviewed_at": review_photo.reviewed_at.isoformat() if review_photo.reviewed_at else None
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
                "issue_id": str(issue.id),
                "title": issue.title,
                "description": issue.description,
                "severity": issue.severity.value,
                "created_at": issue.created_at.isoformat() if issue.created_at else None,
                "created_by": str(issue.created_by) if issue.created_by else None
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
            recommendation_list.append({
                "recommendation_id": str(rec.id),
                "title": rec.title,
                "description": rec.description,
                "priority": rec.priority,
                "due_date": rec.due_date.isoformat() if rec.due_date else None,
                "is_applied": rec.is_applied,
                "created_at": rec.created_at.isoformat() if rec.created_at else None,
                "created_by": str(rec.created_by) if rec.created_by else None
            })
        
        return recommendation_list

