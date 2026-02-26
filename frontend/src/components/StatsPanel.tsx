import type { StrategyStats } from '@/lib/db'

interface Props {
  sharpe: number
  stats: StrategyStats
}

export default function StatsPanel({ sharpe, stats }: Props) {
  const tradesPerYear = stats.years_count > 0 ? stats.total_trades / stats.years_count : 0

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div className="bg-[#111] border border-gray-800 rounded-xl p-5">
        <p className="text-xs text-gray-500 uppercase font-bold mb-2">Sharpe</p>
        <p className="text-3xl font-bold text-purple-400">{sharpe.toFixed(2)}</p>
      </div>
      <div className="bg-[#111] border border-gray-800 rounded-xl p-5">
        <p className="text-xs text-gray-500 uppercase font-bold mb-2">Total Return</p>
        <p className={`text-3xl font-bold ${stats.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {stats.total_return >= 0 ? '+' : ''}{stats.total_return.toFixed(1)}%
        </p>
        <p className="text-xs text-gray-600 mt-1">over {stats.years_count} yrs</p>
      </div>
      <div className="bg-[#111] border border-gray-800 rounded-xl p-5">
        <p className="text-xs text-gray-500 uppercase font-bold mb-2">Max Drawdown</p>
        <p className="text-3xl font-bold text-red-400">{stats.max_drawdown.toFixed(2)}%</p>
      </div>
      <div className="bg-[#111] border border-gray-800 rounded-xl p-5">
        <p className="text-xs text-gray-500 uppercase font-bold mb-2">Trades / Year</p>
        <p className="text-3xl font-bold text-blue-400">{tradesPerYear.toFixed(0)}</p>
        <p className="text-xs text-gray-600 mt-1">{stats.total_trades} total</p>
      </div>
      <div className="bg-[#111] border border-gray-800 rounded-xl p-5">
        <p className="text-xs text-gray-500 uppercase font-bold mb-2">Win Rate</p>
        <p className="text-3xl font-bold text-blue-300">{stats.win_rate.toFixed(1)}%</p>
      </div>
    </div>
  )
}
