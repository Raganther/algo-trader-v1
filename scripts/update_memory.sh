#!/bin/bash

# Create directory if it doesn't exist
mkdir -p .agent/memory

# Generate recent history from git log
echo "# Recent Git History" > .agent/memory/recent_history.md
echo "" >> .agent/memory/recent_history.md
git log -n 20 --pretty=format:"### %h - %s (%cd)%n%b" --date=short >> .agent/memory/recent_history.md

echo "Memory updated: .agent/memory/recent_history.md"
