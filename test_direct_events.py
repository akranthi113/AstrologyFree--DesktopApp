import sys
from pathlib import Path
from backend.events_calc import calculate_events_for_year

ephe_path = Path("ephe").resolve()
try:
    print("Testing calculate_events_for_year directly...")
    res = calculate_events_for_year(2026, str(ephe_path))
    print(f"Year: {res['year']}")
    print(f"Stelliums: {len(res['stelliums'])}")
    print(f"Transits: {len(res['transits'])}")
    print(f"Retrogrades: {len(res['retrogrades'])}")
except Exception as e:
    import traceback
    traceback.print_exc()
