import os
import re

class StrategyRegistrar:
    """
    Automatically registers new strategies in backend/runner.py
    """
    
    RUNNER_PATH = "backend/runner.py"
    
    def register(self, strategy_name: str, file_path: str):
        """
        Adds import and map entry to runner.py
        """
        # 1. Derive Class Name and Module Name
        # strategy_name = "GoldenCross" -> class="GoldenCrossStrategy"
        class_name = strategy_name.replace(" ", "") + "Strategy"
        
        # file_path = "backend/strategies/golden_cross.py" -> module="backend.strategies.golden_cross"
        module_name = file_path.replace("/", ".").replace(".py", "")
        
        # 2. Read runner.py
        with open(self.RUNNER_PATH, "r") as f:
            lines = f.readlines()
            
        # 3. Check if already registered
        if any(class_name in line for line in lines):
            print(f"Strategy {class_name} already registered.")
            return
            
        # 4. Find Insertion Points
        import_insert_idx = -1
        map_insert_idx = -1
        
        for i, line in enumerate(lines):
            if "from backend.strategies" in line:
                import_insert_idx = i # Keep updating to find the last import
            if "STRATEGY_MAP = {" in line:
                map_insert_idx = i
                
        # 5. Insert Import (after the last strategy import)
        new_import = f"from {module_name} import {class_name}\n"
        lines.insert(import_insert_idx + 1, new_import)
        
        # Adjust map index because we added a line
        map_insert_idx += 1
        
        # 6. Insert into Map
        # Find the closing brace of the map
        for i in range(map_insert_idx, len(lines)):
            if "}" in lines[i]:
                # Insert before the closing brace
                new_entry = f"    \"{strategy_name}\": {class_name},\n"
                lines.insert(i, new_entry)
                break
                
        # 7. Write back
        with open(self.RUNNER_PATH, "w") as f:
            f.writelines(lines)
            
        print(f"Successfully registered {strategy_name} in {self.RUNNER_PATH}")
