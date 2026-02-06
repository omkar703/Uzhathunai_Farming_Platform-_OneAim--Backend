import sys
import os
import uuid
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())

from app.core.config import settings
from app.models.user import User
from app.models.audit import Audit, AuditIssue, AuditRecommendation, AuditResponse, AuditResponsePhoto, AuditReview, AuditParameterInstance
from app.models.template import Template, TemplateSection, TemplateParameter
from app.models.enums import AuditStatus, IssueSeverity
from app.services.audit_service import AuditService
from app.services.photo_service import PhotoService

def verify_report():
    print("Connecting to DB...")
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 1. Get a user (superuser usually)
        user = db.query(User).first()
        if not user:
            print("No user found. Cannot proceed.")
            return

        print(f"Using user: {user.email}")

        # 2. Get an existing audit or create one (simpler to pick latest)
        audit = db.query(Audit).order_by(Audit.created_at.desc()).first()
        if not audit:
            print("No audit found. Please run seed scripts first.")
            return
            
        print(f"Using audit: {audit.audit_number} ({audit.id})")

        # 3. Add a standalone recommendation
        print("Adding standalone recommendation...")
        rec = AuditRecommendation(
            audit_id=audit.id,
            title="Maintain irrigation logs",
            description="Ensure daily logs are kept.",
            created_by=user.id
        )
        db.add(rec)
        db.commit()
        
        # 4. Add an issue with recommendation
        print("Adding issue with recommendation...")
        issue = AuditIssue(
            audit_id=audit.id,
            title="Pests detected",
            description="Minor aphid infestation.",
            recommendation="Apply neem oil.",
            severity=IssueSeverity.LOW,
            created_by=user.id
        )
        db.add(issue)
        db.commit()

        # 5. Flag a response (if any exist)
        response = db.query(AuditResponse).filter(AuditResponse.audit_id == audit.id).first()
        if response:
            print(f"Flagging response {response.id}...")
            # Check if review exists
            review = db.query(AuditReview).filter(
                AuditReview.audit_response_id == response.id
            ).first()
            
            if review:
                review.is_flagged_for_report = True
            else:
                review = AuditReview(
                    audit_response_id=response.id,
                    is_flagged_for_report=True,
                    reviewed_by=user.id
                )
                db.add(review)
            db.commit()
        else:
            print("No responses found to flag.")

        # 6. Flag a photo (if any exist)
        # Create a dummy photo if none
        photo = db.query(AuditResponsePhoto).filter(AuditResponsePhoto.audit_id == audit.id).first()
        if not photo:
             print("Creating dummy photo...")
             photo = AuditResponsePhoto(
                 audit_id=audit.id,
                 file_url="https://example.com/dummy.jpg",
                 file_key="dummy.jpg",
                 uploaded_by=user.id
             )
             db.add(photo)
             db.commit()
        
        print(f"Flagging photo {photo.id}...")
        photo.is_flagged_for_report = True
        db.commit()

        # 7. Get Report
        print("Generating report...")
        service = AuditService(db)
        report = service.get_audit_report(audit.id)
        
        # 8. Verify
        print("\n--- Report Verification ---")
        
        # Verify Standalone Recs
        recs = report.get("standalone_recommendations", [])
        has_rec = any(r.title == "Maintain irrigation logs" for r in recs)
        print(f"Standalone Recommendation found: {has_rec}")
        
        # Verify Issue Rec
        issues = report.get("issues", [])
        has_issue_rec = any(i.recommendation == "Apply neem oil." for i in issues)
        print(f"Issue Recommendation found: {has_issue_rec}")
        
        # Verify Flagged Response
        flagged_resps = report.get("flagged_responses", [])
        print(f"Flagged Responses count: {len(flagged_resps)}")
        
        # Verify Flagged Photo
        flagged_photos = report.get("flagged_photos", [])
        has_photo = any(p["file_url"] == photo.file_url for p in flagged_photos)
        print(f"Flagged Photo found: {has_photo}")
        
        if has_rec and has_issue_rec and has_photo:
            print("\nSUCCESS: All new features verified!")
        else:
            print("\nWARNING: Some features missing in report.")

    except Exception as e:
        print(f"Error checking report: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_report()
