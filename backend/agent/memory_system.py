import os

class MemorySystem:
    def __init__(self, memory_file=".agent/memory/research_insights.md"):
        self.memory_file = memory_file
        self.insights = self._load_memory()

    def _load_memory(self):
        """Loads the content of the memory file."""
        if not os.path.exists(self.memory_file):
            return ""
        with open(self.memory_file, "r") as f:
            return f.read()

    def get_proven_strategies(self):
        """Extracts proven strategies from memory."""
        # Simple parsing for now - can be enhanced with LLM or regex
        lines = self.insights.split('\n')
        proven = []
        in_section = False
        for line in lines:
            if "## Proven Strategies" in line:
                in_section = True
                continue
            if line.startswith("##"):
                in_section = False
            
            if in_section and line.strip().startswith("-"):
                proven.append(line.strip())
        return proven

    def get_failed_experiments(self):
        """Extracts failed experiments from memory."""
        lines = self.insights.split('\n')
        failed = []
        in_section = False
        for line in lines:
            if "## Failed Experiments" in line:
                in_section = True
                continue
            if line.startswith("##"):
                in_section = False
            
            if in_section and line.strip().startswith("-"):
                failed.append(line.strip())
        return failed

    def has_run_before(self, strategy_name, symbol=None):
        """Checks if a strategy has been run before (success or fail)."""
        # Check the entire memory content
        # If symbol is provided, check for "Strategy on Symbol"
        if symbol:
            query = f"{strategy_name} on {symbol}"
            return query.lower() in self.insights.lower()
        else:
            return strategy_name.lower() in self.insights.lower()

    def add_insight(self, insight_text, section="New Insights (Auto-Curated)"):
        """Appends a new insight to the memory file."""
        # Reload to ensure we have latest
        current_content = self._load_memory()
        
        if insight_text in current_content:
            return # Duplicate
            
        with open(self.memory_file, "a") as f:
            f.write(f"\n- {insight_text}\n")
        
        # Update local cache
        self.insights = self._load_memory()
