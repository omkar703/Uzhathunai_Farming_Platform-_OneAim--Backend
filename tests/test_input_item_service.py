"""
Unit tests for InputItemService.

Tests:
- System-defined items are read-only
- Organization-specific items ownership validation
- Category and item CRUD operations
- Multilingual support
- Ownership validation for update/delete operations

Requirements: 3.10, 3.11, 3.12, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
"""
import pytest
from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from app.services.input_item_service import InputItemService
from app.models.input_item import InputItemCategory, InputItemCategoryTranslation, InputItem, InputItemTranslation
from app.models.organization import Organization
from app.models.enums import OrganizationType, OrganizationStatus
from app.schemas.input_item import (
    InputItemCategoryCreate, InputItemCategoryUpdate,
    InputItemCreate, InputItemUpdate
)
from app.core.exceptions import NotFoundError, PermissionError, ValidationError


@pytest.fixture
def test_org(db: Session, test_user) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Test Farm Org",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_org2(db: Session, test_user) -> Organization:
    """Create a second test organization."""
    org = Organization(
        name="Test Farm Org 2",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def system_category(db: Session, test_user) -> InputItemCategory:
    """Create a system-defined input item category."""
    category = InputItemCategory(
        code="FERTILIZER",
        is_system_defined=True,
        owner_org_id=None,
        sort_order=1,
        is_active=True,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(category)
    db.flush()
    
    # Add translations
    translations = [
        InputItemCategoryTranslation(
            category_id=category.id,
            language_code="en",
            name="Fertilizer",
            description="Fertilizers and nutrients"
        ),
        InputItemCategoryTranslation(
            category_id=category.id,
            language_code="ta",
            name="உரம்",
            description="உரங்கள் மற்றும் ஊட்டச்சத்துக்கள்"
        )
    ]
    for trans in translations:
        db.add(trans)
    
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def org_category(db: Session, test_org: Organization, test_user) -> InputItemCategory:
    """Create an organization-specific input item category."""
    category = InputItemCategory(
        code="CUSTOM_FERTILIZER",
        is_system_defined=False,
        owner_org_id=test_org.id,
        sort_order=10,
        is_active=True,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(category)
    db.flush()
    
    # Add translations
    translation = InputItemCategoryTranslation(
        category_id=category.id,
        language_code="en",
        name="Custom Fertilizer",
        description="Organization-specific fertilizers"
    )
    db.add(translation)
    
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def system_item(db: Session, system_category: InputItemCategory, test_user) -> InputItem:
    """Create a system-defined input item."""
    item = InputItem(
        code="NPK_19_19_19",
        category_id=system_category.id,
        is_system_defined=True,
        owner_org_id=None,
        item_metadata={
            "brand": "Generic",
            "npk_ratio": "19:19:19",
            "form": "Granular"
        },
        sort_order=1,
        is_active=True,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(item)
    db.flush()
    
    # Add translations
    translations = [
        InputItemTranslation(
            input_item_id=item.id,
            language_code="en",
            name="NPK 19-19-19",
            description="Balanced NPK fertilizer"
        ),
        InputItemTranslation(
            input_item_id=item.id,
            language_code="ta",
            name="NPK 19-19-19",
            description="சமச்சீர் NPK உரம்"
        )
    ]
    for trans in translations:
        db.add(trans)
    
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def org_item(db: Session, org_category: InputItemCategory, test_org: Organization, test_user) -> InputItem:
    """Create an organization-specific input item."""
    item = InputItem(
        code="CUSTOM_NPK",
        category_id=org_category.id,
        is_system_defined=False,
        owner_org_id=test_org.id,
        item_metadata={
            "brand": "Custom Brand",
            "npk_ratio": "20:10:10"
        },
        sort_order=1,
        is_active=True,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(item)
    db.flush()
    
    # Add translation
    translation = InputItemTranslation(
        input_item_id=item.id,
        language_code="en",
        name="Custom NPK",
        description="Custom NPK fertilizer"
    )
    db.add(translation)
    
    db.commit()
    db.refresh(item)
    return item


class TestInputItemCategoryOperations:
    """Test suite for input item category operations."""
    
    def test_get_categories_includes_system_and_org(
        self, 
        db: Session, 
        test_org: Organization,
        system_category: InputItemCategory,
        org_category: InputItemCategory
    ):
        """Test that get_categories returns both system and org-specific categories."""
        service = InputItemService(db)
        
        categories = service.get_categories(test_org.id, language="en", include_system=True)
        
        # Should include both system and org categories
        assert len(categories) >= 2
        
        category_codes = [c.code for c in categories]
        assert "FERTILIZER" in category_codes  # System category
        assert "CUSTOM_FERTILIZER" in category_codes  # Org category
    
    def test_get_categories_only_org_specific(
        self,
        db: Session,
        test_org: Organization,
        system_category: InputItemCategory,
        org_category: InputItemCategory
    ):
        """Test that get_categories can filter to only org-specific categories."""
        service = InputItemService(db)
        
        categories = service.get_categories(test_org.id, language="en", include_system=False)
        
        # Should only include org categories
        category_codes = [c.code for c in categories]
        assert "FERTILIZER" not in category_codes  # System category excluded
        assert "CUSTOM_FERTILIZER" in category_codes  # Org category included
    
    def test_get_categories_multilingual(
        self,
        db: Session,
        test_org: Organization,
        system_category: InputItemCategory
    ):
        """Test that categories return correct translations."""
        service = InputItemService(db)
        
        # Get categories
        categories = service.get_categories(test_org.id, language="en")
        fertilizer = next(c for c in categories if c.code == "FERTILIZER")
        
        # Verify translations are present
        assert len(fertilizer.translations) >= 2
        
        # Check English translation
        en_trans = next((t for t in fertilizer.translations if t.language_code == "en"), None)
        assert en_trans is not None
        assert en_trans.name == "Fertilizer"
        
        # Check Tamil translation
        ta_trans = next((t for t in fertilizer.translations if t.language_code == "ta"), None)
        assert ta_trans is not None
        assert ta_trans.name == "உரம்"
    
    def test_create_org_category_success(self, db: Session, test_org: Organization, test_user):
        """Test creating an organization-specific category."""
        service = InputItemService(db)
        
        data = InputItemCategoryCreate(
            code="PESTICIDE",
            translations=[
                {"language_code": "en", "name": "Pesticide", "description": "Pest control products"},
                {"language_code": "ta", "name": "பூச்சிக்கொல்லி", "description": "பூச்சி கட்டுப்பாடு பொருட்கள்"}
            ],
            sort_order=5
        )
        
        category = service.create_org_category(data, test_org.id, test_user.id)
        
        # Verify category created
        assert category.id is not None
        assert category.code == "PESTICIDE"
        assert category.is_system_defined is False
        assert str(category.owner_org_id) == str(test_org.id)
    
    def test_create_org_category_duplicate_code(
        self,
        db: Session,
        test_org: Organization,
        org_category: InputItemCategory,
        test_user
    ):
        """Test that creating category with duplicate code fails."""
        service = InputItemService(db)
        
        data = InputItemCategoryCreate(
            code="CUSTOM_FERTILIZER",  # Already exists
            translations=[
                {"language_code": "en", "name": "Another Custom Fertilizer"}
            ],
            sort_order=5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            service.create_org_category(data, test_org.id, test_user.id)
        
        assert exc_info.value.error_code == "DUPLICATE_CATEGORY_CODE"
    
    def test_update_org_category_success(
        self,
        db: Session,
        test_org: Organization,
        org_category: InputItemCategory,
        test_user
    ):
        """Test updating an organization-specific category."""
        service = InputItemService(db)
        
        data = InputItemCategoryUpdate(
            translations=[
                {"language_code": "en", "name": "Updated Custom Fertilizer", "description": "Updated description"}
            ],
            sort_order=20
        )
        
        updated = service.update_org_category(org_category.id, data, test_org.id, test_user.id)
        
        # Verify updates
        assert updated.sort_order == 20
    
    def test_update_system_category_fails(
        self,
        db: Session,
        test_org: Organization,
        system_category: InputItemCategory,
        test_user
    ):
        """Test that updating system-defined category fails."""
        service = InputItemService(db)
        
        data = InputItemCategoryUpdate(
            translations=[
                {"language_code": "en", "name": "Modified Fertilizer"}
            ]
        )
        
        with pytest.raises(PermissionError) as exc_info:
            service.update_org_category(system_category.id, data, test_org.id, test_user.id)
        
        assert exc_info.value.error_code == "SYSTEM_DEFINED_IMMUTABLE"
        assert "Cannot update system-defined" in exc_info.value.message
    
    def test_update_other_org_category_fails(
        self,
        db: Session,
        test_org: Organization,
        test_org2: Organization,
        org_category: InputItemCategory,
        test_user
    ):
        """Test that updating another org's category fails."""
        service = InputItemService(db)
        
        data = InputItemCategoryUpdate(
            translations=[
                {"language_code": "en", "name": "Hacked Category"}
            ]
        )
        
        # Try to update with different org ID
        with pytest.raises(PermissionError) as exc_info:
            service.update_org_category(org_category.id, data, test_org2.id, test_user.id)
        
        assert exc_info.value.error_code == "INSUFFICIENT_PERMISSIONS"
        assert "owned by another organization" in exc_info.value.message
    
    def test_delete_org_category_success(
        self,
        db: Session,
        test_org: Organization,
        org_category: InputItemCategory,
        test_user
    ):
        """Test deleting an organization-specific category."""
        service = InputItemService(db)
        
        # Delete category
        service.delete_org_category(org_category.id, test_org.id, test_user.id)
        
        # Verify soft delete
        db.refresh(org_category)
        assert org_category.is_active is False
    
    def test_delete_system_category_fails(
        self,
        db: Session,
        test_org: Organization,
        system_category: InputItemCategory,
        test_user
    ):
        """Test that deleting system-defined category fails."""
        service = InputItemService(db)
        
        with pytest.raises(PermissionError) as exc_info:
            service.delete_org_category(system_category.id, test_org.id, test_user.id)
        
        assert exc_info.value.error_code == "SYSTEM_DEFINED_IMMUTABLE"
        assert "Cannot delete system-defined" in exc_info.value.message
    
    def test_delete_other_org_category_fails(
        self,
        db: Session,
        test_org: Organization,
        test_org2: Organization,
        org_category: InputItemCategory,
        test_user
    ):
        """Test that deleting another org's category fails."""
        service = InputItemService(db)
        
        with pytest.raises(PermissionError) as exc_info:
            service.delete_org_category(org_category.id, test_org2.id, test_user.id)
        
        assert exc_info.value.error_code == "INSUFFICIENT_PERMISSIONS"


class TestInputItemOperations:
    """Test suite for input item operations."""
    
    def test_get_items_includes_system_and_org(
        self,
        db: Session,
        test_org: Organization,
        system_item: InputItem,
        org_item: InputItem
    ):
        """Test that get_items returns both system and org-specific items."""
        service = InputItemService(db)
        
        items = service.get_items(test_org.id, language="en", include_system=True)
        
        # Should include both system and org items
        assert len(items) >= 2
        
        item_codes = [i.code for i in items]
        assert "NPK_19_19_19" in item_codes  # System item
        assert "CUSTOM_NPK" in item_codes  # Org item
    
    def test_get_items_only_org_specific(
        self,
        db: Session,
        test_org: Organization,
        system_item: InputItem,
        org_item: InputItem
    ):
        """Test that get_items can filter to only org-specific items."""
        service = InputItemService(db)
        
        items = service.get_items(test_org.id, language="en", include_system=False)
        
        # Should only include org items
        item_codes = [i.code for i in items]
        assert "NPK_19_19_19" not in item_codes  # System item excluded
        assert "CUSTOM_NPK" in item_codes  # Org item included
    
    def test_get_items_filter_by_category(
        self,
        db: Session,
        test_org: Organization,
        system_category: InputItemCategory,
        system_item: InputItem,
        org_item: InputItem
    ):
        """Test filtering items by category."""
        service = InputItemService(db)
        
        # Get items in system category only
        items = service.get_items(
            test_org.id,
            category_id=system_category.id,
            language="en",
            include_system=True
        )
        
        # Should only include items from that category
        for item in items:
            assert str(item.category_id) == str(system_category.id)
    
    def test_get_items_multilingual(
        self,
        db: Session,
        test_org: Organization,
        system_item: InputItem
    ):
        """Test that items return correct translations."""
        service = InputItemService(db)
        
        # Get items
        items = service.get_items(test_org.id, language="en")
        npk = next(i for i in items if i.code == "NPK_19_19_19")
        
        # Verify translations are present
        assert len(npk.translations) >= 2
        
        # Check English translation
        en_trans = next((t for t in npk.translations if t.language_code == "en"), None)
        assert en_trans is not None
        assert en_trans.name == "NPK 19-19-19"
        
        # Check Tamil translation
        ta_trans = next((t for t in npk.translations if t.language_code == "ta"), None)
        assert ta_trans is not None
        assert ta_trans.name == "NPK 19-19-19"
        assert "சமச்சீர்" in ta_trans.description
    
    def test_create_org_item_success(
        self,
        db: Session,
        test_org: Organization,
        org_category: InputItemCategory,
        test_user
    ):
        """Test creating an organization-specific item."""
        service = InputItemService(db)
        
        data = InputItemCreate(
            code="CUSTOM_UREA",
            category_id=org_category.id,
            translations=[
                {"language_code": "en", "name": "Custom Urea", "description": "Custom urea fertilizer"},
                {"language_code": "ta", "name": "தனிப்பயன் யூரியா", "description": "தனிப்பயன் யூரியா உரம்"}
            ],
            item_metadata={
                "brand": "Custom Brand",
                "npk_ratio": "46:0:0",
                "form": "Granular"
            },
            sort_order=5
        )
        
        item = service.create_org_item(data, test_org.id, test_user.id)
        
        # Verify item created
        assert item.id is not None
        assert item.code == "CUSTOM_UREA"
        assert item.is_system_defined is False
        assert str(item.owner_org_id) == str(test_org.id)
        assert item.item_metadata["brand"] == "Custom Brand"
    
    def test_create_org_item_duplicate_code(
        self,
        db: Session,
        test_org: Organization,
        org_category: InputItemCategory,
        org_item: InputItem,
        test_user
    ):
        """Test that creating item with duplicate code fails."""
        service = InputItemService(db)
        
        data = InputItemCreate(
            code="CUSTOM_NPK",  # Already exists
            category_id=org_category.id,
            translations=[
                {"language_code": "en", "name": "Another Custom NPK"}
            ]
        )
        
        with pytest.raises(ValidationError) as exc_info:
            service.create_org_item(data, test_org.id, test_user.id)
        
        assert exc_info.value.error_code == "DUPLICATE_ITEM_CODE"
    
    def test_create_org_item_invalid_category(
        self,
        db: Session,
        test_org: Organization,
        test_user
    ):
        """Test that creating item with invalid category fails."""
        service = InputItemService(db)
        
        fake_category_id = uuid4()
        
        data = InputItemCreate(
            code="INVALID_ITEM",
            category_id=fake_category_id,
            translations=[
                {"language_code": "en", "name": "Invalid Item"}
            ]
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            service.create_org_item(data, test_org.id, test_user.id)
        
        assert exc_info.value.error_code == "CATEGORY_NOT_FOUND"
    
    def test_update_org_item_success(
        self,
        db: Session,
        test_org: Organization,
        org_item: InputItem,
        test_user
    ):
        """Test updating an organization-specific item."""
        service = InputItemService(db)
        
        data = InputItemUpdate(
            translations=[
                {"language_code": "en", "name": "Updated Custom NPK", "description": "Updated description"}
            ],
            item_metadata={
                "brand": "Updated Brand",
                "npk_ratio": "20:10:10",
                "form": "Liquid"
            },
            sort_order=10
        )
        
        updated = service.update_org_item(org_item.id, data, test_org.id, test_user.id)
        
        # Verify updates
        assert updated.item_metadata["brand"] == "Updated Brand"
        assert updated.item_metadata["form"] == "Liquid"
        assert updated.sort_order == 10
    
    def test_update_system_item_fails(
        self,
        db: Session,
        test_org: Organization,
        system_item: InputItem,
        test_user
    ):
        """Test that updating system-defined item fails."""
        service = InputItemService(db)
        
        data = InputItemUpdate(
            translations=[
                {"language_code": "en", "name": "Modified NPK"}
            ]
        )
        
        with pytest.raises(PermissionError) as exc_info:
            service.update_org_item(system_item.id, data, test_org.id, test_user.id)
        
        assert exc_info.value.error_code == "SYSTEM_DEFINED_IMMUTABLE"
        assert "Cannot update system-defined" in exc_info.value.message
    
    def test_update_other_org_item_fails(
        self,
        db: Session,
        test_org: Organization,
        test_org2: Organization,
        org_item: InputItem,
        test_user
    ):
        """Test that updating another org's item fails."""
        service = InputItemService(db)
        
        data = InputItemUpdate(
            translations=[
                {"language_code": "en", "name": "Hacked Item"}
            ]
        )
        
        # Try to update with different org ID
        with pytest.raises(PermissionError) as exc_info:
            service.update_org_item(org_item.id, data, test_org2.id, test_user.id)
        
        assert exc_info.value.error_code == "INSUFFICIENT_PERMISSIONS"
        assert "owned by another organization" in exc_info.value.message
    
    def test_delete_org_item_success(
        self,
        db: Session,
        test_org: Organization,
        org_item: InputItem,
        test_user
    ):
        """Test deleting an organization-specific item."""
        service = InputItemService(db)
        
        # Delete item
        service.delete_org_item(org_item.id, test_org.id, test_user.id)
        
        # Verify soft delete
        db.refresh(org_item)
        assert org_item.is_active is False
    
    def test_delete_system_item_fails(
        self,
        db: Session,
        test_org: Organization,
        system_item: InputItem,
        test_user
    ):
        """Test that deleting system-defined item fails."""
        service = InputItemService(db)
        
        with pytest.raises(PermissionError) as exc_info:
            service.delete_org_item(system_item.id, test_org.id, test_user.id)
        
        assert exc_info.value.error_code == "SYSTEM_DEFINED_IMMUTABLE"
        assert "Cannot delete system-defined" in exc_info.value.message
    
    def test_delete_other_org_item_fails(
        self,
        db: Session,
        test_org: Organization,
        test_org2: Organization,
        org_item: InputItem,
        test_user
    ):
        """Test that deleting another org's item fails."""
        service = InputItemService(db)
        
        with pytest.raises(PermissionError) as exc_info:
            service.delete_org_item(org_item.id, test_org2.id, test_user.id)
        
        assert exc_info.value.error_code == "INSUFFICIENT_PERMISSIONS"


class TestOwnershipValidation:
    """Test suite for ownership validation rules."""
    
    def test_system_items_visible_to_all_orgs(
        self,
        db: Session,
        test_org: Organization,
        test_org2: Organization,
        system_item: InputItem
    ):
        """Test that system-defined items are visible to all organizations."""
        service = InputItemService(db)
        
        # Get items for org 1
        items_org1 = service.get_items(test_org.id, language="en", include_system=True)
        item_codes_org1 = [i.code for i in items_org1]
        
        # Get items for org 2
        items_org2 = service.get_items(test_org2.id, language="en", include_system=True)
        item_codes_org2 = [i.code for i in items_org2]
        
        # Both should see system item
        assert "NPK_19_19_19" in item_codes_org1
        assert "NPK_19_19_19" in item_codes_org2
    
    def test_org_items_isolated_between_orgs(
        self,
        db: Session,
        test_org: Organization,
        test_org2: Organization,
        org_item: InputItem
    ):
        """Test that org-specific items are isolated between organizations."""
        service = InputItemService(db)
        
        # Get items for org 1 (owner)
        items_org1 = service.get_items(test_org.id, language="en", include_system=True)
        item_codes_org1 = [i.code for i in items_org1]
        
        # Get items for org 2 (not owner)
        items_org2 = service.get_items(test_org2.id, language="en", include_system=True)
        item_codes_org2 = [i.code for i in items_org2]
        
        # Org 1 should see its item
        assert "CUSTOM_NPK" in item_codes_org1
        
        # Org 2 should NOT see org 1's item
        assert "CUSTOM_NPK" not in item_codes_org2
    
    def test_system_items_read_only_enforcement(
        self,
        db: Session,
        test_org: Organization,
        system_item: InputItem
    ):
        """Test that system items cannot be modified by any organization."""
        service = InputItemService(db)
        user_id = uuid4()
        
        # Try to update
        with pytest.raises(PermissionError):
            data = InputItemUpdate(names={"en": "Modified"})
            service.update_org_item(system_item.id, data, test_org.id, user_id)
        
        # Try to delete
        with pytest.raises(PermissionError):
            service.delete_org_item(system_item.id, test_org.id, user_id)
    
    def test_org_items_modifiable_by_owner_only(
        self,
        db: Session,
        test_org: Organization,
        test_org2: Organization,
        org_item: InputItem,
        test_user
    ):
        """Test that org items can only be modified by owning organization."""
        service = InputItemService(db)
        
        # Owner can update
        data = InputItemUpdate(
            translations=[
                {"language_code": "en", "name": "Updated by Owner"}
            ]
        )
        updated = service.update_org_item(org_item.id, data, test_org.id, test_user.id)
        # Verify update succeeded
        assert str(updated.id) == str(org_item.id)
        
        # Non-owner cannot update
        with pytest.raises(PermissionError):
            data = InputItemUpdate(
                translations=[
                    {"language_code": "en", "name": "Hacked"}
                ]
            )
            service.update_org_item(org_item.id, data, test_org2.id, test_user.id)
        
        # Non-owner cannot delete
        with pytest.raises(PermissionError):
            service.delete_org_item(org_item.id, test_org2.id, test_user.id)
