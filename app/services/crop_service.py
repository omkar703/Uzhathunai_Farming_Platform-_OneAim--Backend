"""
Crop service for managing crops with lifecycle state machine.
"""
from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError
from app.core.cache import cache_service
from app.models.crop import Crop
from app.models.plot import Plot
from app.models.farm import Farm
from app.models.crop_data import CropVariety, CropVarietyTranslation, CropType, CropTypeTranslation
from app.models.enums import CropLifecycle
from app.schemas.crop import CropCreate, CropUpdate, CropResponse, CropTypeNested, CropVarietyNested

logger = get_logger(__name__)

# Cache TTL: 5 minutes for crops (frequently updated)
CACHE_TTL = 300


# Lifecycle state machine - defines valid transitions
LIFECYCLE_TRANSITIONS = {
    CropLifecycle.PLANNED: [CropLifecycle.PLANTED, CropLifecycle.TERMINATED],
    CropLifecycle.PLANTED: [CropLifecycle.TRANSPLANTED, CropLifecycle.PRODUCTION, CropLifecycle.TERMINATED],
    CropLifecycle.TRANSPLANTED: [CropLifecycle.PRODUCTION, CropLifecycle.TERMINATED],
    CropLifecycle.PRODUCTION: [CropLifecycle.COMPLETED, CropLifecycle.TERMINATED],
    CropLifecycle.COMPLETED: [CropLifecycle.CLOSED],
    CropLifecycle.TERMINATED: [CropLifecycle.CLOSED],
    CropLifecycle.CLOSED: []  # Terminal state
}


class CropService:
    """Service for crop operations with lifecycle management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = cache_service
    
    def create_crop(
        self,
        plot_id: UUID,
        org_id: UUID,
        data: CropCreate,
        user_id: UUID
    ) -> CropResponse:
        """
        Create a new crop.
        
        Args:
            plot_id: Plot ID
            data: Crop creation data
            org_id: Organization ID
            user_id: User ID creating the crop
            
        Returns:
            Created crop
            
        Raises:
            NotFoundError: If plot not found
            ValidationError: If validation fails
        """
        # Validate plot exists and belongs to org
        plot = (
            self.db.query(Plot)
            .join(Farm)
            .filter(
                and_(
                    Plot.id == plot_id,
                    Farm.organization_id == org_id,
                    Plot.is_active == True,
                    Farm.is_active == True
                )
            )
            .first()
        )
        
        if not plot:
            raise NotFoundError(
                message=f"Plot {plot_id} not found",
                error_code="PLOT_NOT_FOUND",
                details={"plot_id": str(plot_id)}
            )
        
        # Resolve variety_name to crop_variety_id if provided
        crop_variety_id = data.crop_variety_id
        if data.variety_name and not crop_variety_id:
            crop_variety_id = self._find_variety_by_name(data.variety_name)
        
        # Create crop
        crop = Crop(
            plot_id=plot_id,
            name=data.name,
            description=data.description,
            crop_type_id=data.crop_type_id,
            crop_variety_id=crop_variety_id,
            area=data.area,
            area_unit_id=data.area_unit_id,
            plant_count=data.plant_count,
            lifecycle=CropLifecycle.PLANNED,
            planned_date=data.planned_date,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(crop)
        self.db.commit()
        self.db.refresh(crop)
        
        # Invalidate cache
        self._invalidate_crop_cache(org_id, plot_id)
        
        logger.info(
            "Created crop",
            extra={
                "crop_id": str(crop.id),
                "plot_id": str(plot_id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "name": data.name,
                "lifecycle": CropLifecycle.PLANNED.value
            }
        )
        
        return self._to_response(crop)
    
    def get_crops(
        self,
        org_id: UUID,
        filters: Dict[str, Any] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[CropResponse], int]:
        """
        Get crops with filtering and pagination.
        
        Args:
            org_id: Organization ID
            filters: Optional filters dict with plot_id and/or lifecycle
            page: Page number (default: 1)
            limit: Items per page (default: 20)
            
        Returns:
            Tuple of (list of crops, total count)
        """
        if filters is None:
            filters = {}
            
        offset = (page - 1) * limit
        
        # Build query
        query = (
            self.db.query(Crop)
            .join(Plot)
            .join(Farm)
            .filter(Farm.organization_id == org_id)
        )
        
        # Apply filters
        if 'plot_id' in filters:
            query = query.filter(Crop.plot_id == filters['plot_id'])
        
        if 'lifecycle' in filters:
            query = query.filter(Crop.lifecycle == filters['lifecycle'])
        
        # Order by created_at desc
        query = query.order_by(Crop.created_at.desc())
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        crops = query.offset(offset).limit(limit).all()
        
        logger.info(
            "Retrieved crops",
            extra={
                "org_id": str(org_id),
                "plot_id": str(filters.get('plot_id')) if filters.get('plot_id') else None,
                "lifecycle": filters.get('lifecycle').value if filters.get('lifecycle') else None,
                "page": page,
                "limit": limit,
                "count": len(crops),
                "total": total
            }
        )
        
        return [self._to_response(crop) for crop in crops], total
    
    def get_crop_by_id(
        self,
        crop_id: UUID,
        org_id: UUID
    ) -> CropResponse:
        """
        Get crop by ID with ownership validation.
        
        Args:
            crop_id: Crop ID
            org_id: Organization ID
            
        Returns:
            Crop details
            
        Raises:
            NotFoundError: If crop not found or not owned by organization
        """
        crop = (
            self.db.query(Crop)
            .join(Plot)
            .join(Farm)
            .options(
                joinedload(Crop.plot),
                joinedload(Crop.crop_type).joinedload(CropType.translations),
                joinedload(Crop.crop_variety).joinedload(CropVariety.translations),
                joinedload(Crop.area_unit)
            )
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
        
        logger.info(
            "Retrieved crop by ID",
            extra={
                "crop_id": str(crop_id),
                "org_id": str(org_id)
            }
        )
        
        return self._to_response(crop)
    
    def update_crop(
        self,
        crop_id: UUID,
        org_id: UUID,
        data: CropUpdate,
        user_id: UUID
    ) -> CropResponse:
        """
        Update crop.
        
        Args:
            crop_id: Crop ID
            data: Crop update data
            org_id: Organization ID
            user_id: User ID updating the crop
            
        Returns:
            Updated crop
            
        Raises:
            NotFoundError: If crop not found
        """
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
        
        # Update fields
        if data.name is not None:
            crop.name = data.name
        if data.description is not None:
            crop.description = data.description
        if data.crop_type_id is not None:
            crop.crop_type_id = data.crop_type_id
        if data.crop_variety_id is not None:
            crop.crop_variety_id = data.crop_variety_id
        if data.area is not None:
            crop.area = data.area
        if data.area_unit_id is not None:
            crop.area_unit_id = data.area_unit_id
        if data.plant_count is not None:
            crop.plant_count = data.plant_count
        
        crop.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(crop)
        
        # Invalidate cache
        self._invalidate_crop_cache(org_id, crop.plot_id)
        
        logger.info(
            "Updated crop",
            extra={
                "crop_id": str(crop_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_response(crop)
    
    def delete_crop(
        self,
        crop_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete crop (hard delete with cascade).
        
        Args:
            crop_id: Crop ID
            org_id: Organization ID
            user_id: User ID deleting the crop
            
        Raises:
            NotFoundError: If crop not found
        """
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
        
        # Store plot_id before deletion
        plot_id = crop.plot_id
        
        # Hard delete (cascade will delete yields and photos)
        self.db.delete(crop)
        self.db.commit()
        
        # Invalidate cache
        self._invalidate_crop_cache(org_id, plot_id)
        
        logger.info(
            "Deleted crop",
            extra={
                "crop_id": str(crop_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def update_lifecycle(
        self,
        crop_id: UUID,
        new_lifecycle: CropLifecycle,
        org_id: UUID,
        user_id: UUID
    ) -> CropResponse:
        """
        Update crop lifecycle with state machine validation.
        
        Args:
            crop_id: Crop ID
            new_lifecycle: New lifecycle stage
            org_id: Organization ID
            user_id: User ID updating the lifecycle
            
        Returns:
            Updated crop
            
        Raises:
            NotFoundError: If crop not found
            ValidationError: If lifecycle transition is invalid
        """
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
        
        # Validate lifecycle transition
        self.validate_lifecycle_transition(crop.lifecycle, new_lifecycle)
        
        # Update lifecycle
        old_lifecycle = crop.lifecycle
        crop.lifecycle = new_lifecycle
        
        # Update corresponding date field
        today = date.today()
        if new_lifecycle == CropLifecycle.PLANTED:
            crop.planted_date = today
        elif new_lifecycle == CropLifecycle.TRANSPLANTED:
            crop.transplanted_date = today
        elif new_lifecycle == CropLifecycle.PRODUCTION:
            crop.production_start_date = today
        elif new_lifecycle == CropLifecycle.COMPLETED:
            crop.completed_date = today
        elif new_lifecycle == CropLifecycle.TERMINATED:
            crop.terminated_date = today
        elif new_lifecycle == CropLifecycle.CLOSED:
            crop.closed_date = today
        
        crop.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(crop)
        
        # Invalidate cache
        self._invalidate_crop_cache(org_id, crop.plot_id)
        
        logger.info(
            "Updated crop lifecycle",
            extra={
                "crop_id": str(crop_id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "old_lifecycle": old_lifecycle.value,
                "new_lifecycle": new_lifecycle.value
            }
        )
        
        return self._to_response(crop)
    
    def validate_lifecycle_transition(
        self,
        current: CropLifecycle,
        new: CropLifecycle
    ) -> bool:
        """
        Validate lifecycle transition according to state machine.
        
        Args:
            current: Current lifecycle stage
            new: New lifecycle stage
            
        Returns:
            True if transition is valid
            
        Raises:
            ValidationError: If transition is invalid
        """
        valid_transitions = LIFECYCLE_TRANSITIONS.get(current, [])
        
        if new not in valid_transitions:
            valid_transitions_str = ", ".join([t.value for t in valid_transitions]) if valid_transitions else "none"
            raise ValidationError(
                message=f"Invalid lifecycle transition from {current.value} to {new.value}. Valid transitions: {valid_transitions_str}",
                error_code="INVALID_LIFECYCLE_TRANSITION",
                details={
                    "current_lifecycle": current.value,
                    "requested_lifecycle": new.value,
                    "valid_transitions": [t.value for t in valid_transitions]
                }
            )
        
        return True
    
    def get_crop_history(
        self,
        plot_id: UUID,
        org_id: UUID
    ) -> List[CropResponse]:
        """
        Get crop history for a plot (all crops, including closed).
        
        Args:
            plot_id: Plot ID
            org_id: Organization ID
            
        Returns:
            List of crops ordered by created_at desc
            
        Raises:
            NotFoundError: If plot not found
        """
        # Validate plot exists and belongs to org
        plot = (
            self.db.query(Plot)
            .join(Farm)
            .filter(
                and_(
                    Plot.id == plot_id,
                    Farm.organization_id == org_id,
                    Plot.is_active == True,
                    Farm.is_active == True
                )
            )
            .first()
        )
        
        if not plot:
            raise NotFoundError(
                message=f"Plot {plot_id} not found",
                error_code="PLOT_NOT_FOUND",
                details={"plot_id": str(plot_id)}
            )
        
        # Get all crops for plot (including closed)
        crops = (
            self.db.query(Crop)
            .filter(Crop.plot_id == plot_id)
            .order_by(Crop.created_at.desc())
            .all()
        )
        
        logger.info(
            "Retrieved crop history",
            extra={
                "plot_id": str(plot_id),
                "org_id": str(org_id),
                "count": len(crops)
            }
        )
        
        return [self._to_response(crop) for crop in crops]
    
    def _find_variety_by_name(self, variety_name: str) -> UUID:
        """
        Find crop variety by name (case-insensitive search in translations).
        
        Args:
            variety_name: Variety name to search for
            
        Returns:
            UUID of the found variety
            
        Raises:
            NotFoundError: If variety not found
        """
        # Search in crop_variety_translations for matching name (case-insensitive)
        translation = (
            self.db.query(CropVarietyTranslation)
            .join(CropVariety)
            .filter(
                and_(
                    func.lower(CropVarietyTranslation.name) == func.lower(variety_name),
                    CropVariety.is_active == True
                )
            )
            .first()
        )
        
        if not translation:
            raise NotFoundError(
                message=f"Crop variety '{variety_name}' not found",
                error_code="VARIETY_NOT_FOUND",
                details={"variety_name": variety_name}
            )
        
        logger.info(
            "Found variety by name",
            extra={
                "variety_name": variety_name,
                "variety_id": str(translation.crop_variety_id)
            }
        )
        
        return translation.crop_variety_id
    
    def _invalidate_crop_cache(self, org_id: UUID, plot_id: Optional[UUID] = None) -> None:
        """
        Invalidate crop cache for organization and optionally plot.
        
        Args:
            org_id: Organization ID
            plot_id: Optional plot ID
        """
        # Invalidate all crop list caches for this organization
        pattern = f"crops:org:{org_id}:*"
        self.cache.delete_pattern(pattern)
        
        # If plot_id provided, also invalidate plot-specific caches
        if plot_id:
            pattern = f"crops:plot:{plot_id}:*"
            self.cache.delete_pattern(pattern)
        
        logger.debug(
            "Invalidated crop cache",
            extra={
                "org_id": str(org_id),
                "plot_id": str(plot_id) if plot_id else None
            }
        )
    
    def _to_response(self, crop: Crop) -> CropResponse:
        """
        Convert crop model to response schema.
        
        Args:
            crop: Crop model
            
        Returns:
            Crop response schema
        """
        # Calculate expected harvest date
        expected_harvest_date = None
        if crop.planted_date and crop.crop_variety and crop.crop_variety.variety_metadata:
            maturity_days = crop.crop_variety.variety_metadata.get("maturity_days")
            if maturity_days:
                try:
                    from datetime import timedelta
                    expected_harvest_date = crop.planted_date + timedelta(days=int(maturity_days))
                except (ValueError, TypeError):
                    pass

        return CropResponse(
            id=str(crop.id),
            plot_id=str(crop.plot_id),
            name=crop.name,
            description=crop.description,
            crop_type_id=str(crop.crop_type_id) if crop.crop_type_id else None,
            crop_variety_id=str(crop.crop_variety_id) if crop.crop_variety_id else None,
            crop_type=CropTypeNested.from_orm(crop.crop_type) if crop.crop_type else None,
            crop_variety=CropVarietyNested.from_orm(crop.crop_variety) if crop.crop_variety else None,
            area=crop.area,
            area_unit_id=str(crop.area_unit_id) if crop.area_unit_id else None,
            plant_count=crop.plant_count,
            lifecycle=crop.lifecycle,
            planned_date=crop.planned_date,
            planted_date=crop.planted_date,
            transplanted_date=crop.transplanted_date,
            production_start_date=crop.production_start_date,
            completed_date=crop.completed_date,
            terminated_date=crop.terminated_date,
            closed_date=crop.closed_date,
            created_at=crop.created_at,
            updated_at=crop.updated_at,
            created_by=str(crop.created_by) if crop.created_by else None,
            updated_by=str(crop.updated_by) if crop.updated_by else None,
            
            # Aliases
            variety=CropVarietyNested.from_orm(crop.crop_variety) if crop.crop_variety else None,
            sowing_date=crop.planted_date,
            status=crop.lifecycle.value if crop.lifecycle else None,
            expected_harvest_date=expected_harvest_date
        )
