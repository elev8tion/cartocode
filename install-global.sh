#!/bin/bash
# Install Cartographer as a global command
# After running this, you can use: carto [project_path]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/bin"

echo "🗺️  Installing Cartographer globally..."
echo ""

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Create the global command
cat > "$INSTALL_DIR/carto" << 'EOF'
#!/bin/bash
# Cartographer global launcher
CARTOGRAPHER_PATH="SCRIPT_DIR_PLACEHOLDER"
PROJECT_PATH="${1:-.}"

# Resolve to absolute path
if [ "$PROJECT_PATH" != "." ]; then
    PROJECT_PATH="${PROJECT_PATH/#\~/$HOME}"
    PROJECT_PATH="$(cd "$PROJECT_PATH" 2>/dev/null && pwd)"
else
    PROJECT_PATH="$(pwd)"
fi

if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ Directory not found: $PROJECT_PATH"
    exit 1
fi

echo "🗺️  Launching Cartographer"
echo "📂 Project: $PROJECT_PATH"
echo ""

python3 "$CARTOGRAPHER_PATH/cartographer.py" "$PROJECT_PATH"
EOF

# Replace placeholder with actual path
sed -i.bak "s|SCRIPT_DIR_PLACEHOLDER|$SCRIPT_DIR|" "$INSTALL_DIR/carto"
rm "$INSTALL_DIR/carto.bak"

# Make executable
chmod +x "$INSTALL_DIR/carto"

echo "✅ Installed to: $INSTALL_DIR/carto"
echo ""
echo "To use from anywhere, add this to your ~/.zshrc or ~/.bashrc:"
echo ""
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "Then restart your terminal or run: source ~/.zshrc"
echo ""
echo "Usage:"
echo "  carto              # Analyze current directory"
echo "  carto ~/myproject  # Analyze specific project"
echo ""

# Check if already in PATH
if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    echo "✅ $HOME/.local/bin is already in your PATH!"
    echo ""
    echo "You can now run: carto"
else
    echo "⚠️  Remember to add ~/.local/bin to your PATH!"
fi
