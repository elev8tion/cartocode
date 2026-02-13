#!/bin/bash
# Auto-configure MCP server in Claude Code

CONFIG_FILE="$HOME/.claude/claude_desktop_config.json"
MCP_PATH="$(cd "$(dirname "$0")" && pwd)/cartographer_mcp.py"

echo "🔧 Configuring Cartographer MCP Server"
echo "======================================"
echo ""
echo "Config file: $CONFIG_FILE"
echo "MCP server: $MCP_PATH"
echo ""

# Create .claude directory if it doesn't exist
mkdir -p "$HOME/.claude"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "📝 Creating new config file..."
    cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "cartographer": {
      "command": "python3",
      "args": ["$MCP_PATH"]
    }
  }
}
EOF
    echo "✅ Config file created!"
else
    echo "⚠️  Config file already exists."
    echo ""
    echo "Please manually add this to your mcpServers section:"
    echo ""
    cat << EOF
    "cartographer": {
      "command": "python3",
      "args": ["$MCP_PATH"]
    }
EOF
    echo ""
fi

echo ""
echo "✨ Configuration complete!"
echo ""
echo "📚 Next steps:"
echo "  1. Restart Claude Code (if running)"
echo "  2. Start cartographer: python3 cartographer.py /path/to/project"
echo "  3. In Claude Code, ask: 'What project is loaded in Cartographer?'"
echo ""
