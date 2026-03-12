from backend.events_calc import calculate_events_for_year

data = calculate_events_for_year(2026, ephe_path='ephe')
print(f"Total stelliums: {len(data['stelliums'])}")
print()
for s in data['stelliums']:
    pp = s.get('peak_planets', s['planets'])
    print(f"Sign        : {s['sign']}")
    print(f"Peak date   : {s.get('peak_date', '?')} ({len(pp)} planets simultaneously)")
    print(f"Peak planets: {', '.join(pp)}")
    print(f"Active range: {s['start_date']} -> {s.get('end_date','?')}")
    print()
