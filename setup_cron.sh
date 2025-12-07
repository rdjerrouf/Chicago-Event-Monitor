#!/bin/bash
# Setup script for Chicago Event Monitor cron job
# This adds a daily job to run at 8 AM

echo "=========================================="
echo "Chicago Event Monitor - Cron Setup"
echo "=========================================="
echo ""

# Get the current directory (where this script is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Project directory: $SCRIPT_DIR"
echo ""

# Create the cron job command
CRON_COMMAND="0 4 * * * cd $SCRIPT_DIR && $SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/main.py >> $SCRIPT_DIR/logs/cron.log 2>&1"

echo "This will add the following cron job:"
echo "$CRON_COMMAND"
echo ""
echo "Translation: Run daily at 4:00 AM"
echo ""

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Ask for confirmation
read -p "Do you want to add this cron job? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

    echo ""
    echo "✅ Cron job added successfully!"
    echo ""
    echo "Your Chicago Event Monitor will now run automatically every day at 4:00 AM."
    echo ""
    echo "Useful cron commands:"
    echo "  - View cron jobs: crontab -l"
    echo "  - Edit cron jobs: crontab -e"
    echo "  - Remove cron jobs: crontab -r"
    echo "  - View logs: cat $SCRIPT_DIR/logs/cron.log"
    echo ""
else
    echo ""
    echo "❌ Cron job not added."
    echo ""
    echo "To add it manually later, run: crontab -e"
    echo "Then add this line:"
    echo "$CRON_COMMAND"
    echo ""
fi

echo "=========================================="
