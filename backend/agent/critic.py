import os
import re

class Critic:
    def __init__(self, memory_system):
        self.memory = memory_system

    def curate_memory(self):
        """
        Organizes the memory file.
        1. Moves 'Success' or positive return items to 'Proven Strategies'.
        2. Moves 'Failed' or negative return items to 'Failed Experiments'.
        3. Cleans up formatting.
        """
        content = self.memory._load_memory()
        lines = content.split('\n')
        
        new_insights = []
        proven_strategies = []
        failed_experiments = []
        other_lines = []
        
        # Simple state machine parser
        current_section = "Header"
        
        for line in lines:
            stripped = line.strip()
            
            # Detect Sections
            if "## Proven Strategies" in line:
                current_section = "Proven"
                other_lines.append(line)
                continue
            elif "## Failed Experiments" in line:
                current_section = "Failed"
                other_lines.append(line)
                continue
            elif "## New Insights" in line:
                current_section = "New"
                other_lines.append(line)
                continue
            elif line.startswith("##"):
                current_section = "Other"
                other_lines.append(line)
                continue
                
            if not stripped.startswith("-"):
                other_lines.append(line)
                continue
                
            # Process Bullet Points
            if current_section == "New":
                # Analyze the insight
                if "Return" in line and "%" in line:
                    # Extract Return
                    try:
                        # Regex to find "X% Return" or "Return: X%"
                        # This is a basic heuristic
                        if "FAILED" in line or "negative" in line.lower() or "- " in line and "Return" in line and "-" in line.split("Return")[0]: 
                             # Check for negative sign before return number? 
                             # Simpler: Check if return is positive or negative
                             pass
                        
                        # Heuristic: If it says "Winner" or "Success" or has positive return > 0
                        is_success = False
                        is_failure = False
                        
                        if "Winner" in line or "Success" in line:
                            is_success = True
                        elif "FAILED" in line or "Failed" in line:
                            is_failure = True
                        else:
                            # Try to parse number
                            # Look for "+X%" or "-X%"
                            match = re.search(r'([+-]?\d+\.?\d*)%', line)
                            if match:
                                val = float(match.group(1))
                                if val > 0:
                                    is_success = True
                                else:
                                    is_failure = True
                        
                        if is_success:
                            proven_strategies.append(line)
                        elif is_failure:
                            failed_experiments.append(line)
                        else:
                            new_insights.append(line) # Keep in new if unsure
                            
                    except:
                        new_insights.append(line)
                else:
                    new_insights.append(line)
            
            elif current_section == "Proven":
                proven_strategies.append(line)
            elif current_section == "Failed":
                failed_experiments.append(line)
            else:
                other_lines.append(line)

        # Reconstruct File
        # We need to preserve the structure: Header -> Proven -> Failed -> Others -> New
        # But wait, the file structure is fixed.
        
        # Let's rebuild based on the known structure in memory_system
        # Actually, simpler approach:
        # 1. Read all existing Proven/Failed
        # 2. Add new ones from "New Insights"
        # 3. Clear "New Insights"
        
        # Let's use the MemorySystem's structure knowledge if possible, 
        # but here we are manipulating the text directly.
        
        output_lines = []
        
        # We'll iterate through the original lines again, but this time we replace the sections
        # This is tricky because we want to APPEND to existing sections.
        
        # Better approach:
        # 1. Parse everything into lists (done above, roughly).
        # 2. Write it back out in order.
        
        # Refined Parsing:
        # We need to capture the "Header" (everything before first ##)
        # And "Market Mechanics" etc.
        
        # Let's try a robust rewrite.
        
        final_content = ""
        
        # Header
        final_content += "# Research Insights\n\n"
        final_content += "This file serves as the \"Long Term Semantic Memory\" for the agent.\n"
        final_content += "It contains curated insights, proven strategies, and failed experiments derived from the \"Episodic Memory\" (Git History).\n\n"
        
        # Proven
        final_content += "## Proven Strategies\n"
        final_content += "<!-- Strategies that have passed verification -->\n"
        seen_proven = set()
        for line in proven_strategies:
            if line not in seen_proven:
                final_content += f"{line}\n"
                seen_proven.add(line)
        final_content += "\n"
        
        # Failed
        final_content += "## Failed Experiments\n"
        final_content += "<!-- Strategies that failed and why, to avoid repeating mistakes -->\n"
        seen_failed = set()
        for line in failed_experiments:
            if line not in seen_failed:
                final_content += f"{line}\n"
                seen_failed.add(line)
        final_content += "\n"
        
        # Market Mechanics (We didn't parse this specifically, let's assume it's static or we need to preserve it)
        # The simple parser above put everything else in "other_lines" or "new_insights".
        # This is risky.
        
        # SAFE APPROACH:
        # Only move things from "New Insights" to the other sections.
        # Don't rewrite the whole file from scratch if we can avoid it.
        
        # Let's use string replacement.
        
        # 1. Get content of "New Insights" section.
        # 2. Identify items to move.
        # 3. Remove them from New Insights.
        # 4. Append them to Proven or Failed.
        
        # This preserves other sections like "Market Mechanics".
        
        self._move_items(content)

    def _move_items(self, content):
        lines = content.split('\n')
        new_proven = []
        new_failed = []
        kept_new = []
        
        in_new_section = False
        
        # Pass 1: Identify items in "New Insights"
        for line in lines:
            if "## New Insights" in line:
                in_new_section = True
                continue
            if in_new_section and line.startswith("##"):
                in_new_section = False
            
            if in_new_section and line.strip().startswith("-"):
                # Logic to classify
                if self._is_proven(line):
                    new_proven.append(line)
                elif self._is_failed(line):
                    new_failed.append(line)
                else:
                    kept_new.append(line)
        
        # Pass 2: Rewrite file
        with open(self.memory.memory_file, "w") as f:
            in_proven = False
            in_failed = False
            in_new = False
            
            for line in lines:
                # Detect Sections
                if "## Proven Strategies" in line:
                    in_proven = True
                    f.write(line + "\n")
                    continue
                elif "## Failed Experiments" in line:
                    in_failed = True
                    f.write(line + "\n")
                    continue
                elif "## New Insights" in line:
                    in_new = True
                    f.write(line + "\n")
                    continue
                elif line.startswith("##"):
                    in_proven = False
                    in_failed = False
                    in_new = False
                    f.write(line + "\n")
                    continue
                
                # Handle Content
                if in_proven:
                    f.write(line + "\n")
                    # Append new proven items at end of section? 
                    # No, we should append them after we finish writing the existing ones.
                    # But we don't know when the section ends easily line-by-line without lookahead.
                    # Actually, we can just write them immediately after the header? 
                    # Or wait until next section start?
                    pass 
                elif in_failed:
                    f.write(line + "\n")
                    pass
                elif in_new:
                    # Skip the lines we moved
                    if line in new_proven or line in new_failed:
                        continue
                    f.write(line + "\n")
                else:
                    f.write(line + "\n")
            
            # This logic is flawed because we need to insert the new items.
            # Let's do a simpler "Split by Section" approach.
            
        # Robust Split
        sections = re.split(r'(^## .*$)', content, flags=re.MULTILINE)
        # sections[0] = Header
        # sections[1] = "## Proven Strategies"
        # sections[2] = Content of Proven
        # ...
        
        new_content = sections[0]
        
        for i in range(1, len(sections), 2):
            header = sections[i]
            body = sections[i+1]
            
            if "Proven Strategies" in header:
                new_content += header
                new_content += body
                for item in new_proven:
                    if item not in body:
                        new_content += item + "\n"
            elif "Failed Experiments" in header:
                new_content += header
                new_content += body
                for item in new_failed:
                    if item not in body:
                        new_content += item + "\n"
            elif "New Insights" in header:
                new_content += header
                # Filter body
                body_lines = body.split('\n')
                for bl in body_lines:
                    if bl.strip() in new_proven or bl.strip() in new_failed:
                        continue
                    new_content += bl + "\n"
            else:
                new_content += header + body
                
        with open(self.memory.memory_file, "w") as f:
            f.write(new_content)

    def _is_proven(self, line):
        if "Winner" in line or "Success" in line:
            return True
        # Check for positive return
        match = re.search(r'([+-]?\d+\.?\d*)% Total Return', line)
        if match:
            if float(match.group(1)) > 0:
                return True
        return False

    def _is_failed(self, line):
        if "FAILED" in line or "Failed" in line:
            return True
        # Check for negative return
        match = re.search(r'([+-]?\d+\.?\d*)% Total Return', line)
        if match:
            if float(match.group(1)) <= 0:
                return True
        return False

    def update_system_manual(self):
        """
        Scans recent history for system updates ([Feat], [Refactor], [Docs]) 
        and appends them to the System Manual.
        """
        history_content = self.memory._load_memory_file(".agent/memory/recent_history.md")
        manual_content = self.memory._load_memory_file(".agent/memory/system_manual.md")
        
        if not history_content or not manual_content:
            return

        updates = []
        lines = history_content.split('\n')
        
        # Simple Parser for Git Log format: "### <hash> - [Type]: <Title>"
        for line in lines:
            if line.startswith("###") and ("[Feat]" in line or "[Refactor]" in line or "[Docs]" in line):
                # Extract the update description
                # Format: ### <hash> - [Feat]: Title (Date)
                parts = line.split(" - ")
                if len(parts) > 1:
                    desc = parts[1].strip()
                    updates.append(desc)
        
        if not updates:
            return

        # Deduplicate against existing manual
        new_updates = [u for u in updates if u not in manual_content]
        
        if not new_updates:
            print("No new system updates found.")
            return
            
        print(f"Adding {len(new_updates)} system updates to System Manual...")
        
        # Append to Manual
        # Check if section exists
        header = "## Recent System Updates"
        
        if header not in manual_content:
            # Append header to end
            with open(".agent/memory/system_manual.md", "a") as f:
                f.write(f"\n\n{header}\n")
                for update in new_updates:
                    f.write(f"- {update}\n")
        else:
            # Append to existing section (Naive append for now)
            # Ideally we insert after the header, but appending to file is safer/easier
            # unless the header is in the middle.
            # Let's assume header is at the end or we just append.
            # Actually, let's just append to the file.
            with open(".agent/memory/system_manual.md", "a") as f:
                for update in new_updates:
                    f.write(f"- {update}\n")
