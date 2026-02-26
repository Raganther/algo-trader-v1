import Link from 'next/link'
import type { ValidatedStrategy } from '@/lib/db'
import { getStatus } from '@/lib/registry'

const STATUS_STYLES = {
  validated: 'bg-green-900/30 text-green-400 border-green-800/50',
  promising: 'bg-amber-900/30 text-amber-400 border-amber-800/50',
  researched: 'bg-gray-900/30 text-gray-400 border-gray-800/50',
}

interface Props {
  strategy: ValidatedStrategy
}

export default function StrategyCard({ strategy }: Props) {
  const status = getStatus(strategy.sharpe)

  return (
    <Link href={`/strategy/${strategy.slug}`}>
      <div className="bg-[#111] border border-gray-800 rounded-xl p-6 hover:border-gray-600 transition-colors cursor-pointer group h-full">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-2">
            <span className="bg-blue-900/30 text-blue-300 px-2 py-0.5 rounded text-xs font-bold border border-blue-800/50">
              {strategy.symbol}
            </span>
            <span className="bg-gray-900 text-gray-400 px-2 py-0.5 rounded text-xs font-mono border border-gray-700">
              {strategy.timeframe}
            </span>
          </div>
          <span className={`px-2 py-0.5 rounded text-xs font-bold border uppercase ${STATUS_STYLES[status]}`}>
            {status}
          </span>
        </div>

        <h3 className="text-base font-bold text-white mb-4 group-hover:text-blue-300 transition-colors">
          {strategy.strategy.replace(/Strategy$/, '')}
        </h3>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <p className="text-xs text-gray-600 uppercase font-bold mb-1">Sharpe</p>
            <p className="text-xl font-bold text-purple-400">{strategy.sharpe.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-600 uppercase font-bold mb-1">Ann. Return</p>
            <p className={`text-xl font-bold ${strategy.annualised_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {strategy.annualised_return >= 0 ? '+' : ''}{strategy.annualised_return.toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600 uppercase font-bold mb-1">Max DD</p>
            <p className="text-xl font-bold text-red-400">{strategy.max_drawdown.toFixed(1)}%</p>
          </div>
        </div>
      </div>
    </Link>
  )
}
