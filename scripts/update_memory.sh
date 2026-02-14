#!/bin/bash

# Create directory if it doesn't exist
mkdir -p .claude

# Generate recent history from git log
echo "# Recent Git History" > .claude/recent_history.md
echo "" >> .claude/recent_history.md
git log -n 20 --pretty=format:"### %h - %s (%cd)%n%b" --date=short >> .claude/recent_history.md

echo "Memory updated: .claude/recent_history.md"
