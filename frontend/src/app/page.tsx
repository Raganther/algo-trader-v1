'use client';

import { useEffect, useState } from 'react';
import { fetchRuns, fetchEdges, TestRun } from '@/lib/api';
import { ArrowUpRight, ArrowDownRight, Filter, Search, Trophy, TrendingUp, Activity, Layers } from 'lucide-react';
import { useRouter } from 'next/navigation';


export default function Dashboard() {
    const [runs, setRuns] = useState<TestRun[]>([]);
    const [edges, setEdges] = useState<any[]>([]);
    const [filteredRuns, setFilteredRuns] = useState<TestRun[]>([]);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState<'matrix' | 'edges'>('matrix');
    const router = useRouter();


    // Filters
    const [selectedStrategy, setSelectedStrategy] = useState('All');
    const [selectedSymbol, setSelectedSymbol] = useState('All');
    const [selectedTimeframe, setSelectedTimeframe] = useState('All');
    const [selectedYear, setSelectedYear] = useState('All');

    // Sorting
    const [sortByReturn, setSortByReturn] = useState(false);

    useEffect(() => {
        async function load() {
            try {
                const [runsData, edgesData] = await Promise.all([fetchRuns(), fetchEdges()]);
                setRuns(runsData);
                setFilteredRuns(runsData);
                setEdges(edgesData);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    useEffect(() => {
        let res = [...runs]; // Create a copy to sort
        if (selectedStrategy !== 'All') res = res.filter(r => r.strategy === selectedStrategy);
        if (selectedSymbol !== 'All') res = res.filter(r => r.symbol === selectedSymbol);
        if (selectedTimeframe !== 'All') res = res.filter(r => r.timeframe === selectedTimeframe);
        if (selectedYear !== 'All') res = res.filter(r => r.start_date.startsWith(selectedYear));

        if (sortByReturn) {
            res.sort((a, b) => b.return_pct - a.return_pct);
        } else {
            // Default sequential sort (by year/date)
            res.sort((a, b) => a.start_date.localeCompare(b.start_date));
        }

        setFilteredRuns(res);
    }, [selectedStrategy, selectedSymbol, selectedTimeframe, selectedYear, sortByReturn, runs]);

    // Unique Options
    const strategies = ['All', ...Array.from(new Set(runs.map(r => r.strategy)))];
    const symbols = ['All', ...Array.from(new Set(runs.map(r => r.symbol)))];
    const timeframes = ['All', ...Array.from(new Set(runs.map(r => r.timeframe)))];
    const years = ['All', ...Array.from(new Set(runs.map(r => r.start_date.split('-')[0]))).sort()];

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
            <header className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                        Strategy Lab
                    </h1>
                    <p className="text-gray-400 mt-1">AI Research Engine • Verified Results</p>
                </div>
                <div className="flex gap-4 items-center">
                    <button
                        onClick={() => setViewMode(viewMode === 'matrix' ? 'edges' : 'matrix')}
                        className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors flex items-center gap-2 ${viewMode === 'edges'
                            ? 'bg-purple-600 border-purple-500 text-white'
                            : 'bg-gray-900 border-gray-800 text-gray-400 hover:bg-gray-800'
                            }`}
                    >
                        <Trophy size={16} />
                        {viewMode === 'edges' ? 'View Matrix' : 'View Edges'}
                    </button>

                    {viewMode === 'matrix' && (
                        <button
                            onClick={() => setSortByReturn(!sortByReturn)}
                            className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${sortByReturn
                                ? 'bg-blue-600 border-blue-500 text-white'
                                : 'bg-gray-900 border-gray-800 text-gray-400 hover:bg-gray-800'
                                }`}
                        >
                            {sortByReturn ? 'Sorted: Highest Return' : 'Sort: Sequential'}
                        </button>
                    )}

                    <div className="bg-gray-900 px-4 py-2 rounded-lg border border-gray-800 text-sm">
                        {runs.length} Total Runs
                    </div>
                </div>
            </header>

            {viewMode === 'edges' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {edges.map((edge, i) => {
                        return (
                            <div
                                key={i}
                                onClick={() => router.push(`/strategy/overview?strategy=${edge.strategy}&symbol=${encodeURIComponent(edge.symbol)}&timeframe=${edge.timeframe || '1h'}`)}
                                className="bg-[#111] border border-gray-800 rounded-xl p-6 hover:border-purple-500/50 transition-colors group relative overflow-hidden cursor-pointer"
                            >
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                    <Trophy size={64} className="text-purple-500" />
                                </div>

                                <div
                                    className="flex justify-between items-start mb-4 cursor-pointer hover:opacity-80 transition-opacity"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        router.push(`/strategy/overview?strategy=${edge.strategy}&symbol=${encodeURIComponent(edge.symbol)}&timeframe=${edge.timeframe || '1h'}`);
                                    }}
                                >
                                    <div>
                                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                            {edge.symbol}
                                            <Layers size={16} className="text-purple-400" />
                                        </h3>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className="bg-blue-900/30 text-blue-300 px-2 py-0.5 rounded text-xs font-bold border border-blue-800/50">
                                                {edge.timeframe || '1h'}
                                            </span>
                                            <p className="text-sm text-gray-400">{edge.strategy}</p>
                                        </div>
                                    </div>
                                    <div className="bg-green-900/30 text-green-400 px-3 py-1 rounded-full text-xs font-bold border border-green-800/50">
                                        VERIFIED EDGE
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div>
                                        <p className="text-xs text-gray-500 uppercase font-bold">Avg Annual Return</p>
                                        <p className="text-2xl font-bold text-green-400">+{edge.avg_annual_return?.toFixed(2)}%</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-gray-500 uppercase font-bold">Win Rate</p>
                                        <p className="text-2xl font-bold text-blue-400">{(edge.avg_win_rate > 1 ? edge.avg_win_rate : edge.avg_win_rate * 100)?.toFixed(1)}%</p>
                                    </div>
                                </div>

                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-500">Consistency</span>
                                        <span className="text-gray-300">{edge.profitable_years} / {edge.years_tested} Years Profitable</span>
                                    </div>
                                    <div className="w-full bg-gray-800 rounded-full h-2">
                                        <div
                                            className="bg-purple-500 h-2 rounded-full"
                                            style={{ width: `${(edge.profitable_years / edge.years_tested) * 100}%` }}
                                        ></div>
                                    </div>
                                </div>

                                {/* Yearly Breakdown */}
                                <div className="mt-6 border-t border-gray-800 pt-4">
                                    <h4 className="text-xs font-bold text-gray-500 uppercase mb-3">Yearly Performance</h4>
                                    <div className="overflow-hidden rounded-lg border border-gray-800/30 bg-black/20">
                                        <table className="w-full text-xs border-collapse">
                                            <thead>
                                                <tr className="bg-purple-900/10 text-purple-200/70">
                                                    <th className="py-3 px-4 text-left font-medium tracking-wider">YEAR</th>
                                                    <th className="py-3 px-4 text-right font-medium tracking-wider">RETURN</th>
                                                    <th className="py-3 px-4 text-right font-medium tracking-wider">DD</th>
                                                    <th className="py-3 px-4 text-right font-medium tracking-wider">WR</th>
                                                </tr>
                                            </thead>
                                            <tbody className="text-gray-400">
                                                {runs
                                                    .filter(r => r.strategy === edge.strategy && r.symbol === edge.symbol && r.timeframe === (edge.timeframe || '1h'))
                                                    .sort((a, b) => b.start_date.localeCompare(a.start_date))
                                                    .map((run, idx) => (
                                                        <tr
                                                            key={run.test_id}
                                                            className={`
                                                                cursor-pointer transition-colors group border-none
                                                                ${idx % 2 === 0 ? 'bg-transparent' : 'bg-white/[0.02]'}
                                                                hover:bg-white/[0.05]
                                                            `}
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                router.push(`/details?id=${encodeURIComponent(run.test_id)}`);
                                                            }}
                                                        >
                                                            <td className="py-3 px-4 font-medium group-hover:text-white transition-colors">{run.start_date.split('-')[0]}</td>
                                                            <td
                                                                className="py-3 px-4 text-right font-mono font-bold"
                                                                style={{
                                                                    color: run.return_pct > 0 ? '#4ade80' : '#f87171'
                                                                }}
                                                            >
                                                                {run.return_pct > 0 ? '+' : ''}{run.return_pct.toFixed(1)}%
                                                            </td>
                                                            <td className="py-3 px-4 text-right text-red-400/60 group-hover:text-red-400 transition-colors">{run.max_drawdown.toFixed(1)}%</td>
                                                            <td className="py-3 px-4 text-right text-gray-500 group-hover:text-gray-300 transition-colors">{(run.win_rate > 1 ? run.win_rate : run.win_rate * 100).toFixed(0)}%</td>
                                                        </tr>
                                                    ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            ) : (
                <>
                    {/* Filters */}
                    <div className="grid grid-cols-4 gap-4 mb-8">
                        <FilterSelect label="Strategy" value={selectedStrategy} onChange={setSelectedStrategy} options={strategies} />
                        <FilterSelect label="Symbol" value={selectedSymbol} onChange={setSelectedSymbol} options={symbols} />
                        <FilterSelect label="Timeframe" value={selectedTimeframe} onChange={setSelectedTimeframe} options={timeframes} />
                        <FilterSelect label="Year" value={selectedYear} onChange={setSelectedYear} options={years} />
                    </div>

                    {/* Matrix Table */}
                    <div className="bg-[#111] rounded-xl border border-gray-800 overflow-hidden shadow-2xl">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-900/50 text-gray-400 text-sm uppercase tracking-wider">
                                    <th className="p-4 font-medium">Strategy</th>
                                    <th className="p-4 font-medium">Symbol</th>
                                    <th className="p-4 font-medium">TF</th>
                                    <th className="p-4 font-medium">Year</th>
                                    <th className="p-4 font-medium text-right">Return</th>
                                    <th className="p-4 font-medium text-right">Drawdown</th>
                                    <th className="p-4 font-medium text-right">Trades</th>
                                    <th className="p-4 font-medium text-right">Win Rate</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-800">
                                {loading ? (
                                    <tr><td colSpan={8} className="p-8 text-center text-gray-500">Loading Matrix...</td></tr>
                                ) : filteredRuns.map((run) => (
                                    <tr
                                        key={run.test_id}
                                        onClick={() => router.push(`/details?id=${run.test_id}`)}
                                        className="hover:bg-gray-800/50 transition-colors cursor-pointer group"
                                    >
                                        <td className="p-4 text-gray-300 font-medium">{run.strategy}</td>
                                        <td className="p-4 text-blue-400 font-mono">{run.symbol}</td>
                                        <td className="p-4 text-purple-400 font-mono">{run.timeframe}</td>
                                        <td className="p-4 text-gray-400">
                                            {(() => {
                                                const startYear = run.start_date.split('-')[0];
                                                const endYear = run.end_date?.split('-')[0];
                                                return startYear === endYear || !endYear ? startYear : `${startYear}-${endYear}`;
                                            })()}
                                        </td>
                                        <td
                                            className="p-4 text-right font-bold"
                                            style={{
                                                color: run.return_pct > 10 ? '#4ade80' : // green-400
                                                    run.return_pct >= 0 ? '#fb923c' : // orange-400
                                                        '#f87171'                         // red-400
                                            }}
                                        >
                                            {run.return_pct.toFixed(2)}%
                                        </td>
                                        <td className="p-4 text-right text-red-300">{run.max_drawdown.toFixed(2)}%</td>
                                        <td className="p-4 text-right text-gray-400">{run.total_trades}</td>
                                        <td className="p-4 text-right text-gray-400">{(run.win_rate * 100).toFixed(1)}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}
        </div>
    );
}

function FilterSelect({ label, value, onChange, options }: any) {
    return (
        <div className="flex flex-col gap-1">
            <label className="text-xs text-gray-500 uppercase font-bold tracking-wider">{label}</label>
            <select
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="bg-[#111] border border-gray-800 rounded-lg p-2 text-sm text-gray-300 focus:border-blue-500 focus:outline-none transition-colors"
            >
                {options.map((opt: string) => (
                    <option key={opt} value={opt}>{opt}</option>
                ))}
            </select>
        </div>
    )
}
