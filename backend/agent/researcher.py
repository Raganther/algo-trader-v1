from backend.agent.toolbox import ToolBox
from backend.agent.memory_system import MemorySystem
from backend.agent.critic import Critic
from backend.agent.planner import RuleBasedPlanner
from backend.agent.strategy_generator import StrategyGenerator
from backend.agent.registrar import StrategyRegistrar
import argparse

class ResearcherAgent:
    def __init__(self):
        self.memory = MemorySystem()
        self.planner = RuleBasedPlanner(self.memory)
        self.toolbox = ToolBox()
        self.critic = Critic(self.memory)
        self.generator = StrategyGenerator()
        self.registrar = StrategyRegistrar()

    def run_mission(self, goal: str, symbol: str, timeframe: str):
        print(f"🤖 Agent: Received Mission -> {goal} on {symbol}")
        
        # 1. Plan
        action = self.planner.decide_action(goal, symbol)
        
        if action["type"] == "create":
            self._handle_creation(action, symbol, timeframe)
        else:
            self._handle_research(action, symbol, timeframe)

    def _handle_creation(self, action, symbol, timeframe):
        name = action["name"]
        desc = action["description"]
        print(f"🤖 Agent: Creating new strategy '{name}'...")
        
        # 1. Generate Code
        code = self.generator.generate(name, desc)
        file_path = self.generator.save_strategy(name, code)
        print(f"✅ Code generated: {file_path}")
        
        # 2. Register
        self.registrar.register(name, file_path)
        print(f"✅ Registered '{name}' in runner.py")
        
        # 3. Verify (Run Backtest)
        print(f"🤖 Agent: Verifying '{name}' with a quick backtest...")
        # Note: We need to reload runner or import dynamically? 
        # Since we are running this script, runner.py is external. 
        # The toolbox runs runner.py as a subprocess, so it should pick up the changes!
        raw_output = self.toolbox.run_backtest(name, symbol, timeframe)
        
        # 4. Report
        metrics = self._parse_result(raw_output)
        if metrics:
            print(f"✅ Verification Successful: {metrics['return_pct']}% Return")
        else:
            print(f"❌ Verification Failed. Output:\n{raw_output[:200]}...")

    def _handle_research(self, action, symbol, timeframe):
        strategy = action["strategy"]
        params = action["parameters"]
        
        print(f"🤖 Agent: Hypothesis -> {strategy} is best.")
        if params:
            print(f"    Optimization -> Trying parameters: {params}")
        
        # 2. Execute
        raw_output = self.toolbox.run_backtest(strategy, symbol, timeframe, parameters=params)
        
        # 3. Critique & Learn
        metrics = self._parse_result(raw_output)
        if metrics:
            # Construct a result dict for the critic
            results = {
                "return_pct": metrics["return_pct"],
                "max_drawdown": metrics["max_drawdown"],
                "total_trades": metrics["total_trades"],
                "win_rate": metrics["win_rate"]
            }
            insight = self.critic.evaluate(results, strategy, symbol)
            print(f"🧠 Insight: {insight}")
            self.memory.add_insight(insight)
            self.memory.log_run(strategy, symbol, results)
        else:
            print(f"❌ Execution Failed. Output:\n{raw_output[:200]}...")

    def _parse_result(self, output: str) -> dict:
        """Parses the stdout from runner.py to extract metrics."""
        import re
        try:
            if "Error:" in output:
                return None
                
            ret_match = re.search(r'Return: ([+-]?\d+\.?\d*)%', output)
            dd_match = re.search(r'Max DD: (\d+\.?\d*)%', output)
            trades_match = re.search(r'Trades: (\d+)', output)
            win_match = re.search(r'Win Rate: (\d+\.?\d*)%', output)
            
            if ret_match and dd_match:
                return {
                    "return_pct": float(ret_match.group(1)),
                    "max_drawdown": float(dd_match.group(1)),
                    "total_trades": int(trades_match.group(1)) if trades_match else 0,
                    "win_rate": float(win_match.group(1)) if win_match else 0.0
                }
            return None
        except Exception as e:
            print(f"Error parsing output: {e}")
            return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Researcher Agent")
    parser.add_argument("--goal", type=str, required=True, help="Research Goal or Creation Intent")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol to trade")
    parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe")
    
    args = parser.parse_args()
    
    agent = ResearcherAgent()
    agent.run_mission(args.goal, args.symbol, args.timeframe)
