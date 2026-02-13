#!/usr/bin/env python3
"""
Cartographer MCP Server
Bridges Claude Code to whatever project is loaded in the Cartographer dashboard
"""
import asyncio
import json
from functools import lru_cache, wraps
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

import requests
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Cartographer Bridge")

# Configuration
CARTOGRAPHER_URL = "http://localhost:3001"  # Match actual server port

# ═══════════════════════════════════════════════════════════
# OPTIMIZED API CLIENT FOR CODEBASE MANIPULATION
# ═══════════════════════════════════════════════════════════

class OptimizedAPIClient:
    """Enhanced API client for chat-based codebase manipulation"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or CARTOGRAPHER_URL
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)

    def cached_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Cached API request with automatic retry"""
        cache_key = f"{method}:{endpoint}:{json.dumps(kwargs, sort_keys=True)}"

        if cache_key in self._cache:
            cached_time, response = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                return response

        for attempt in range(3):
            try:
                url = f"{self.base_url}/{endpoint}"
                resp = requests.request(method, url, timeout=10, **kwargs)
                resp.raise_for_status()
                result = resp.json() if resp.content else {}
                self._cache[cache_key] = (datetime.now(), result)
                return result
            except Exception as e:
                if attempt == 2:
                    raise
                import time
                time.sleep(1 * (attempt + 1))

    def manipulate_codebase(self, file_path: str, changes: Dict) -> Dict:
        """Optimized method for chat-driven codebase manipulation"""
        return self.cached_request(
            "POST",
            "api/codebase/manipulate",
            json={"file_path": file_path, "changes": changes}
        )

    def ui_enhancement(self, component: str, enhancements: Dict) -> Dict:
        """Apply UI enhancements from chat commands"""
        return self.cached_request(
            "POST",
            "api/ui/enhance",
            json={"component": component, "enhancements": enhancements}
        )

# Decorator for API-optimized functions
def api_optimized(func):
    """Decorator for API-optimized functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        client = OptimizedAPIClient()
        kwargs['api_client'] = client
        return func(*args, **kwargs)
    return wrapper

# ═══════════════════════════════════════════════════════════
# UI ENHANCEMENT REGISTRY
# ═══════════════════════════════════════════════════════════

class UIComponent(Enum):
    CODE_EDITOR = "code_editor"
    FILE_TREE = "file_tree"
    TERMINAL = "terminal"
    CHAT_INTERFACE = "chat_interface"
    RISK_VISUALIZER = "risk_visualizer"
    GRAPH_VIEW = "graph_view"
    LIST_VIEW = "list_view"

@dataclass
class UIEnhancement:
    component: UIComponent
    enhancement_type: str
    implementation: str
    priority: int = 1

    def apply(self, context: Dict) -> Dict:
        """Apply this enhancement to the given context"""
        return {
            "component": self.component.value,
            "enhancement": self.enhancement_type,
            "code_snippet": self.implementation,
            "context_applied": context,
            "priority": self.priority
        }

class UIEnhancementRegistry:
    """Registry of reusable UI enhancements"""

    def __init__(self):
        self.enhancements = self._load_default_enhancements()

    def _load_default_enhancements(self) -> List[UIEnhancement]:
        return [
            # Chat Interface Enhancements
            UIEnhancement(
                component=UIComponent.CHAT_INTERFACE,
                enhancement_type="code_suggestion",
                implementation="""
// Auto-suggest code changes based on chat
function enableCodeSuggestions(chatInput) {
    chatInput.addEventListener('input', async (e) => {
        if (e.target.value.includes('modify') || e.target.value.includes('add')) {
            const suggestions = await fetchCodeSuggestions(e.target.value);
            showSuggestions(suggestions);
        }
    });
}
                """,
                priority=1
            ),

            UIEnhancement(
                component=UIComponent.CHAT_INTERFACE,
                enhancement_type="syntax_highlighting",
                implementation="""
// Enhanced syntax highlighting for code in chat
function highlightChatCode(messageElement) {
    const codeBlocks = messageElement.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        hljs.highlightElement(block);
        addCopyButton(block);
    });
}
                """,
                priority=2
            ),

            # Risk Visualizer Enhancements
            UIEnhancement(
                component=UIComponent.RISK_VISUALIZER,
                enhancement_type="heatmap_overlay",
                implementation="""
// Add risk heatmap overlay to file tree
function addRiskHeatmap(fileNodes, riskData) {
    fileNodes.forEach(node => {
        const risk = riskData[node.path] || 0;
        const color = getRiskColor(risk);
        node.style.background = `linear-gradient(90deg, ${color}20, transparent)`;
        node.setAttribute('data-risk', risk);
    });
}

function getRiskColor(risk) {
    if (risk >= 75) return '#ef4444';
    if (risk >= 50) return '#f97316';
    if (risk >= 25) return '#fbbf24';
    return '#10b981';
}
                """,
                priority=1
            ),

            # Graph View Enhancements
            UIEnhancement(
                component=UIComponent.GRAPH_VIEW,
                enhancement_type="dependency_highlighting",
                implementation="""
// Highlight dependency chains on hover
function highlightDependencyChain(nodeId, graphData) {
    const visited = new Set();
    const queue = [nodeId];

    while (queue.length > 0) {
        const current = queue.shift();
        if (visited.has(current)) continue;
        visited.add(current);

        // Highlight node
        const node = document.querySelector(`[data-node-id="${current}"]`);
        if (node) {
            node.classList.add('dependency-highlight');
        }

        // Find connected nodes
        graphData.edges
            .filter(e => e.source === current || e.target === current)
            .forEach(e => {
                const next = e.source === current ? e.target : e.source;
                queue.push(next);
            });
    }
}
                """,
                priority=1
            ),

            # Code Editor Enhancements
            UIEnhancement(
                component=UIComponent.CODE_EDITOR,
                enhancement_type="inline_risk_indicators",
                implementation="""
// Show inline risk indicators in code editor
function addInlineRiskIndicators(editor, riskAnalysis) {
    riskAnalysis.bindings.forEach(binding => {
        const line = binding.line;
        const riskLevel = binding.risk;

        editor.addLineWidget(line, createRiskWidget(riskLevel, binding));
    });
}

function createRiskWidget(risk, binding) {
    const widget = document.createElement('div');
    widget.className = 'risk-indicator';
    widget.innerHTML = `
        <span class="risk-icon" style="color: ${getRiskColor(risk)}">⚠️</span>
        <span class="risk-text">${binding.type}: ${binding.description}</span>
    `;
    return widget;
}
                """,
                priority=2
            ),

            # File Tree Enhancements
            UIEnhancement(
                component=UIComponent.FILE_TREE,
                enhancement_type="smart_filtering",
                implementation="""
// Smart filtering with fuzzy search
function enableSmartFiltering(fileTree, filterInput) {
    filterInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const files = fileTree.querySelectorAll('.file-item');

        files.forEach(file => {
            const path = file.getAttribute('data-path').toLowerCase();
            const score = fuzzyMatch(query, path);

            if (score > 0) {
                file.style.display = '';
                file.style.opacity = Math.min(1, score / 10);
            } else {
                file.style.display = 'none';
            }
        });
    });
}

function fuzzyMatch(query, text) {
    let score = 0;
    let queryIndex = 0;

    for (let i = 0; i < text.length && queryIndex < query.length; i++) {
        if (text[i] === query[queryIndex]) {
            score += 1;
            queryIndex++;
        }
    }

    return queryIndex === query.length ? score : 0;
}
                """,
                priority=1
            ),
        ]

    def get_enhancements_for_component(self, component: UIComponent) -> List[UIEnhancement]:
        """Get all enhancements for a specific component"""
        return [e for e in self.enhancements if e.component == component]

    def get_enhancement_by_type(self, enhancement_type: str) -> Optional[UIEnhancement]:
        """Get enhancement by type"""
        for e in self.enhancements:
            if e.enhancement_type == enhancement_type:
                return e
        return None

    def add_enhancement(self, enhancement: UIEnhancement):
        """Add a custom enhancement to the registry"""
        self.enhancements.append(enhancement)

    def apply_all_for_component(self, component: UIComponent, context: Dict) -> List[Dict]:
        """Apply all enhancements for a component"""
        enhancements = self.get_enhancements_for_component(component)
        enhancements.sort(key=lambda x: x.priority)
        return [e.apply(context) for e in enhancements]

# Global registry instance
ui_registry = UIEnhancementRegistry()

def get_project_root():
    """Get the currently loaded project path from cartographer"""
    try:
        resp = requests.get(f"{CARTOGRAPHER_URL}/api/project-root", timeout=5)
        resp.raise_for_status()
        return resp.json()['project_root']
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Cartographer: {e}\nMake sure cartographer.py is running!")

@mcp.tool()
def get_loaded_project() -> str:
    """Get information about the currently loaded project in the Cartographer dashboard.

    Returns:
        Project root path and metadata
    """
    try:
        # Get project root
        root_resp = requests.get(f"{CARTOGRAPHER_URL}/api/project-root", timeout=5)
        root_resp.raise_for_status()
        project_root = root_resp.json()['project_root']

        # Get scan data for metadata
        scan_resp = requests.get(f"{CARTOGRAPHER_URL}/api/scan", timeout=5)
        scan_resp.raise_for_status()
        metadata = scan_resp.json().get('metadata', {})

        return f"""Currently Loaded Project:
Path: {project_root}
Name: {metadata.get('project_name', 'Unknown')}
Files: {metadata.get('total_files', 0)}
Languages: {', '.join(metadata.get('languages', []))}
Health Score: {metadata.get('health_score', 0)}/100

You can now use the other Cartographer tools to work with this project!
"""
    except Exception as e:
        return f"Error: Failed to connect to Cartographer. Make sure it's running on {CARTOGRAPHER_URL}\n{str(e)}"

@mcp.tool()
def read_project_file(path: str) -> str:
    """Read a file from the loaded project.

    Args:
        path: Relative path to file in the project (e.g., "src/App.tsx")

    Returns:
        File contents
    """
    try:
        resp = requests.post(
            f"{CARTOGRAPHER_URL}/api/read-file",
            json={"path": path},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        return data['content']
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"Error: File not found: {path}"
        elif e.response.status_code == 403:
            return f"Error: Access denied - path is outside project: {path}"
        else:
            return f"Error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def execute_in_project(command: str) -> str:
    """Execute a shell command in the loaded project's directory.

    Args:
        command: Shell command to execute (e.g., "npm test", "git status")

    Returns:
        Command output (stdout and stderr)
    """
    try:
        resp = requests.post(
            f"{CARTOGRAPHER_URL}/api/exec-command",
            json={"command": command},
            timeout=35
        )
        resp.raise_for_status()
        result = resp.json()

        output = []
        if result['stdout']:
            output.append(f"STDOUT:\n{result['stdout']}")
        if result['stderr']:
            output.append(f"STDERR:\n{result['stderr']}")
        output.append(f"\nExit code: {result['returncode']}")

        return '\n'.join(output)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 408:
            return "Error: Command timed out (30s limit)"
        else:
            return f"Error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@mcp.tool()
def get_risk_map() -> str:
    """Get the AI agent safety context / risk map for the loaded project.
    This shows critical files, binding points, and safe-to-modify files.

    Returns:
        Markdown-formatted risk map with file safety information
    """
    try:
        resp = requests.get(f"{CARTOGRAPHER_URL}/api/agent-context", timeout=5)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"Error getting risk map: {str(e)}"

@mcp.tool()
def search_project_files(pattern: str) -> str:
    """Search for files in the loaded project using glob patterns.

    Args:
        pattern: Glob pattern (e.g., "**/*.tsx", "src/**/*.ts", "*.json")

    Returns:
        List of matching file paths
    """
    try:
        resp = requests.post(
            f"{CARTOGRAPHER_URL}/api/glob-files",
            json={"pattern": pattern},
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        matches = result['matches']

        if not matches:
            return f"No files found matching pattern: {pattern}"

        return f"Found {len(matches)} files:\n" + '\n'.join(f"  - {m}" for m in matches[:100])
    except Exception as e:
        return f"Error searching files: {str(e)}"

@mcp.tool()
def get_file_risk_info(filename: str) -> str:
    """Get detailed risk analysis for a specific file in the loaded project.

    Args:
        filename: Name or path of the file to analyze

    Returns:
        Risk score, dependencies, tags, and safety information
    """
    try:
        resp = requests.get(f"{CARTOGRAPHER_URL}/api/scan", timeout=5)
        resp.raise_for_status()
        scan_data = resp.json()

        # Find matching nodes
        matches = [
            n for n in scan_data['nodes']
            if filename in n['path'] or filename == n['name']
        ]

        if not matches:
            return f"File not found: {filename}"

        if len(matches) > 1:
            paths = '\n'.join(f"  - {m['path']}" for m in matches[:10])
            return f"Multiple files match '{filename}':\n{paths}\n\nPlease be more specific."

        node = matches[0]

        output = [
            f"File: {node['path']}",
            f"Risk Score: {node['risk_score']}/100",
            f"Language: {node['language']}",
            f"Lines: {node['lines']}",
            f"Complexity: {node['complexity']}",
            f"Dependents (Fan-In): {node['fan_in']}",
            f"Dependencies (Fan-Out): {node['fan_out']}",
            f"Has Tests: {'Yes' if node['has_tests'] else 'No'}",
        ]

        if node.get('tags'):
            output.append(f"Tags: {', '.join(node['tags'])}")

        if node.get('concerns'):
            output.append(f"Concerns: {', '.join(node['concerns'])}")

        if node.get('plain_english'):
            output.append(f"\n{node['plain_english']}")

        return '\n'.join(output)
    except Exception as e:
        return f"Error analyzing file: {str(e)}"

@mcp.tool()
def apply_ui_enhancement(component: str, enhancement_type: str, context: dict = None) -> str:
    """Apply a UI enhancement to a specific component.

    Args:
        component: Component name (chat_interface, risk_visualizer, graph_view, etc.)
        enhancement_type: Type of enhancement (code_suggestion, syntax_highlighting, etc.)
        context: Optional context for the enhancement

    Returns:
        Applied enhancement details and implementation code
    """
    try:
        # Convert string to enum
        component_enum = UIComponent(component)
        enhancement = ui_registry.get_enhancement_by_type(enhancement_type)

        if not enhancement:
            available = [e.enhancement_type for e in ui_registry.enhancements]
            return f"Enhancement '{enhancement_type}' not found. Available: {', '.join(available)}"

        if enhancement.component != component_enum:
            return f"Enhancement '{enhancement_type}' is for {enhancement.component.value}, not {component}"

        result = enhancement.apply(context or {})
        return json.dumps(result, indent=2)
    except ValueError:
        valid_components = [c.value for c in UIComponent]
        return f"Invalid component. Valid options: {', '.join(valid_components)}"
    except Exception as e:
        return f"Error applying enhancement: {str(e)}"

@mcp.tool()
def list_ui_enhancements(component: str = None) -> str:
    """List available UI enhancements, optionally filtered by component.

    Args:
        component: Optional component name to filter by

    Returns:
        List of available enhancements
    """
    try:
        if component:
            component_enum = UIComponent(component)
            enhancements = ui_registry.get_enhancements_for_component(component_enum)
        else:
            enhancements = ui_registry.enhancements

        output = []
        for e in enhancements:
            output.append(f"• {e.enhancement_type} ({e.component.value}) - Priority: {e.priority}")

        if not output:
            return f"No enhancements found{' for ' + component if component else ''}"

        header = f"Available UI Enhancements{' for ' + component if component else ''}:\n"
        return header + '\n'.join(output)
    except ValueError:
        valid_components = [c.value for c in UIComponent]
        return f"Invalid component. Valid options: {', '.join(valid_components)}"
    except Exception as e:
        return f"Error listing enhancements: {str(e)}"

@mcp.tool()
@api_optimized
def manipulate_codebase_optimized(file_path: str, changes: dict, api_client: OptimizedAPIClient = None) -> str:
    """Perform optimized codebase manipulation with caching and retry logic.

    Args:
        file_path: Path to the file to modify
        changes: Dictionary of changes to apply (e.g., {"add_function": {...}, "update_line": {...}})

    Returns:
        Result of the manipulation
    """
    try:
        result = api_client.manipulate_codebase(file_path, changes)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error manipulating codebase: {str(e)}"

@mcp.tool()
@api_optimized
def enhance_ui_component(component: str, enhancements: dict, api_client: OptimizedAPIClient = None) -> str:
    """Apply UI enhancements to a component with optimization.

    Args:
        component: Component identifier
        enhancements: Dictionary of enhancement parameters

    Returns:
        Result of the enhancement
    """
    try:
        result = api_client.ui_enhancement(component, enhancements)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error enhancing UI: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
