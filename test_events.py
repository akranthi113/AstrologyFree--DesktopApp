import urllib.request
import json
import traceback

try:
    print("Fetching events for 2026...")
    with urllib.request.urlopen("http://127.0.0.1:8000/api/events/2026") as response:
        data = json.loads(response.read().decode())
        print(f"Year: {data.get('year')}")
        print(f"Stelliums Found: {len(data.get('stelliums', []))}")
        print(f"Transits Found: {len(data.get('transits', []))}")
        print(f"Retrogrades Found: {len(data.get('retrogrades', []))}")
        if data.get('stelliums'):
            print("\nFirst Stellium:", data['stelliums'][0])
except Exception as e:
    print("Error:", e)
    traceback.print_exc()
