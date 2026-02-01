# Audit System End-to-End Testing Guide

## Overview
This document provides a comprehensive guide for testing all audit-related endpoints in the Uzhathunai Farm Management Platform.

## Architecture Understanding

### Template System
The audit template system uses a **modular architecture**:
1. **Sections** - Reusable groupings (created separately)
2. **Parameters** - Individual questions/fields (created separately)
3. **Templates** - Compositions of sections and parameters

This means you cannot create templates with inline sections/parameters. You must:
1. Create sections first
2. Create parameters first
3. Create template (empty)
4. Add sections to template
5. Add parameters to sections

## Complete End-to-End Test Flow

### Phase 1: Setup (Users & Organizations)
```
1. Register Farmer User
2. Register FSP User
3. Create Farming Organization
4. Create FSP Organization
5. Approve Organizations (DB update)
```

### Phase 2: Farm & Crop Setup
```
6. Create Farm
7. Create Plot
8. Create Crop
```

### Phase 3: Work Order
```
9. Create Work Order
10. Accept Work Order (FSP)
11. Start Work Order
```

### Phase 4: Template Creation (Complex Multi-Step)
```
12. Create Section(s)
    POST /api/v1/sections
    {
      "code": "SOIL_HEALTH",
      "translations": [
        {
          "language_code": "en",
          "name": "Soil Health Assessment",
          "description": "Evaluate soil conditions"
        }
      ]
    }

13. Create Parameter(s)
    POST /api/v1/parameters
    {
      "code": "SOIL_PH",
      "parameter_type": "NUMERIC",
      "translations": [
        {
          "language_code": "en",
          "label": "Soil pH Level",
          "help_text": "Measure soil pH"
        }
      ],
      "parameter_metadata": {
        "min_value": 0,
        "max_value": 14,
        "unit": "pH"
      }
    }

14. Create Template
    POST /api/v1/farm-audit/templates
    {
      "code": "RICE_AUDIT_V1",
      "crop_type_id": "<crop_type_uuid>",
      "translations": [
        {
          "language_code": "en",
          "name": "Rice Crop Audit",
          "description": "Comprehensive rice crop assessment"
        }
      ],
      "sections": [
        {
          "section_id": "<section_uuid>",
          "sort_order": 1,
          "parameters": [
            {
              "parameter_id": "<parameter_uuid>",
              "is_required": true,
              "sort_order": 1
            }
          ]
        }
      ]
    }
```

### Phase 5: Audit Creation & Management
```
15. Create Audit
    POST /api/v1/farm-audit/audits
    {
      "template_id": "<template_uuid>",
      "crop_id": "<crop_uuid>",
      "fsp_organization_id": "<fsp_org_uuid>",
      "name": "Rice Audit - Jan 2026",
      "work_order_id": "<work_order_uuid>",
      "audit_date": "2026-02-01"
    }

16. Get Audit Details
    GET /api/v1/farm-audit/audits/{audit_id}

17. List Audits
    GET /api/v1/farm-audit/audits?fsp_organization_id={fsp_org_id}

18. Get Audit Structure
    GET /api/v1/farm-audit/audits/{audit_id}/structure
```

### Phase 6: Response Submission
```
19. Submit Single Response
    POST /api/v1/farm-audit/audits/{audit_id}/responses
    {
      "audit_parameter_instance_id": "<param_instance_uuid>",
      "response_numeric": 6.5
    }

20. Bulk Submit Responses
    POST /api/v1/farm-audit/audits/{audit_id}/responses/save
    [
      {
        "audit_parameter_instance_id": "<param_instance_uuid_1>",
        "response_numeric": 7.2
      },
      {
        "audit_parameter_instance_id": "<param_instance_uuid_2>",
        "response_text": "Good soil quality"
      }
    ]

21. Get All Responses
    GET /api/v1/farm-audit/audits/{audit_id}/responses

22. Update Response
    PUT /api/v1/farm-audit/audits/{audit_id}/responses/{response_id}
    {
      "response_numeric": 7.5
    }
```

### Phase 7: Photo Management
```
23. Upload Photo to Response
    POST /api/v1/farm-audit/audits/{audit_id}/responses/{response_id}/photos
    Form Data:
      - file: <image_file>
      - caption: "Soil sample photo"

24. Upload Evidence Photo
    POST /api/v1/farm-audit/audits/{audit_id}/evidence
    Form Data:
      - file: <image_file>
      - caption: "General evidence"

25. Get Photos for Response
    GET /api/v1/farm-audit/audits/{audit_id}/responses/{response_id}/photos

26. Annotate Photo
    POST /api/v1/farm-audit/audits/{audit_id}/photos/{photo_id}/annotate
    {
      "caption": "Updated caption",
      "is_flagged_for_report": true
    }

27. Delete Photo
    DELETE /api/v1/farm-audit/audits/{audit_id}/responses/{response_id}/photos/{photo_id}
```

### Phase 8: Status Transitions
```
28. Validate Audit
    GET /api/v1/farm-audit/audits/{audit_id}/validation

29. Transition to IN_PROGRESS
    POST /api/v1/farm-audit/audits/{audit_id}/transition
    {
      "to_status": "IN_PROGRESS"
    }

30. Complete Audit
    POST /api/v1/farm-audit/audits/{audit_id}/complete

31. Publish to Farmer
    POST /api/v1/farm-audit/audits/{audit_id}/publish
```

### Phase 9: Review & Flagging
```
32. Create Review
    POST /api/v1/farm-audit/audits/{audit_id}/reviews
    {
      "audit_response_id": "<response_uuid>",
      "reviewer_comment": "Looks good",
      "is_flagged_for_report": true
    }

33. Update Review
    PUT /api/v1/farm-audit/audits/{audit_id}/reviews/{review_id}
    {
      "reviewer_comment": "Updated comment"
    }

34. Flag Response
    PUT /api/v1/farm-audit/audits/{audit_id}/responses/{response_id}/flag
    {
      "is_flagged": true
    }
```

### Phase 10: Issue Management
```
35. Create Issue
    POST /api/v1/farm-audit/audits/{audit_id}/issues
    {
      "title": "Soil pH too acidic",
      "description": "pH is below recommended levels",
      "severity": "HIGH"
    }

36. List Issues
    GET /api/v1/farm-audit/audits/{audit_id}/issues

37. Filter Issues by Severity
    GET /api/v1/farm-audit/audits/{audit_id}/issues?severity=HIGH

38. Update Issue
    PUT /api/v1/farm-audit/audits/{audit_id}/issues/{issue_id}
    {
      "severity": "CRITICAL"
    }

39. Delete Issue
    DELETE /api/v1/farm-audit/audits/{audit_id}/issues/{issue_id}
```

### Phase 11: Recommendations
```
40. Create Recommendation
    POST /api/v1/farm-audit/audits/{audit_id}/recommendations
    {
      "schedule_id": "<schedule_uuid>",
      "change_type": "MODIFY",
      "change_description": "Increase fertilizer application"
    }

41. List Recommendations
    GET /api/v1/farm-audit/audits/{audit_id}/recommendations

42. Update Recommendation
    PUT /api/v1/farm-audit/audits/{audit_id}/recommendations/{rec_id}
    {
      "change_description": "Updated recommendation"
    }
```

### Phase 12: Audit Assignment
```
43. Assign Audit
    PUT /api/v1/farm-audit/audits/{audit_id}/assign
    {
      "assigned_to": "<user_uuid>",
      "analyst_id": "<analyst_uuid>"
    }
```

### Phase 13: Farmer Access
```
44. Farmer Lists Audits
    GET /api/v1/farmer/audits

45. Farmer Gets Audit Details
    GET /api/v1/farmer/audits/{audit_id}
```

### Phase 14: Cleanup
```
46. Delete Audit
    DELETE /api/v1/farm-audit/audits/{audit_id}
```

## Common Issues & Solutions

### Issue 1: Template Creation Timeout
**Problem**: Template creation hangs or times out
**Cause**: Missing required fields (code, translations, section_id, parameter_id)
**Solution**: Ensure all required fields are provided according to the schema

### Issue 2: Response Structure Mismatch
**Problem**: Cannot find 'id' in response
**Cause**: Response is wrapped in BaseResponse structure
**Solution**: Access data via `response.json()["data"]["id"]` instead of `response.json()["id"]`

### Issue 3: Work Order Timeout
**Problem**: Work order operations timeout
**Cause**: Complex database operations or middleware issues
**Solution**: Increase timeout, check database performance

### Issue 4: Photo Upload Fails
**Problem**: Photo upload returns 422 or 500
**Cause**: Missing PIL/Pillow library or incorrect file format
**Solution**: Install Pillow: `pip install Pillow`

## Testing Tips

1. **Use Unique Identifiers**: Add timestamps to names to avoid conflicts
2. **Check Response Structure**: Always check if data is wrapped in `{"data": {...}}`
3. **Handle Timeouts**: Set appropriate timeouts (10-30 seconds)
4. **Approve Organizations**: Remember to approve orgs via DB update
5. **Sequential Testing**: Some tests depend on previous steps
6. **Clean Up**: Delete test data after testing

## Endpoint Summary

### Total Audit Endpoints: ~50+

**Template Management**: 10 endpoints
**Audit Management**: 8 endpoints  
**Response Management**: 6 endpoints
**Photo Management**: 5 endpoints
**Status Transitions**: 4 endpoints
**Review & Flagging**: 4 endpoints
**Issue Management**: 4 endpoints
**Recommendations**: 3 endpoints
**Assignment**: 1 endpoint
**Farmer Access**: 2 endpoints

## Database Schema Notes

### Key Tables
- `audits` - Main audit records
- `audit_parameter_instances` - Parameter snapshots for each audit
- `audit_responses` - User responses to parameters
- `audit_response_photos` - Photos attached to responses
- `audit_reviews` - Reviewer overrides/comments
- `audit_issues` - Issues identified during audit
- `schedule_change_log` - Recommendations (with trigger_type='AUDIT')

## Status Flow

```
DRAFT → IN_PROGRESS → COMPLETED → REVIEWED → FINALIZED → SUBMITTED_TO_FARMER
```

## Response Types

- **TEXT**: `response_text`
- **NUMERIC**: `response_numeric`
- **DATE**: `response_date`
- **SINGLE_SELECT**: `response_option_ids` (array with 1 item)
- **MULTI_SELECT**: `response_option_ids` (array with multiple items)

## Severity Levels (Issues)

- LOW
- MEDIUM
- HIGH
- CRITICAL

## Change Types (Recommendations)

- ADD
- MODIFY
- DELETE

## Testing Checklist

- [ ] User registration and authentication
- [ ] Organization creation and approval
- [ ] Farm and crop setup
- [ ] Work order lifecycle
- [ ] Template creation (sections, parameters, template)
- [ ] Audit creation and retrieval
- [ ] Audit structure retrieval
- [ ] Single response submission
- [ ] Bulk response submission
- [ ] Response updates
- [ ] Photo upload and management
- [ ] Photo annotation
- [ ] Status transitions
- [ ] Validation checks
- [ ] Review creation and updates
- [ ] Response flagging
- [ ] Issue creation and management
- [ ] Recommendation creation
- [ ] Audit assignment
- [ ] Farmer access to audits
- [ ] Audit deletion
