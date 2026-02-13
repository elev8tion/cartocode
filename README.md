# 🗺️ Cartographer - Codebase Analysis & MCP Bridge

A powerful codebase analyzer with an interactive dashboard **and** an MCP bridge that lets Claude Code work with any project you're analyzing!

## 🚀 Features

### 1. **Interactive Codebase Dashboard**
- Visualize code dependencies as an interactive graph
- Risk scoring for files based on complexity, dependencies, and change frequency
- Identify critical files, binding points, and safe-to-modify areas
- Filter by language, concerns, and risk levels
- Generate AI agent safety context

### 2. **MCP Bridge for Claude Code** 🆕
- Work with analyzed projects **directly from Claude Code**
- Read files, execute commands, search files in the loaded project
- Get risk analysis and safety context for files
- Bridge the gap between different project directories!

## 📦 Setup

### Install Dependencies

```bash
pip install mcp fastmcp requests
```

### Configure Claude Code MCP

Add this to your `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cartographer": {
      "command": "python",
      "args": ["/Users/kcdacre8tor/cartocode/cartographer_mcp.py"]
    }
  }
}
```

## 🎯 Usage

### Step 1: Start Cartographer

The simplest way to launch:

```bash
# Start with project picker (recommended)
python3 cartographer.py

# Or analyze a specific project
python3 cartographer.py /path/to/your/project

# Custom port
python3 cartographer.py /path/to/your/project --port 3000

# Or use the alias (add to ~/.zshrc):
# alias carto="python3 /Users/kcdacre8tor/cartocode/cartographer.py"
carto
```

This will:
- Show an interactive **project picker** in your browser (if no path specified)
- Display recent projects from `~/.cartographer_history`
- Scan the selected project and analyze dependencies
- Open an interactive dashboard at http://localhost:3000
- Generate a risk map and save it as `CODEBASE_AGENT_CONTEXT.md`

### Step 2: Use Claude Code with MCP Bridge

Now when you're in Claude Code (even in a different directory!), you can:

```
# Check what project is loaded
> What project is currently loaded in Cartographer?

# Read files from the loaded project
> Read the package.json from the loaded project

# Execute commands in that project
> Run npm test in the loaded project

# Get risk analysis
> What's the risk score for lib/booking/types.ts?

# Search for files
> Find all TypeScript files in the loaded project
```

### Available MCP Tools

1. **get_loaded_project()** - See what project is currently loaded
2. **read_project_file(path)** - Read any file from the loaded project
3. **execute_in_project(command)** - Run shell commands in the project directory
4. **get_risk_map()** - Get the AI safety context / risk map
5. **search_project_files(pattern)** - Find files using glob patterns
6. **get_file_risk_info(filename)** - Get detailed risk analysis for a file

## 🔥 Example Workflow

```bash
# Terminal 1: Start cartographer on your main project
cd ~/
python ~/cartocode/cartographer.py ~/my-big-project

# Terminal 2: Open Claude Code anywhere
cd ~/some-other-directory
claude

# Now in Claude Code, you can work with my-big-project!
# > "Read the src/App.tsx file from the loaded project"
# > "What are the critical files in the loaded project?"
# > "Run git status in the loaded project"
```

## 🎨 Dashboard Views

- **Graph View** - Visual dependency graph with risk-based coloring
- **List View** - Sortable table of all files with risk scores
- **Concerns View** - Files grouped by domain concerns (auth, database, etc.)
- **Matrix View** - Binding points and architectural connections

## 🛡️ Risk Scoring

Files are scored 0-100 based on:
- **Fan-in** (35%): How many files depend on it
- **Fan-out** (15%): How many dependencies it has
- **Binding points** (25%): Interfaces, events, APIs it exposes
- **Complexity** (10%): Lines of code
- **High-risk patterns** (15%): API endpoints, data models, unsafe code
- **Git activity** (bonus): Recent change frequency

## 🏷️ Tags Explained

- 🔌 **interface** - Defines contracts (protocols, interfaces, traits)
- 📡 **event-driven** - Emits/receives events
- 🌐 **api-endpoint** - HTTP route handler
- 📤 **api-consumer** - Makes network calls
- 💾 **data-model** - Database/storage schema
- ⚙️ **config-dependent** - Reads env vars
- 🔄 **state-management** - App state logic
- ⚠️ **unsafe-code** - Contains unsafe/low-level code
- ⚡ **concurrent** - Uses concurrency primitives
- 🧪 **test** - Test file

## 🎯 Use Cases

1. **Onboarding** - Quickly understand a new codebase's structure and risks
2. **Refactoring** - Identify safe areas to modify vs critical binding points
3. **Code Review** - Assess blast radius of changes
4. **AI Pair Programming** - Give Claude context about project safety
5. **Technical Debt** - Find high-risk, untested files
6. **Cross-Project Work** - Work on Project A while Claude analyzes Project B

## 🔒 Security

The MCP bridge includes:
- Path validation to prevent directory traversal attacks
- Command timeout limits (30s)
- Read-only file access (no writes through MCP)
- CORS headers for dashboard API

## 📝 License

MIT
