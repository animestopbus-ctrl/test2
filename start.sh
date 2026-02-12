#!/bin/bash
# start.sh - Startup script for the bot

set -e

echo "Starting LastPerson07Bot..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Check required environment variables
if [ -z "$TELEGRAM_TOKEN" ]; then
    echo "ERROR: TELEGRAM_TOKEN is not set"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the bot
exec python app.py
