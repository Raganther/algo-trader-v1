class RuleBasedPlanner:
    def __init__(self, memory_system):
        self.memory = memory_system

    def formulate_hypothesis(self, goal: str, symbol: str) -> str:
        """
        Decides which strategy to run based on the goal keywords.
        """
        goal_lower = goal.lower()
        
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
            # Default fallback
            return "StochRSIQuant"

    def optimize_parameters(self, strategy: str, symbol: str) -> dict:
        """
        Decides whether to run Baseline or Optimized parameters based on memory.
        """
        # Check if we have run this Strategy on this Symbol before
        has_run = self.memory.has_run_before(strategy, symbol)
        
        if not has_run:
            # First time? Run Baseline (None params)
            return None
            
        # If run before, suggest optimization based on strategy type
        if strategy == "StochRSIMeanReversion":
            # Simple toggle: If 21 (Safe) is done, try 7 (Aggressive)
            if "rsi_period': 21" in self.memory.insights:
                return {"rsi_period": 7, "stoch_period": 7}
            else:
                return {"rsi_period": 21, "stoch_period": 21}
                
        elif strategy == "DonchianTrend":
            return {"donchian_period": 50}

        elif strategy == "GammaScalping":
            # Optimization 2: Faster Reaction (RSI 7) since Volatility Filter failed
            return {"rsi_period": 7, "stoch_period": 7}

        elif strategy == "HybridRegime":
            # Optimization 3: Tune Sub-Strategy (RSI 9) for faster mean reversion
            return {"rsi_period": 9, "stoch_period": 9}
            
        return None
