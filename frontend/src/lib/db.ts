import Database from 'better-sqlite3'
import path from 'path'

function getDb() {
  return new Database(path.join(process.cwd(), '../backend/research.db'), { readonly: true })
}

// ─── Types ────────────────────────────────────────────────────────────────────

export interface ValidatedStrategy {
  slug: string
  strategy: string       // e.g. "StochRSIMeanReversionStrategy"
  symbol: string         // e.g. "GLD"
  timeframe: string      // e.g. "15m"
  sharpe: number
  annualised_return: number
  max_drawdown: number
  win_rate: number
  trades_per_year: number
}

export interface YearlyRun {
  test_id: string
  year: string
  return_pct: number
  max_drawdown: number
  win_rate: number
  total_trades: number
}

export interface StrategyStats {
  total_return: number
  avg_annual_return: number
  max_drawdown: number
  win_rate: number
  total_trades: number
  years_count: number
}

export interface EquityPoint {
  time: number
  equity: number
}

// ─── Internal row types ───────────────────────────────────────────────────────

interface ExperimentRow {
  strategy: string
  symbol: string
  timeframe: string
  sharpe: number
  annualised_return: number
  max_drawdown: number
  win_rate: number
  trades_per_year: number
}

interface TestRunRow {
  test_id: string
  start_date: string
  return_pct: number
  max_drawdown: number
  win_rate: number
  total_trades: number
}

interface TestIdRow {
  test_id: string
}

interface EquityCurveRow {
  data: string
}

// ─── Slug helpers ─────────────────────────────────────────────────────────────

export function makeSlug(strategy: string, symbol: string, timeframe: string): string {
  // StochRSIMeanReversionStrategy + GLD + 15m → "gld-15m-stochrsi-mean-reversion"
  const stratSlug = strategy
    .replace(/Strategy$/, '')
    .replace(/([A-Z])/g, '-$1')
    .toLowerCase()
    .replace(/^-/, '')
    .replace(/[^a-z0-9-]+/g, '-')
  return `${symbol.toLowerCase()}-${timeframe}-${stratSlug}`
}

export function parseSlug(slug: string, all: ValidatedStrategy[]): ValidatedStrategy | undefined {
  return all.find((s) => s.slug === slug)
}

// ─── DB-driven strategy discovery ────────────────────────────────────────────

export function getValidatedStrategies(minSharpe = 1.0): ValidatedStrategy[] {
  const db = getDb()

  // Best experiment per strategy/symbol/timeframe combo, filtered by passed + Sharpe threshold
  const rows = db
    .prepare<[], ExperimentRow>(
      `SELECT strategy, symbol, timeframe, sharpe, annualised_return, max_drawdown, win_rate, trades_per_year
       FROM experiments
       WHERE validation_status = 'passed'
         AND sharpe = (
           SELECT MAX(e2.sharpe)
           FROM experiments e2
           WHERE e2.validation_status = 'passed'
             AND e2.strategy = experiments.strategy
             AND e2.symbol = experiments.symbol
             AND e2.timeframe = experiments.timeframe
         )
       GROUP BY strategy, symbol, timeframe
       ORDER BY sharpe DESC`,
    )
    .all()

  db.close()

  return rows
    .filter((r) => r.sharpe >= minSharpe)
    .map((r) => ({
      slug: makeSlug(r.strategy, r.symbol, r.timeframe),
      strategy: r.strategy,
      symbol: r.symbol,
      timeframe: r.timeframe,
      sharpe: r.sharpe,
      annualised_return: r.annualised_return,
      max_drawdown: r.max_drawdown,
      win_rate: r.win_rate > 1 ? r.win_rate : r.win_rate * 100,
      trades_per_year: r.trades_per_year,
    }))
}

// ─── Test run data (for detail page) ─────────────────────────────────────────

// Map experiments.strategy → test_runs.strategy (they differ by "Strategy" suffix)
function testRunsStrategy(strategy: string): string {
  return strategy.replace(/Strategy$/, '')
}

export function getYearlyRuns(
  strategy: string,
  symbol: string,
  timeframe: string,
): YearlyRun[] {
  const db = getDb()
  const strat = testRunsStrategy(strategy)

  // Pick the iteration_index with the most years of data.
  // If all iterations have 1 year each (runs were done year-by-year independently),
  // fall back to collecting one row per year across all iterations.
  const bestIteration = db
    .prepare<[string, string, string], { iteration_index: number; cnt: number }>(
      `SELECT iteration_index, COUNT(*) as cnt
       FROM test_runs
       WHERE strategy = ? AND symbol = ? AND timeframe = ?
       GROUP BY iteration_index
       ORDER BY cnt DESC, SUM(return_pct) DESC
       LIMIT 1`,
    )
    .get(strat, symbol, timeframe)

  let rows: TestRunRow[] = []

  if (bestIteration && bestIteration.cnt > 1) {
    // Multi-year iteration — use it directly
    rows = db
      .prepare<[string, string, string, number], TestRunRow>(
        `SELECT test_id, start_date, return_pct, max_drawdown, win_rate, total_trades
         FROM test_runs
         WHERE strategy = ? AND symbol = ? AND timeframe = ? AND iteration_index = ?
         ORDER BY start_date ASC`,
      )
      .all(strat, symbol, timeframe, bestIteration.iteration_index)
  } else if (bestIteration) {
    // Each year was run separately — take one row per calendar year (highest return)
    rows = db
      .prepare<[string, string, string], TestRunRow>(
        `SELECT test_id, start_date, return_pct, max_drawdown, win_rate, total_trades
         FROM test_runs t
         WHERE strategy = ? AND symbol = ? AND timeframe = ?
           AND return_pct = (
             SELECT MAX(t2.return_pct) FROM test_runs t2
             WHERE t2.strategy = t.strategy AND t2.symbol = t.symbol
               AND t2.timeframe = t.timeframe
               AND strftime('%Y', t2.start_date) = strftime('%Y', t.start_date)
           )
         GROUP BY strftime('%Y', start_date)
         ORDER BY start_date ASC`,
      )
      .all(strat, symbol, timeframe)
  }

  db.close()

  return rows.map((r) => ({
    test_id: r.test_id,
    year: r.start_date.split('-')[0],
    return_pct: r.return_pct,
    max_drawdown: r.max_drawdown,
    win_rate: r.win_rate > 1 ? r.win_rate : r.win_rate * 100,
    total_trades: r.total_trades,
  }))
}

export function getStrategyStats(strategy: string, symbol: string, timeframe: string): StrategyStats | null {
  const rows = getYearlyRuns(strategy, symbol, timeframe)
  const active = rows.filter((r) => r.total_trades > 0)
  if (active.length === 0) return null

  const total_return = active.reduce((s, r) => s + r.return_pct, 0)
  const max_drawdown = Math.max(...active.map((r) => r.max_drawdown))
  const win_rate = active.reduce((s, r) => s + r.win_rate, 0) / active.length
  const total_trades = active.reduce((s, r) => s + r.total_trades, 0)

  return {
    total_return,
    avg_annual_return: total_return / active.length,
    max_drawdown,
    win_rate,
    total_trades,
    years_count: active.length,
  }
}

export function getEquityCurve(strategy: string, symbol: string, timeframe: string): EquityPoint[] {
  const db = getDb()
  const strat = testRunsStrategy(strategy)

  const bestIteration = db
    .prepare<[string, string, string], { iteration_index: number; cnt: number }>(
      `SELECT iteration_index, COUNT(*) as cnt
       FROM test_runs
       WHERE strategy = ? AND symbol = ? AND timeframe = ?
       GROUP BY iteration_index
       ORDER BY cnt DESC, SUM(return_pct) DESC
       LIMIT 1`,
    )
    .get(strat, symbol, timeframe)

  if (!bestIteration) {
    db.close()
    return []
  }

  let testIds: string[]

  if (bestIteration.cnt > 1) {
    testIds = db
      .prepare<[string, string, string, number], TestIdRow>(
        `SELECT test_id FROM test_runs
         WHERE strategy = ? AND symbol = ? AND timeframe = ? AND iteration_index = ?
         ORDER BY start_date ASC`,
      )
      .all(strat, symbol, timeframe, bestIteration.iteration_index)
      .map((r) => r.test_id)
  } else {
    // One row per iteration — take one test_id per calendar year (highest return)
    testIds = db
      .prepare<[string, string, string], TestIdRow>(
        `SELECT test_id FROM test_runs t
         WHERE strategy = ? AND symbol = ? AND timeframe = ?
           AND return_pct = (
             SELECT MAX(t2.return_pct) FROM test_runs t2
             WHERE t2.strategy = t.strategy AND t2.symbol = t.symbol
               AND t2.timeframe = t.timeframe
               AND strftime('%Y', t2.start_date) = strftime('%Y', t.start_date)
           )
         GROUP BY strftime('%Y', start_date)
         ORDER BY start_date ASC`,
      )
      .all(strat, symbol, timeframe)
      .map((r) => r.test_id)
  }

  const allPoints: EquityPoint[] = []
  let lastEquity = 10000

  for (const testId of testIds) {
    const row = db
      .prepare<[string], EquityCurveRow>('SELECT data FROM equity_curves WHERE test_id = ?')
      .get(testId)

    if (!row) continue
    const points: EquityPoint[] = JSON.parse(row.data)
    if (points.length === 0) continue

    const scale = lastEquity / points[0].equity
    for (const p of points) {
      allPoints.push({ time: p.time, equity: p.equity * scale })
    }
    lastEquity = allPoints[allPoints.length - 1].equity
  }

  db.close()
  return allPoints
}
