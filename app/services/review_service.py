"""
Review Service for Farm Audit Management System.

This service manages audit reviews, photo annotations, and flagging for reports.
Handles reviewer modifications to audit responses and photo annotations.
"""

from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.models.audit import AuditReview, AuditReviewPhoto, AuditResponse, AuditResponsePhoto
from app.models.user import User

logger = get_logger(__name__)


class ReviewService:
    """
    Service for managing audit reviews and photo annotations.
    
    Handles reviewer modifications to audit responses, photo annotations,
    and flagging content for report inclusion. Enforces one review per response.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_review(
        self,
        audit_response_id: UUID,
        user_id: UUID,
        response_text: Optional[str] = None,
        response_numeric: Optional[float] = None,
        response_date: Optional[datetime] = None,
        response_option_ids: Optional[list[UUID]] = None,
        is_flagged_for_report: bool = False
    ) -> AuditReview:
        """
        Create or update a review for an audit response.
        
        Enforces one review per audit response. If a review already exists,
        it will be updated instead of creating a new one.
        
        Args:
            audit_response_id: UUID of the audit response being reviewed
            user_id: ID of the user creating the review
            response_text: Optional text response override
            response_numeric: Optional numeric response override
            response_date: Optional date response override
            response_option_ids: Optional option IDs override
            is_flagged_for_report: Whether to flag this response for report inclusion
            
        Returns:
            Created or updated audit review
            
        Raises:
            NotFoundError: If audit response not found
        """
        logger.info(
            "Creating/updating audit review",
            extra={
                "audit_response_id": str(audit_response_id),
                "user_id": str(user_id),
                "is_flagged_for_report": is_flagged_for_report
            }
        )

        # Validate audit response exists
        audit_response = self.db.query(AuditResponse).filter(
            AuditResponse.id == audit_response_id
        ).first()
        
        if not audit_response:
            raise NotFoundError(
                message=f"Audit response {audit_response_id} not found",
                error_code="AUDIT_RESPONSE_NOT_FOUND",
                details={"audit_response_id": str(audit_response_id)}
            )

        # Check if review already exists (one review per response)
        existing_review = self.db.query(AuditReview).filter(
            AuditReview.audit_response_id == audit_response_id
        ).first()

        if existing_review:
            # Update existing review
            logger.info(
                "Updating existing review",
                extra={
                    "review_id": str(existing_review.id),
                    "audit_response_id": str(audit_response_id)
                }
            )
            
            existing_review.response_text = response_text
            existing_review.response_numeric = response_numeric
            existing_review.response_date = response_date
            existing_review.response_option_ids = response_option_ids
            existing_review.is_flagged_for_report = is_flagged_for_report
            existing_review.reviewed_by = user_id
            existing_review.reviewed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(existing_review)
            
            return existing_review
        else:
            # Create new review
            review = AuditReview(
                audit_response_id=audit_response_id,
                response_text=response_text,
                response_numeric=response_numeric,
                response_date=response_date,
                response_option_ids=response_option_ids,
                is_flagged_for_report=is_flagged_for_report,
                reviewed_by=user_id
            )
            
            self.db.add(review)
            self.db.commit()
            self.db.refresh(review)
            
            logger.info(
                "Audit review created",
                extra={
                    "review_id": str(review.id),
                    "audit_response_id": str(audit_response_id),
                    "user_id": str(user_id)
                }
            )
            
            return review

    def flag_response_for_report(
        self,
        audit_response_id: UUID,
        flag: bool,
        user_id: UUID
    ) -> AuditReview:
        """
        Flag or unflag an audit response for report inclusion.
        
        Creates a review if one doesn't exist, or updates the existing review's flag.
        
        Args:
            audit_response_id: UUID of the audit response
            flag: True to flag for report, False to unflag
            user_id: ID of the user performing the action
            
        Returns:
            Updated or created audit review
            
        Raises:
            NotFoundError: If audit response not found
        """
        logger.info(
            "Flagging response for report",
            extra={
                "audit_response_id": str(audit_response_id),
                "flag": flag,
                "user_id": str(user_id)
            }
        )

        # Check if review exists
        existing_review = self.db.query(AuditReview).filter(
            AuditReview.audit_response_id == audit_response_id
        ).first()

        if existing_review:
            # Update existing review
            existing_review.is_flagged_for_report = flag
            existing_review.reviewed_by = user_id
            existing_review.reviewed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(existing_review)
            
            return existing_review
        else:
            # Create new review with just the flag
            return self.create_review(
                audit_response_id=audit_response_id,
                user_id=user_id,
                is_flagged_for_report=flag
            )

    def annotate_photo(
        self,
        audit_response_photo_id: UUID,
        user_id: UUID,
        caption: Optional[str] = None,
        is_flagged_for_report: bool = False
    ) -> AuditReviewPhoto:
        """
        Annotate a photo with caption and/or flag for report inclusion.
        
        Creates or updates a review photo annotation.
        
        Args:
            audit_response_photo_id: UUID of the photo being annotated
            user_id: ID of the user creating the annotation
            caption: Optional caption for the photo
            is_flagged_for_report: Whether to flag this photo for report inclusion
            
        Returns:
            Created or updated audit review photo
            
        Raises:
            NotFoundError: If photo not found
        """
        logger.info(
            "Annotating photo",
            extra={
                "audit_response_photo_id": str(audit_response_photo_id),
                "user_id": str(user_id),
                "is_flagged_for_report": is_flagged_for_report
            }
        )

        # Validate photo exists
        photo = self.db.query(AuditResponsePhoto).filter(
            AuditResponsePhoto.id == audit_response_photo_id
        ).first()
        
        if not photo:
            raise NotFoundError(
                message=f"Audit response photo {audit_response_photo_id} not found",
                error_code="AUDIT_RESPONSE_PHOTO_NOT_FOUND",
                details={"audit_response_photo_id": str(audit_response_photo_id)}
            )

        # Check if review photo already exists
        existing_review_photo = self.db.query(AuditReviewPhoto).filter(
            AuditReviewPhoto.audit_response_photo_id == audit_response_photo_id
        ).first()

        if existing_review_photo:
            # Update existing review photo
            logger.info(
                "Updating existing photo annotation",
                extra={
                    "review_photo_id": str(existing_review_photo.id),
                    "audit_response_photo_id": str(audit_response_photo_id)
                }
            )
            
            existing_review_photo.caption = caption
            existing_review_photo.is_flagged_for_report = is_flagged_for_report
            existing_review_photo.reviewed_by = user_id
            existing_review_photo.reviewed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(existing_review_photo)
            
            return existing_review_photo
        else:
            # Create new review photo
            review_photo = AuditReviewPhoto(
                audit_response_photo_id=audit_response_photo_id,
                caption=caption,
                is_flagged_for_report=is_flagged_for_report,
                reviewed_by=user_id
            )
            
            self.db.add(review_photo)
            self.db.commit()
            self.db.refresh(review_photo)
            
            logger.info(
                "Photo annotation created",
                extra={
                    "review_photo_id": str(review_photo.id),
                    "audit_response_photo_id": str(audit_response_photo_id),
                    "user_id": str(user_id)
                }
            )
            
            return review_photo

    def get_review_by_response_id(self, audit_response_id: UUID) -> Optional[AuditReview]:
        """
        Get review for a specific audit response.
        
        Args:
            audit_response_id: UUID of the audit response
            
        Returns:
            Audit review if exists, None otherwise
        """
        return self.db.query(AuditReview).filter(
            AuditReview.audit_response_id == audit_response_id
        ).first()

    def get_review_photo_by_photo_id(self, audit_response_photo_id: UUID) -> Optional[AuditReviewPhoto]:
        """
        Get review photo annotation for a specific photo.
        
        Args:
            audit_response_photo_id: UUID of the audit response photo
            
        Returns:
            Audit review photo if exists, None otherwise
        """
        return self.db.query(AuditReviewPhoto).filter(
            AuditReviewPhoto.audit_response_photo_id == audit_response_photo_id
        ).first()
