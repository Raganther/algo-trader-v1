const API_BASE = 'http://localhost:8000/api';

export interface TestRun {
    test_id: string;
    strategy: string;
    symbol: string;
    timeframe: string;
    start_date: string;
    end_date: string;
    return_pct: number;
    max_drawdown: number;
    win_rate: number;
    total_trades: number;
    parameters: any;
}

export async function fetchRuns(): Promise<TestRun[]> {
    const res = await fetch(`${API_BASE}/runs`);
    if (!res.ok) throw new Error('Failed to fetch runs');
    return res.json();
}

export async function fetchEdges(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/edges`);
    if (!res.ok) throw new Error('Failed to fetch edges');
    return res.json();
}

export async function fetchTestDetails(testId: string): Promise<TestRun & { equity_curve: any[] }> {
    const res = await fetch(`${API_BASE}/runs/${encodeURIComponent(testId)}`);
    if (!res.ok) throw new Error('Failed to fetch test details');
    return res.json();
}
export async function fetchCompositeDetails(strategy: string, symbol: string, timeframe: string): Promise<TestRun & { equity_curve: any[] }> {
    const res = await fetch(`${API_BASE}/results/composite?strategy=${encodeURIComponent(strategy)}&symbol=${encodeURIComponent(symbol)}&timeframe=${encodeURIComponent(timeframe)}`);
    if (!res.ok) throw new Error('Failed to fetch composite details');
    return res.json();
}
