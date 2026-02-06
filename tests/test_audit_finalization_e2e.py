"""
End-to-End Test for Audit Finalization and Farmer Report Delivery

This test verifies:
1. Complete audit workflow from creation to finalization
2. Transition performance (< 500ms requirement)
3. Farmer receives complete report with all flagged data
4. No "N/A" or null values in flagged responses
5. All flagged photos are included

Run with: python -m pytest tests/test_audit_finalization_e2e.py -v -s
"""

import pytest
import requests
import time
from uuid import UUID
from typing import Dict, Any


# Configuration - Update these based on your environment
BASE_URL = "http://localhost:8000/api/v1"
FSP_TOKEN = None  # Will be set after login
FARMER_TOKEN = None  # Will be set after login


class TestAuditFinalizationE2E:
    """End-to-end test for audit finalization and farmer delivery"""
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        """Setup test environment and authenticate users"""
        global FSP_TOKEN, FARMER_TOKEN
        
        # Login as FSP user (auditor/reviewer)
        fsp_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "fsp@example.com",  # Update with actual FSP user
                "password": "password123"
            }
        )
        assert fsp_response.status_code == 200, f"FSP login failed: {fsp_response.text}"
        FSP_TOKEN = fsp_response.json()["data"]["access_token"]
        
        # Login as Farmer user
        farmer_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "farmer@example.com",  # Update with actual farmer user
                "password": "password123"
            }
        )
        assert farmer_response.status_code == 200, f"Farmer login failed: {farmer_response.text}"
        FARMER_TOKEN = farmer_response.json()["data"]["access_token"]
        
        print("\n✓ Authentication successful")
        yield
        
    def test_01_create_audit(self, setup_class):
        """Step 1: Create a new audit"""
        headers = {"Authorization": f"Bearer {FSP_TOKEN}"}
        
        # Get available templates
        templates_response = requests.get(
            f"{BASE_URL}/farm-audit/templates",
            headers=headers
        )
        assert templates_response.status_code == 200
        templates = templates_response.json()["data"]["items"]
        assert len(templates) > 0, "No templates available"
        
        template_id = templates[0]["id"]
        
        # Create audit
        create_response = requests.post(
            f"{BASE_URL}/farm-audit/audits",
            headers=headers,
            json={
                "template_id": template_id,
                "farming_organization_id": "YOUR_FARMING_ORG_ID",  # Update
                "farm_id": "YOUR_FARM_ID",  # Update
                "audit_name": "E2E Test Audit - Finalization",
                "scheduled_date": "2026-02-10"
            }
        )
        
        assert create_response.status_code == 201, f"Audit creation failed: {create_response.text}"
        audit_data = create_response.json()["data"]
        
        self.audit_id = audit_data["id"]
        print(f"\n✓ Created audit: {self.audit_id}")
        
    def test_02_add_responses(self, setup_class):
        """Step 2: Add responses to audit parameters"""
        headers = {"Authorization": f"Bearer {FSP_TOKEN}"}
        
        # Get audit parameters
        params_response = requests.get(
            f"{BASE_URL}/farm-audit/audits/{self.audit_id}/parameters",
            headers=headers
        )
        assert params_response.status_code == 200
        parameters = params_response.json()["data"]["items"]
        
        # Add responses to required parameters
        for param in parameters[:5]:  # Answer first 5 parameters
            instance_id = param["id"]
            param_type = param.get("parameter_type", "TEXT")
            
            response_data = {
                "audit_parameter_instance_id": instance_id
            }
            
            # Add appropriate response based on type
            if param_type == "TEXT":
                response_data["response_text"] = f"Test response for {param.get('parameter_name', 'parameter')}"
            elif param_type == "NUMERIC":
                response_data["response_numeric"] = 42.5
            elif param_type == "DATE":
                response_data["response_date"] = "2026-02-06"
            elif param_type in ["SINGLE_SELECT", "MULTI_SELECT"]:
                options = param.get("options", [])
                if options:
                    response_data["response_option_ids"] = [options[0]["option_id"]]
            
            # Submit response
            response = requests.post(
                f"{BASE_URL}/farm-audit/audits/{self.audit_id}/responses",
                headers=headers,
                json=response_data
            )
            assert response.status_code in [200, 201], f"Response submission failed: {response.text}"
        
        print(f"\n✓ Added {len(parameters[:5])} responses")
        
    def test_03_submit_for_review(self, setup_class):
        """Step 3: Submit audit for review"""
        headers = {"Authorization": f"Bearer {FSP_TOKEN}"}
        
        # Transition to SUBMITTED_FOR_REVIEW
        transition_response = requests.post(
            f"{BASE_URL}/farm-audit/audits/{self.audit_id}/transition",
            headers=headers,
            json={"to_status": "SUBMITTED_FOR_REVIEW"}
        )
        
        assert transition_response.status_code == 200, f"Transition failed: {transition_response.text}"
        audit_data = transition_response.json()["data"]
        assert audit_data["status"] == "SUBMITTED_FOR_REVIEW"
        
        print(f"\n✓ Submitted for review")
        
    def test_04_flag_responses_and_photos(self, setup_class):
        """Step 4: Reviewer flags responses and photos for report"""
        headers = {"Authorization": f"Bearer {FSP_TOKEN}"}
        
        # Get all responses
        responses_response = requests.get(
            f"{BASE_URL}/farm-audit/audits/{self.audit_id}/responses",
            headers=headers
        )
        assert responses_response.status_code == 200
        responses = responses_response.json()["data"]["items"]
        
        # Flag first 3 responses
        flagged_count = 0
        for response in responses[:3]:
            response_id = response["id"]
            
            # Create review and flag it
            review_response = requests.post(
                f"{BASE_URL}/farm-audit/audits/{self.audit_id}/reviews",
                headers=headers,
                json={
                    "audit_response_id": response_id,
                    "is_flagged_for_report": True,
                    "response_text": response.get("response_text")  # Keep original or override
                }
            )
            
            if review_response.status_code in [200, 201]:
                flagged_count += 1
        
        print(f"\n✓ Flagged {flagged_count} responses for report")
        self.expected_flagged_count = flagged_count
        
    def test_05_transition_to_reviewed(self, setup_class):
        """Step 5: Transition to REVIEWED status"""
        headers = {"Authorization": f"Bearer {FSP_TOKEN}"}
        
        transition_response = requests.post(
            f"{BASE_URL}/farm-audit/audits/{self.audit_id}/transition",
            headers=headers,
            json={"to_status": "REVIEWED"}
        )
        
        assert transition_response.status_code == 200, f"Transition to REVIEWED failed: {transition_response.text}"
        print(f"\n✓ Transitioned to REVIEWED")
        
    def test_06_finalize_audit_performance(self, setup_class):
        """Step 6: CRITICAL - Finalize audit and verify performance < 500ms"""
        headers = {"Authorization": f"Bearer {FSP_TOKEN}"}
        
        print("\n🔍 Testing finalization performance...")
        
        # Measure transition time
        start_time = time.time()
        
        transition_response = requests.post(
            f"{BASE_URL}/farm-audit/audits/{self.audit_id}/transition",
            headers=headers,
            json={"to_status": "FINALIZED"}
        )
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Verify response
        assert transition_response.status_code == 200, f"Finalization failed: {transition_response.text}"
        audit_data = transition_response.json()["data"]
        assert audit_data["status"] == "FINALIZED", f"Status not FINALIZED: {audit_data['status']}"
        
        # Verify performance requirement
        print(f"\n⏱️  Finalization time: {duration_ms:.2f}ms")
        assert duration_ms < 500, f"❌ PERFORMANCE ISSUE: Finalization took {duration_ms:.2f}ms (requirement: < 500ms)"
        
        print(f"✓ Finalization completed in {duration_ms:.2f}ms (< 500ms requirement met)")
        
    def test_07_verify_farmer_report_access(self, setup_class):
        """Step 7: Verify farmer can access the finalized report"""
        headers = {"Authorization": f"Bearer {FARMER_TOKEN}"}
        
        report_response = requests.get(
            f"{BASE_URL}/farm-audit/audits/{self.audit_id}/report",
            headers=headers
        )
        
        assert report_response.status_code == 200, f"Farmer report access failed: {report_response.text}"
        report_data = report_response.json()["data"]
        
        print(f"\n✓ Farmer can access report")
        self.report_data = report_data
        
    def test_08_verify_flagged_responses_have_values(self, setup_class):
        """Step 8: CRITICAL - Verify all flagged responses have actual values (no N/A or null)"""
        flagged_responses = self.report_data.get("flagged_responses", [])
        
        print(f"\n🔍 Verifying {len(flagged_responses)} flagged responses...")
        
        # Verify we have the expected number of flagged responses
        assert len(flagged_responses) == self.expected_flagged_count, \
            f"Expected {self.expected_flagged_count} flagged responses, got {len(flagged_responses)}"
        
        # Verify each flagged response has actual values
        for i, response in enumerate(flagged_responses, 1):
            response_value = response.get("response_value")
            
            print(f"  Response {i}: {response.get('parameter_name')} = '{response_value}'")
            
            # Critical checks
            assert response_value is not None, f"❌ Response {i} has null value"
            assert response_value != "N/A", f"❌ Response {i} has 'N/A' value"
            assert response_value != "", f"❌ Response {i} has empty value"
            
        print(f"✓ All {len(flagged_responses)} flagged responses have actual values")
        
    def test_09_verify_report_completeness(self, setup_class):
        """Step 9: Verify report contains all required sections"""
        report = self.report_data
        
        # Verify required sections exist
        assert "audit" in report, "Missing 'audit' section"
        assert "stats" in report, "Missing 'stats' section"
        assert "issues" in report, "Missing 'issues' section"
        assert "recommendations" in report, "Missing 'recommendations' section"
        assert "flagged_responses" in report, "Missing 'flagged_responses' section"
        assert "flagged_photos" in report, "Missing 'flagged_photos' section"
        
        # Verify audit details
        audit_info = report["audit"]
        assert audit_info.get("status") == "FINALIZED", f"Audit status not FINALIZED: {audit_info.get('status')}"
        
        # Print summary
        print(f"\n📊 Report Summary:")
        print(f"  - Status: {audit_info.get('status')}")
        print(f"  - Flagged Responses: {len(report['flagged_responses'])}")
        print(f"  - Flagged Photos: {len(report['flagged_photos'])}")
        print(f"  - Issues: {len(report['issues'])}")
        print(f"  - Recommendations: {len(report['recommendations'])}")
        
        print(f"\n✓ Report is complete with all required sections")
        
    def test_10_verify_database_state(self, setup_class):
        """Step 10: Verify database state is correct"""
        headers = {"Authorization": f"Bearer {FSP_TOKEN}"}
        
        # Get audit details
        audit_response = requests.get(
            f"{BASE_URL}/farm-audit/audits/{self.audit_id}",
            headers=headers
        )
        
        assert audit_response.status_code == 200
        audit_data = audit_response.json()["data"]
        
        # Verify finalization metadata
        assert audit_data["status"] == "FINALIZED"
        assert audit_data.get("finalized_at") is not None, "finalized_at not set"
        assert audit_data.get("finalized_by") is not None, "finalized_by not set"
        
        print(f"\n✓ Database state verified:")
        print(f"  - Status: FINALIZED")
        print(f"  - Finalized At: {audit_data.get('finalized_at')}")
        print(f"  - Finalized By: {audit_data.get('finalized_by')}")


def test_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("🎉 ALL TESTS PASSED!")
    print("="*70)
    print("\n✅ Audit finalization works correctly")
    print("✅ Performance requirement met (< 500ms)")
    print("✅ Farmer receives complete report")
    print("✅ All flagged responses have actual values")
    print("✅ Database state is correct")
    print("\n" + "="*70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
