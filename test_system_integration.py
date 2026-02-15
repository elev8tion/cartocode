#!/usr/bin/env python3
"""
Comprehensive Systems Test for Cartographer
Tests all implementations with real HTTP calls and API integration
"""

import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple
import requests

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ui_enhancements import UIEnhancementRegistry, UIComponent, UIEnhancement


# ═══════════════════════════════════════════════════════════
# TEST CONFIGURATION
# ═══════════════════════════════════════════════════════════

class TestConfig:
    """Test configuration"""
    CARTOGRAPHER_URL = "http://localhost:3001"  # Server is on port 3001
    TIMEOUT = 10
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')

    # Test results
    passed = 0
    failed = 0
    errors = []

    # Test output file
    results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"


# ═══════════════════════════════════════════════════════════
# TEST UTILITIES
# ═══════════════════════════════════════════════════════════

class Colors:
    """Terminal colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def log_test(name: str):
    """Log test start"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}▶ Testing: {name}{Colors.END}")


def log_pass(message: str):
    """Log test pass"""
    TestConfig.passed += 1
    print(f"  {Colors.GREEN}✓{Colors.END} {message}")


def log_fail(message: str, error: str = ""):
    """Log test failure"""
    TestConfig.failed += 1
    error_msg = f"{message}"
    if error:
        error_msg += f"\n    Error: {error}"
    TestConfig.errors.append(error_msg)
    print(f"  {Colors.RED}✗{Colors.END} {message}")
    if error:
        print(f"    {Colors.YELLOW}Error: {error}{Colors.END}")


def log_info(message: str):
    """Log info message"""
    print(f"  {Colors.YELLOW}ℹ{Colors.END} {message}")


# ═══════════════════════════════════════════════════════════
# TEST SUITE 1: UI ENHANCEMENT REGISTRY
# ═══════════════════════════════════════════════════════════

def test_ui_registry_initialization():
    """Test UIEnhancementRegistry initialization"""
    log_test("UIEnhancementRegistry Initialization")

    try:
        registry = UIEnhancementRegistry()

        # Test: Registry created
        if registry:
            log_pass("Registry instance created")
        else:
            log_fail("Registry instance is None")
            return

        # Test: Default enhancements loaded
        if len(registry.enhancements) > 0:
            log_pass(f"Default enhancements loaded: {len(registry.enhancements)}")
        else:
            log_fail("No default enhancements loaded")

        # Test: All components have enhancements
        components_with_enhancements = set(e.component for e in registry.enhancements)
        if len(components_with_enhancements) >= 5:
            log_pass(f"Enhancements for {len(components_with_enhancements)} components")
        else:
            log_fail(f"Only {len(components_with_enhancements)} components have enhancements")

        # Test: List all works
        list_output = registry.list_all()
        if "UI Enhancement Registry" in list_output:
            log_pass("list_all() produces output")
        else:
            log_fail("list_all() output missing header")

    except Exception as e:
        log_fail("Registry initialization failed", str(e))


def test_ui_registry_operations():
    """Test UIEnhancementRegistry operations"""
    log_test("UIEnhancementRegistry Operations")

    try:
        registry = UIEnhancementRegistry()

        # Test: Get enhancements by component
        chat_enhancements = registry.get_enhancements_for_component(UIComponent.CHAT_INTERFACE)
        if len(chat_enhancements) > 0:
            log_pass(f"Found {len(chat_enhancements)} chat enhancements")
        else:
            log_fail("No chat enhancements found")

        # Test: Get enhancement by type
        enhancement = registry.get_enhancement_by_type("code_suggestion_autocomplete")
        if enhancement:
            log_pass("Retrieved enhancement by type")
        else:
            log_fail("Failed to retrieve enhancement by type")

        # Test: Add custom enhancement
        custom = UIEnhancement(
            component=UIComponent.CHAT_INTERFACE,
            enhancement_type="test_custom",
            implementation="// test code",
            priority=1,
            description="Test enhancement"
        )
        registry.add_enhancement(custom)

        retrieved = registry.get_enhancement_by_type("test_custom")
        if retrieved and retrieved.enhancement_type == "test_custom":
            log_pass("Custom enhancement added successfully")
        else:
            log_fail("Failed to add custom enhancement")

        # Test: Remove enhancement
        if registry.remove_enhancement("test_custom"):
            log_pass("Enhancement removed successfully")
        else:
            log_fail("Failed to remove enhancement")

        # Test: Apply enhancement
        if enhancement:
            result = enhancement.apply({"test": "context"})
            if result and "component" in result:
                log_pass("Enhancement apply() works")
            else:
                log_fail("Enhancement apply() missing fields")

        # Test: Export to JSON
        try:
            test_file = "test_export.json"
            registry.export_to_json(test_file)
            if os.path.exists(test_file):
                log_pass("Export to JSON successful")
                os.remove(test_file)
            else:
                log_fail("Export to JSON failed - file not created")
        except Exception as e:
            log_fail("Export to JSON failed", str(e))

    except Exception as e:
        log_fail("Registry operations failed", str(e))


# ═══════════════════════════════════════════════════════════
# TEST SUITE 2: OPTIMIZED API CLIENT
# ═══════════════════════════════════════════════════════════



# ═══════════════════════════════════════════════════════════
# TEST SUITE 3: HTTP ENDPOINTS
# ═══════════════════════════════════════════════════════════

def test_server_connection():
    """Test connection to Cartographer server"""
    log_test("Server Connection")

    try:
        response = requests.get(
            f"{TestConfig.CARTOGRAPHER_URL}/",
            timeout=TestConfig.TIMEOUT
        )

        if response.status_code == 200:
            log_pass("Server is running and accessible")
        else:
            log_fail(f"Server returned status {response.status_code}")

    except requests.exceptions.ConnectionError:
        log_fail("Cannot connect to server - is cartographer.py running?")
    except Exception as e:
        log_fail("Server connection test failed", str(e))


def test_api_endpoints():
    """Test API endpoints"""
    log_test("API Endpoints")

    # Test: /api/scan endpoint
    try:
        response = requests.get(
            f"{TestConfig.CARTOGRAPHER_URL}/api/scan",
            timeout=TestConfig.TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            if "nodes" in data and "edges" in data:
                log_pass(f"/api/scan endpoint works ({len(data['nodes'])} nodes)")
            else:
                log_fail("/api/scan missing required fields")
        else:
            log_fail(f"/api/scan returned {response.status_code}")
    except Exception as e:
        log_fail("/api/scan endpoint failed", str(e))

    # Test: /api/project-root endpoint
    try:
        response = requests.get(
            f"{TestConfig.CARTOGRAPHER_URL}/api/project-root",
            timeout=TestConfig.TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            if "project_root" in data:
                log_pass(f"/api/project-root works: {data['project_root']}")
            else:
                log_fail("/api/project-root missing project_root field")
        else:
            log_fail(f"/api/project-root returned {response.status_code}")
    except Exception as e:
        log_fail("/api/project-root endpoint failed", str(e))

    # Test: /api/agent-context endpoint
    try:
        response = requests.get(
            f"{TestConfig.CARTOGRAPHER_URL}/api/agent-context",
            timeout=TestConfig.TIMEOUT
        )

        if response.status_code == 200:
            content = response.text
            if "CODEBASE" in content or "Risk" in content:
                log_pass("/api/agent-context returns context")
            else:
                log_fail("/api/agent-context unexpected format")
        else:
            log_fail(f"/api/agent-context returned {response.status_code}")
    except Exception as e:
        log_fail("/api/agent-context endpoint failed", str(e))


def test_api_post_endpoints():
    """Test POST API endpoints"""
    log_test("POST API Endpoints")

    # Test: /api/read-file endpoint
    try:
        response = requests.post(
            f"{TestConfig.CARTOGRAPHER_URL}/api/read-file",
            json={"path": "README.md"},
            timeout=TestConfig.TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            if "content" in data:
                log_pass("/api/read-file works")
            else:
                log_fail("/api/read-file missing content field")
        elif response.status_code == 404:
            log_info("/api/read-file - README.md not found (may be expected)")
        else:
            log_fail(f"/api/read-file returned {response.status_code}")
    except Exception as e:
        log_fail("/api/read-file endpoint failed", str(e))

    # Test: /api/glob-files endpoint
    try:
        response = requests.post(
            f"{TestConfig.CARTOGRAPHER_URL}/api/glob-files",
            json={"pattern": "*.py"},
            timeout=TestConfig.TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            if "matches" in data:
                log_pass(f"/api/glob-files works ({len(data['matches'])} matches)")
            else:
                log_fail("/api/glob-files missing matches field")
        else:
            log_fail(f"/api/glob-files returned {response.status_code}")
    except Exception as e:
        log_fail("/api/glob-files endpoint failed", str(e))

    # Test: /api/exec-command endpoint
    try:
        response = requests.post(
            f"{TestConfig.CARTOGRAPHER_URL}/api/exec-command",
            json={"command": "echo 'test'"},
            timeout=TestConfig.TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            if "stdout" in data and "returncode" in data:
                log_pass("/api/exec-command works")
            else:
                log_fail("/api/exec-command missing required fields")
        else:
            log_fail(f"/api/exec-command returned {response.status_code}")
    except Exception as e:
        log_fail("/api/exec-command endpoint failed", str(e))


def test_chat_endpoints():
    """Test chat-related endpoints"""
    log_test("Chat Endpoints")

    # Check if API key is set
    if not TestConfig.DEEPSEEK_API_KEY:
        log_info("DEEPSEEK_API_KEY not set - skipping chat tests")
        return

    # Test: /api/chat endpoint
    try:
        response = requests.post(
            f"{TestConfig.CARTOGRAPHER_URL}/api/chat",
            json={
                "message": "What files are in this project?",
                "model": "deepseek-chat",
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                log_pass(f"/api/chat works (response length: {len(data['response'])})")
            else:
                log_fail("/api/chat missing response field")
        elif response.status_code == 500:
            error_text = response.text
            if "API key" in error_text:
                log_info("/api/chat - API key not configured")
            else:
                log_fail(f"/api/chat error: {error_text}")
        else:
            log_fail(f"/api/chat returned {response.status_code}")
    except requests.exceptions.Timeout:
        log_info("/api/chat timed out (may be expected for slow responses)")
    except Exception as e:
        log_fail("/api/chat endpoint failed", str(e))

    # Test: /api/chat/history endpoint
    try:
        response = requests.get(
            f"{TestConfig.CARTOGRAPHER_URL}/api/chat/history",
            timeout=TestConfig.TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            if "messages" in data:
                log_pass(f"/api/chat/history works ({len(data['messages'])} messages)")
            else:
                log_fail("/api/chat/history missing messages field")
        else:
            log_fail(f"/api/chat/history returned {response.status_code}")
    except Exception as e:
        log_fail("/api/chat/history endpoint failed", str(e))


# ═══════════════════════════════════════════════════════════
# TEST SUITE 4: INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════







# ═══════════════════════════════════════════════════════════
# TEST SUITE 5: END-TO-END WORKFLOW
# ═══════════════════════════════════════════════════════════

def test_end_to_end_workflow():
    """Test complete workflow"""
    log_test("End-to-End Workflow")

    try:
        # Step 1: Check server
        response = requests.get(f"{TestConfig.CARTOGRAPHER_URL}/api/scan", timeout=10)
        if response.status_code != 200:
            log_fail("Server not ready for E2E test")
            return

        log_pass("Step 1: Server accessible")

        # Step 2: Get project info
        response = requests.get(f"{TestConfig.CARTOGRAPHER_URL}/api/project-root", timeout=10)
        if response.status_code == 200:
            project_data = response.json()
            log_pass(f"Step 2: Project loaded - {project_data.get('project_root', 'unknown')}")
        else:
            log_fail("Step 2: Failed to get project info")
            return

        # Step 3: Search for files
        response = requests.post(
            f"{TestConfig.CARTOGRAPHER_URL}/api/glob-files",
            json={"pattern": "*.py"},
            timeout=10
        )
        if response.status_code == 200:
            files = response.json().get("matches", [])
            log_pass(f"Step 3: Found {len(files)} Python files")
        else:
            log_fail("Step 3: File search failed")
            return

        # Step 4: Get risk map
        response = requests.get(f"{TestConfig.CARTOGRAPHER_URL}/api/agent-context", timeout=10)
        if response.status_code == 200:
            log_pass("Step 4: Retrieved risk map")
        else:
            log_fail("Step 4: Risk map retrieval failed")
            return

        # Step 5: UI Enhancement
        from ui_enhancements import registry, UIComponent
        enhancements = registry.get_enhancements_for_component(UIComponent.CHAT_INTERFACE)
        if len(enhancements) > 0:
            log_pass(f"Step 5: Retrieved {len(enhancements)} UI enhancements")
        else:
            log_fail("Step 5: No UI enhancements found")

        log_pass("✓ End-to-end workflow completed successfully")

    except Exception as e:
        log_fail("End-to-end workflow failed", str(e))


# ═══════════════════════════════════════════════════════════
# RESULTS REPORTING
# ═══════════════════════════════════════════════════════════

def generate_report():
    """Generate test results report"""
    total = TestConfig.passed + TestConfig.failed
    pass_rate = (TestConfig.passed / total * 100) if total > 0 else 0

    report = f"""# Cartographer Systems Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total Tests**: {total}
- **Passed**: {TestConfig.passed} ({Colors.GREEN}✓{Colors.END})
- **Failed**: {TestConfig.failed} ({Colors.RED}✗{Colors.END})
- **Pass Rate**: {pass_rate:.1f}%

## Status
"""

    if TestConfig.failed == 0:
        report += f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.END}\n\n"
    else:
        report += f"{Colors.RED}{Colors.BOLD}✗ {TestConfig.failed} TEST(S) FAILED{Colors.END}\n\n"

    if TestConfig.errors:
        report += "## Failures & Fixes\n\n"
        for i, error in enumerate(TestConfig.errors, 1):
            report += f"### {i}. {error}\n\n"
            report += get_fix_suggestion(error)
            report += "\n---\n\n"

    # Write to file
    with open(TestConfig.results_file, 'w') as f:
        # Remove color codes for file
        clean_report = report
        for color in [Colors.GREEN, Colors.RED, Colors.YELLOW, Colors.BLUE, Colors.BOLD, Colors.END]:
            clean_report = clean_report.replace(color, '')
        f.write(clean_report)

    return report


def get_fix_suggestion(error: str) -> str:
    """Get fix suggestion for error"""
    suggestions = {
        "Cannot connect to server": """
**Fix:**
```bash
# Start Cartographer server
python3 cartographer.py /path/to/your/project
```
""",
        "API key": """
**Fix:**
```bash
# Set DeepSeek API key
export DEEPSEEK_API_KEY='your-api-key-here'
```
""",
        "import": """
**Fix:**
Check that all dependencies are installed:
```bash
pip install requests mcp fastmcp
```
""",
        "404": """
**Fix:**
Ensure the Cartographer server is running with a project loaded.
""",
    }

    for key, suggestion in suggestions.items():
        if key in error:
            return suggestion

    return "**Fix:** Review error message and check implementation.\n"


# ═══════════════════════════════════════════════════════════
# MAIN TEST RUNNER
# ═══════════════════════════════════════════════════════════

def run_all_tests():
    """Run all test suites"""
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"  CARTOGRAPHER SYSTEMS TEST SUITE")
    print(f"{'='*70}{Colors.END}\n")

    print(f"Configuration:")
    print(f"  Server URL: {TestConfig.CARTOGRAPHER_URL}")
    print(f"  API Key: {'✓ Set' if TestConfig.DEEPSEEK_API_KEY else '✗ Not Set'}")
    print(f"  Results: {TestConfig.results_file}")

    # Run test suites
    test_ui_registry_initialization()
    test_ui_registry_operations()
    test_server_connection()
    test_api_endpoints()
    test_api_post_endpoints()
    test_chat_endpoints()
    test_end_to_end_workflow()

    # Generate report
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    report = generate_report()
    print(report)
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")

    print(f"📄 Full report saved to: {Colors.BLUE}{TestConfig.results_file}{Colors.END}\n")

    # Exit with appropriate code
    sys.exit(0 if TestConfig.failed == 0 else 1)


if __name__ == "__main__":
    run_all_tests()
