"""
Reference Data service for managing general reference data.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError
from app.core.cache import cache_service
from app.models.reference_data import ReferenceDataType, ReferenceData, ReferenceDataTranslation
from app.schemas.reference_data import (
    ReferenceDataTypeResponse,
    ReferenceDataResponse,
    ReferenceDataTranslationResponse
)

logger = get_logger(__name__)

# Cache TTL: 24 hours for reference data (system-defined, rarely change)
CACHE_TTL = 86400


class ReferenceDataService:
    """Service for reference data operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = cache_service
    
    def get_reference_types(self) -> List[ReferenceDataTypeResponse]:
        """
        Get all reference data types.
        
        Returns:
            List of reference data types
        """
        # Check cache first
        cache_key = self.cache._get_key("reference_data_types")
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info(
                "Cache hit for reference data types",
                extra={
                    "cache_key": cache_key
                }
            )
            return [ReferenceDataTypeResponse(**item) for item in cached_data]
        
        # Cache miss - query database
        types = (
            self.db.query(ReferenceDataType)
            .order_by(ReferenceDataType.name)
            .all()
        )
        
        result = [
            ReferenceDataTypeResponse(
                id=str(ref_type.id),
                code=ref_type.code,
                name=ref_type.name,
                description=ref_type.description
            )
            for ref_type in types
        ]
        
        # Cache the result
        cache_data = [item.dict() for item in result]
        self.cache.set(cache_key, cache_data, CACHE_TTL)
        
        logger.info(
            "Retrieved reference data types from database and cached",
            extra={
                "count": len(result),
                "cache_key": cache_key,
                "ttl": CACHE_TTL
            }
        )
        
        return result
    
    def get_reference_data_by_type(
        self, 
        type_code: str, 
        language: str = "en"
    ) -> List[ReferenceDataResponse]:
        """
        Get all reference data for a specific type.
        
        Args:
            type_code: Reference data type code (e.g., 'soil_types', 'water_sources')
            language: Language code for translations (default: en)
            
        Returns:
            List of reference data with translations
            
        Raises:
            NotFoundError: If reference data type not found
        """
        # Check cache first
        cache_key = self.cache._get_key("reference_data", type_code, language)
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info(
                "Cache hit for reference data by type",
                extra={
                    "type_code": type_code,
                    "language": language,
                    "cache_key": cache_key
                }
            )
            return [ReferenceDataResponse(**item) for item in cached_data]
        
        # Cache miss - query database
        # Get reference data type
        ref_type = (
            self.db.query(ReferenceDataType)
            .filter(ReferenceDataType.code == type_code)
            .first()
        )
        
        if not ref_type:
            raise NotFoundError(
                message=f"Reference data type '{type_code}' not found",
                error_code="REFERENCE_DATA_TYPE_NOT_FOUND",
                details={"type_code": type_code}
            )
        
        # Get reference data for this type
        reference_data = (
            self.db.query(ReferenceData)
            .filter(ReferenceData.type_id == ref_type.id)
            .filter(ReferenceData.is_active == True)
            .order_by(ReferenceData.sort_order, ReferenceData.code)
            .all()
        )
        
        result = []
        for ref_data in reference_data:
            # Build translation responses
            translation_responses = [
                ReferenceDataTranslationResponse(
                    language_code=t.language_code,
                    display_name=t.display_name,
                    description=t.description
                )
                for t in ref_data.translations
            ]
            
            result.append(ReferenceDataResponse(
                id=str(ref_data.id),
                type_id=str(ref_data.type_id),
                code=ref_data.code,
                sort_order=ref_data.sort_order,
                is_active=ref_data.is_active,
                reference_metadata=ref_data.reference_metadata,
                translations=translation_responses
            ))
        
        # Cache the result
        cache_data = [item.dict() for item in result]
        self.cache.set(cache_key, cache_data, CACHE_TTL)
        
        logger.info(
            "Retrieved reference data by type from database and cached",
            extra={
                "type_code": type_code,
                "language": language,
                "count": len(result),
                "cache_key": cache_key,
                "ttl": CACHE_TTL
            }
        )
        
        return result
    
    def get_reference_data_by_id(
        self, 
        ref_id: UUID, 
        language: str = "en"
    ) -> ReferenceDataResponse:
        """
        Get a specific reference data by ID.
        
        Args:
            ref_id: Reference data ID
            language: Language code for translations (default: en)
            
        Returns:
            Reference data with translations
            
        Raises:
            NotFoundError: If reference data not found
        """
        # Check cache first
        cache_key = self.cache._get_key("reference_data_item", str(ref_id), language)
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info(
                "Cache hit for reference data by ID",
                extra={
                    "ref_id": str(ref_id),
                    "language": language,
                    "cache_key": cache_key
                }
            )
            return ReferenceDataResponse(**cached_data)
        
        # Cache miss - query database
        ref_data = (
            self.db.query(ReferenceData)
            .filter(ReferenceData.id == ref_id)
            .first()
        )
        
        if not ref_data:
            raise NotFoundError(
                message=f"Reference data {ref_id} not found",
                error_code="REFERENCE_DATA_NOT_FOUND",
                details={"ref_id": str(ref_id)}
            )
        
        # Build translation responses
        translation_responses = [
            ReferenceDataTranslationResponse(
                language_code=t.language_code,
                display_name=t.display_name,
                description=t.description
            )
            for t in ref_data.translations
        ]
        
        result = ReferenceDataResponse(
            id=str(ref_data.id),
            type_id=str(ref_data.type_id),
            code=ref_data.code,
            sort_order=ref_data.sort_order,
            is_active=ref_data.is_active,
            reference_metadata=ref_data.reference_metadata,
            translations=translation_responses
        )
        
        # Cache the result
        self.cache.set(cache_key, result.dict(), CACHE_TTL)
        
        logger.info(
            "Retrieved reference data by ID from database and cached",
            extra={
                "ref_id": str(ref_id),
                "code": ref_data.code,
                "language": language,
                "cache_key": cache_key,
                "ttl": CACHE_TTL
            }
        )
        
        return result

    def get_application_methods(self, language: str = "en") -> List[dict]:
        """
        Get application methods with specific formatting.
        
        Args:
            language: Language code (default: en)
            
        Returns:
            List of application methods with id, name, requires_concentration
        """
        # Reuse existing logic to hit cache/db
        try:
            methods = self.get_reference_data_by_type("application_methods", language)
        except NotFoundError:
             # Try singular if plural failed
             try:
                 methods = self.get_reference_data_by_type("application_method", language)
             except NotFoundError:
                 return []

        result = []
        for method in methods:
            name = method.code 
            for trans in method.translations:
                if trans.language_code == language:
                    name = trans.display_name
                    break
            else:
                 if method.translations:
                     name = method.translations[0].display_name
            
            requires_concentration = False
            if method.reference_metadata:
                requires_concentration = method.reference_metadata.get("requires_concentration", False)

            result.append({
                "id": method.id,
                "name": name,
                "requires_concentration": requires_concentration
            })
        return result
