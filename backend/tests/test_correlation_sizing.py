from backend.engine.correlation_sizing import (
    risk_fraction_for,
    cluster_for,
    BASE_RISK,
    CLUSTERS,
)


def test_no_peers_full_risk():
    assert risk_fraction_for("GLD", {}) == BASE_RISK


def test_one_peer_half_risk():
    positions = {"IAU": {"size": 100, "avg_price": 50.0}}
    assert risk_fraction_for("GLD", positions) == BASE_RISK / 2


def test_two_peers_third_risk():
    positions = {
        "IAU": {"size": 100, "avg_price": 50.0},
        "SLV": {"size": 200, "avg_price": 25.0},
    }
    assert risk_fraction_for("GLD", positions) == BASE_RISK / 3


def test_three_peers_quarter_risk():
    positions = {
        "IAU": {"size": 100},
        "SLV": {"size": 200},
        "GDX": {"size": 300},
    }
    assert risk_fraction_for("GLD", positions) == BASE_RISK / 4


def test_flat_peer_does_not_count():
    positions = {"IAU": {"size": 0}}
    assert risk_fraction_for("GLD", positions) == BASE_RISK


def test_negative_size_short_counts():
    positions = {"IAU": {"size": -100}}
    assert risk_fraction_for("GLD", positions) == BASE_RISK / 2


def test_self_in_positions_does_not_double_count():
    positions = {"GLD": {"size": 50}, "IAU": {"size": 100}}
    assert risk_fraction_for("GLD", positions) == BASE_RISK / 2


def test_unclustered_symbol_passthrough():
    positions = {"GLD": {"size": 100}}
    assert risk_fraction_for("SPY", positions) == BASE_RISK


def test_unclustered_returns_base_with_empty_positions():
    assert risk_fraction_for("SPY", {}) == BASE_RISK


def test_energy_cluster():
    positions = {"XOP": {"size": 100}}
    assert risk_fraction_for("OIH", positions) == BASE_RISK / 2


def test_cross_cluster_peer_does_not_count():
    positions = {"XOP": {"size": 100}}
    assert risk_fraction_for("GLD", positions) == BASE_RISK


def test_cluster_for_lookup():
    assert cluster_for("GLD") == "gold"
    assert cluster_for("OIH") == "energy"
    assert cluster_for("XBI") == "biotech"
    assert cluster_for("SPY") is None


def test_cluster_membership():
    assert "GLD" in CLUSTERS["gold"]
    assert "IAU" in CLUSTERS["gold"]
    assert "SLV" in CLUSTERS["gold"]
    assert "GDX" in CLUSTERS["gold"]
    assert "OIH" in CLUSTERS["energy"]
    assert "XOP" in CLUSTERS["energy"]
    assert "XLE" in CLUSTERS["energy"]
    assert "XBI" in CLUSTERS["biotech"]


if __name__ == "__main__":
    import sys
    funcs = [v for k, v in dict(globals()).items() if k.startswith("test_") and callable(v)]
    failed = 0
    for f in funcs:
        try:
            f()
            print(f"PASS  {f.__name__}")
        except AssertionError as e:
            print(f"FAIL  {f.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {f.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{len(funcs) - failed}/{len(funcs)} passed")
    sys.exit(0 if failed == 0 else 1)
