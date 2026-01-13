"""
Crop Yield service for managing crop yields with photo associations.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError
from app.models.crop import Crop, CropYield, CropLifecyclePhoto, CropYieldPhoto
from app.models.plot import Plot
from app.models.farm import Farm
from app.schemas.crop import (
    CropYieldCreate, 
    CropYieldUpdate, 
    CropYieldResponse,
    YieldComparisonResponse
)
from app.services.measurement_unit_service import MeasurementUnitService

logger = get_logger(__name__)


class CropYieldService:
    """Service for crop yield operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.measurement_service = MeasurementUnitService(db)
    
    def create_yield(
        self,
        crop_id: UUID,
        data: CropYieldCreate,
        org_id: UUID,
        user_id: UUID
    ) -> CropYieldResponse:
        """
        Create a new crop yield record.
        
        Args:
            crop_id: Crop ID
            data: Yield creation data
            org_id: Organization ID
            user_id: User ID creating the yield
            
        Returns:
            Created yield
            
        Raises:
            NotFoundError: If crop not found
            ValidationError: If validation fails
        """
        # Validate crop exists and belongs to org
        crop = (
            self.db.query(Crop)
            .join(Plot)
            .join(Farm)
            .filter(
                and_(
                    Crop.id == crop_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop:
            raise NotFoundError(
                message=f"Crop {crop_id} not found",
                error_code="CROP_NOT_FOUND",
                details={"crop_id": str(crop_id)}
            )
        
        # Create yield
        crop_yield = CropYield(
            crop_id=crop_id,
            yield_type=data.yield_type,
            harvest_date=data.harvest_date,
            quantity=data.quantity,
            quantity_unit_id=data.quantity_unit_id,
            harvest_area=data.harvest_area,
            harvest_area_unit_id=data.harvest_area_unit_id,
            notes=data.notes,
            created_by=user_id
        )
        
        self.db.add(crop_yield)
        self.db.commit()
        self.db.refresh(crop_yield)
        
        logger.info(
            "Created crop yield",
            extra={
                "yield_id": str(crop_yield.id),
                "crop_id": str(crop_id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "yield_type": data.yield_type,
                "quantity": float(data.quantity)
            }
        )
        
        return self._to_response(crop_yield)
    
    def get_yields_by_crop(
        self,
        crop_id: UUID,
        org_id: UUID
    ) -> List[CropYieldResponse]:
        """
        Get all yields for a crop.
        
        Args:
            crop_id: Crop ID
            org_id: Organization ID
            
        Returns:
            List of yields
            
        Raises:
            NotFoundError: If crop not found
        """
        # Validate crop exists and belongs to org
        crop = (
            self.db.query(Crop)
            .join(Plot)
            .join(Farm)
            .filter(
                and_(
                    Crop.id == crop_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop:
            raise NotFoundError(
                message=f"Crop {crop_id} not found",
                error_code="CROP_NOT_FOUND",
                details={"crop_id": str(crop_id)}
            )
        
        # Get yields
        yields = (
            self.db.query(CropYield)
            .filter(CropYield.crop_id == crop_id)
            .order_by(CropYield.created_at.desc())
            .all()
        )
        
        logger.info(
            "Retrieved yields by crop",
            extra={
                "crop_id": str(crop_id),
                "org_id": str(org_id),
                "count": len(yields)
            }
        )
        
        return [self._to_response(y) for y in yields]
    
    def get_yield_by_id(
        self,
        yield_id: UUID,
        org_id: UUID
    ) -> CropYieldResponse:
        """
        Get yield by ID with ownership validation.
        
        Args:
            yield_id: Yield ID
            org_id: Organization ID
            
        Returns:
            Yield details
            
        Raises:
            NotFoundError: If yield not found or not owned by organization
        """
        crop_yield = (
            self.db.query(CropYield)
            .join(Crop)
            .join(Plot)
            .join(Farm)
            .options(
                joinedload(CropYield.crop),
                joinedload(CropYield.quantity_unit),
                joinedload(CropYield.harvest_area_unit)
            )
            .filter(
                and_(
                    CropYield.id == yield_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop_yield:
            raise NotFoundError(
                message=f"Yield {yield_id} not found",
                error_code="YIELD_NOT_FOUND",
                details={"yield_id": str(yield_id)}
            )
        
        logger.info(
            "Retrieved yield by ID",
            extra={
                "yield_id": str(yield_id),
                "org_id": str(org_id)
            }
        )
        
        return self._to_response(crop_yield)
    
    def update_yield(
        self,
        yield_id: UUID,
        data: CropYieldUpdate,
        org_id: UUID,
        user_id: UUID
    ) -> CropYieldResponse:
        """
        Update crop yield.
        
        Args:
            yield_id: Yield ID
            data: Yield update data
            org_id: Organization ID
            user_id: User ID updating the yield
            
        Returns:
            Updated yield
            
        Raises:
            NotFoundError: If yield not found
        """
        crop_yield = (
            self.db.query(CropYield)
            .join(Crop)
            .join(Plot)
            .join(Farm)
            .filter(
                and_(
                    CropYield.id == yield_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop_yield:
            raise NotFoundError(
                message=f"Yield {yield_id} not found",
                error_code="YIELD_NOT_FOUND",
                details={"yield_id": str(yield_id)}
            )
        
        # Update fields
        if data.harvest_date is not None:
            crop_yield.harvest_date = data.harvest_date
        if data.quantity is not None:
            crop_yield.quantity = data.quantity
        if data.quantity_unit_id is not None:
            crop_yield.quantity_unit_id = data.quantity_unit_id
        if data.harvest_area is not None:
            crop_yield.harvest_area = data.harvest_area
        if data.harvest_area_unit_id is not None:
            crop_yield.harvest_area_unit_id = data.harvest_area_unit_id
        if data.notes is not None:
            crop_yield.notes = data.notes
        
        self.db.commit()
        self.db.refresh(crop_yield)
        
        logger.info(
            "Updated crop yield",
            extra={
                "yield_id": str(yield_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_response(crop_yield)
    
    def delete_yield(
        self,
        yield_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete crop yield (hard delete with cascade).
        
        Args:
            yield_id: Yield ID
            org_id: Organization ID
            user_id: User ID deleting the yield
            
        Raises:
            NotFoundError: If yield not found
        """
        crop_yield = (
            self.db.query(CropYield)
            .join(Crop)
            .join(Plot)
            .join(Farm)
            .filter(
                and_(
                    CropYield.id == yield_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop_yield:
            raise NotFoundError(
                message=f"Yield {yield_id} not found",
                error_code="YIELD_NOT_FOUND",
                details={"yield_id": str(yield_id)}
            )
        
        # Hard delete (cascade will delete photo associations)
        self.db.delete(crop_yield)
        self.db.commit()
        
        logger.info(
            "Deleted crop yield",
            extra={
                "yield_id": str(yield_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def associate_photo(
        self,
        yield_id: UUID,
        photo_id: UUID,
        org_id: UUID
    ) -> None:
        """
        Associate a photo with a yield.
        
        Args:
            yield_id: Yield ID
            photo_id: Photo ID
            org_id: Organization ID
            
        Raises:
            NotFoundError: If yield or photo not found
            ValidationError: If photo doesn't belong to same crop
        """
        # Validate yield exists and belongs to org
        crop_yield = (
            self.db.query(CropYield)
            .join(Crop)
            .join(Plot)
            .join(Farm)
            .filter(
                and_(
                    CropYield.id == yield_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop_yield:
            raise NotFoundError(
                message=f"Yield {yield_id} not found",
                error_code="YIELD_NOT_FOUND",
                details={"yield_id": str(yield_id)}
            )
        
        # Validate photo exists and belongs to same crop
        photo = (
            self.db.query(CropLifecyclePhoto)
            .filter(CropLifecyclePhoto.id == photo_id)
            .first()
        )
        
        if not photo:
            raise NotFoundError(
                message=f"Photo {photo_id} not found",
                error_code="PHOTO_NOT_FOUND",
                details={"photo_id": str(photo_id)}
            )
        
        if photo.crop_id != crop_yield.crop_id:
            raise ValidationError(
                message="Photo must belong to the same crop as the yield",
                error_code="PHOTO_CROP_MISMATCH",
                details={
                    "photo_crop_id": str(photo.crop_id),
                    "yield_crop_id": str(crop_yield.crop_id)
                }
            )
        
        # Check if association already exists
        existing = (
            self.db.query(CropYieldPhoto)
            .filter(
                and_(
                    CropYieldPhoto.crop_yield_id == yield_id,
                    CropYieldPhoto.photo_id == photo_id
                )
            )
            .first()
        )
        
        if existing:
            logger.info(
                "Photo already associated with yield",
                extra={
                    "yield_id": str(yield_id),
                    "photo_id": str(photo_id),
                    "org_id": str(org_id)
                }
            )
            return
        
        # Create association
        association = CropYieldPhoto(
            crop_yield_id=yield_id,
            photo_id=photo_id
        )
        
        self.db.add(association)
        self.db.commit()
        
        logger.info(
            "Associated photo with yield",
            extra={
                "yield_id": str(yield_id),
                "photo_id": str(photo_id),
                "org_id": str(org_id)
            }
        )
    
    def calculate_yield_per_area(
        self,
        yield_id: UUID,
        org_id: UUID
    ) -> Decimal:
        """
        Calculate yield per area (yield per base area unit).
        
        Args:
            yield_id: Yield ID
            org_id: Organization ID
            
        Returns:
            Yield per area in base units (e.g., kg per acre)
            
        Raises:
            NotFoundError: If yield not found
            ValidationError: If area information is missing
        """
        # Get yield with crop details
        crop_yield = (
            self.db.query(CropYield)
            .join(Crop)
            .join(Plot)
            .join(Farm)
            .options(
                joinedload(CropYield.crop)
            )
            .filter(
                and_(
                    CropYield.id == yield_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop_yield:
            raise NotFoundError(
                message=f"Yield {yield_id} not found",
                error_code="YIELD_NOT_FOUND",
                details={"yield_id": str(yield_id)}
            )
        
        # Determine area to use (harvest_area if provided, otherwise crop area)
        area = crop_yield.harvest_area if crop_yield.harvest_area else crop_yield.crop.area
        area_unit_id = crop_yield.harvest_area_unit_id if crop_yield.harvest_area_unit_id else crop_yield.crop.area_unit_id
        
        if not area or not area_unit_id:
            raise ValidationError(
                message="Area information is required to calculate yield per area",
                error_code="MISSING_AREA_INFO",
                details={"yield_id": str(yield_id)}
            )
        
        # Convert quantity to base unit (e.g., kg)
        quantity_in_base = self.measurement_service.convert_to_base_unit(
            crop_yield.quantity,
            crop_yield.quantity_unit_id
        )
        
        # Convert area to base unit (e.g., acres)
        area_in_base = self.measurement_service.convert_to_base_unit(
            area,
            area_unit_id
        )
        
        # Calculate yield per area
        yield_per_area = quantity_in_base / area_in_base
        
        logger.info(
            "Calculated yield per area",
            extra={
                "yield_id": str(yield_id),
                "org_id": str(org_id),
                "quantity_in_base": float(quantity_in_base),
                "area_in_base": float(area_in_base),
                "yield_per_area": float(yield_per_area)
            }
        )
        
        return yield_per_area
    
    def compare_planned_vs_actual(
        self,
        crop_id: UUID,
        org_id: UUID
    ) -> YieldComparisonResponse:
        """
        Compare planned vs actual yields for a crop.
        
        Args:
            crop_id: Crop ID
            org_id: Organization ID
            
        Returns:
            Yield comparison with variance and achievement rate
            
        Raises:
            NotFoundError: If crop not found
        """
        # Validate crop exists and belongs to org
        crop = (
            self.db.query(Crop)
            .join(Plot)
            .join(Farm)
            .filter(
                and_(
                    Crop.id == crop_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop:
            raise NotFoundError(
                message=f"Crop {crop_id} not found",
                error_code="CROP_NOT_FOUND",
                details={"crop_id": str(crop_id)}
            )
        
        # Get all yields for crop
        yields = (
            self.db.query(CropYield)
            .filter(CropYield.crop_id == crop_id)
            .all()
        )
        
        # Separate planned and actual yields
        planned_yields = [y for y in yields if y.yield_type == 'PLANNED']
        actual_yields = [y for y in yields if y.yield_type == 'ACTUAL']
        
        # Convert all yields to base unit and sum
        total_planned = Decimal('0')
        for y in planned_yields:
            quantity_in_base = self.measurement_service.convert_to_base_unit(
                y.quantity,
                y.quantity_unit_id
            )
            total_planned += quantity_in_base
        
        total_actual = Decimal('0')
        for y in actual_yields:
            quantity_in_base = self.measurement_service.convert_to_base_unit(
                y.quantity,
                y.quantity_unit_id
            )
            total_actual += quantity_in_base
        
        # Calculate variance and achievement rate
        variance = total_actual - total_planned
        variance_percentage = float((variance / total_planned * 100)) if total_planned > 0 else 0.0
        achievement_rate = float((total_actual / total_planned * 100)) if total_planned > 0 else 0.0
        
        logger.info(
            "Compared planned vs actual yields",
            extra={
                "crop_id": str(crop_id),
                "org_id": str(org_id),
                "total_planned": float(total_planned),
                "total_actual": float(total_actual),
                "variance": float(variance),
                "variance_percentage": variance_percentage,
                "achievement_rate": achievement_rate
            }
        )
        
        return YieldComparisonResponse(
            total_planned=total_planned,
            total_actual=total_actual,
            variance=variance,
            variance_percentage=variance_percentage,
            achievement_rate=achievement_rate,
            planned_yields=[self._to_response(y) for y in planned_yields],
            actual_yields=[self._to_response(y) for y in actual_yields]
        )
    
    def _to_response(self, crop_yield: CropYield) -> CropYieldResponse:
        """
        Convert crop yield model to response schema.
        
        Args:
            crop_yield: CropYield model
            
        Returns:
            Crop yield response schema
        """
        return CropYieldResponse(
            id=str(crop_yield.id),
            crop_id=str(crop_yield.crop_id),
            yield_type=crop_yield.yield_type,
            harvest_date=crop_yield.harvest_date,
            quantity=crop_yield.quantity,
            quantity_unit_id=str(crop_yield.quantity_unit_id),
            harvest_area=crop_yield.harvest_area,
            harvest_area_unit_id=str(crop_yield.harvest_area_unit_id) if crop_yield.harvest_area_unit_id else None,
            notes=crop_yield.notes,
            created_at=crop_yield.created_at,
            created_by=str(crop_yield.created_by) if crop_yield.created_by else None
        )
