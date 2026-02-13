#!/usr/bin/env bash
#
# Cartographer Launcher Diagnostic Test
# Systematically tests each component to identify the issue
#

set -x  # Show all commands
exec 2>&1  # Redirect stderr to stdout

echo "========================================="
echo "CARTOGRAPHER LAUNCHER DIAGNOSTIC"
echo "========================================="
echo ""

# Kill any existing servers
echo "1. Cleaning up existing servers..."
pkill -f "cartographer.py" 2>/dev/null || true
sleep 1

# Test 1: Verify project files exist
echo ""
echo "2. Checking project files..."
BUNDLE_DIR="$(cd "$(dirname "$0")/Cartographer.app" && pwd)"
PROJECT_DIR="$(dirname "$BUNDLE_DIR")"
echo "   Bundle: $BUNDLE_DIR"
echo "   Project: $PROJECT_DIR"

if [ -f "$PROJECT_DIR/cartographer.py" ]; then
    echo "   ✓ cartographer.py exists"
else
    echo "   ✗ cartographer.py NOT FOUND"
    exit 1
fi

if [ -f "$PROJECT_DIR/dashboard.html" ]; then
    echo "   ✓ dashboard.html exists"
else
    echo "   ✗ dashboard.html NOT FOUND"
    exit 1
fi

# Test 2: Verify Python
echo ""
echo "3. Checking Python..."
which python3
python3 --version

# Test 3: Test server startup manually
echo ""
echo "4. Testing server startup..."
cd "$PROJECT_DIR"
PORT=3000

echo "   Starting server on port $PORT..."
python3 cartographer.py --port $PORT > /tmp/diagnostic-server.log 2>&1 &
SERVER_PID=$!
echo "   Server PID: $SERVER_PID"

# Test 4: Wait and check if server is alive
echo ""
echo "5. Checking if server is running..."
sleep 3

if kill -0 $SERVER_PID 2>/dev/null; then
    echo "   ✓ Server process is alive"
else
    echo "   ✗ Server process died"
    echo "   Server log:"
    cat /tmp/diagnostic-server.log
    exit 1
fi

# Test 5: Check if port is listening
echo ""
echo "6. Checking if port $PORT is listening..."
if lsof -i :$PORT | grep LISTEN; then
    echo "   ✓ Port $PORT is listening"
else
    echo "   ✗ Port $PORT is NOT listening"
    cat /tmp/diagnostic-server.log
    kill $SERVER_PID
    exit 1
fi

# Test 6: Test HTTP response
echo ""
echo "7. Testing HTTP response..."
sleep 1
HTTP_CODE=$(curl -s -o /tmp/diagnostic-response.html -w "%{http_code}" http://localhost:$PORT/)
echo "   HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✓ Server responding with 200 OK"
else
    echo "   ✗ Server returned $HTTP_CODE"
    cat /tmp/diagnostic-server.log
    kill $SERVER_PID
    exit 1
fi

# Test 7: Check API endpoints
echo ""
echo "8. Testing API endpoints..."

echo "   Testing /api/projects..."
curl -s http://localhost:$PORT/api/projects | python3 -m json.tool | head -10

echo ""
echo "   Testing /api/scan..."
curl -s http://localhost:$PORT/api/scan | python3 -c "import json, sys; d=json.load(sys.stdin); print(f\"   Nodes: {len(d.get('nodes', []))}\"); print(f\"   Metadata: {d.get('metadata', {}).get('project_name', 'None')}\")"

# Test 8: Check what the dashboard shows
echo ""
echo "9. Checking dashboard content..."
if grep -q "project-picker" /tmp/diagnostic-response.html; then
    echo "   ✓ Dashboard contains project picker"
elif grep -q "Codebase Cartographer" /tmp/diagnostic-response.html; then
    echo "   ✓ Dashboard loaded"
else
    echo "   ✗ Unexpected dashboard content"
    head -20 /tmp/diagnostic-response.html
fi

# Test 9: Check server log for any errors
echo ""
echo "10. Server log output:"
cat /tmp/diagnostic-server.log

# Cleanup
echo ""
echo "========================================="
echo "DIAGNOSTIC COMPLETE"
echo "========================================="
echo ""
echo "Server is still running on PID $SERVER_PID, port $PORT"
echo "To stop: kill $SERVER_PID"
echo ""
echo "Open browser to: http://localhost:$PORT"
