import sqlite3
import json
import hashlib
from datetime import datetime

DB_FILE = "backend/research.db"


class ExperimentTracker:
    """Central store for all automated backtest results.

    Replaces research_insights.md and the analyze_results.py pipeline.
    All experiment data uses spread=0.0003, delay=0 (validated against live).
    """

    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self._ensure_table()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self):
        conn = self._get_conn()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT,
                strategy TEXT,
                strategy_source TEXT,
                symbol TEXT,
                timeframe TEXT,
                parameters TEXT,
                return_pct REAL,
                annualised_return REAL,
                max_drawdown REAL,
                total_trades INTEGER,
                trades_per_year REAL,
                win_rate REAL,
                profit_factor REAL,
                sharpe REAL,
                score REAL,
                train_period TEXT,
                test_period TEXT,
                test_return_pct REAL,
                validation_status TEXT DEFAULT 'pending',
                validation_details TEXT,
                parent_experiment_id TEXT,
                created_at TEXT,
                spread REAL DEFAULT 0.0003,
                execution_delay INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save(self, experiment_id, strategy, symbol, timeframe, params,
             results, strategy_source="existing", score=None,
             parent_experiment_id=None, train_period=None, test_period=None):
        """Save a single backtest result to the experiments table."""
        conn = self._get_conn()

        total_trades = results.get("total_trades", 0)
        return_pct = results.get("return_pct", 0.0)

        # Estimate annualised return and trades/year from equity curve
        equity_curve = results.get("equity_curve", [])
        years = self._estimate_years(equity_curve)
        if years and years > 0:
            annualised = ((1 + return_pct / 100) ** (1 / years) - 1) * 100
            trades_per_year = total_trades / years
        else:
            annualised = return_pct
            trades_per_year = total_trades

        conn.execute('''
            INSERT INTO experiments (
                experiment_id, strategy, strategy_source, symbol, timeframe,
                parameters, return_pct, annualised_return, max_drawdown,
                total_trades, trades_per_year, win_rate, profit_factor,
                sharpe, score, train_period, test_period,
                parent_experiment_id, created_at, spread, execution_delay
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            experiment_id, strategy, strategy_source, symbol, timeframe,
            json.dumps(params), return_pct, annualised,
            results.get("max_drawdown", 0.0), total_trades, trades_per_year,
            results.get("win_rate", 0.0), results.get("profit_factor", 0.0),
            results.get("sharpe", 0.0), score,
            train_period, test_period,
            parent_experiment_id, datetime.now().isoformat(),
            0.0003, 0
        ))
        conn.commit()
        conn.close()

    def update_validation(self, row_id, validation_status, test_return_pct=None,
                          validation_details=None):
        """Update validation results for an existing experiment row."""
        conn = self._get_conn()
        conn.execute('''
            UPDATE experiments
            SET validation_status = ?,
                test_return_pct = ?,
                validation_details = ?
            WHERE id = ?
        ''', (
            validation_status,
            test_return_pct,
            json.dumps(validation_details) if validation_details else None,
            row_id
        ))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Read / Query
    # ------------------------------------------------------------------

    def get_top_candidates(self, n=10, min_trades=30, validation_status=None):
        """Top N experiments by score. Optionally filter by validation status."""
        conn = self._get_conn()
        if validation_status:
            rows = conn.execute('''
                SELECT * FROM experiments
                WHERE total_trades >= ? AND validation_status = ?
                ORDER BY score DESC
                LIMIT ?
            ''', (min_trades, validation_status, n)).fetchall()
        else:
            rows = conn.execute('''
                SELECT * FROM experiments
                WHERE total_trades >= ?
                ORDER BY score DESC
                LIMIT ?
            ''', (min_trades, n)).fetchall()
        conn.close()
        return [self._row_to_dict(r) for r in rows]

    def get_failures_for_strategy(self, strategy_name):
        """All experiments for a strategy with score <= 0 or rejected validation."""
        conn = self._get_conn()
        rows = conn.execute('''
            SELECT * FROM experiments
            WHERE strategy = ? AND (score <= 0 OR validation_status = 'rejected')
            ORDER BY score ASC
        ''', (strategy_name,)).fetchall()
        conn.close()
        return [self._row_to_dict(r) for r in rows]

    def get_experiments_by_source(self, source):
        """All experiments from a given source (existing, composable, llm_generated)."""
        conn = self._get_conn()
        rows = conn.execute('''
            SELECT * FROM experiments
            WHERE strategy_source = ?
            ORDER BY created_at DESC
        ''', (source,)).fetchall()
        conn.close()
        return [self._row_to_dict(r) for r in rows]

    def get_experiments_by_asset(self, symbol):
        """Everything tried on a symbol."""
        conn = self._get_conn()
        rows = conn.execute('''
            SELECT * FROM experiments
            WHERE symbol = ?
            ORDER BY score DESC
        ''', (symbol,)).fetchall()
        conn.close()
        return [self._row_to_dict(r) for r in rows]

    def get_untested_combinations(self, strategies, symbols, timeframes):
        """Identify strategy/symbol/timeframe combos not yet tested."""
        conn = self._get_conn()
        tested = set()
        rows = conn.execute(
            'SELECT DISTINCT strategy, symbol, timeframe FROM experiments'
        ).fetchall()
        for r in rows:
            tested.add((r["strategy"], r["symbol"], r["timeframe"]))
        conn.close()

        untested = []
        for s in strategies:
            for sym in symbols:
                for tf in timeframes:
                    if (s, sym, tf) not in tested:
                        untested.append({"strategy": s, "symbol": sym, "timeframe": tf})
        return untested

    def has_been_tested(self, strategy, symbol, timeframe, params):
        """Check if an exact strategy/symbol/timeframe/params combo exists."""
        params_hash = self._params_hash(params)
        conn = self._get_conn()
        row = conn.execute('''
            SELECT COUNT(*) as cnt FROM experiments
            WHERE strategy = ? AND symbol = ? AND timeframe = ?
        ''', (strategy, symbol, timeframe)).fetchone()
        conn.close()

        if row["cnt"] == 0:
            return False

        # Check param-level match
        conn = self._get_conn()
        rows = conn.execute('''
            SELECT parameters FROM experiments
            WHERE strategy = ? AND symbol = ? AND timeframe = ?
        ''', (strategy, symbol, timeframe)).fetchall()
        conn.close()

        for r in rows:
            if self._params_hash(json.loads(r["parameters"])) == params_hash:
                return True
        return False

    def count(self):
        """Total number of experiments."""
        conn = self._get_conn()
        row = conn.execute('SELECT COUNT(*) as cnt FROM experiments').fetchone()
        conn.close()
        return row["cnt"]

    # ------------------------------------------------------------------
    # LLM Summary
    # ------------------------------------------------------------------

    def get_summary_for_llm(self, max_results=20):
        """Build a concise text summary for the LLM agent prompt.

        Replaces research_insights.md with clean, up-to-date data.
        """
        conn = self._get_conn()

        # Top performers
        top = conn.execute('''
            SELECT strategy, symbol, timeframe, annualised_return, sharpe, score,
                   validation_status, total_trades
            FROM experiments
            WHERE total_trades >= 30
            ORDER BY score DESC
            LIMIT ?
        ''', (max_results,)).fetchall()

        # Worst failures
        worst = conn.execute('''
            SELECT strategy, symbol, timeframe, annualised_return, sharpe, score,
                   total_trades
            FROM experiments
            WHERE total_trades >= 10
            ORDER BY score ASC
            LIMIT 10
        ''').fetchall()

        # Strategy-level summary
        strat_summary = conn.execute('''
            SELECT strategy, COUNT(*) as runs,
                   AVG(annualised_return) as avg_return,
                   MAX(annualised_return) as best_return,
                   AVG(score) as avg_score
            FROM experiments
            GROUP BY strategy
            ORDER BY avg_score DESC
        ''').fetchall()

        conn.close()

        lines = []
        lines.append("=== EXPERIMENT SUMMARY ===\n")

        lines.append(f"Total experiments: {self.count()}\n")

        if strat_summary:
            lines.append("STRATEGY OVERVIEW:")
            for s in strat_summary:
                lines.append(
                    f"  {s['strategy']}: {s['runs']} runs, "
                    f"avg {s['avg_return']:.2f}% ann, "
                    f"best {s['best_return']:.2f}% ann, "
                    f"avg score {s['avg_score']:.3f}"
                )
            lines.append("")

        if top:
            lines.append(f"TOP {len(top)} EXPERIMENTS:")
            for i, r in enumerate(top, 1):
                status = f" [{r['validation_status']}]" if r["validation_status"] != "pending" else ""
                lines.append(
                    f"  {i}. {r['strategy']} on {r['symbol']} {r['timeframe']}: "
                    f"{r['annualised_return']:.2f}% ann, "
                    f"Sharpe {r['sharpe']:.2f}, "
                    f"score {r['score']:.3f}, "
                    f"{r['total_trades']} trades{status}"
                )
            lines.append("")

        if worst:
            lines.append("NOTABLE FAILURES:")
            for i, r in enumerate(worst, 1):
                lines.append(
                    f"  {i}. {r['strategy']} on {r['symbol']} {r['timeframe']}: "
                    f"{r['annualised_return']:.2f}% ann, "
                    f"score {r['score']:.3f}, "
                    f"{r['total_trades']} trades"
                )
            lines.append("")

        untested_indicators = [
            "OBV (volume confirmation)",
            "VWAP (institutional fair value)",
            "CHOP index (only indicator not yet used in any strategy)",
            "Multi-timeframe confluence",
            "Economic calendar events (on_event wiring exists but unused)",
        ]
        lines.append("UNTESTED DIRECTIONS:")
        for u in untested_indicators:
            lines.append(f"  - {u}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_dict(row):
        d = dict(row)
        if d.get("parameters"):
            d["parameters"] = json.loads(d["parameters"])
        if d.get("validation_details"):
            d["validation_details"] = json.loads(d["validation_details"])
        return d

    @staticmethod
    def _params_hash(params):
        """Deterministic hash of a params dict for dedup."""
        return hashlib.md5(
            json.dumps(params, sort_keys=True).encode()
        ).hexdigest()

    @staticmethod
    def _estimate_years(equity_curve):
        """Estimate the number of years from an equity curve."""
        if not equity_curve or len(equity_curve) < 2:
            return None
        try:
            first = equity_curve[0].get("time") or equity_curve[0].get("timestamp")
            last = equity_curve[-1].get("time") or equity_curve[-1].get("timestamp")
            if first and last:
                t0 = datetime.fromisoformat(str(first).replace("Z", ""))
                t1 = datetime.fromisoformat(str(last).replace("Z", ""))
                days = (t1 - t0).days
                return days / 365.25 if days > 0 else None
        except (ValueError, TypeError, KeyError):
            return None
        return None
