import { notFound } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { getValidatedStrategies, getStrategyStats, getYearlyRuns, getEquityCurve } from '@/lib/db'
import { getMarkdownFile, getStatus } from '@/lib/registry'
import { readStrategyMarkdown } from '@/lib/markdown'
import StatsPanel from '@/components/StatsPanel'
import YearlyTable from '@/components/YearlyTable'
import EquityCurve from '@/components/EquityCurve'
import DrawdownChart from '@/components/DrawdownChart'
import ResearchNotes from '@/components/ResearchNotes'

export const dynamic = 'force-dynamic'

const STATUS_STYLES = {
  validated: 'bg-green-900/20 text-green-400 border-green-800/40',
  promising: 'bg-amber-900/20 text-amber-400 border-amber-800/40',
  researched: 'bg-gray-900/20 text-gray-400 border-gray-800/40',
}

interface Props {
  params: Promise<{ slug: string }>
}

export default async function StrategyDetailPage({ params }: Props) {
  const { slug } = await params

  const all = getValidatedStrategies(0)
  const strategy = all.find((s) => s.slug === slug)
  if (!strategy) notFound()

  const status = getStatus(strategy.sharpe)
  const markdownFile = getMarkdownFile(strategy.strategy, strategy.symbol, strategy.timeframe)

  const stats = getStrategyStats(strategy.strategy, strategy.symbol, strategy.timeframe)
  const yearlyRuns = getYearlyRuns(strategy.strategy, strategy.symbol, strategy.timeframe)
  const equityCurve = getEquityCurve(strategy.strategy, strategy.symbol, strategy.timeframe)
  const markdown = markdownFile ? readStrategyMarkdown(markdownFile) : null

  return (
    <div className="px-8 py-8 max-w-5xl">
      <Link href="/" className="inline-flex items-center gap-1.5 text-gray-600 hover:text-gray-300 text-sm mb-6 transition-colors">
        <ArrowLeft size={14} /> Strategy Lab
      </Link>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-2xl font-bold text-white tracking-tight">
            {strategy.strategy.replace(/Strategy$/, '')}
          </h1>
          <span className={`px-2 py-0.5 rounded text-xs font-semibold border uppercase ${STATUS_STYLES[status]}`}>
            {status}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="bg-blue-900/20 text-blue-300 px-2 py-0.5 rounded text-xs font-bold border border-blue-800/40">
            {strategy.symbol}
          </span>
          <span className="bg-white/5 text-gray-400 px-2 py-0.5 rounded text-xs font-mono border border-white/10">
            {strategy.timeframe}
          </span>
          <span className="text-gray-600 text-xs">
            Sharpe {strategy.sharpe.toFixed(2)} · {strategy.trades_per_year.toFixed(0)} trades/yr
          </span>
        </div>
      </div>

      <div className="space-y-5">
        {stats && <StatsPanel sharpe={strategy.sharpe} stats={stats} />}
        {yearlyRuns.length > 0 && <YearlyTable runs={yearlyRuns} />}
        {equityCurve.length > 0 && <EquityCurve data={equityCurve} />}
        {equityCurve.length > 0 && <DrawdownChart data={equityCurve} />}
        {markdown && <ResearchNotes content={markdown} />}
      </div>
    </div>
  )
}
