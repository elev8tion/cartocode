#!/usr/bin/env python3
"""
Cartographer MCP Server
Bridges Claude Code to whatever project is loaded in the Cartographer dashboard
"""
import requests
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Cartographer Bridge")

# Configuration
CARTOGRAPHER_URL = "http://localhost:3000"

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

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
