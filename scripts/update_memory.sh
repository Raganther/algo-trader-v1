#!/bin/bash

# Create directory if it doesn't exist
mkdir -p .claude/memory

# Generate recent history from git log
echo "# Recent Git History" > .claude/memory/recent_history.md
echo "" >> .claude/memory/recent_history.md
git log -n 20 --pretty=format:"### %h - %s (%cd)%n%b" --date=short >> .claude/memory/recent_history.md

echo "Memory updated: .claude/memory/recent_history.md"
