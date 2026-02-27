// Markdown file mapping: "Strategy|SYMBOL|TF" → .md filename
// Key = strategy class name (from experiments) + "|" + symbol + "|" + timeframe
// Falls back to strategy-only key if symbol/TF-specific key doesn't exist.
// Add an entry here when you write research notes for a strategy.
export const MARKDOWN_MAP: Record<string, string> = {
  // Keyed by "Strategy|SYMBOL|TF" — must be exact match, no fallback
  'StochRSIMeanReversionStrategy|GLD|15m': 'stochrsi_enhanced_gld.md',
  'StochRSIMeanReversionStrategy|SLV|15m': 'stochrsi_enhanced_slv.md',
  'StochRSIMeanReversionStrategy|GDX|15m': 'stochrsi_enhanced_gdx.md',
  'EventSurprise|GLD|15m': 'event_surprise.md',
  'ComposableStrategy|GLD|1h': 'composable_results.md',
}

export function getMarkdownFile(strategy: string, symbol: string, timeframe: string): string | null {
  return (
    MARKDOWN_MAP[`${strategy}|${symbol}|${timeframe}`] ??
    MARKDOWN_MAP[strategy] ??
    null
  )
}

// Status badge derived from Sharpe
export type StrategyStatus = 'validated' | 'promising' | 'researched'

export function getStatus(sharpe: number): StrategyStatus {
  if (sharpe >= 1.3) return 'validated'
  if (sharpe >= 0.8) return 'promising'
  return 'researched'
}
