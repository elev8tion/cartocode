#!/bin/bash
# Cartographer Cleanup Script
# Kills all running Cartographer server processes

echo "🧹 Cleaning up Cartographer processes..."

# Kill processes using the PID file
PID_FILE="$HOME/.cartographer/server.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "  Killing process $PID from PID file..."
        kill "$PID" 2>/dev/null
        sleep 1
        kill -9 "$PID" 2>/dev/null || true
    fi
    rm "$PID_FILE"
fi

# Kill any remaining cartographer.py processes
PIDS=$(pgrep -f "python.*cartographer.py" 2>/dev/null)
if [ -n "$PIDS" ]; then
    echo "  Found running processes: $PIDS"
    echo "$PIDS" | xargs kill 2>/dev/null
    sleep 1
    # Force kill any survivors
    echo "$PIDS" | xargs kill -9 2>/dev/null || true
    echo "  ✓ All processes killed"
else
    echo "  No running Cartographer processes found"
fi

# Show ports that were freed
echo ""
echo "Ports 3000-3009 status:"
for port in {3000..3009}; do
    if lsof -i :"$port" >/dev/null 2>&1; then
        echo "  Port $port: IN USE"
    else
        echo "  Port $port: available"
    fi
done

echo ""
echo "✨ Cleanup complete!"
