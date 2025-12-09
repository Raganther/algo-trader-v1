'use client';

import { useEffect, useState, Suspense, useMemo } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { ArrowLeft, TrendingUp, TrendingDown, Activity, Calendar } from 'lucide-react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, LineChart, Line } from 'recharts';
import { fetchTestDetails, TestRun } from '@/lib/api';

interface DetailedTestRun extends TestRun {
    equity_curve: { time: number | string; equity: number }[];
}

function DetailsContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const testId = searchParams.get('id');

    const [data, setData] = useState<DetailedTestRun | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!testId) return;

        async function load() {
            try {
                const res = await fetchTestDetails(testId!);
                setData(res);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load data');
            } finally {
                setLoading(false);
            }
        }
        load();
    }, [testId]);

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

            return {
                time: dateStr,
                timestamp: date.getTime(),
                equity,
                drawdown
            };
        });
    }, [data]);

    if (loading) return <div className="min-h-screen bg-[#0a0a0a] text-white p-8 flex items-center justify-center">Loading Analysis...</div>;
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
                        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                            {data.symbol} Analysis
                        </h1>
                        <p className="text-gray-400 mt-1 flex items-center gap-2">
                            <span className="bg-gray-800 px-2 py-0.5 rounded text-sm">{data.strategy}</span>
                            <span className="bg-gray-800 px-2 py-0.5 rounded text-sm">{data.timeframe}</span>
                            <span className="text-sm flex items-center gap-1"><Calendar size={14} /> {data.start_date} - {data.end_date}</span>
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
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-bold">Win Rate</p>
                            <p className="text-3xl font-bold text-blue-400">
                                {(data.win_rate > 1 ? data.win_rate : data.win_rate * 100).toFixed(1)}%
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Equity Curve */}
                <div className="bg-[#111] border border-gray-800 rounded-xl p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <TrendingUp size={20} className="text-blue-400" />
                        Equity Curve
                    </h3>
                    <div className="h-[350px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                <XAxis
                                    dataKey="time"
                                    stroke="#666"
                                    minTickGap={50}
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
                                />
                                <Area
                                    type="monotone"
                                    dataKey="equity"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorEquity)"
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
                    <div className="h-[350px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                <XAxis
                                    dataKey="time"
                                    stroke="#666"
                                    minTickGap={50}
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

            {/* Parameters & Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Parameters */}
                <div className="bg-[#111] border border-gray-800 rounded-xl overflow-hidden">
                    <div className="p-6 border-b border-gray-800">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <Activity size={20} className="text-purple-400" />
                            Strategy Parameters
                        </h3>
                    </div>
                    <div className="p-6">
                        <div className="grid grid-cols-2 gap-4">
                            {Object.entries(data.parameters || {}).map(([key, value]) => (
                                <div key={key} className="bg-gray-900/50 p-3 rounded border border-gray-800">
                                    <p className="text-xs text-gray-500 uppercase mb-1">{key.replace(/_/g, ' ')}</p>
                                    <p className="text-sm font-mono text-gray-300 truncate" title={String(value)}>
                                        {String(value)}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Trade Stats */}
                <div className="lg:col-span-2 bg-[#111] border border-gray-800 rounded-xl overflow-hidden">
                    <div className="p-6 border-b border-gray-800">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <Activity size={20} className="text-green-400" />
                            Performance Metrics
                        </h3>
                    </div>
                    <div className="p-6 grid grid-cols-2 lg:grid-cols-4 gap-6">
                        <div>
                            <p className="text-sm text-gray-500">Total Trades</p>
                            <p className="text-2xl font-bold text-white">{data.total_trades}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Avg Return / Year</p>
                            <p className="text-2xl font-bold text-white">
                                {(data.return_pct / (chartData.length / 252)).toFixed(2)}%
                                <span className="text-xs text-gray-600 ml-1">(Est)</span>
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Profit Factor</p>
                            <p className="text-2xl font-bold text-white">--</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Sharpe Ratio</p>
                            <p className="text-2xl font-bold text-white">--</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function DetailsPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-[#0a0a0a] text-white p-8">Loading...</div>}>
            <DetailsContent />
        </Suspense>
    );
}
