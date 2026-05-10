import csv, collections, json

with open('Datasets/Top Indian Places to Visit.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def safe_float(v):
    try: return float(v)
    except: return 0.0

# Top 15 rated
top_rated = sorted(rows, key=lambda r: safe_float(r.get('Google review rating', 0)), reverse=True)[:15]
print('=== TOP 15 RATED PLACES ===')
for r in top_rated:
    print(f"  [{r['Google review rating']}] {r['Name']} | {r['City']}, {r['State']} | {r['Type']} | Fee: INR {r['Entrance Fee in INR']} | Best: {r['Best Time to visit']}")

print()
types = collections.Counter(r['Type'] for r in rows)
print('=== CATEGORY BREAKDOWN ===')
for t, c in types.most_common(12):
    print(f"  {t}: {c}")

print()
zones = collections.Counter(r['Zone'] for r in rows)
print('=== BY ZONE ===')
for z, c in zones.most_common():
    print(f"  {z}: {c}")

print()
states = collections.Counter(r['State'] for r in rows)
print('=== TOP STATES ===')
for s, c in states.most_common(10):
    print(f"  {s}: {c}")

print()
free = [r for r in rows if r.get('Entrance Fee in INR','').strip() == '0']
print(f'=== FREE ENTRY PLACES: {len(free)} total ===')
free_top = sorted(free, key=lambda r: safe_float(r.get('Google review rating', 0)), reverse=True)[:10]
for r in free_top:
    print(f"  [{r['Google review rating']}] {r['Name']} | {r['City']}, {r['State']}")

print()
budget = [r for r in rows if safe_float(r.get('Entrance Fee in INR', 999)) < 50 and safe_float(r.get('Entrance Fee in INR', 0)) > 0]
print(f'=== BUDGET PLACES (fee under INR 50): {len(budget)} ===')
for r in sorted(budget, key=lambda r: safe_float(r.get('Google review rating', 0)), reverse=True)[:8]:
    print(f"  [{r['Google review rating']}] {r['Name']} | {r['City']} | Fee: INR {r['Entrance Fee in INR']}")

print()
times = collections.Counter(r['Best Time to visit'] for r in rows)
print('=== BEST TIME BREAKDOWN ===')
for t, c in times.most_common():
    print(f"  {t}: {c}")

print()
# Hidden gems (high rating, low reviews count)
hidden = sorted(rows, key=lambda r: (safe_float(r.get('Google review rating',0)), -safe_float(r.get('Number of google review in lakhs', 99))), reverse=True)[:10]
print('=== HIDDEN GEMS (high rating, fewer crowds) ===')
for r in hidden:
    print(f"  [{r['Google review rating']}] {r['Name']} | {r['City']}, {r['State']} | Reviews: {r['Number of google review in lakhs']}L")
