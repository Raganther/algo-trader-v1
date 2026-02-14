"""Quick test: connect to IG API and fetch gold 15m data."""

from backend.engine.ig_loader import IGDataLoader

loader = IGDataLoader()

# Step 1: Search for gold to find the correct epic
print("=== Searching for Gold ===")
results = loader.search_epic("Gold")
for r in results[:5]:
    print(f"  {r['epic']} — {r['instrumentName']} ({r['instrumentType']})")

# Step 2: Fetch 2 days of 15m gold data
print("\n=== Fetching Gold 15m Data ===")
df = loader.fetch_data('GOLD', '15m', '2026-02-12', '2026-02-13')

if not df.empty:
    print(f"\nRows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 5 rows:")
    print(df.head())
    print(f"\nLast 5 rows:")
    print(df.tail())
    print(f"\nPrice range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
else:
    print("❌ No data returned")
