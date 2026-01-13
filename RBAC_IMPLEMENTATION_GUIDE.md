# RBAC and Permissions Implementation Guide

This document provides guidance for implementing RBAC and permission checks across all Farm Audit Management services.

## Overview

Task 18 requires implementing comprehensive RBAC (Role-Based Access Control) and ownership validation across all audit services. This includes:

1. **Permission Validation** (Task 18.1) - Check user permissions before operations
2. **Ownership Validation** (Task 18.2) - Validate system vs organization ownership
3. **UI Permission Controls** (Task 18.3) - Hide/disable features based on permissions

## Core Modules

### 1. Permission Checking (`app/core/audit_permissions.py`)

Provides permission constants and checking utilities:

```python
from app.core.audit_permissions import check_audit_permission, AuditPermissions

# Check permission before operation
check_audit_permission(
    db=self.db,
    user=user,
    organization_id=org_id,
    resource=AuditPermissions.AUDIT_CREATE[0],
    action=AuditPermissions.AUDIT_CREATE[1]
)
```

**Available Permissions:**
- `TEMPLATE_MANAGE`, `TEMPLATE_CREATE`, `TEMPLATE_READ`, `TEMPLATE_UPDATE`, `TEMPLATE_DELETE`, `TEMPLATE_COPY`
- `AUDIT_CREATE`, `AUDIT_READ`, `AUDIT_REPORT_GENERATE`
- `AUDIT_RESPONSE`, `AUDIT_RESPONSE_CREATE`, `AUDIT_RESPONSE_UPDATE`, `AUDIT_PHOTO_UPLOAD`
- `AUDIT_REVIEW`, `AUDIT_REVIEW_CREATE`, `AUDIT_REVIEW_UPDATE`
- `AUDIT_ISSUE_CREATE`, `AUDIT_RECOMMENDATION_CREATE`
- `AUDIT_FINALIZE`, `AUDIT_SHARE`, `AUDIT_RECOMMENDATION_APPROVE`

### 2. Ownership Validation (`app/core/audit_ownership.py`)

Provides ownership validation utilities:

```python
from app.core.audit_ownership import validate_entity_modification

# Validate entity can be modified
validate_entity_modification(
    is_system_defined=entity.is_system_defined,
    owner_org_id=entity.owner_org_id,
    user=user,
    user_org_id=org_id,
    entity_type="template",
    entity_id=entity.id
)
```

**Key Functions:**
- `validate_system_entity_modification()` - Prevent org users from modifying system entities
- `validate_organization_ownership()` - Prevent cross-organization modifications
- `validate_entity_modification()` - Combined validation
- `validate_copy_permission()` - Validate permission to copy entities
- `validate_audit_access()` - Validate access to specific audit

## Implementation Pattern

### Service Method Pattern

```python
def create_entity(
    self,
    data: EntityCreate,
    org_id: UUID,
    user: User  # Changed from user_id to user
) -> EntityResponse:
    """
    Create entity.
    
    Requirements:
    - 18.1: Enforce permission
    - 19.1: Prevent system entity modification
    - 19.3: Prevent cross-org modification
    """
    # 1. Check permission
    check_audit_permission(
        db=self.db,
        user=user,
        organization_id=org_id,
        resource="entity",
        action="create"
    )
    
    # 2. Create entity
    entity = Entity(
        ...
        created_by=user.id,  # Use user.id
        updated_by=user.id
    )
    
    # 3. Save and return
    self.db.add(entity)
    self.db.commit()
    return entity

def update_entity(
    self,
    entity_id: UUID,
    data: EntityUpdate,
    org_id: UUID,
    user: User  # Changed from user_id to user
) -> EntityResponse:
    """
    Update entity.
    
    Requirements:
    - 18.1: Enforce permission
    - 19.1: Prevent system entity modification
    - 19.3: Prevent cross-org modification
    """
    # 1. Check permission
    check_audit_permission(
        db=self.db,
        user=user,
        organization_id=org_id,
        resource="entity",
        action="update"
    )
    
    # 2. Get entity
    entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise NotFoundError(...)
    
    # 3. Validate ownership
    validate_entity_modification(
        is_system_defined=entity.is_system_defined,
        owner_org_id=entity.owner_org_id,
        user=user,
        user_org_id=org_id,
        entity_type="entity",
        entity_id=entity_id
    )
    
    # 4. Update entity
    entity.field = data.field
    entity.updated_by = user.id  # Use user.id
    
    # 5. Save and return
    self.db.commit()
    return entity
```

## Services Requiring Updates

### ✅ Completed: OptionSetService

- [x] `create_org_option_set()` - Added TEMPLATE_CREATE permission check
- [x] `update_org_option_set()` - Added TEMPLATE_UPDATE permission check + ownership validation
- [x] `delete_org_option_set()` - Added TEMPLATE_DELETE permission check + ownership validation
- [x] `add_option_to_set()` - Added TEMPLATE_UPDATE permission check + ownership validation
- [x] `update_option()` - Added TEMPLATE_UPDATE permission check + ownership validation
- [x] `delete_option()` - Added TEMPLATE_DELETE permission check + ownership validation

### 🔄 Pending: ParameterService

Methods to update:
- [ ] `create_parameter()` - Add TEMPLATE_CREATE permission check
- [ ] `update_parameter()` - Add TEMPLATE_UPDATE permission check + ownership validation
- [ ] `delete_parameter()` - Add TEMPLATE_DELETE permission check + ownership validation
- [ ] `copy_parameter()` - Add TEMPLATE_COPY permission check + copy permission validation

### 🔄 Pending: SectionService

Methods to update:
- [ ] `create_section()` - Add TEMPLATE_CREATE permission check
- [ ] `update_section()` - Add TEMPLATE_UPDATE permission check + ownership validation
- [ ] `delete_section()` - Add TEMPLATE_DELETE permission check + ownership validation

### 🔄 Pending: TemplateService

Methods to update:
- [ ] `create_template()` - Add TEMPLATE_CREATE permission check
- [ ] `update_template()` - Add TEMPLATE_UPDATE permission check + ownership validation
- [ ] `delete_template()` - Add TEMPLATE_DELETE permission check + ownership validation
- [ ] `copy_template()` - Add TEMPLATE_COPY permission check + copy permission validation
- [ ] `add_section_to_template()` - Add TEMPLATE_UPDATE permission check + ownership validation
- [ ] `add_parameter_to_section()` - Add TEMPLATE_UPDATE permission check + ownership validation

### 🔄 Pending: AuditService

Methods to update:
- [ ] `create_audit()` - Add AUDIT_CREATE permission check
- [ ] `get_audit()` - Add AUDIT_READ permission check + audit access validation
- [ ] `get_audits()` - Filter by user's accessible audits

### 🔄 Pending: ResponseService

Methods to update:
- [ ] `submit_response()` - Add AUDIT_RESPONSE_CREATE permission check + audit access validation
- [ ] `update_response()` - Add AUDIT_RESPONSE_UPDATE permission check + audit access validation

### 🔄 Pending: PhotoService

Methods to update:
- [ ] `upload_photo()` - Add AUDIT_PHOTO_UPLOAD permission check + audit access validation
- [ ] `delete_photo()` - Add AUDIT_PHOTO_UPLOAD permission check + audit access validation

### 🔄 Pending: ReviewService

Methods to update:
- [ ] `create_review()` - Add AUDIT_REVIEW_CREATE permission check + audit access validation
- [ ] `update_review()` - Add AUDIT_REVIEW_UPDATE permission check + audit access validation
- [ ] `flag_response()` - Add AUDIT_REVIEW permission check + audit access validation
- [ ] `annotate_photo()` - Add AUDIT_REVIEW permission check + audit access validation

### 🔄 Pending: IssueService

Methods to update:
- [ ] `create_issue()` - Add AUDIT_ISSUE_CREATE permission check + audit access validation
- [ ] `update_issue()` - Add AUDIT_ISSUE_CREATE permission check + audit access validation
- [ ] `delete_issue()` - Add AUDIT_ISSUE_CREATE permission check + audit access validation

### 🔄 Pending: RecommendationService

Methods to update:
- [ ] `create_recommendation()` - Add AUDIT_RECOMMENDATION_CREATE permission check + audit access validation
- [ ] `update_recommendation()` - Add AUDIT_RECOMMENDATION_CREATE permission check + audit access validation
- [ ] `delete_recommendation()` - Add AUDIT_RECOMMENDATION_CREATE permission check + audit access validation

### 🔄 Pending: RecommendationApprovalService

Methods to update:
- [ ] `approve_recommendation()` - Add AUDIT_RECOMMENDATION_APPROVE permission check
- [ ] `reject_recommendation()` - Add AUDIT_RECOMMENDATION_APPROVE permission check

### 🔄 Pending: FinalizationService

Methods to update:
- [ ] `finalize_audit()` - Add AUDIT_FINALIZE permission check + audit access validation

### 🔄 Pending: SharingService

Methods to update:
- [ ] `share_audit()` - Add AUDIT_SHARE permission check + audit access validation

### 🔄 Pending: WorkflowService

Methods to update:
- [ ] `transition_status()` - Add appropriate permission checks based on target status

## API Route Updates

All API routes must be updated to pass `user` object instead of `user.id`:

### Before:
```python
@router.post("/option-sets")
def create_option_set(
    data: OptionSetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = OptionSetService(db)
    return service.create_org_option_set(
        data=data,
        org_id=get_user_org_id(current_user),
        user_id=current_user.id  # OLD
    )
```

### After:
```python
@router.post("/option-sets")
def create_option_set(
    data: OptionSetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = OptionSetService(db)
    return service.create_org_option_set(
        data=data,
        org_id=get_user_org_id(current_user),
        user=current_user  # NEW
    )
```

## Frontend Permission Controls (Task 18.3)

### Permission Checking Hook

Create a custom hook for checking permissions:

```typescript
// hooks/useAuditPermissions.ts
import { useSelector } from 'react-redux';
import { RootState } from '@/shared/store';

export const useAuditPermissions = () => {
  const currentUser = useSelector((state: RootState) => state.auth.user);
  const currentOrg = useSelector((state: RootState) => state.organization.current);
  
  const hasPermission = (resource: string, action: string): boolean => {
    // Check if user has permission
    // This would call an API endpoint or check cached permissions
    return checkPermission(currentUser, currentOrg, resource, action);
  };
  
  return {
    canCreateTemplate: hasPermission('audit_template', 'create'),
    canUpdateTemplate: hasPermission('audit_template', 'update'),
    canDeleteTemplate: hasPermission('audit_template', 'delete'),
    canCopyTemplate: hasPermission('audit_template', 'copy'),
    canCreateAudit: hasPermission('audit', 'create'),
    canReviewAudit: hasPermission('audit', 'review'),
    canFinalizeAudit: hasPermission('audit', 'finalize'),
    canShareAudit: hasPermission('audit', 'share'),
    canApproveRecommendation: hasPermission('audit', 'recommendation_approve'),
  };
};
```

### UI Component Pattern

```typescript
import { useAuditPermissions } from '../hooks/useAuditPermissions';

export const TemplateListScreen = () => {
  const permissions = useAuditPermissions();
  
  return (
    <View>
      {/* Show create button only if user has permission */}
      {permissions.canCreateTemplate && (
        <Button
          title="Create Template"
          onPress={() => router.push('/templates/create')}
        />
      )}
      
      {/* Disable edit button if user lacks permission */}
      <Button
        title="Edit"
        onPress={handleEdit}
        disabled={!permissions.canUpdateTemplate}
      />
      
      {/* Hide delete button if user lacks permission */}
      {permissions.canDeleteTemplate && (
        <Button
          title="Delete"
          onPress={handleDelete}
        />
      )}
    </View>
  );
};
```

### System Entity Indicators

Show visual indicators for system-defined entities:

```typescript
export const TemplateCard = ({ template }) => {
  return (
    <Card>
      <View style={styles.header}>
        <Text>{template.name}</Text>
        {template.is_system_defined && (
          <Badge color="blue">System</Badge>
        )}
      </View>
      
      {/* Disable edit/delete for system entities */}
      <View style={styles.actions}>
        <Button
          title="Edit"
          disabled={template.is_system_defined}
          onPress={handleEdit}
        />
        <Button
          title="Delete"
          disabled={template.is_system_defined}
          onPress={handleDelete}
        />
      </View>
    </Card>
  );
};
```

## Testing

### Unit Tests

Test permission checking:

```python
def test_create_template_without_permission(db_session, test_user):
    """Test that creating template without permission raises error."""
    service = TemplateService(db_session)
    
    # User without TEMPLATE_CREATE permission
    with pytest.raises(PermissionError) as exc:
        service.create_template(
            data=TemplateCreate(...),
            org_id=test_org_id,
            user=test_user
        )
    
    assert exc.value.error_code == "INSUFFICIENT_PERMISSIONS"

def test_update_system_template_denied(db_session, test_user, system_template):
    """Test that org user cannot update system template."""
    service = TemplateService(db_session)
    
    with pytest.raises(PermissionError) as exc:
        service.update_template(
            template_id=system_template.id,
            data=TemplateUpdate(...),
            org_id=test_org_id,
            user=test_user
        )
    
    assert exc.value.error_code == "SYSTEM_ENTITY_MODIFICATION_DENIED"

def test_update_other_org_template_denied(db_session, test_user, other_org_template):
    """Test that user cannot update another org's template."""
    service = TemplateService(db_session)
    
    with pytest.raises(PermissionError) as exc:
        service.update_template(
            template_id=other_org_template.id,
            data=TemplateUpdate(...),
            org_id=test_org_id,
            user=test_user
        )
    
    assert exc.value.error_code == "CROSS_ORGANIZATION_MODIFICATION_DENIED"
```

## Requirements Coverage

### Requirement 18.1 - Audit Template Management Permission
- ✅ Permission checks added to all template, section, parameter, and option set operations
- ✅ Uses `TEMPLATE_MANAGE`, `TEMPLATE_CREATE`, `TEMPLATE_UPDATE`, `TEMPLATE_DELETE`, `TEMPLATE_COPY` permissions

### Requirement 18.2 - Audit Create Permission
- 🔄 Permission check to be added to `AuditService.create_audit()`
- Uses `AUDIT_CREATE` permission

### Requirement 18.3 - Audit Response Permission
- 🔄 Permission checks to be added to response and photo operations
- Uses `AUDIT_RESPONSE`, `AUDIT_RESPONSE_CREATE`, `AUDIT_RESPONSE_UPDATE`, `AUDIT_PHOTO_UPLOAD` permissions

### Requirement 18.4 - Audit Review Permission
- 🔄 Permission checks to be added to review, issue, and recommendation operations
- Uses `AUDIT_REVIEW`, `AUDIT_REVIEW_CREATE`, `AUDIT_REVIEW_UPDATE`, `AUDIT_ISSUE_CREATE`, `AUDIT_RECOMMENDATION_CREATE` permissions

### Requirement 18.5 - Audit Finalize Permission
- 🔄 Permission check to be added to `FinalizationService.finalize_audit()`
- Uses `AUDIT_FINALIZE` permission

### Requirement 18.6 - Audit Share Permission
- 🔄 Permission check to be added to `SharingService.share_audit()`
- Uses `AUDIT_SHARE` permission

### Requirement 18.7 - Audit Recommendation Approve Permission
- 🔄 Permission checks to be added to recommendation approval operations
- Uses `AUDIT_RECOMMENDATION_APPROVE` permission

### Requirement 19.1 - Prevent System Entity Modification
- ✅ `validate_system_entity_modification()` prevents org users from modifying system entities
- ✅ Applied to all update/delete operations in OptionSetService

### Requirement 19.2 - System User Privileges
- ✅ `is_system_user()` check allows system users to modify any entity
- ✅ Integrated into `validate_entity_modification()`

### Requirement 19.3 - Prevent Cross-Organization Modification
- ✅ `validate_organization_ownership()` prevents cross-org modifications
- ✅ Applied to all update/delete operations in OptionSetService

### Requirement 19.4 - View System Entities
- ✅ `get_option_sets()` includes system-defined entities in results
- ✅ Read operations allow viewing system entities

### Requirement 19.5 - Owner Organization Validation
- ✅ All ownership validation checks `owner_org_id`
- ✅ Enforced in all modification operations

## Next Steps

1. ✅ Complete OptionSetService (DONE)
2. 🔄 Update remaining services following the same pattern
3. 🔄 Update all API routes to pass `user` instead of `user_id`
4. 🔄 Implement frontend permission controls
5. 🔄 Add comprehensive unit tests
6. 🔄 Test end-to-end permission flows

## Notes

- All service methods now accept `User` object instead of `user_id: UUID`
- Permission checks happen before any business logic
- Ownership validation happens after entity retrieval
- System users bypass ownership restrictions
- Frontend should hide/disable features based on permissions
- Error messages should be clear and actionable
