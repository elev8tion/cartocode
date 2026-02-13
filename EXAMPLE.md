# 🎯 Cartographer MCP Bridge - Example Workflow

## The Problem

You have:
- **Project A** (ai-smb-partners) that you want to analyze and work on
- **Claude Code** running in a different directory (cartocode)
- No way for Claude to access Project A's files!

## The Solution

Cartographer MCP Bridge creates a connection between:
1. The **Cartographer Dashboard** (analyzing Project A)
2. **Claude Code** (running anywhere)

## Step-by-Step Example

### 1️⃣ Start Cartographer on Your Project

```bash
# Open Terminal 1
cd ~
python3 ~/cartocode/cartographer.py ~/ai-smb-partners

# Output:
#   ◆ CODEBASE CARTOGRAPHER
#   ━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   Scanning: /Users/kcdacre8tor/ai-smb-partners
#   Files:    150
#   Edges:    320
#   Bindings: 89
#   Health:   72/100
#   Languages: typescript, javascript
#
#   🌐 Dashboard: http://localhost:3000
```

### 2️⃣ Open Claude Code Anywhere

```bash
# Open Terminal 2 (different directory!)
cd ~/Documents/random-folder
claude
```

### 3️⃣ Use Claude Code to Work with ai-smb-partners

```
You: What project is currently loaded in Cartographer?

Claude: [Uses get_loaded_project() tool]
Currently Loaded Project:
Path: /Users/kcdacre8tor/ai-smb-partners
Name: ai-smb-partners
Files: 150
Languages: typescript, javascript
Health Score: 72/100

You can now use the other Cartographer tools to work with this project!

---

You: Show me the risk map for this project

Claude: [Uses get_risk_map() tool]
# ⚠️ CODEBASE RISK MAP — READ BEFORE MODIFYING

## 🔴 Critical Files (DO NOT modify without review)

- **lib/booking/types.ts** — Risk: 62.8/100 | Dependents: 13 | 🔌 interface
- **components/ROICalculator/index.tsx** — Risk: 43.1/100 | Dependents: 0
...

---

You: Read lib/booking/types.ts from the loaded project

Claude: [Uses read_project_file("lib/booking/types.ts")]
[Shows file contents]

---

You: What's the risk score for this file?

Claude: [Uses get_file_risk_info("lib/booking/types.ts")]
File: lib/booking/types.ts
Risk Score: 62.8/100
Language: typescript
Lines: 156
Complexity: medium
Dependents (Fan-In): 13
Dependencies (Fan-Out): 3
Has Tests: No
Tags: 🔌 interface

⚠️ **lib/booking/types.ts** is critical. Treat changes with extreme care.
**13 other files depend on this.** Changes cascade widely.
**🔌 interface** — Defines a contract other files must follow. Changes break implementers.

---

You: Run git status in the loaded project

Claude: [Uses execute_in_project("git status")]
STDOUT:
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   lib/booking/types.ts
...

---

You: Find all test files

Claude: [Uses search_project_files("**/*.test.ts*")]
Found 12 files:
  - lib/booking/__tests__/availability.test.ts
  - components/Booking/__tests__/BookingForm.test.tsx
  - lib/i18n/__tests__/translations.test.ts
...
```

## 🎯 Key Benefits

1. **Work Across Projects**: Claude Code in directory A can work with files in directory B
2. **Risk Awareness**: Claude knows which files are safe to modify
3. **Seamless Integration**: No need to change directories or restart
4. **Full Project Access**: Read files, run commands, search, analyze
5. **Safety Context**: AI gets codebase risk map before making changes

## 🔥 Advanced Use Cases

### Parallel Analysis
```bash
# Terminal 1: Analyze backend
python3 cartographer.py ~/backend-api --port 3000

# Terminal 2: Analyze frontend (different instance)
python3 cartographer.py ~/frontend-app --port 3001

# Configure second MCP server to point to port 3001
# Now Claude can work with BOTH projects!
```

### CI/CD Integration
```bash
# Pre-commit hook: Analyze changed files
python3 cartographer.py .
curl http://localhost:3000/api/agent-context > .claude-context.md
git add .claude-context.md
```

### Remote Projects
```bash
# Mount remote project and analyze
sshfs user@remote:/app ~/remote-app
python3 cartographer.py ~/remote-app

# Now Claude can safely work with remote codebase!
```

## 🛠️ Troubleshooting

**"Failed to connect to Cartographer"**
- Make sure `python3 cartographer.py /path/to/project` is running
- Check it's on port 3000 (or update CARTOGRAPHER_URL in cartographer_mcp.py)
- Visit http://localhost:3000 in your browser to verify

**"MCP server not found"**
- Restart Claude Code after adding MCP config
- Check `~/.claude/claude_desktop_config.json` is correct
- Verify path to `cartographer_mcp.py` is absolute

**"Permission denied" errors**
- Make sure scripts are executable: `chmod +x *.sh *.py`
- Check Python path in MCP config matches your system

## 📚 Resources

- Dashboard: http://localhost:3000
- API Docs: http://localhost:3000/api/scan
- Agent Context: http://localhost:3000/api/agent-context
