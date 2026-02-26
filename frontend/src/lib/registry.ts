// Markdown file mapping: experiments.strategy → .md filename
// Add an entry here when you write research notes for a strategy.
// If no entry exists, the detail page just shows DB stats with no notes.
export const MARKDOWN_MAP: Record<string, string> = {
  StochRSIMeanReversionStrategy: 'stochrsi_enhanced_gld.md',
  StochRSIMeanReversion: 'stochrsi_enhanced_gld.md',
  EventSurprise: 'event_surprise.md',
  ComposableStrategy: 'composable_results.md',
}

// Status badge derived from Sharpe
export type StrategyStatus = 'validated' | 'promising' | 'researched'

export function getStatus(sharpe: number): StrategyStatus {
  if (sharpe >= 1.3) return 'validated'
  if (sharpe >= 0.8) return 'promising'
  return 'researched'
}
