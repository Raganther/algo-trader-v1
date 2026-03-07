import { getPriceData } from '@/lib/db'
import PriceChart from '@/components/PriceChart'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

const SYMBOLS = ['GLD', 'IAU', 'SLV', 'GDX']
const RANGE_OPTIONS = [1, 3, 6, 12, 24, 60]

interface Props {
  searchParams: Promise<{ symbol?: string; months?: string }>
}

export default async function ChartPage({ searchParams }: Props) {
  const params = await searchParams
  const symbol = SYMBOLS.includes(params.symbol ?? '') ? (params.symbol as string) : 'GLD'
  const months = parseInt(params.months ?? '6', 10)

  const startTs = (() => {
    const d = new Date()
    d.setMonth(d.getMonth() - months)
    return Math.floor(d.getTime() / 1000)
  })()

  const data = getPriceData(symbol, startTs)

  return (
    <div className="px-8 py-8 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white tracking-tight">Price Action</h1>
        <p className="text-gray-500 mt-1 text-sm">
          15m candlestick — {data.length.toLocaleString()} bars
        </p>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-6 mb-5">
        {/* Symbol selector */}
        <div className="flex gap-1.5">
          {SYMBOLS.map((s) => (
            <Link
              key={s}
              href={`/chart?symbol=${s}&months=${months}`}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                s === symbol
                  ? 'bg-violet-600 text-white'
                  : 'bg-white/5 text-gray-400 hover:text-white border border-white/10'
              }`}
            >
              {s}
            </Link>
          ))}
        </div>

        <div className="w-px h-5 bg-white/10" />

        {/* Time range */}
        <div className="flex gap-1">
          {RANGE_OPTIONS.map((m) => (
            <Link
              key={m}
              href={`/chart?symbol=${symbol}&months=${m}`}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                m === months
                  ? 'bg-white/10 text-white'
                  : 'text-gray-600 hover:text-gray-300'
              }`}
            >
              {m >= 12 ? `${m / 12}Y` : `${m}M`}
            </Link>
          ))}
        </div>
      </div>

      <PriceChart data={data} symbol={symbol} />
    </div>
  )
}
