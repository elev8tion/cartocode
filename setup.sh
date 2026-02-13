#!/bin/bash
# Cartographer Setup Script

echo "🗺️  Cartographer Setup"
echo "====================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install mcp fastmcp requests

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🔧 MCP Configuration"
echo "===================="
echo ""
echo "Add this to your ~/.claude/claude_desktop_config.json:"
echo ""
cat << EOF
{
  "mcpServers": {
    "cartographer": {
      "command": "python3",
      "args": ["$(pwd)/cartographer_mcp.py"]
    }
  }
}
EOF

echo ""
echo "Or run this command to add it automatically:"
echo ""
echo "  ./configure_mcp.sh"
echo ""
echo "✨ Setup complete!"
echo ""
echo "📚 Usage:"
echo "  1. Start cartographer: python3 cartographer.py /path/to/project"
echo "  2. Open Claude Code anywhere"
echo "  3. Use MCP tools to work with the loaded project!"
echo ""
