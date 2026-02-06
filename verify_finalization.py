#!/usr/bin/env python3
"""
Quick Verification Script for Audit Finalization & Farmer Report Delivery

This script tests the critical finalization workflow:
1. Finds or creates an audit in REVIEWED status
2. Finalizes the audit (measures performance)
3. Retrieves farmer report
4. Verifies all flagged data is present

Run: python verify_finalization.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 10

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(title):
    print(f"\n{BOLD}{CYAN}{'=' * 80}{RESET}")
    print(f"{BOLD}{CYAN}{title.center(80)}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 80}{RESET}\n")


def print_success(message):
    print(f"{GREEN}✓{RESET} {message}")


def print_error(message):
    print(f"{RED}✗{RESET} {message}")


def print_info(message):
    print(f"{BLUE}ℹ{RESET} {message}")


def print_warning(message):
    print(f"{YELLOW}⚠{RESET} {message}")


def main():
    print_header("AUDIT FINALIZATION & FARMER REPORT VERIFICATION")
    
    # Step 1: Login as FSP user
    print_info("Step 1: Authenticating as FSP user...")
    
    # Try to find existing FSP user or use test credentials
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "fsp@example.com",  # Update with actual credentials
            "password": "password123"
        },
        timeout=TIMEOUT
    )
    
    if login_response.status_code != 200:
        print_error(f"FSP login failed: {login_response.status_code}")
        print_warning("Please update FSP credentials in the script")
        return False
    
    fsp_token = login_response.json()["data"]["access_token"]
    fsp_headers = {"Authorization": f"Bearer {fsp_token}"}
    print_success("FSP authenticated")
    
    # Step 2: Find an audit in REVIEWED status or create one
    print_info("\nStep 2: Finding audit in REVIEWED status...")
    
    audits_response = requests.get(
        f"{BASE_URL}/farm-audit/audits?status=REVIEWED",
        headers=fsp_headers,
        timeout=TIMEOUT
    )
    
    audit_id = None
    if audits_response.status_code == 200:
        audits = audits_response.json()["data"]["items"]
        if audits:
            audit_id = audits[0]["id"]
            print_success(f"Found audit in REVIEWED status: {audit_id}")
        else:
            print_warning("No audits in REVIEWED status found")
            
            # Try to find any audit we can transition
            all_audits_response = requests.get(
                f"{BASE_URL}/farm-audit/audits",
                headers=fsp_headers,
                timeout=TIMEOUT
            )
            
            if all_audits_response.status_code == 200:
                all_audits = all_audits_response.json()["data"]["items"]
                if all_audits:
                    audit_id = all_audits[0]["id"]
                    current_status = all_audits[0]["status"]
                    print_info(f"Using audit {audit_id} (current status: {current_status})")
                    
                    # Try to transition to REVIEWED
                    if current_status != "REVIEWED":
                        print_info(f"Attempting to transition from {current_status} to REVIEWED...")
                        transition_response = requests.post(
                            f"{BASE_URL}/farm-audit/audits/{audit_id}/transition",
                            json={"to_status": "REVIEWED"},
                            headers=fsp_headers,
                            timeout=TIMEOUT
                        )
                        
                        if transition_response.status_code == 200:
                            print_success("Transitioned to REVIEWED")
                        else:
                            print_warning(f"Could not transition to REVIEWED: {transition_response.status_code}")
                            print_info(f"Response: {transition_response.text[:200]}")
    
    if not audit_id:
        print_error("No suitable audit found for testing")
        print_warning("Please create an audit with responses and flag some items for the report")
        return False
    
    # Step 3: CRITICAL - Finalize the audit and measure performance
    print_header("STEP 3: FINALIZE AUDIT (PERFORMANCE TEST)")
    
    print_info(f"Finalizing audit {audit_id}...")
    print_info("Measuring transition time (requirement: < 500ms)...")
    
    start_time = time.time()
    
    finalize_response = requests.post(
        f"{BASE_URL}/farm-audit/audits/{audit_id}/transition",
        json={"to_status": "FINALIZED"},
        headers=fsp_headers,
        timeout=TIMEOUT
    )
    
    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000
    
    print(f"\n{BOLD}⏱️  Finalization Time: {duration_ms:.2f}ms{RESET}\n")
    
    if finalize_response.status_code == 200:
        print_success(f"Audit finalized successfully")
        
        if duration_ms < 500:
            print_success(f"✓ Performance requirement MET (< 500ms)")
        else:
            print_error(f"✗ Performance requirement FAILED ({duration_ms:.2f}ms > 500ms)")
        
        # Check finalization metadata
        audit_data = finalize_response.json()["data"]
        if audit_data.get("finalized_at"):
            print_success(f"finalized_at: {audit_data['finalized_at']}")
        if audit_data.get("finalized_by"):
            print_success(f"finalized_by: {audit_data['finalized_by']}")
    else:
        print_error(f"Finalization failed: {finalize_response.status_code}")
        print_info(f"Response: {finalize_response.text[:500]}")
        return False
    
    # Step 4: Login as Farmer
    print_header("STEP 4: FARMER REPORT ACCESS")
    
    print_info("Authenticating as Farmer...")
    
    farmer_login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "farmer@example.com",  # Update with actual credentials
            "password": "password123"
        },
        timeout=TIMEOUT
    )
    
    if farmer_login_response.status_code != 200:
        print_warning("Farmer login failed - using FSP token for testing")
        farmer_headers = fsp_headers  # Fallback to FSP token
    else:
        farmer_token = farmer_login_response.json()["data"]["access_token"]
        farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
        print_success("Farmer authenticated")
    
    # Step 5: Get Farmer Report
    print_info("\nRetrieving farmer report...")
    
    report_response = requests.get(
        f"{BASE_URL}/farm-audit/audits/{audit_id}/report",
        headers=farmer_headers,
        timeout=TIMEOUT
    )
    
    if report_response.status_code != 200:
        print_error(f"Failed to retrieve report: {report_response.status_code}")
        print_info(f"Response: {report_response.text[:500]}")
        return False
    
    report_data = report_response.json()["data"]
    print_success("Farmer report retrieved successfully")
    
    # Step 6: Verify Report Completeness
    print_header("STEP 6: REPORT DATA VERIFICATION")
    
    # Check sections
    sections = ["audit", "stats", "issues", "recommendations", "flagged_responses", "flagged_photos"]
    for section in sections:
        if section in report_data:
            print_success(f"✓ Section '{section}' present")
        else:
            print_error(f"✗ Section '{section}' MISSING")
    
    # Verify flagged responses have actual values
    print(f"\n{BOLD}Flagged Responses Verification:{RESET}")
    flagged_responses = report_data.get("flagged_responses", [])
    
    if not flagged_responses:
        print_warning("No flagged responses found in report")
    else:
        print_info(f"Found {len(flagged_responses)} flagged responses")
        
        all_valid = True
        for i, response in enumerate(flagged_responses, 1):
            param_name = response.get("parameter_name", "Unknown")
            response_value = response.get("response_value")
            
            # Check for invalid values
            if response_value is None:
                print_error(f"  {i}. {param_name}: NULL VALUE")
                all_valid = False
            elif response_value == "N/A":
                print_error(f"  {i}. {param_name}: 'N/A' VALUE")
                all_valid = False
            elif response_value == "":
                print_error(f"  {i}. {param_name}: EMPTY VALUE")
                all_valid = False
            else:
                print_success(f"  {i}. {param_name}: '{response_value}'")
        
        if all_valid:
            print(f"\n{GREEN}{BOLD}✓ ALL FLAGGED RESPONSES HAVE VALID VALUES{RESET}")
        else:
            print(f"\n{RED}{BOLD}✗ SOME FLAGGED RESPONSES HAVE INVALID VALUES{RESET}")
    
    # Verify flagged photos
    print(f"\n{BOLD}Flagged Photos Verification:{RESET}")
    flagged_photos = report_data.get("flagged_photos", [])
    
    if not flagged_photos:
        print_warning("No flagged photos found in report")
    else:
        print_info(f"Found {len(flagged_photos)} flagged photos")
        
        for i, photo in enumerate(flagged_photos, 1):
            file_url = photo.get("file_url")
            caption = photo.get("caption", "No caption")
            
            if file_url:
                print_success(f"  {i}. {caption[:50]}: {file_url[:60]}...")
            else:
                print_error(f"  {i}. {caption[:50]}: NO FILE URL")
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    
    print(f"{BOLD}Audit ID:{RESET} {audit_id}")
    print(f"{BOLD}Finalization Time:{RESET} {duration_ms:.2f}ms")
    print(f"{BOLD}Performance:{RESET} {'PASS' if duration_ms < 500 else 'FAIL'} (< 500ms)")
    print(f"{BOLD}Flagged Responses:{RESET} {len(flagged_responses)}")
    print(f"{BOLD}Flagged Photos:{RESET} {len(flagged_photos)}")
    print(f"{BOLD}Issues:{RESET} {len(report_data.get('issues', []))}")
    print(f"{BOLD}Recommendations:{RESET} {len(report_data.get('recommendations', []))}")
    
    print(f"\n{GREEN}{BOLD}{'✓ VERIFICATION COMPLETE' if duration_ms < 500 else '⚠ VERIFICATION COMPLETE WITH WARNINGS'}{RESET}\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
