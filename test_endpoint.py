
import requests

# The URL user was trying (expected 404)
try:
    print("Testing incorrect URL: http://localhost:8000/api/v1/audits")
    r = requests.get("http://localhost:8000/api/v1/audits")
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Incorrect URL check failed: {e}")

# The URL I suspect is correct (expected 401 or 200, but NOT 404)
# Note: It might be 403/401 because I'm not sending a token, but that confirms 
# the path exists. 404 means path doesn't exist.
try:
    print("\nTesting correct URL: http://localhost:8000/api/v1/farm-audit/audits")
    r = requests.get("http://localhost:8000/api/v1/farm-audit/audits")
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Correct URL check failed: {e}")
