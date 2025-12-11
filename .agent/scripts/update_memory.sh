#!/bin/bash
# Update recent_history.md with the last 20 commits including detailed bodies
git log -n 20 --pretty=format:"### %h - %s (%cr)%n%n%b%n---" > .agent/memory/recent_history.md
echo "Updated .agent/memory/recent_history.md"
