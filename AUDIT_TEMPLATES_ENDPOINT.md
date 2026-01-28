# Audit Templates Endpoint Documentation

## Answer 1: YES, the endpoint exists! ✅

**Endpoint:** `GET /api/v1/farm-audit/templates`

## Answer 2: What it Returns

### Request
```
GET /api/v1/farm-audit/templates
Authorization: Bearer {access_token}
```

### Query Parameters (Optional)
- `crop_type_id` (UUID): Filter by crop type
- `is_active` (boolean): Filter by active status
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)

### Response Structure
```json
{
  "items": [
    {
      "id": "32ed7afe-093f-486a-91df-8dcf4c2f3996",
      "code": "SOIL_AUDIT_V1",
      "crop_type_id": null,
      "is_system_defined": false,
      "owner_org_id": "5504357f-21a4-4877-b78e-37f8fe7dfec5",
      "version": 1,
      "is_active": true,
      "created_at": "2026-01-21T17:00:00Z",
      "updated_at": "2026-01-21T17:00:00Z",
      "created_by": "74b6458f-e7ee-46f3-8261-eb98eda69bd2",
      "updated_by": "74b6458f-e7ee-46f3-8261-eb98eda69bd2",
      "translations": [
        {
          "language_code": "en",
          "name": "Standard Soil Audit",
          "description": "Comprehensive soil health analysis"
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "total_pages": 1
}
```

## Answer 3: How to Use It

### For Your UI Display
Extract the relevant fields for your audit type cards:

```typescript
// Map API response to your UI format
const auditTypes = response.items.map(template => ({
  id: template.id,
  name: template.translations.find(t => t.language_code === 'en')?.name || template.code,
  description: template.translations.find(t => t.language_code === 'en')?.description || '',
  category: template.is_system_defined ? 'System' : 'Custom',
  // You can add icon mapping based on template code or name:
  icon: getIconForTemplate(template.code) // e.g., '🌱' for soil audit
}));
```

### Icon Mapping Example
```typescript
function getIconForTemplate(code: string): string {
  const iconMap = {
    'SOIL_AUDIT_V1': '🌱',
    'CROP_AUDIT': '🌾',
    'PEST_AUDIT': '🐛',
    'IRRIGATION_AUDIT': '💧',
    // Add more mappings as needed
  };
  return iconMap[code] || '📋'; // Default icon
}
```

### Estimated Duration
The API doesn't currently provide `estimated_duration`. You can either:
1. **Hardcode it client-side** based on template code/name
2. **Request backend to add it** to the `template_metadata` JSON field

Example client-side mapping:
```typescript
const durationMap = {
  'SOIL_AUDIT_V1': '2 hours',
  'CROP_AUDIT': '1 hour',
  // etc.
};
```

## Current Data Available

Currently, there is **1 audit template** in the database:
- **Name:** Standard Soil Audit
- **Code:** SOIL_AUDIT_V1
- **Sections:** 1 (SOIL_CONDITION)
- **Parameters:** 1 (SOIL_MOISTURE)

## Important Notes

1. **Authentication Required:** All users must be authenticated
2. **Organization Context:** 
   - FSP users see system templates + their own org templates
   - Farming users see system templates + their org templates
3. **Translations:** Always check for translations in user's language
4. **Template Details:** Use `GET /api/v1/farm-audit/templates/{template_id}` for full template structure

## Example Frontend Code

```typescript
async function fetchAuditTemplates() {
  const response = await fetch('/api/v1/farm-audit/templates', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  
  return data.items.map(template => ({
    id: template.id,
    name: template.translations[0]?.name || template.code,
    description: template.translations[0]?.description || '',
    category: template.is_system_defined ? 'System Templates' : 'My Templates',
    icon: getIconForTemplate(template.code),
    estimatedDuration: getDuration(template.code)
  }));
}
```

## Recommendation

**Use the API endpoint** - don't hardcode audit types. This allows:
- Dynamic template management
- Organization-specific templates
- System-wide template updates
- Multilingual support

The backend will handle creating more templates as needed. For now, map the fields you need client-side (icon, duration) until those are added to the API.
