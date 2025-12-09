'use client';

import { useEffect, useState, Suspense, useMemo } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { ArrowLeft, TrendingUp, TrendingDown, Activity, Calendar, Layers } from 'lucide-react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { fetchCompositeDetails, TestRun } from '@/lib/api';

interface CompositeRun extends TestRun {
    equity_curve: { time: number | string; equity: number }[];
}

function OverviewContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const strategy = searchParams.get('strategy');
    const symbol = searchParams.get('symbol');
    const timeframe = searchParams.get('timeframe') || '1h';

    const [data, setData] = useState<CompositeRun | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!strategy || !symbol) return;

        async function load() {
            try {
                const res = await fetchCompositeDetails(strategy!, symbol!, timeframe);
                setData(res);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load data');
            } finally {
                setLoading(false);
            }
        }
        load();
    }, [strategy, symbol, timeframe]);

    // Process Data for Charts
    const chartData = useMemo(() => {
        if (!data?.equity_curve) return [];

        let peak = -Infinity;
        return data.equity_curve.map((point) => {
            const equity = point.equity;
            if (equity > peak) peak = equity;
            const drawdown = peak > 0 ? (equity - peak) / peak : 0;

            // Format time
            const date = new Date(typeof point.time === 'number' ? point.time * 1000 : point.time);
            const dateStr = date.toLocaleDateString();
            const year = date.getFullYear();

            return {
                time: dateStr,
                year: year,
                timestamp: date.getTime(),
                equity,
                drawdown
            };
        });
    }, [data]);

    if (loading) return <div className="min-h-screen bg-[#0a0a0a] text-white p-8 flex items-center justify-center">Loading Composite Analysis...</div>;
    if (error) return <div className="min-h-screen bg-[#0a0a0a] text-white p-8 flex items-center justify-center text-red-500">{error}</div>;
    if (!data) return <div className="min-h-screen bg-[#0a0a0a] text-white p-8">No Data Found</div>;

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
            {/* Header */}
            <div className="mb-8">
                <button
                    onClick={() => router.back()}
                    className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
                >
                    <ArrowLeft size={20} /> Back to Lab
                </button>
                <div className="flex justify-between items-end">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-500">
                                {symbol} Master Overview
                            </h1>
                            <span className="bg-purple-900/50 text-purple-300 px-3 py-1 rounded-full text-xs font-bold border border-purple-700/50 flex items-center gap-1">
                                <Layers size={12} /> COMPOSITE VIEW
                            </span>
                        </div>
                        <p className="text-gray-400 mt-1 flex items-center gap-2">
                            <span className="bg-gray-800 px-2 py-0.5 rounded text-sm">{data.strategy}</span>
                            <span className="bg-gray-800 px-2 py-0.5 rounded text-sm">{data.timeframe}</span>
                            <span className="text-sm flex items-center gap-1"><Calendar size={14} /> Full History (2002 - 2024)</span>
                        </p>
                    </div>
                    <div className="flex gap-8 text-right">
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-bold">Total Return</p>
                            <p className={`text-3xl font-bold ${data.return_pct > 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {data.return_pct > 0 ? '+' : ''}{data.return_pct.toFixed(2)}%
                            </p>
                        </div>
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-bold">Max Drawdown</p>
                            <p className="text-3xl font-bold text-red-400">
                                {data.max_drawdown.toFixed(2)}%
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 gap-8 mb-8">
                {/* Equity Curve */}
                <div className="bg-[#111] border border-gray-800 rounded-xl p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <TrendingUp size={20} className="text-purple-400" />
                        Master Equity Curve (22 Years)
                    </h3>
                    <div className="h-[400px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="colorEquityComposite" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                <XAxis
                                    dataKey="time"
                                    stroke="#666"
                                    minTickGap={100}
                                    tickFormatter={(str) => str.split('/')[2]} // Show Year only
                                    tick={{ fontSize: 12 }}
                                />
                                <YAxis
                                    stroke="#666"
                                    domain={['auto', 'auto']}
                                    tick={{ fontSize: 12 }}
                                    tickFormatter={(val) => `$${val.toLocaleString()}`}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }}
                                    formatter={(value: number) => [`$${value.toLocaleString()}`, 'Equity']}
                                    labelFormatter={(label) => `Date: ${label}`}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="equity"
                                    stroke="#8b5cf6"
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorEquityComposite)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Drawdown Underwater Chart */}
                <div className="bg-[#111] border border-gray-800 rounded-xl p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <TrendingDown size={20} className="text-red-400" />
                        Drawdown (Underwater)
                    </h3>
                    <div className="h-[200px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                <XAxis
                                    dataKey="time"
                                    stroke="#666"
                                    minTickGap={100}
                                    tickFormatter={(str) => str.split('/')[2]}
                                    tick={{ fontSize: 12 }}
                                />
                                <YAxis
                                    stroke="#666"
                                    tickFormatter={(val) => `${(val * 100).toFixed(0)}%`}
                                    tick={{ fontSize: 12 }}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }}
                                    formatter={(value: number) => [`${(value * 100).toFixed(2)}%`, 'Drawdown']}
                                />
                                <Area
                                    type="step"
                                    dataKey="drawdown"
                                    stroke="#ef4444"
                                    fill="#ef4444"
                                    fillOpacity={0.3}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function StrategyOverviewPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-[#0a0a0a] text-white p-8">Loading...</div>}>
            <OverviewContent />
        </Suspense>
    );
}
