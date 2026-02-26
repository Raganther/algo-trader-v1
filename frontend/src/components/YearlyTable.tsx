import type { YearlyRun } from '@/lib/db'

interface Props {
  runs: YearlyRun[]
}

export default function YearlyTable({ runs }: Props) {
  if (runs.length === 0) return null

  return (
    <div className="bg-[#111] border border-gray-800 rounded-xl overflow-hidden">
      <div className="p-5 border-b border-gray-800">
        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Year-by-Year Performance</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-gray-900/50 text-gray-500 text-xs uppercase tracking-wider">
              <th className="py-3 px-5 text-left font-medium">Year</th>
              <th className="py-3 px-5 text-right font-medium">Return</th>
              <th className="py-3 px-5 text-right font-medium">Max DD</th>
              <th className="py-3 px-5 text-right font-medium">Win Rate</th>
              <th className="py-3 px-5 text-right font-medium">Trades</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run, idx) => (
              <tr
                key={run.test_id}
                className={`border-t border-gray-800/50 ${idx % 2 === 0 ? '' : 'bg-white/[0.02]'}`}
              >
                <td className="py-3 px-5 font-medium text-gray-300">{run.year}</td>
                <td
                  className="py-3 px-5 text-right font-mono font-bold"
                  style={{ color: run.return_pct >= 0 ? '#4ade80' : '#f87171' }}
                >
                  {run.return_pct >= 0 ? '+' : ''}
                  {run.return_pct.toFixed(2)}%
                </td>
                <td className="py-3 px-5 text-right text-red-400/70">{run.max_drawdown.toFixed(2)}%</td>
                <td className="py-3 px-5 text-right text-gray-400">{run.win_rate.toFixed(0)}%</td>
                <td className="py-3 px-5 text-right text-gray-500">{run.total_trades}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
