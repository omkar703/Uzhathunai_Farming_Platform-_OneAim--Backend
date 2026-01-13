"""
PDF Service for Farm Audit Management System.

This service generates PDF reports from audit report data.
Includes organization branding and proper formatting.

Requirements: 18.8
"""

from typing import Dict, Any, Optional
from uuid import UUID
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.core.logging import get_logger
from app.services.report_service import ReportService

logger = get_logger(__name__)


class PDFService:
    """
    Service for generating PDF reports.
    
    Generates formatted PDF reports with organization branding
    and proper section formatting.
    """

    def __init__(self, report_service: ReportService):
        self.report_service = report_service

    def generate_pdf(
        self,
        audit_id: UUID,
        language: str = "en"
    ) -> bytes:
        """
        Generate PDF report for an audit.
        
        Creates a formatted PDF with:
        - Organization branding (header)
        - Audit details
        - Template information
        - Crop and organization information
        - Flagged responses
        - Flagged photos
        - Issues by severity
        - Recommendations
        
        Args:
            audit_id: UUID of the audit
            language: Language code for report (en, ta, ml)
            
        Returns:
            PDF file as bytes
            
        Requirements: 18.8
        """
        logger.info(
            "Generating PDF report",
            extra={
                "audit_id": str(audit_id),
                "language": language
            }
        )

        # Get report data
        report_data = self.report_service.generate_report(audit_id, language)

        # Create PDF buffer
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build PDF content
        story = []
        styles = self._get_styles()

        # Add header with branding
        story.extend(self._add_header(report_data, styles))

        # Add audit details
        story.extend(self._add_audit_details(report_data, styles))

        # Add template info
        story.extend(self._add_template_info(report_data, styles))

        # Add crop and organization info
        story.extend(self._add_crop_org_info(report_data, styles))

        # Add flagged responses
        story.extend(self._add_flagged_responses(report_data, styles))

        # Add flagged photos
        story.extend(self._add_flagged_photos(report_data, styles))

        # Add issues
        story.extend(self._add_issues(report_data, styles))

        # Add recommendations
        story.extend(self._add_recommendations(report_data, styles))

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(
            "PDF report generated",
            extra={
                "audit_id": str(audit_id),
                "language": language,
                "pdf_size_bytes": len(pdf_bytes)
            }
        )

        return pdf_bytes

    def _get_styles(self) -> Dict[str, ParagraphStyle]:
        """Get custom paragraph styles."""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#5f6368'),
            spaceAfter=10,
            spaceBefore=10
        ))
        
        return styles

    def _add_header(self, report_data: Dict[str, Any], styles: Dict) -> list:
        """Add header with organization branding."""
        elements = []
        
        # Organization name (branding)
        org_info = report_data.get("organization_info", {})
        fsp_org = org_info.get("fsp_organization", {})
        org_name = fsp_org.get("name", "Uzhathunai")
        
        elements.append(Paragraph(org_name, styles['CustomTitle']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Report title
        audit_details = report_data.get("audit_details", {})
        audit_number = audit_details.get("audit_number", "")
        
        elements.append(Paragraph(
            f"Farm Audit Report - {audit_number}",
            styles['Heading1']
        ))
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements

    def _add_audit_details(self, report_data: Dict[str, Any], styles: Dict) -> list:
        """Add audit details section."""
        elements = []
        audit_details = report_data.get("audit_details", {})
        
        elements.append(Paragraph("Audit Details", styles['CustomHeading']))
        
        # Create table with audit details
        data = [
            ["Audit Number:", audit_details.get("audit_number", "")],
            ["Audit Name:", audit_details.get("name", "")],
            ["Audit Date:", audit_details.get("audit_date", "")],
            ["Status:", audit_details.get("status", "")],
            ["Created At:", audit_details.get("created_at", "")],
        ]
        
        if audit_details.get("finalized_at"):
            data.append(["Finalized At:", audit_details.get("finalized_at", "")])
        
        if audit_details.get("shared_at"):
            data.append(["Shared At:", audit_details.get("shared_at", "")])
        
        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#5f6368')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements

    def _add_template_info(self, report_data: Dict[str, Any], styles: Dict) -> list:
        """Add template information section."""
        elements = []
        template_info = report_data.get("template_info", {})
        
        elements.append(Paragraph("Template Information", styles['CustomHeading']))
        
        data = [
            ["Template Name:", template_info.get("template_name", "")],
            ["Template Code:", template_info.get("template_code", "")],
            ["Version:", str(template_info.get("template_version", ""))],
        ]
        
        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#5f6368')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements

    def _add_crop_org_info(self, report_data: Dict[str, Any], styles: Dict) -> list:
        """Add crop and organization information section."""
        elements = []
        
        elements.append(Paragraph("Crop & Organization Information", styles['CustomHeading']))
        
        # Crop info
        crop_info = report_data.get("crop_info", {})
        org_info = report_data.get("organization_info", {})
        
        data = [
            ["Crop Name:", crop_info.get("crop_name", "")],
            ["Variety:", crop_info.get("variety", "")],
            ["Planting Date:", crop_info.get("planting_date", "")],
            ["Expected Harvest:", crop_info.get("expected_harvest_date", "")],
            ["", ""],  # Spacer row
            ["FSP Organization:", org_info.get("fsp_organization", {}).get("name", "")],
            ["Farming Organization:", org_info.get("farming_organization", {}).get("name", "")],
            ["District:", org_info.get("farming_organization", {}).get("district", "")],
        ]
        
        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#5f6368')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements

    def _add_flagged_responses(self, report_data: Dict[str, Any], styles: Dict) -> list:
        """Add flagged responses section."""
        elements = []
        flagged_responses = report_data.get("flagged_responses", [])
        
        if not flagged_responses:
            return elements
        
        elements.append(Paragraph("Flagged Responses", styles['CustomHeading']))
        
        for response in flagged_responses:
            elements.append(Paragraph(
                f"<b>{response.get('parameter_name', '')}</b>",
                styles['CustomSubHeading']
            ))
            
            elements.append(Paragraph(
                f"Response: {response.get('response_value', '')}",
                styles['Normal']
            ))
            
            if response.get('notes'):
                elements.append(Paragraph(
                    f"Notes: {response.get('notes', '')}",
                    styles['Normal']
                ))
            
            elements.append(Spacer(1, 0.1 * inch))
        
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements

    def _add_flagged_photos(self, report_data: Dict[str, Any], styles: Dict) -> list:
        """Add flagged photos section."""
        elements = []
        flagged_photos = report_data.get("flagged_photos", [])
        
        if not flagged_photos:
            return elements
        
        elements.append(Paragraph("Flagged Photos", styles['CustomHeading']))
        
        for photo in flagged_photos:
            elements.append(Paragraph(
                f"Photo: {photo.get('file_key', '')}",
                styles['Normal']
            ))
            
            if photo.get('caption'):
                elements.append(Paragraph(
                    f"Caption: {photo.get('caption', '')}",
                    styles['Normal']
                ))
            
            elements.append(Spacer(1, 0.1 * inch))
        
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements

    def _add_issues(self, report_data: Dict[str, Any], styles: Dict) -> list:
        """Add issues section categorized by severity."""
        elements = []
        issues_by_severity = report_data.get("issues", {})
        
        # Check if there are any issues
        has_issues = any(len(issues) > 0 for issues in issues_by_severity.values())
        if not has_issues:
            return elements
        
        elements.append(Paragraph("Issues", styles['CustomHeading']))
        
        # Add issues by severity
        severity_colors = {
            "CRITICAL": colors.HexColor('#d32f2f'),
            "HIGH": colors.HexColor('#f57c00'),
            "MEDIUM": colors.HexColor('#fbc02d'),
            "LOW": colors.HexColor('#388e3c')
        }
        
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            issues = issues_by_severity.get(severity, [])
            if not issues:
                continue
            
            elements.append(Paragraph(
                f"{severity} Issues ({len(issues)})",
                styles['CustomSubHeading']
            ))
            
            for issue in issues:
                # Issue title with severity color
                elements.append(Paragraph(
                    f"<font color='{severity_colors[severity]}'><b>{issue.get('title', '')}</b></font>",
                    styles['Normal']
                ))
                
                if issue.get('description'):
                    elements.append(Paragraph(
                        issue.get('description', ''),
                        styles['Normal']
                    ))
                
                elements.append(Spacer(1, 0.1 * inch))
        
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements

    def _add_recommendations(self, report_data: Dict[str, Any], styles: Dict) -> list:
        """Add recommendations section."""
        elements = []
        recommendations = report_data.get("recommendations", [])
        
        if not recommendations:
            return elements
        
        elements.append(Paragraph("Recommendations", styles['CustomHeading']))
        
        for rec in recommendations:
            elements.append(Paragraph(
                f"<b>{rec.get('title', '')}</b>",
                styles['CustomSubHeading']
            ))
            
            elements.append(Paragraph(
                rec.get('description', ''),
                styles['Normal']
            ))
            
            # Add priority and due date
            priority = rec.get('priority', '')
            due_date = rec.get('due_date', '')
            status = "Applied" if rec.get('is_applied') else "Pending"
            
            elements.append(Paragraph(
                f"Priority: {priority} | Due Date: {due_date} | Status: {status}",
                styles['Normal']
            ))
            
            elements.append(Spacer(1, 0.1 * inch))
        
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements

