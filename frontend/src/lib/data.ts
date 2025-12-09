import fs from 'fs';
import path from 'path';

export interface ResearchResult {
    pair: string;
    year: number;
    timeframe: string;
    strategy_name?: string; // Added strategy_name
    status: string;
    return_pct?: number;
    trades?: number;
    win_rate?: number;
    final_equity?: number;
}

export async function getResearchResults(): Promise<ResearchResult[]> {
    // Path to backend/research_results.json
    // Assuming frontend is at /Users/alistairelliman/DEV/gemini 3 test/frontend
    // and backend is at /Users/alistairelliman/DEV/gemini 3 test/backend
    const filePath = path.join(process.cwd(), '../backend/research_results.json');

    try {
        const fileContents = fs.readFileSync(filePath, 'utf8');
        const data = JSON.parse(fileContents);
        return data as ResearchResult[];
    } catch (error) {
        console.error("Error reading research results:", error);
        return [];
    }
}
