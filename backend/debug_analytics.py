from backend.analytics import DrawdownAnalyzer
import pandas as pd

analyzer = DrawdownAnalyzer()
print("Running analysis for StochRSIMeanReversion GBPJPY=X 1h...")
result = analyzer.analyze("StochRSIMeanReversion", "GBPJPY=X", "1h")

if result:
    print(f"Result keys: {result.keys()}")
    curve = result['equity_curve']
    print(f"Curve length: {len(curve)}")
    if len(curve) > 0:
        print("First 5 points:")
        for p in curve[:5]:
            print(p)
        print("Last 5 points:")
        for p in curve[-5:]:
            print(p)
else:
    print("No result found")
