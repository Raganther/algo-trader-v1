#!/bin/bash
# Setup pm2-logrotate to prevent unbounded log growth
# Run this on the server: bash scripts/setup_logrotate.sh

pm2 install pm2-logrotate

# Max 10MB per log file, retain 3 rotated files, compress old logs
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 3
pm2 set pm2-logrotate:compress true
pm2 set pm2-logrotate:rotateInterval '0 0 * * *'

echo "✅ pm2-logrotate configured: 10MB max, 3 retained, daily rotation"
