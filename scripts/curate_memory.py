import os
import re

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MEMORY_DIR = ".agent/memory"
RECENT_HISTORY_FILE = os.path.join(MEMORY_DIR, "recent_history.md")
RESEARCH_INSIGHTS_FILE = os.path.join(MEMORY_DIR, "research_insights.md")

KEYWORDS = ["Insight:", "Result:", "Failed:", "Lesson:", "Note:"]

def read_file(filepath):
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r") as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, "w") as f:
        f.write(content)

def extract_insights(history_content):
    insights = []
    lines = history_content.split('\n')
    for line in lines:
        clean_line = line.strip()
        # Check for keywords
        for keyword in KEYWORDS:
            if keyword in clean_line:
                # Remove the bullet point if it exists
                content = clean_line.lstrip("- ").lstrip("* ")
                insights.append(content)
                break
    return insights

def append_insights(new_insights):
    if not new_insights:
        print("No new insights found.")
        return

    current_content = read_file(RESEARCH_INSIGHTS_FILE)
    
    # Simple check to avoid exact duplicates
    unique_insights = [i for i in new_insights if i not in current_content]
    
    if not unique_insights:
        print("No *new* insights to add (duplicates skipped).")
        return

    print(f"Adding {len(unique_insights)} new insights to {RESEARCH_INSIGHTS_FILE}...")
    
    with open(RESEARCH_INSIGHTS_FILE, "a") as f:
        f.write("\n## New Insights (Auto-Curated)\n")
        for insight in unique_insights:
            f.write(f"- {insight}\n")

from backend.agent.memory_system import MemorySystem
from backend.agent.critic import Critic

def main():
    print("Curating memory...")
    history = read_file(RECENT_HISTORY_FILE)
    if not history:
        print(f"No history found at {RECENT_HISTORY_FILE}")
        return

    insights = extract_insights(history)
    append_insights(insights)
    
    # Trigger Critic
    print("Triggering Critic Agent...")
    memory = MemorySystem()
    critic = Critic(memory)
    critic.curate_memory()
    
    # Trigger System Manual Update
    print("Updating System Manual...")
    critic.update_system_manual()
    
    print("Memory curation complete.")

if __name__ == "__main__":
    main()
