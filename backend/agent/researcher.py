from backend.agent.toolbox import ToolBox
from backend.agent.memory_system import MemorySystem
from backend.agent.critic import Critic
from backend.agent.planner import RuleBasedPlanner
import re

class Researcher:
    def __init__(self):
        self.tools = ToolBox()
        self.memory = MemorySystem()
        self.critic = Critic(self.memory)
        self.planner = RuleBasedPlanner(self.memory)

    def _parse_result(self, result_text):
        """Extracts key metrics from runner output."""
        try:
            # Check for explicit errors first
            error_match = re.search(r'Error: (.*)', result_text)
            if error_match:
                return f"Error: {error_match.group(1)}"

            # Look for "Return: X%"
            ret_match = re.search(r'Return: ([+-]?\d+\.?\d*)%', result_text)
            dd_match = re.search(r'Max DD: (\d+\.?\d*)%', result_text)
            
            if ret_match and dd_match:
                return f"{ret_match.group(1)}% Total Return, {dd_match.group(1)}% Max Drawdown"
            return "Metrics not found in output"
        except:
            return "Error parsing metrics"

    def run_research_cycle(self, goal: str, symbol: str, timeframe: str):
        print(f"--- Starting Research Cycle for: {goal} ---")
        
        # 1. Plan (Planner)
        strategy = self.planner.formulate_hypothesis(goal, symbol)
        print(f"Hypothesis: {strategy} is suitable for {symbol}.")

        # 2. Optimize (Planner)
        params = self.planner.optimize_parameters(strategy, symbol)
        
        # 3. Execute (Tool Use)
        if params:
            print(f"Action: Running backtest for {strategy} with params {params}...")
        else:
            print(f"Action: Running backtest for {strategy}...")
            
        result = self.tools.run_backtest(strategy, symbol, timeframe, params=params)
        
        # 4. Analyze & Learn
        metrics = self._parse_result(result)
        insight = f"Tested {strategy} on {symbol} ({timeframe}) with params {params}. Result: {metrics}."
        
        print(f"Result received: {metrics}")
        self.memory.add_insight(insight)
        print("Insight saved to memory.")
        
        # 5. Critic Review
        print("Critic is reviewing memory...")
        self.critic.curate_memory()
        print("Memory curated.")
        
        return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Researcher Agent")
    parser.add_argument("--goal", type=str, required=True, help="Research Goal")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol to trade")
    parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe")
    
    args = parser.parse_args()
    
    agent = Researcher()
    agent.run_research_cycle(args.goal, args.symbol, args.timeframe)
