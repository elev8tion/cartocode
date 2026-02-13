# 🗺️ Cartographer - Quick Start Guide

## 🚀 The Simplest Way to Launch

Just run:

```bash
python3 cartographer.py
```

That's it! This will:
1. ✅ Open your browser to http://localhost:3000
2. ✅ Show an **interactive project picker**
3. ✅ Display your recent projects
4. ✅ Let you select a project or enter a new path
5. ✅ Scan and analyze the selected project
6. ✅ Generate interactive dashboard with risk analysis

---

## 🎯 Make It Even Easier

### Add an Alias (Recommended)

Add this to your `~/.zshrc`:

```bash
alias carto="python3 /Users/kcdacre8tor/cartocode/cartographer.py"
```

Then reload:
```bash
source ~/.zshrc
```

Now you can just type:
```bash
carto
```

---

## 📦 First Time Setup

```bash
# 1. Install dependencies (only once)
pip3 install mcp fastmcp requests

# 2. (Optional) Configure MCP for Claude Code
./configure_mcp.sh

# 3. Add the alias to your shell
echo 'alias carto="python3 /Users/kcdacre8tor/cartocode/cartographer.py"' >> ~/.zshrc
source ~/.zshrc

# 4. Launch!
carto
```

---

## 🎨 What You Get

When you launch, you'll see:

### Interactive Project Picker
```
🗺️  Project Picker
━━━━━━━━━━━━━━━━━━━━

Recent Projects:
  /Users/kcdacre8tor/my-app
  /Users/kcdacre8tor/my-website
  /Users/kcdacre8tor/old-project

Or enter new project path:
[                        ]
```

### Dashboard Views
- **Graph View** - Visual dependency graph with risk-based coloring
- **List View** - Sortable table of all files with risk scores
- **Concerns View** - Files grouped by domain (auth, database, API, etc.)
- **Matrix View** - Binding points and architectural connections

---

## 🔥 Common Workflows

### Daily Use
```bash
# Just run carto and pick from recent projects
carto
```

### Analyze New Project
```bash
# Run carto and enter the new path in the picker
carto

# Or pass the path directly
carto ~/new-project
```

### Use with Claude Code MCP
```bash
# Terminal 1: Start cartographer on your project
carto
# Select your project from the picker

# Terminal 2: Open Claude Code anywhere
cd ~/some-other-directory
claude

# Now in Claude Code, you can work with the loaded project!
# > "Read the src/App.tsx file from the loaded project"
# > "What are the critical files in the loaded project?"
# > "Run npm test in the loaded project"
```

---

## 🎯 Command Options

```bash
# Start with project picker
carto

# Analyze specific project
carto /path/to/project

# Use custom port
carto /path/to/project --port 3001

# Skip browser opening
carto /path/to/project --no-browser
```

---

## 🛡️ What Gets Analyzed?

Cartographer analyzes:
- **Dependencies** - What imports what
- **Risk Scores** - Based on complexity, fan-in/out, bindings
- **Binding Points** - APIs, events, interfaces, protocols
- **Concerns** - Authentication, database, networking, UI, etc.
- **Git Activity** - Change frequency (if git repo)

Files are scored 0-100 based on:
- **Fan-in** (35%): How many files depend on it
- **Fan-out** (15%): How many dependencies it has
- **Binding points** (25%): Interfaces, events, APIs it exposes
- **Complexity** (10%): Lines of code
- **High-risk patterns** (15%): API endpoints, data models, unsafe code

---

## 🏷️ Understanding Tags

- 🔌 **interface** - Defines contracts (protocols, interfaces)
- 📡 **event-driven** - Emits/receives events
- 🌐 **api-endpoint** - HTTP route handler
- 📤 **api-consumer** - Makes network calls
- 💾 **data-model** - Database schema
- ⚙️ **config-dependent** - Reads env vars
- 🔄 **state-management** - App state logic
- ⚠️ **unsafe-code** - Low-level/unsafe code
- ⚡ **concurrent** - Concurrency primitives
- 🧪 **test** - Test file

---

## 💡 Pro Tips

**Tip 1:** The project picker remembers your last 10 projects
```bash
carto  # Shows your recent projects automatically
```

**Tip 2:** You can switch projects without restarting
- Just use the "Load Project" button in the dashboard header

**Tip 3:** Use with Claude Code MCP to work across projects
```bash
# Analyze project A, then work on it from Claude in project B!
```

**Tip 4:** Generated `CODEBASE_AGENT_CONTEXT.md` is perfect for AI agents
- Copy it into your project
- Helps AI understand what's safe to modify

---

## 🔧 Troubleshooting

**Port already in use?**
```bash
carto --port 3001
```

**Browser didn't open?**
- Manually go to http://localhost:3000

**Want to reset project history?**
```bash
rm ~/.cartographer_history
```

**Dependencies not installed?**
```bash
pip3 install mcp fastmcp requests
```

---

## 🎉 That's It!

The old way required multiple launcher scripts and confusing options. Now it's just:

```bash
carto
```

Pick your project from the browser, and you're done!
