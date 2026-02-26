'use client'

import { useMemo } from 'react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { EquityPoint } from '@/lib/db'

interface Props {
  data: EquityPoint[]
}

export default function DrawdownChart({ data }: Props) {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return []
    let peak = -Infinity
    return data.map((p) => {
      if (p.equity > peak) peak = p.equity
      const drawdown = peak > 0 ? (p.equity - peak) / peak : 0
      const date = new Date(p.time * 1000)
      return {
        time: date.toLocaleDateString('en-GB', { year: 'numeric', month: 'short' }),
        drawdown,
      }
    })
  }, [data])

  if (chartData.length === 0) return null

  return (
    <div className="bg-[#111] border border-gray-800 rounded-xl p-6">
      <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-5">Drawdown (Underwater)</h3>
      <div className="h-[200px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
            <XAxis
              dataKey="time"
              stroke="#555"
              minTickGap={80}
              tick={{ fontSize: 11, fill: '#666' }}
            />
            <YAxis
              stroke="#555"
              tick={{ fontSize: 11, fill: '#666' }}
              tickFormatter={(val) => `${(val * 100).toFixed(0)}%`}
              width={50}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
              formatter={(value: number) => [`${(value * 100).toFixed(2)}%`, 'Drawdown']}
              labelFormatter={(label) => label}
            />
            <Area
              type="step"
              dataKey="drawdown"
              stroke="#ef4444"
              fill="#ef4444"
              fillOpacity={0.25}
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
