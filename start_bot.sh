#!/bin/bash
# Script to start the Talia Bot with correct PYTHONPATH

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set PYTHONPATH to include the parent directory
export PYTHONPATH="$PYTHONPATH:$DIR/.."

# Run the bot
python3 "$DIR/talia_bot/main.py"
