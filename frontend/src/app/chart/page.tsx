import { getPriceData } from '@/lib/db'
import PriceChart from '@/components/PriceChart'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

const SYMBOLS = ['GLD', 'IAU', 'SLV', 'GDX']

// Default: last 6 months
function defaultStartTs(): number {
  const d = new Date()
  d.setMonth(d.getMonth() - 6)
  return Math.floor(d.getTime() / 1000)
}

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

  const rangeOptions = [1, 3, 6, 12, 24, 60]

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <Link href="/" className="text-gray-600 text-sm hover:text-gray-400 transition-colors">
            ← Strategy Lab
          </Link>
          <h1 className="text-3xl font-bold text-white tracking-tight mt-2">Price Action</h1>
          <p className="text-gray-500 mt-1">15m candlestick chart — {data.length} bars loaded</p>
        </div>
      </header>

      {/* Symbol selector */}
      <div className="flex gap-2 mb-4">
        {SYMBOLS.map((s) => (
          <Link
            key={s}
            href={`/chart?symbol=${s}&months=${months}`}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              s === symbol
                ? 'bg-violet-600 text-white'
                : 'bg-[#1a1a1a] text-gray-400 hover:text-white border border-gray-800'
            }`}
          >
            {s}
          </Link>
        ))}
      </div>

      {/* Time range selector */}
      <div className="flex gap-2 mb-6">
        {rangeOptions.map((m) => (
          <Link
            key={m}
            href={`/chart?symbol=${symbol}&months=${m}`}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              m === months
                ? 'bg-[#333] text-white'
                : 'text-gray-600 hover:text-gray-400'
            }`}
          >
            {m >= 12 ? `${m / 12}Y` : `${m}M`}
          </Link>
        ))}
      </div>

      <PriceChart data={data} symbol={symbol} />
    </div>
  )
}
