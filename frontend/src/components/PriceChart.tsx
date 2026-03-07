'use client'

import { useEffect, useRef } from 'react'
import { createChart, ColorType, CandlestickData, UTCTimestamp } from 'lightweight-charts'
import type { OHLCBar } from '@/lib/db'

interface Props {
  data: OHLCBar[]
  symbol: string
}

export default function PriceChart({ data, symbol }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#111111' },
        textColor: '#888888',
      },
      grid: {
        vertLines: { color: '#1a1a1a' },
        horzLines: { color: '#1a1a1a' },
      },
      crosshair: {
        vertLine: { color: '#444', labelBackgroundColor: '#222' },
        horzLine: { color: '#444', labelBackgroundColor: '#222' },
      },
      timeScale: {
        borderColor: '#222',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: '#222',
      },
      width: containerRef.current.clientWidth,
      height: 500,
    })

    const candleSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    const seriesData: CandlestickData[] = data.map((b) => ({
      time: b.time as UTCTimestamp,
      open: b.open,
      high: b.high,
      low: b.low,
      close: b.close,
    }))

    candleSeries.setData(seriesData)
    chart.timeScale().fitContent()

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth })
      }
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [data])

  if (data.length === 0) {
    return (
      <div className="bg-[#111] border border-gray-800 rounded-xl p-6 flex items-center justify-center h-[500px]">
        <p className="text-gray-600 text-sm">No price data for {symbol}. Run <code className="text-gray-400">python scripts/fetch_price_data.py</code> first.</p>
      </div>
    )
  }

  return (
    <div className="bg-[#111] border border-gray-800 rounded-xl p-4">
      <div ref={containerRef} />
    </div>
  )
}
