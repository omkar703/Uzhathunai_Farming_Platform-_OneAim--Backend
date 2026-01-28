
import urllib.request
import urllib.error

def test_url(url):
    print(f"Testing: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            print(f"Status: {response.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"Status: {e.code}")
    except Exception as e:
        print(f"Error: {e}")

print("Testing incorrect URL:")
test_url("http://localhost:8000/api/v1/audits")

print("\nTesting correct URL:")
test_url("http://localhost:8000/api/v1/farm-audit/audits")
