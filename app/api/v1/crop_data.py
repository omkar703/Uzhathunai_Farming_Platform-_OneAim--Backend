"""
Crop Data API endpoints for Uzhathunai v2.0.
"""
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.crop_data import (
    CropCategoryResponse,
    CropTypeResponse,
    CropTypeCreate,
    CropVarietyResponse
)
from app.schemas.response import BaseResponse
from app.services.crop_data_service import CropDataService

router = APIRouter()


@router.get("/categories", response_model=BaseResponse[list[CropCategoryResponse]])
def get_crop_categories(
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all crop categories.

    - **language**: Language code for translations (default: en)

    Returns list of crop categories with translations.
    """
    service = CropDataService(db)
    categories = service.get_crop_categories(language)
    return {
        "success": True,
        "message": "Crop categories retrieved successfully",
        "data": categories
    }


@router.get("/types/frequent", response_model=BaseResponse[list[CropTypeResponse]])
def get_frequent_crop_types(
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get top-5 most frequently used crop types for the current user's organization.

    Returns a list of up to 5 crop types ordered by usage frequency (most used first).
    Useful for showing quick-access suggestions when selecting a crop type.
    """
    service = CropDataService(db)
    org_id = current_user.current_organization_id
    types = service.get_frequent_crop_types(org_id=org_id, limit=5, language=language)
    return {
        "success": True,
        "message": "Frequent crop types retrieved successfully",
        "data": types
    }


@router.get("/types", response_model=BaseResponse[list[CropTypeResponse]])
def get_crop_types(
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search by name or code (case-insensitive)"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get crop types, optionally filtered by category and/or search term.

    - **category_id**: Optional filter by crop category UUID
    - **search**: Optional substring filter applied to name/code
    - **language**: Language code for translations (default: en)

    Returns list of crop types with translations.
    """
    service = CropDataService(db)

    if category_id:
        types = service.get_crop_types_by_category(category_id, language)
    else:
        # Get all types across all categories
        categories = service.get_crop_categories(language)
        types = []
        for category in categories:
            cat_types = service.get_crop_types_by_category(category.id, language)
            types.extend(cat_types)

    # Apply optional search filter (case-insensitive on name and code)
    if search:
        search_lower = search.lower()
        types = [
            t for t in types
            if search_lower in (t.name or "").lower() or search_lower in t.code.lower()
        ]

    return {
        "success": True,
        "message": "Crop types retrieved successfully",
        "data": types
    }


@router.post("/types", response_model=BaseResponse[CropTypeResponse])
def create_crop_type(
    data: CropTypeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a custom crop type (any authenticated user).

    Farmers can add their own crop types here. The type is stored under a
    special 'custom' category and becomes globally available for all users.
    If a type with the same name already exists, it is returned as-is
    (idempotent).

    - **name**: Human-readable name for the crop type (e.g. "Wheat Winter 2025-26")
    """
    service = CropDataService(db)
    crop_type = service.create_custom_crop_type(name=data.name)
    return {
        "success": True,
        "message": "Crop type created successfully",
        "data": crop_type
    }


# ─────────────────────────────────────────────────────────────────────────────
# Admin-only endpoints for managing crop types
# ─────────────────────────────────────────────────────────────────────────────

def _require_admin(user: User) -> None:
    """Raise 403 if user is not an admin or super-admin."""
    from app.core.exceptions import ForbiddenError
    # Check primary role code on the user object (set by auth middleware)
    role_code = getattr(user, "primary_role_code", None) or getattr(user, "role_code", None)
    if role_code not in ("ADMIN", "SUPER_ADMIN"):
        raise ForbiddenError(
            message="Only administrators can perform this action.",
            error_code="ADMIN_REQUIRED"
        )


class AdminCropTypeCreate(CropTypeCreate):
    """Admin version of crop type creation — allows specifying category code."""
    category_code: str = "custom"
    description: str | None = None


@router.post("/admin/types", response_model=BaseResponse[CropTypeResponse])
def admin_create_crop_type(
    data: CropTypeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[Admin only]** Create a named crop type under any category.

    Unlike the regular POST /types which always puts things under 'custom',
    this endpoint creates a crop type that will appear in the main catalogue.

    - **name**: Display name (e.g. "Paddy – Kharif 2026")
    """
    _require_admin(current_user)
    service = CropDataService(db)
    crop_type = service.create_custom_crop_type(name=data.name)
    return {
        "success": True,
        "message": "Crop type created by admin",
        "data": crop_type
    }


@router.patch("/admin/types/{type_id}", response_model=BaseResponse[CropTypeResponse])
def admin_update_crop_type(
    type_id: UUID,
    data: CropTypeCreate,
    language: str = Query("en", description="Language code"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[Admin only]** Update the name of an existing crop type.

    - **type_id**: UUID of the crop type to update
    - **name**: New display name
    """
    _require_admin(current_user)

    from app.models.crop_data import CropType, CropTypeTranslation

    crop_type = db.query(CropType).filter(CropType.id == type_id).first()
    if not crop_type:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(message=f"Crop type {type_id} not found", error_code="CROP_TYPE_NOT_FOUND")

    # Update or create the translation for the requested language
    translation = next((t for t in crop_type.translations if t.language_code == language), None)
    if translation:
        translation.name = data.name.strip()
    else:
        import uuid as _uuid
        new_trans = CropTypeTranslation(
            id=_uuid.uuid4(),
            crop_type_id=crop_type.id,
            language_code=language,
            name=data.name.strip(),
        )
        db.add(new_trans)

    db.commit()
    db.refresh(crop_type)

    final_trans = next((t for t in crop_type.translations if t.language_code == language), None)
    return {
        "success": True,
        "message": "Crop type updated",
        "data": {
            "id": str(crop_type.id),
            "category_id": str(crop_type.category_id),
            "code": crop_type.code,
            "sort_order": crop_type.sort_order,
            "is_active": crop_type.is_active,
            "name": final_trans.name if final_trans else crop_type.code,
            "description": final_trans.description if final_trans else None,
        }
    }


@router.delete("/admin/types/{type_id}", response_model=BaseResponse[dict])
def admin_delete_crop_type(
    type_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[Admin only]** Deactivate a crop type (soft-delete).

    The crop type is not removed from the database; it is marked inactive
    so existing crop records remain intact.

    - **type_id**: UUID of the crop type to deactivate
    """
    _require_admin(current_user)

    from app.models.crop_data import CropType

    crop_type = db.query(CropType).filter(CropType.id == type_id).first()
    if not crop_type:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(message=f"Crop type {type_id} not found", error_code="CROP_TYPE_NOT_FOUND")

    crop_type.is_active = False
    db.commit()

    return {
        "success": True,
        "message": f"Crop type '{crop_type.code}' deactivated",
        "data": {"id": str(type_id), "deactivated": True}
    }


@router.post("/admin/seed-defaults", response_model=BaseResponse[dict])
def admin_seed_default_crop_types(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[Admin only]** Seed the database with standard Indian crop types.

    This endpoint seeds all pre-defined Indian crop categories and types
    (Kharif, Rabi, Zaid seasons for 2024-2026) into the database.
    It is idempotent — running it multiple times will not create duplicates.

    Use this after initial deployment to populate the crop type catalogue.
    """
    _require_admin(current_user)

    import sys
    import os

    # Import the seed function from the seed script
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    try:
        # Import the seed data definitions directly to avoid re-importing SessionLocal
        from seed_crop_types import CATEGORIES, CROP_TYPES
        import uuid as _uuid
        from app.models.crop_data import (
            CropCategory, CropCategoryTranslation,
            CropType, CropTypeTranslation,
        )

        cat_map = {}
        created_cats = 0
        created_types = 0
        skipped = 0

        for cat_data in CATEGORIES:
            existing = db.query(CropCategory).filter(CropCategory.code == cat_data["code"]).first()
            if existing:
                cat_map[cat_data["code"]] = existing
                continue
            cat = CropCategory(
                id=_uuid.uuid4(),
                code=cat_data["code"],
                sort_order=cat_data["sort_order"],
                is_active=True,
            )
            db.add(cat)
            db.flush()
            db.add(CropCategoryTranslation(
                id=_uuid.uuid4(),
                crop_category_id=cat.id,
                language_code="en",
                name=cat_data["name_en"],
                description=cat_data["desc_en"],
            ))
            cat_map[cat_data["code"]] = cat
            created_cats += 1

        db.flush()

        for (cat_code, crop_code, crop_name, sort_order, desc) in CROP_TYPES:
            if db.query(CropType).filter(CropType.code == crop_code).first():
                skipped += 1
                continue
            category = cat_map.get(cat_code)
            if not category:
                continue
            ct = CropType(id=_uuid.uuid4(), category_id=category.id, code=crop_code, sort_order=sort_order, is_active=True)
            db.add(ct)
            db.flush()
            db.add(CropTypeTranslation(id=_uuid.uuid4(), crop_type_id=ct.id, language_code="en", name=crop_name, description=desc))
            created_types += 1

        db.commit()
        return {
            "success": True,
            "message": "Default crop types seeded successfully",
            "data": {
                "categories_created": created_cats,
                "crop_types_created": created_types,
                "crop_types_skipped": skipped,
            }
        }
    except Exception as e:
        db.rollback()
        raise


class CropYearUpdateRequest(BaseModel):
    """Schema for the bulk crop-year update endpoint."""
    from_year: int = Field(
        ...,
        ge=2000, le=2100,
        description="The year currently in crop names (e.g. 2025)",
        examples=[2025]
    )
    to_year: int = Field(
        ...,
        ge=2000, le=2100,
        description="The year to replace it with (e.g. 2026)",
        examples=[2026]
    )
    dry_run: bool = Field(
        False,
        description="If true, previews changes without saving them to the DB"
    )

    @validator("to_year")
    def years_must_differ(cls, v, values):
        if "from_year" in values and v == values["from_year"]:
            raise ValueError("to_year must be different from from_year")
        return v


@router.post("/admin/update-year", response_model=BaseResponse[dict])
def admin_update_crop_year(
    data: CropYearUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **[Admin only]** Bulk-shift all year references in crop type names.

    Every year, the admin can call this endpoint to roll all crop type names
    forward — e.g. from 2025 to 2026.  The function replaces:

    - `from_year`   → `to_year`
    - `from_year+1` → `to_year+1`

    So a name like **"Wheat – Oct 2025–Apr 2026"** becomes
    **"Wheat – Oct 2026–Apr 2027"** automatically.

    - **from_year**: Year currently in the names (e.g. `2025`)
    - **to_year**: New year to write (e.g. `2026`)
    - **dry_run**: If `true`, previews the changes without saving them
    """
    _require_admin(current_user)

    from app.models.crop_data import CropType, CropTypeTranslation

    # Build replacement pairs — order matters: replace higher year first
    # so "2025" and "2026" replacements don't cascade into each other.
    from_y  = str(data.from_year)
    to_y    = str(data.to_year)
    from_y1 = str(data.from_year + 1)
    to_y1   = str(data.to_year + 1)

    translations = (
        db.query(CropTypeTranslation)
        .join(CropType, CropTypeTranslation.crop_type_id == CropType.id)
        .filter(CropType.is_active.is_(True))
        .all()
    )

    updated = []
    skipped = 0

    for trans in translations:
        original = trans.name or ""
        # Replace higher year first to avoid double-replacement
        new_name = original.replace(from_y1, to_y1).replace(from_y, to_y)
        if new_name != original:
            updated.append({
                "id":       str(trans.id),
                "old_name": original,
                "new_name": new_name,
            })
            if not data.dry_run:
                trans.name = new_name
        else:
            skipped += 1

    if not data.dry_run and updated:
        db.commit()

    return {
        "success": True,
        "message": (
            f"[DRY RUN] Would update {len(updated)} crop type name(s)"
            if data.dry_run
            else f"Updated {len(updated)} crop type name(s) from {data.from_year} → {data.to_year}"
        ),
        "data": {
            "dry_run":        data.dry_run,
            "from_year":      data.from_year,
            "to_year":        data.to_year,
            "updated_count":  len(updated),
            "skipped_count":  skipped,
            "changes":        updated if data.dry_run else [],
        }
    }


@router.get("/varieties", response_model=BaseResponse[list[CropVarietyResponse]])
def get_crop_varieties(
    type_id: Optional[UUID] = Query(None, alias="crop_type_id", description="Filter by type ID"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get crop varieties, optionally filtered by type.

    - **type_id**: Optional filter by crop type UUID
    - **language**: Language code for translations (default: en)

    Returns list of crop varieties with translations and metadata.
    """
    service = CropDataService(db)

    if type_id:
        varieties = service.get_crop_varieties_by_type(type_id, language)
    else:
        # Get all varieties across all types
        categories = service.get_crop_categories(language)
        varieties = []
        for category in categories:
            types = service.get_crop_types_by_category(category.id, language)
            for crop_type in types:
                cat_varieties = service.get_crop_varieties_by_type(crop_type.id, language)
                varieties.extend(cat_varieties)

    return {
        "success": True,
        "message": "Crop varieties retrieved successfully",
        "data": varieties
    }


@router.get("/varieties/{variety_id}", response_model=BaseResponse[CropVarietyResponse])
def get_crop_variety(
    variety_id: UUID,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific crop variety by ID.

    - **variety_id**: UUID of the crop variety
    - **language**: Language code for translations (default: en)

    Returns crop variety details with translation and metadata.
    """
    service = CropDataService(db)

    # Get the variety from database
    from app.models.crop_data import CropVariety, CropVarietyTranslation
    variety = db.query(CropVariety).filter(CropVariety.id == variety_id).first()

    if not variety:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(
            message=f"Crop variety {variety_id} not found",
            error_code="CROP_VARIETY_NOT_FOUND"
        )

    # Get translation
    translation = db.query(CropVarietyTranslation).filter(
        CropVarietyTranslation.variety_id == variety_id,
        CropVarietyTranslation.language_code == language
    ).first()

    # Fallback to English if translation not found
    if not translation:
        translation = db.query(CropVarietyTranslation).filter(
            CropVarietyTranslation.variety_id == variety_id,
            CropVarietyTranslation.language_code == "en"
        ).first()

    res = CropVarietyResponse(
        id=variety.id,
        crop_type_id=variety.crop_type_id,
        code=variety.code,
        name=translation.name if translation else variety.code,
        description=translation.description if translation else None,
        variety_metadata=variety.variety_metadata or {},
        sort_order=variety.sort_order,
        is_active=variety.is_active
    )
    return {
        "success": True,
        "message": "Crop variety retrieved successfully",
        "data": res
    }
