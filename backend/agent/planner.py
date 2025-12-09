class RuleBasedPlanner:
    def __init__(self, memory_system):
        self.memory = memory_system

    def decide_action(self, goal: str, symbol: str) -> dict:
        """
        Decides the next action based on the goal.
        Returns a dict: {"type": "research"|"create", "details": ...}
        """
        goal_lower = goal.lower()
        
        # Intent Detection: Creation
        if any(w in goal_lower for w in ["create", "build", "make", "generate", "code"]):
            # Extract Strategy Name (Simple heuristic: "Create Golden Cross" -> "Golden Cross")
            # Remove the action verbs
            clean_name = goal_lower
            for w in ["create ", "build ", "make ", "generate ", "code ", "strategy", "bot", " a ", " an "]:
                clean_name = clean_name.replace(w, "")
            
            # Capitalize
            strategy_name = clean_name.title().replace(" ", "")
            
            return {
                "type": "create",
                "name": strategy_name,
                "description": goal
            }
            
        # Intent Detection: Research (Default)
        strategy = self._map_strategy(goal_lower)
        params = self._optimize_parameters(strategy, symbol)
        
        return {
            "type": "research",
            "strategy": strategy,
            "parameters": params
        }

    def _map_strategy(self, goal_lower: str) -> str:
        if "trend" in goal_lower:
            return "DonchianTrend"
        elif "reversion" in goal_lower or "range" in goal_lower:
            return "StochRSIMeanReversion"
        elif "gamma" in goal_lower or "volatility" in goal_lower:
            return "GammaScalping"
        elif "quant" in goal_lower:
            return "StochRSIQuant"
        elif "hybrid" in goal_lower or "regime" in goal_lower:
            return "HybridRegime"
        else:
            return "StochRSIQuant"

    def _optimize_parameters(self, strategy: str, symbol: str) -> dict:
        # Check if we have run this Strategy on this Symbol before
        has_run = self.memory.has_run_before(strategy, symbol)
        
        if not has_run:
            return None
            
        if strategy == "StochRSIMeanReversion":
            if "rsi_period': 21" in self.memory.insights:
                return {"rsi_period": 7, "stoch_period": 7}
            else:
                return {"rsi_period": 21, "stoch_period": 21}
        elif strategy == "DonchianTrend":
            return {"donchian_period": 50}
        elif strategy == "GammaScalping":
            return {"rsi_period": 7, "stoch_period": 7}
        elif strategy == "HybridRegime":
            return {"rsi_period": 9, "stoch_period": 9}
            
        return None
