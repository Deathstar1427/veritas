import requests
from pathlib import Path

# Test 1: Check response structure
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
test_file = FIXTURES_DIR / "test_data.csv"

with test_file.open("rb") as f:
    files = {"file": f}
    data = {"domain": "hiring"}
    response = requests.post(
        "http://127.0.0.1:8000/api/analyze", files=files, data=data
    )

print("Response Structure:")
result = response.json()
print(f"Keys in response: {list(result.keys())}")
print(f"Keys in results: {list(result.get('results', {}).keys())}")
print("\nCORS Headers in response:")
has_cors = False
for header, value in response.headers.items():
    if "access-control" in header.lower() or "cors" in header.lower():
        print(f"  {header}: {value}")
        has_cors = True

if not has_cors:
    print("  No CORS headers found")

print("\nAll Response Headers:")
for header, value in list(response.headers.items())[:15]:
    print(f"  {header}: {value}")

