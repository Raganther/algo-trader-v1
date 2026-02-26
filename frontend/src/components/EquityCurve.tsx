'use client'

import { useMemo } from 'react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { EquityPoint } from '@/lib/db'

interface Props {
  data: EquityPoint[]
}

export default function EquityCurve({ data }: Props) {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return []
    return data.map((p) => {
      const date = new Date(p.time * 1000)
      return {
        time: date.toLocaleDateString('en-GB', { year: 'numeric', month: 'short' }),
        timestamp: date.getTime(),
        equity: Math.round(p.equity),
      }
    })
  }, [data])

  if (chartData.length === 0) return null

  return (
    <div className="bg-[#111] border border-gray-800 rounded-xl p-6">
      <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-5">Equity Curve</h3>
      <div className="h-[320px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
            <XAxis
              dataKey="time"
              stroke="#555"
              minTickGap={80}
              tick={{ fontSize: 11, fill: '#666' }}
            />
            <YAxis
              stroke="#555"
              domain={['auto', 'auto']}
              tick={{ fontSize: 11, fill: '#666' }}
              tickFormatter={(val) => `$${val.toLocaleString()}`}
              width={70}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
              formatter={(value: number) => [`$${value.toLocaleString()}`, 'Equity']}
              labelFormatter={(label) => label}
            />
            <Area
              type="monotone"
              dataKey="equity"
              stroke="#8b5cf6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorEquity)"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
