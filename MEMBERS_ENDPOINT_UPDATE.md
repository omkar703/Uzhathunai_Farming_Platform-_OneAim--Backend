# Frontend Integration Guide - Members Endpoint

## Updated Response Format

The `GET /api/v1/organizations/{org_id}/members` endpoint now returns enhanced member data:

```json
{
  "items": [
    {
      "id": "member_uuid",
      "user_id": "user_uuid",
      "user_name": "John Doe",
      "user_email": "john@example.com",
      "status": "ACTIVE",
      "joined_at": "2024-01-23T00:00:00Z",
      
      // Top-level role info (primary role)
      "role_id": "role_uuid",
      "role_name": "WORKER",  // or "OWNER", "MANAGER", "FSP_OWNER", etc.
      "is_owner": false,
      
      // Full roles array (for users with multiple roles)
      "roles": [
        {
          "role_id": "role_uuid",
          "role_name": "Worker",
          "role_code": "WORKER",
          "is_primary": true
        }
      ]
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 20,
  "total_pages": 1
}
```

## What Changed

### Added Fields:
1. **`role_id`** - UUID of the user's primary role
2. **`role_name`** - Code of the primary role (WORKER, OWNER, MANAGER, etc.)
3. **`is_owner`** - Boolean flag to identify organization owners

### Existing Fields (unchanged):
- `user_name` - User's full name
- `user_email` - User's email
- `roles` - Array of all roles (for multi-role support)

## Frontend Usage

### Display Member List
```typescript
members.forEach(member => {
  console.log(`${member.user_name} - ${member.role_name}`);
  
  // Show owner badge
  if (member.is_owner) {
    showOwnerBadge();
  }
});
```

### Role-based UI
```typescript
// Show owner badge
if (member.is_owner) {
  return <Badge>Owner</Badge>;
}

// Display role
<span>{member.role_name}</span>
```

### Check Permissions
```typescript
const canEdit = member.role_name === 'OWNER' || member.role_name === 'ADMIN';
```

## Role Codes Reference

Common role codes you'll see:
- `OWNER` - Organization owner (Farming)
- `FSP_OWNER` - FSP organization owner
- `ADMIN` - Administrator
- `MANAGER` - Manager
- `WORKER` - Worker/Member
- `TECHNICAL_ANALYST` - Technical analyst

## Notes

- `role_name` uses the **role code** (e.g., "WORKER") not the display name
- `is_owner` is `true` if user has OWNER or FSP_OWNER role
- `roles` array contains full details if you need them
- All existing fields remain unchanged for backward compatibility
