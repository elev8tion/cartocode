# ⚡ Quick Start Guide

Get Cartographer MCP Bridge running in 3 minutes!

## 🚀 Installation

```bash
cd ~/cartocode

# Install dependencies
pip3 install -r requirements.txt

# Configure MCP (follow prompts)
./configure_mcp.sh
```

## 🎯 Basic Usage

### 1. Start Cartographer
```bash
# Analyze any project
python3 cartographer.py /path/to/your/project

# Example with your ai-smb-partners project
python3 cartographer.py ~/ai-smb-partners
```

### 2. Open Claude Code
```bash
# Open in ANY directory (doesn't have to be the analyzed project!)
cd ~/anywhere
claude
```

### 3. Start Working!
```
"What project is loaded in Cartographer?"
"Read package.json from the loaded project"
"Show me the critical files in this project"
"Run npm test in the loaded project"
```

## 🔌 Available MCP Tools

| Tool | Description | Example |
|------|-------------|---------|
| `get_loaded_project()` | Get current project info | "What project is loaded?" |
| `read_project_file(path)` | Read a file | "Read src/App.tsx from the loaded project" |
| `execute_in_project(cmd)` | Run shell commands | "Run git status in the loaded project" |
| `get_risk_map()` | Get safety context | "Show me the risk map" |
| `search_project_files(pattern)` | Find files | "Find all .tsx files" |
| `get_file_risk_info(file)` | Analyze file risk | "What's the risk of types.ts?" |

## 📊 Dashboard Features

Visit **http://localhost:3000** after starting Cartographer:

- **Graph View** 🌐 - Visual dependency map
- **List View** 📋 - Sortable file table
- **Concerns View** 🏷️ - Domain-based grouping
- **Matrix View** 🔷 - Binding point analysis

## 💡 Pro Tips

1. **Keep Cartographer Running** - Leave it running while you work with Claude
2. **Use Risk Scores** - Ask Claude to check risk before modifying files
3. **Multi-Project** - Run multiple instances on different ports
4. **Git Integration** - Risk scores consider recent file changes
5. **Safety First** - Use the risk map to identify critical files

## 🆘 Troubleshooting

**"Connection refused"**
```bash
# Make sure Cartographer is running
python3 cartographer.py /path/to/project

# Check the dashboard loads
open http://localhost:3000
```

**"MCP server not found"**
```bash
# Restart Claude Code
# Check config file
cat ~/.claude/claude_desktop_config.json
```

**"Module not found"**
```bash
# Reinstall dependencies
pip3 install -r requirements.txt
```

## 🎓 Learn More

- Full documentation: [README.md](README.md)
- Example workflows: [EXAMPLE.md](EXAMPLE.md)
- Dashboard at: http://localhost:3000

---

**Need help?** Check that:
1. ✅ Cartographer is running (`python3 cartographer.py /path`)
2. ✅ Dashboard loads (http://localhost:3000)
3. ✅ Claude Code is restarted after MCP config
4. ✅ Dependencies installed (`pip3 install -r requirements.txt`)
