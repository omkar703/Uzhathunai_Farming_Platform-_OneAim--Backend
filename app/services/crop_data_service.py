"""
Crop Data service for managing crop categories, types, and varieties.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import re
import uuid as uuid_mod
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError
from app.models.crop import Crop
from app.models.crop_data import (
    CropCategory, CropCategoryTranslation,
    CropType, CropTypeTranslation,
    CropVariety, CropVarietyTranslation
)
from app.schemas.crop_data import (
    CropCategoryResponse,
    CropTypeResponse,
    CropVarietyResponse
)

logger = get_logger(__name__)


class CropDataService:
    """Service for crop hierarchy operations (categories, types, varieties)."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_crop_categories(self, language: str = "en") -> List[CropCategoryResponse]:
        """
        Get all crop categories with translations.
        
        Args:
            language: Language code for translations (default: en)
            
        Returns:
            List of crop categories
        """
        categories = (
            self.db.query(CropCategory)
            .filter(CropCategory.is_active == True)
            .order_by(CropCategory.sort_order, CropCategory.code)
            .all()
        )
        
        result = []
        for category in categories:
            # Get translation for requested language
            translation = next(
                (t for t in category.translations if t.language_code == language),
                None
            )
            
            # Fallback to English if translation not found
            if not translation:
                translation = next(
                    (t for t in category.translations if t.language_code == "en"),
                    None
                )
            
            result.append(CropCategoryResponse(
                id=category.id,
                code=category.code,
                sort_order=category.sort_order,
                is_active=category.is_active,
                name=translation.name if translation else category.code,
                description=translation.description if translation else None
            ))
        
        logger.info(
            "Retrieved crop categories",
            extra={
                "language": language,
                "count": len(result)
            }
        )
        
        return result
    
    def get_crop_types_by_category(
        self, 
        category_id: Optional[UUID] = None, 
        language: str = "en"
    ) -> List[CropTypeResponse]:
        """
        Get crop types, optionally filtered by category.
        
        Args:
            category_id: Optional category ID to filter by
            language: Language code for translations (default: en)
            
        Returns:
            List of crop types
        """
        query = self.db.query(CropType).filter(CropType.is_active == True)
        
        if category_id:
            query = query.filter(CropType.category_id == category_id)
        
        types = query.order_by(CropType.sort_order, CropType.code).all()
        
        result = []
        for crop_type in types:
            # Get translation for requested language
            translation = next(
                (t for t in crop_type.translations if t.language_code == language),
                None
            )
            
            # Fallback to English if translation not found
            if not translation:
                translation = next(
                    (t for t in crop_type.translations if t.language_code == "en"),
                    None
                )
            
            result.append(CropTypeResponse(
                id=crop_type.id,
                category_id=crop_type.category_id,
                code=crop_type.code,
                sort_order=crop_type.sort_order,
                is_active=crop_type.is_active,
                name=translation.name if translation else crop_type.code,
                description=translation.description if translation else None
            ))
        
        logger.info(
            "Retrieved crop types",
            extra={
                "category_id": str(category_id) if category_id else None,
                "language": language,
                "count": len(result)
            }
        )
        
        return result
    
    def get_crop_varieties_by_type(
        self, 
        type_id: Optional[UUID] = None, 
        language: str = "en"
    ) -> List[CropVarietyResponse]:
        """
        Get crop varieties, optionally filtered by type.
        
        Args:
            type_id: Optional type ID to filter by
            language: Language code for translations (default: en)
            
        Returns:
            List of crop varieties
        """
        query = self.db.query(CropVariety).filter(CropVariety.is_active == True)
        
        if type_id:
            query = query.filter(CropVariety.crop_type_id == type_id)
        
        varieties = query.order_by(CropVariety.sort_order, CropVariety.code).all()
        
        result = []
        for variety in varieties:
            # Get translation for requested language
            translation = next(
                (t for t in variety.translations if t.language_code == language),
                None
            )
            
            # Fallback to English if translation not found
            if not translation:
                translation = next(
                    (t for t in variety.translations if t.language_code == "en"),
                    None
                )
            
            result.append(CropVarietyResponse(
                id=variety.id,
                crop_type_id=variety.crop_type_id,
                code=variety.code,
                sort_order=variety.sort_order,
                is_active=variety.is_active,
                variety_metadata=variety.variety_metadata or {},
                name=translation.name if translation else variety.code,
                description=translation.description if translation else None
            ))
        
        logger.info(
            "Retrieved crop varieties",
            extra={
                "type_id": str(type_id) if type_id else None,
                "language": language,
                "count": len(result)
            }
        )
        
        return result
    
    def get_variety_by_id(
        self, 
        variety_id: UUID, 
        language: str = "en"
    ) -> CropVarietyResponse:
        """
        Get a specific crop variety by ID.
        
        Args:
            variety_id: Variety ID
            language: Language code for translations (default: en)
            
        Returns:
            Crop variety with metadata
            
        Raises:
            NotFoundError: If variety not found
        """
        variety = (
            self.db.query(CropVariety)
            .filter(CropVariety.id == variety_id)
            .first()
        )
        
        if not variety:
            raise NotFoundError(
                message=f"Crop variety {variety_id} not found",
                error_code="CROP_VARIETY_NOT_FOUND",
                details={"variety_id": str(variety_id)}
            )
        
        # Get translation for requested language
        translation = next(
            (t for t in variety.translations if t.language_code == language),
            None
        )
        
        # Fallback to English if translation not found
        if not translation:
            translation = next(
                (t for t in variety.translations if t.language_code == "en"),
                None
            )
        
        logger.info(
            "Retrieved crop variety by ID",
            extra={
                "variety_id": str(variety_id),
                "code": variety.code,
                "language": language
            }
        )
        
        return CropVarietyResponse(
            id=variety.id,
            crop_type_id=variety.crop_type_id,
            code=variety.code,
            sort_order=variety.sort_order,
            is_active=variety.is_active,
            variety_metadata=variety.variety_metadata or {},
            name=translation.name if translation else variety.code,
            description=translation.description if translation else None
        )
    
    def get_variety_metadata(self, variety_id: UUID) -> Dict[str, Any]:
        """
        Get metadata for a crop variety.
        
        Args:
            variety_id: Variety ID
            
        Returns:
            Variety metadata dictionary
            
        Raises:
            NotFoundError: If variety not found
        """
        variety = (
            self.db.query(CropVariety)
            .filter(CropVariety.id == variety_id)
            .first()
        )
        
        if not variety:
            raise NotFoundError(
                message=f"Crop variety {variety_id} not found",
                error_code="CROP_VARIETY_NOT_FOUND",
                details={"variety_id": str(variety_id)}
            )
        
        metadata = variety.variety_metadata or {}
        
        logger.info(
            "Retrieved variety metadata",
            extra={
                "variety_id": str(variety_id),
                "code": variety.code,
                "metadata_keys": list(metadata.keys())
            }
        )
        
        return metadata
    
    def get_category_by_id(
        self, 
        category_id: UUID, 
        language: str = "en"
    ) -> CropCategoryResponse:
        """
        Get a specific crop category by ID.
        
        Args:
            category_id: Category ID
            language: Language code for translations (default: en)
            
        Returns:
            Crop category
            
        Raises:
            NotFoundError: If category not found
        """
        category = (
            self.db.query(CropCategory)
            .filter(CropCategory.id == category_id)
            .first()
        )
        
        if not category:
            raise NotFoundError(
                message=f"Crop category {category_id} not found",
                error_code="CROP_CATEGORY_NOT_FOUND",
                details={"category_id": str(category_id)}
            )
        
        # Get translation for requested language
        translation = next(
            (t for t in category.translations if t.language_code == language),
            None
        )
        
        # Fallback to English if translation not found
        if not translation:
            translation = next(
                (t for t in category.translations if t.language_code == "en"),
                None
            )
        
        logger.info(
            "Retrieved crop category by ID",
            extra={
                "category_id": str(category_id),
                "code": category.code,
                "language": language
            }
        )
        
        return CropCategoryResponse(
            id=category.id,
            code=category.code,
            sort_order=category.sort_order,
            is_active=category.is_active,
            name=translation.name if translation else category.code,
            description=translation.description if translation else None
        )
    
    def get_type_by_id(
        self, 
        type_id: UUID, 
        language: str = "en"
    ) -> CropTypeResponse:
        """
        Get a specific crop type by ID.
        
        Args:
            type_id: Type ID
            language: Language code for translations (default: en)
            
        Returns:
            Crop type
            
        Raises:
            NotFoundError: If type not found
        """
        crop_type = (
            self.db.query(CropType)
            .filter(CropType.id == type_id)
            .first()
        )
        
        if not crop_type:
            raise NotFoundError(
                message=f"Crop type {type_id} not found",
                error_code="CROP_TYPE_NOT_FOUND",
                details={"type_id": str(type_id)}
            )
        
        # Get translation for requested language
        translation = next(
            (t for t in crop_type.translations if t.language_code == language),
            None
        )
        
        # Fallback to English if translation not found
        if not translation:
            translation = next(
                (t for t in crop_type.translations if t.language_code == "en"),
                None
            )
        
        logger.info(
            "Retrieved crop type by ID",
            extra={
                "type_id": str(type_id),
                "code": crop_type.code,
                "language": language
            }
        )
        
        return CropTypeResponse(
            id=crop_type.id,
            category_id=crop_type.category_id,
            code=crop_type.code,
            sort_order=crop_type.sort_order,
            is_active=crop_type.is_active,
            name=translation.name if translation else crop_type.code,
            description=translation.description if translation else None
        )

    def create_custom_crop_type(self, name: str) -> CropTypeResponse:
        """
        Create a custom crop type under a special 'custom' category.
        Idempotent: returns existing type if the same name (code) already exists.

        Args:
            name: Human-readable name for the crop type

        Returns:
            Created (or existing) CropTypeResponse
        """
        # Generate a safe code from the name
        code = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
        if len(code) > 48:
            code = code[:48]
        code = f"custom_{code}"

        # Ensure "custom" category exists
        custom_category = (
            self.db.query(CropCategory)
            .filter(CropCategory.code == "custom")
            .first()
        )
        if not custom_category:
            custom_category = CropCategory(
                id=uuid_mod.uuid4(),
                code="custom",
                sort_order=9999,
                is_active=True,
            )
            self.db.add(custom_category)
            self.db.flush()

            # Add English translation for the custom category
            cat_translation = CropCategoryTranslation(
                id=uuid_mod.uuid4(),
                crop_category_id=custom_category.id,
                language_code="en",
                name="Custom",
                description="User-defined custom crop types",
            )
            self.db.add(cat_translation)
            self.db.flush()

        # Check if crop type with same code already exists
        existing = (
            self.db.query(CropType)
            .filter(CropType.code == code)
            .first()
        )
        if existing:
            translation = next(
                (t for t in existing.translations if t.language_code == "en"), None
            )
            return CropTypeResponse(
                id=existing.id,
                category_id=existing.category_id,
                code=existing.code,
                sort_order=existing.sort_order,
                is_active=existing.is_active,
                name=translation.name if translation else existing.code,
                description=None,
            )

        # Create the crop type
        crop_type = CropType(
            id=uuid_mod.uuid4(),
            category_id=custom_category.id,
            code=code,
            sort_order=9999,
            is_active=True,
        )
        self.db.add(crop_type)
        self.db.flush()

        # Add English translation
        translation = CropTypeTranslation(
            id=uuid_mod.uuid4(),
            crop_type_id=crop_type.id,
            language_code="en",
            name=name,
            description=None,
        )
        self.db.add(translation)
        self.db.commit()
        self.db.refresh(crop_type)

        logger.info(
            "Created custom crop type",
            extra={"code": code, "name": name}
        )

        return CropTypeResponse(
            id=crop_type.id,
            category_id=crop_type.category_id,
            code=crop_type.code,
            sort_order=crop_type.sort_order,
            is_active=crop_type.is_active,
            name=name,
            description=None,
        )

    def get_frequent_crop_types(self, org_id: UUID, limit: int = 5, language: str = "en") -> List[CropTypeResponse]:
        """
        Get the most frequently used crop types for an organization.

        Args:
            org_id: Organization ID (used via farms/plots/crops join)
            limit: Max number of results (default 5)
            language: Language code for translations

        Returns:
            List of CropTypeResponse ordered by usage frequency
        """
        from app.models.plot import Plot
        from app.models.farm import Farm

        # Count usage of each crop_type_id within the org's crops
        rows = (
            self.db.query(
                Crop.crop_type_id,
                func.count(Crop.id).label("usage_count")
            )
            .join(Plot, Crop.plot_id == Plot.id)
            .join(Farm, Plot.farm_id == Farm.id)
            .filter(
                Farm.organization_id == org_id,
                Crop.crop_type_id.isnot(None)
            )
            .group_by(Crop.crop_type_id)
            .order_by(func.count(Crop.id).desc())
            .limit(limit)
            .all()
        )

        result = []
        for row in rows:
            crop_type = self.db.query(CropType).filter(CropType.id == row.crop_type_id).first()
            if not crop_type:
                continue
            translation = next(
                (t for t in crop_type.translations if t.language_code == language), None
            )
            if not translation:
                translation = next(
                    (t for t in crop_type.translations if t.language_code == "en"), None
                )
            result.append(CropTypeResponse(
                id=crop_type.id,
                category_id=crop_type.category_id,
                code=crop_type.code,
                sort_order=crop_type.sort_order,
                is_active=crop_type.is_active,
                name=translation.name if translation else crop_type.code,
                description=translation.description if translation else None,
            ))

        logger.info(
            "Retrieved frequent crop types",
            extra={"org_id": str(org_id), "count": len(result)}
        )
        return result

