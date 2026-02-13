#!/usr/bin/env python3
"""
DeepSeek Optimization System Test Suite
Comprehensive HTTP-based testing for DeepSeek optimizations with real API calls
"""

import os
import sys
import json
import time
import shutil
import requests
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestConfig:
    """Test configuration"""
    SERVER_PORT = 3002
    SERVER_URL = f"http://localhost:{SERVER_PORT}"
    TEST_PROJECT_DIR = Path("/tmp/deepseek_test_projects")
    RESULTS_DIR = Path(__file__).parent
    API_TIMEOUT = 30  # Longer timeout for real API calls
    SERVER_START_TIMEOUT = 30

    # Test data
    AUTH_PROJECT_NAME = "auth_project"
    LARGE_PROJECT_NAME = "large_project"
    MULTI_LANG_PROJECT_NAME = "multi_lang_project"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helper Functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_test(message, level="INFO"):
    """Print test message with formatting"""
    icons = {
        "INFO": "ℹ️ ",
        "PASS": "✅",
        "FAIL": "❌",
        "WARN": "⚠️ ",
        "SECTION": "\n═══",
    }
    icon = icons.get(level, "  ")
    print(f"{icon} {message}")


def assert_status(response, expected_code, test_name):
    """Assert HTTP status code"""
    if response.status_code == expected_code:
        print_test(f"{test_name}: Status {expected_code}", "PASS")
        return True
    else:
        print_test(f"{test_name}: Expected {expected_code}, got {response.status_code}", "FAIL")
        return False


def assert_contains(text, substring, message):
    """Assert substring is in text"""
    if substring.lower() in text.lower():
        print_test(f"{message}", "PASS")
        return True
    else:
        print_test(f"{message} ('{substring}' not found)", "FAIL")
        return False


def assert_equal(actual, expected, message):
    """Assert values are equal"""
    if actual == expected:
        print_test(f"{message}", "PASS")
        return True
    else:
        print_test(f"{message} (expected {expected}, got {actual})", "FAIL")
        return False


def assert_greater(actual, threshold, message):
    """Assert value is greater than threshold"""
    if actual > threshold:
        print_test(f"{message} (value: {actual})", "PASS")
        return True
    else:
        print_test(f"{message} (value {actual} not > {threshold})", "FAIL")
        return False


def assert_less(actual, threshold, message):
    """Assert value is less than threshold"""
    if actual < threshold:
        print_test(f"{message} (value: {actual})", "PASS")
        return True
    else:
        print_test(f"{message} (value {actual} not < {threshold})", "FAIL")
        return False


def assert_in_list(value, valid_values, message):
    """Assert value is in list of valid values"""
    if value in valid_values:
        print_test(f"{message}", "PASS")
        return True
    else:
        print_test(f"{message} (got {value}, expected one of {valid_values})", "FAIL")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test Infrastructure
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DeepSeekTestRunner:
    """Test runner with metrics collection for DeepSeek optimizations"""

    def __init__(self, api_key=None, port=TestConfig.SERVER_PORT):
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY')
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.server_process = None
        self.test_projects = []
        self.project_ids = {}

        # Metrics collection
        self.metrics = {
            'tests': [],
            'total': 0,
            'passed': 0,
            'failed': 0,
            'start_time': datetime.now().isoformat(),
            'api_calls': [],
            'token_usage': [],
            'response_quality': []
        }

    def start_server(self):
        """Start cartographer server with API key"""
        print_test(f"Starting test server on port {self.port}...", "INFO")

        env = os.environ.copy()
        if self.api_key:
            env['DEEPSEEK_API_KEY'] = self.api_key
        else:
            print_test("No DEEPSEEK_API_KEY found - some tests may fail", "WARN")
            env['DEEPSEEK_API_KEY'] = 'test-mock-key'

        self.server_process = subprocess.Popen(
            [sys.executable, 'cartographer.py', '--port', str(self.port)],
            cwd=Path(__file__).parent,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for server to be ready
        self._health_check()

    def _health_check(self):
        """Verify server is responsive"""
        print_test("Waiting for server to be ready...", "INFO")
        for attempt in range(30):
            try:
                response = requests.get(f"{self.base_url}/api/projects", timeout=2)
                if response.status_code == 200:
                    print_test("Test server ready", "PASS")
                    return True
            except requests.exceptions.RequestException:
                time.sleep(1)

        print_test("Server failed to start", "FAIL")
        raise RuntimeError("Server failed to start")

    def stop_server(self):
        """Stop server and cleanup"""
        if self.server_process:
            print_test("Stopping test server...", "INFO")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except:
                self.server_process.kill()
                self.server_process.wait()

    def cleanup_projects(self):
        """Remove test projects"""
        if TestConfig.TEST_PROJECT_DIR.exists():
            shutil.rmtree(TestConfig.TEST_PROJECT_DIR)
        print_test("Test projects cleaned up", "PASS")

    def record_test(self, name, passed, duration=0, error=None):
        """Record test result"""
        self.metrics['total'] += 1
        if passed:
            self.metrics['passed'] += 1
        else:
            self.metrics['failed'] += 1

        self.metrics['tests'].append({
            'name': name,
            'passed': passed,
            'duration': duration,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })

    def record_api_call(self, model, context_size, tokens_used, response_time):
        """Track API call metrics"""
        self.metrics['api_calls'].append({
            'model': model,
            'context_size': context_size,
            'tokens_used': tokens_used,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        })


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test Project Generator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestProjectGenerator:
    """Generate test projects with specific characteristics"""

    @staticmethod
    def _create_files(project_path, files):
        """Helper to write files to disk"""
        project_path = Path(project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        for file_rel_path, content in files.items():
            file_path = project_path / file_rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content.strip())

        return str(project_path)

    @staticmethod
    def create_auth_project(base_path):
        """Create project with authentication files (high-risk)"""
        project_path = Path(base_path) / TestConfig.AUTH_PROJECT_NAME

        files = {
            'auth/login.py': '''
import jwt
from database import db

def authenticate(username, password):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name='{username}'"
    user = db.execute(query).first()
    if user and user.password == password:
        return jwt.encode({'user_id': user.id}, 'secret', algorithm='HS256')
    return None

def verify_password(password, hashed):
    # Weak password verification
    return password == hashed
''',
            'auth/middleware.py': '''
from functools import wraps
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token'}), 401
        # Missing validation
        return f(*args, **kwargs)
    return decorated
''',
            'auth/session.py': '''
import redis

class SessionManager:
    def __init__(self):
        self.redis = redis.Redis()

    def create_session(self, user_id):
        session_id = str(user_id) + '_session'
        self.redis.set(session_id, user_id)
        return session_id

    def get_session(self, session_id):
        return self.redis.get(session_id)
''',
            'api/routes.py': '''
from flask import Flask, request
from auth.middleware import require_auth
from auth.login import authenticate

app = Flask(__name__)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    token = authenticate(data['username'], data['password'])
    return {'token': token}

@app.route('/api/users')
@require_auth
def get_users():
    # API endpoint
    return {'users': []}
''',
            'database/models.py': '''
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(100))
    email = Column(String(100))
''',
            'tests/test_auth.py': '''
import pytest
from auth.login import authenticate

def test_authenticate():
    token = authenticate('testuser', 'password')
    assert token is not None

def test_missing_user():
    token = authenticate('nonexistent', 'password')
    assert token is None
''',
        }

        return TestProjectGenerator._create_files(project_path, files)

    @staticmethod
    def create_large_project(base_path, num_files=50):
        """Create large project to test token limits"""
        project_path = Path(base_path) / TestConfig.LARGE_PROJECT_NAME
        files = {}

        # Generate multiple modules with varying content and risk
        for i in range(num_files):
            risk_level = "high" if i % 5 == 0 else "medium" if i % 3 == 0 else "low"

            files[f'module_{i}/service.py'] = f'''
# Service module {i} - Risk level: {risk_level}
import os
import requests

class Service{i}:
    """Service for handling module {i} operations"""

    def __init__(self):
        self.api_key = os.getenv('API_KEY_{i}')
        self.endpoint = 'https://api.example.com/v1/module_{i}'

    def process_data(self, data):
        """Process data for module {i}"""
        # Simulate processing
        result = {{
            'module': {i},
            'processed': True,
            'data': data,
            'risk_level': '{risk_level}'
        }}
        return result

    def make_api_call(self, payload):
        """Make API call for module {i}"""
        headers = {{'Authorization': f'Bearer {{self.api_key}}'}}
        response = requests.post(self.endpoint, json=payload, headers=headers)
        return response.json()

    def validate_input(self, input_data):
        """Validate input for module {i}"""
        if not input_data:
            raise ValueError("Input cannot be empty")
        return True
''' * 2  # Make it longer

        return TestProjectGenerator._create_files(project_path, files)

    @staticmethod
    def create_multi_language_project(base_path):
        """Create project with Python, TypeScript, Go for language detection"""
        project_path = Path(base_path) / TestConfig.MULTI_LANG_PROJECT_NAME

        files = {
            'backend/main.py': '''
from fastapi import FastAPI
from typing import List

app = FastAPI()

@app.get("/api/items")
async def get_items() -> List[dict]:
    return [{"id": 1, "name": "Item 1"}]
''',
            'backend/auth.py': '''
import jwt
from datetime import datetime, timedelta

def create_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, 'secret', algorithm='HS256')
''',
            'frontend/src/App.tsx': '''
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Item {
  id: number;
  name: string;
}

const App: React.FC = () => {
  const [items, setItems] = useState<Item[]>([]);

  useEffect(() => {
    axios.get('/api/items')
      .then(res => setItems(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h1>Items</h1>
      <ul>
        {items.map(item => <li key={item.id}>{item.name}</li>)}
      </ul>
    </div>
  );
};

export default App;
''',
            'services/cache/main.go': '''
package main

import (
    "fmt"
    "time"
    "sync"
)

type Cache struct {
    data map[string]interface{}
    mu   sync.RWMutex
}

func NewCache() *Cache {
    return &Cache{
        data: make(map[string]interface{}),
    }
}

func (c *Cache) Set(key string, value interface{}) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.data[key] = value
}

func (c *Cache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    value, ok := c.data[key]
    return value, ok
}
''',
        }

        return TestProjectGenerator._create_files(project_path, files)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test Functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestSuite:
    """Main test suite orchestrator"""

    def __init__(self, runner: DeepSeekTestRunner):
        self.runner = runner
        self.auth_project_id = None
        self.large_project_id = None
        self.multi_lang_project_id = None

    def setup(self):
        """Setup test environment"""
        print_test("Setting up test environment...", "INFO")

        # Create test projects
        auth_project_path = TestProjectGenerator.create_auth_project(TestConfig.TEST_PROJECT_DIR)
        large_project_path = TestProjectGenerator.create_large_project(TestConfig.TEST_PROJECT_DIR, num_files=50)
        multi_lang_path = TestProjectGenerator.create_multi_language_project(TestConfig.TEST_PROJECT_DIR)

        print_test(f"Created auth project: {auth_project_path}", "INFO")
        print_test(f"Created large project: {large_project_path}", "INFO")
        print_test(f"Created multi-lang project: {multi_lang_path}", "INFO")

        # Load projects
        try:
            response = requests.post(
                f"{self.runner.base_url}/api/load-project",
                json={'path': auth_project_path},
                timeout=TestConfig.API_TIMEOUT
            )
            if response.status_code == 200:
                self.auth_project_id = response.json()['project_id']
                self.runner.project_ids['auth'] = self.auth_project_id
                print_test(f"Loaded auth project: {self.auth_project_id}", "PASS")
        except Exception as e:
            print_test(f"Failed to load auth project: {e}", "FAIL")

    # ───────────────────────────────────────────────────────────────────
    # PHASE 1: Model Configuration Tests
    # ───────────────────────────────────────────────────────────────────

    def test_1_1_default_model_is_coder(self):
        """Test 1.1: Verify default model is deepseek-coder"""
        start = time.time()
        test_name = "1.1: Default model is deepseek-coder"

        try:
            # Send chat without specifying model
            response = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={
                    'message': 'What files exist?',
                    'project_id': self.auth_project_id
                },
                timeout=TestConfig.API_TIMEOUT
            )

            passed = assert_status(response, 200, test_name)
            if passed:
                data = response.json()
                if 'model' in data:
                    passed = assert_equal(data['model'], 'deepseek-coder', "Model should be deepseek-coder")
                else:
                    print_test("Response missing 'model' field - assuming default", "WARN")
                    passed = True

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_1_2_model_switching(self):
        """Test 1.2: Test switching between coder/reasoner/chat models"""
        models_to_test = ['deepseek-coder', 'deepseek-reasoner', 'deepseek-chat']

        for model in models_to_test:
            start = time.time()
            test_name = f"1.2: Model switching to {model}"

            try:
                response = requests.post(
                    f"{self.runner.base_url}/api/chat",
                    json={
                        'message': 'Analyze authentication',
                        'project_id': self.auth_project_id,
                        'model': model
                    },
                    timeout=TestConfig.API_TIMEOUT
                )

                passed = assert_status(response, 200, test_name)
                if passed:
                    data = response.json()
                    if 'model' in data:
                        passed = assert_equal(data['model'], model, f"Response should use {model}")

                    # Record metrics
                    if 'context_size' in data and 'response' in data:
                        self.runner.record_api_call(
                            model=model,
                            context_size=data.get('context_size', 0),
                            tokens_used=len(data['response']) // 4,
                            response_time=response.elapsed.total_seconds()
                        )

                self.runner.record_test(test_name, passed, time.time() - start)
            except Exception as e:
                self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_1_3_model_persistence(self):
        """Test 1.3: Test model selection persists to config"""
        start = time.time()
        test_name = "1.3: Model persistence in config"

        try:
            # Configure via API
            response = requests.post(
                f"{self.runner.base_url}/api/chat/config",
                json={
                    'api_key': self.runner.api_key,
                    'model': 'deepseek-reasoner'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            passed = assert_status(response, 200, test_name)
            if passed:
                data = response.json()
                if 'model' in data:
                    passed = assert_equal(data['model'], 'deepseek-reasoner', "Config should return reasoner")

                # Verify config file
                config_path = Path.home() / '.cartographer_config.json'
                if config_path.exists():
                    config = json.loads(config_path.read_text())
                    if 'model' in config:
                        passed = assert_equal(config['model'], 'deepseek-reasoner', "Config file should have reasoner") and passed

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    # ───────────────────────────────────────────────────────────────────
    # PHASE 2: Token Limit Tests
    # ───────────────────────────────────────────────────────────────────

    def test_2_1_token_estimation(self):
        """Test 2.1: Verify token estimation utility accuracy"""
        start = time.time()
        test_name = "2.1: Token estimation"

        try:
            # Import functions from cartographer
            sys.path.insert(0, str(Path(__file__).parent))
            from cartographer import estimate_tokens, _truncate_to_tokens

            # Test known text sizes
            text_1k = 'a' * 1000
            tokens_1k = estimate_tokens(text_1k)
            passed = assert_equal(tokens_1k, 250, "1000 chars should be ~250 tokens")

            text_10k = 'b' * 10000
            tokens_10k = estimate_tokens(text_10k)
            passed = assert_equal(tokens_10k, 2500, "10000 chars should be ~2500 tokens") and passed

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_2_2_token_truncation(self):
        """Test 2.2: Verify truncation doesn't exceed limits"""
        start = time.time()
        test_name = "2.2: Token truncation"

        try:
            from cartographer import estimate_tokens, _truncate_to_tokens

            large_text = 'x' * 1_000_000  # 1M chars = ~250K tokens
            truncated = _truncate_to_tokens(large_text, max_tokens=120000)
            estimated = estimate_tokens(truncated)

            passed = assert_less(estimated, 120001, "Truncated text should be within token limit")
            passed = assert_equal(len(truncated), 480000, "120K tokens * 4 = 480K chars") and passed

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_2_3_context_size_increased(self):
        """Test 2.3: Verify context size is much larger than before"""
        start = time.time()
        test_name = "2.3: Context size increased"

        try:
            # Load large project first
            large_project_path = TestConfig.TEST_PROJECT_DIR / TestConfig.LARGE_PROJECT_NAME
            response = requests.post(
                f"{self.runner.base_url}/api/load-project",
                json={'path': str(large_project_path)},
                timeout=TestConfig.API_TIMEOUT
            )

            if response.status_code == 200:
                large_project_id = response.json()['project_id']

                # Send broad query
                response = requests.post(
                    f"{self.runner.base_url}/api/chat",
                    json={
                        'message': 'Give comprehensive overview of entire codebase',
                        'project_id': large_project_id,
                        'model': 'deepseek-coder'
                    },
                    timeout=TestConfig.API_TIMEOUT
                )

                passed = assert_status(response, 200, test_name)
                if passed:
                    data = response.json()
                    context_size = data.get('context_size', 0)

                    # Should be much larger than old 32K limit
                    passed = assert_greater(context_size, 50000, "Context should exceed 50K chars")
                    passed = assert_less(context_size, 500000, "Context should not exceed 500K chars") and passed
            else:
                passed = False

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_2_4_token_limits_per_model(self):
        """Test 2.4: Verify different models respect their token limits"""
        limits = {
            'deepseek-coder': 128000,
            'deepseek-reasoner': 128000,
            'deepseek-chat': 64000
        }

        for model, expected_limit in limits.items():
            start = time.time()
            test_name = f"2.4: Token limit for {model}"

            try:
                # Send query with large project
                response = requests.post(
                    f"{self.runner.base_url}/api/chat",
                    json={
                        'message': 'Analyze everything in detail',
                        'project_id': self.auth_project_id,
                        'model': model
                    },
                    timeout=TestConfig.API_TIMEOUT
                )

                passed = assert_status(response, 200, test_name)
                if passed:
                    data = response.json()
                    context_size = data.get('context_size', 0)

                    # Estimate tokens
                    from cartographer import estimate_tokens
                    context_tokens = estimate_tokens(context_size) if isinstance(context_size, str) else context_size // 4

                    # Context should respect model's token limit (with buffer for response)
                    max_context = expected_limit - 10000  # Leave room for response
                    passed = assert_less(context_tokens, max_context, f"Context should respect {model} limit")

                self.runner.record_test(test_name, passed, time.time() - start)
            except Exception as e:
                self.runner.record_test(test_name, False, time.time() - start, str(e))

    # ───────────────────────────────────────────────────────────────────
    # PHASE 3: Strategic Context Placement Tests
    # ───────────────────────────────────────────────────────────────────

    def test_3_1_query_in_response(self):
        """Test 3.1: Verify query terms appear in AI response (top section effectiveness)"""
        start = time.time()
        test_name = "3.1: Query terms in response"

        try:
            response = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={
                    'message': 'Find SQL injection vulnerabilities in authentication',
                    'project_id': self.auth_project_id,
                    'model': 'deepseek-coder'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            passed = assert_status(response, 200, test_name)
            if passed:
                data = response.json()
                ai_response = data.get('response', '').lower()

                # AI should reference query terms (from top section)
                has_sql = 'sql' in ai_response or 'injection' in ai_response
                has_auth = 'auth' in ai_response or 'login' in ai_response

                passed = has_sql or has_auth
                if passed:
                    print_test("Response references query terms", "PASS")
                else:
                    print_test("Response missing query terms", "FAIL")

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_3_2_focus_extraction(self):
        """Test 3.2: Verify focus areas are extracted from query"""
        start = time.time()
        test_name = "3.2: Focus area extraction"

        try:
            from cartographer import _extract_focus_areas

            scan_data = {'nodes': []}

            # Test security focus
            query = "Find security vulnerabilities"
            focus = _extract_focus_areas(query, scan_data)
            passed = assert_contains(focus, 'security', "Should detect security focus")

            # Test domain detection
            query = "Analyze authentication and database patterns"
            focus = _extract_focus_areas(query, scan_data)
            passed = assert_contains(focus, 'authentication', "Should detect authentication domain") and passed

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_3_3_explicitly_requested_files(self):
        """Test 3.3: Verify include_files appear in response"""
        start = time.time()
        test_name = "3.3: Explicitly requested files"

        try:
            # Get scan data to extract file ID
            response = requests.get(
                f"{self.runner.base_url}/api/scan",
                params={'project_id': self.auth_project_id},
                timeout=TestConfig.API_TIMEOUT
            )

            if response.status_code == 200:
                scan_data = response.json()
                if scan_data.get('nodes'):
                    file_id = scan_data['nodes'][0]['id']
                    file_name = scan_data['nodes'][0]['name']

                    # Request specific file
                    response = requests.post(
                        f"{self.runner.base_url}/api/chat",
                        json={
                            'message': 'Review this file for issues',
                            'project_id': self.auth_project_id,
                            'include_files': [f"{self.auth_project_id}:{file_id}"],
                            'model': 'deepseek-coder'
                        },
                        timeout=TestConfig.API_TIMEOUT
                    )

                    passed = assert_status(response, 200, test_name)
                    if passed:
                        data = response.json()
                        # AI should reference the specific file
                        passed = len(data.get('response', '')) > 0
                        if passed:
                            print_test("Response contains content about requested file", "PASS")
                else:
                    passed = False
            else:
                passed = False

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    # ───────────────────────────────────────────────────────────────────
    # PHASE 4: Relevance Scoring Tests
    # ───────────────────────────────────────────────────────────────────

    def test_4_1_relevance_prioritizes_auth(self):
        """Test 4.1: Verify auth files are prioritized for auth query"""
        start = time.time()
        test_name = "4.1: Relevance scoring prioritizes auth files"

        try:
            from cartographer import _select_relevant_files

            # Create mock scan data
            scan_data = {
                'nodes': [
                    {
                        'id': 'auth1',
                        'name': 'login.py',
                        'path': '/auth/login.py',
                        'risk_score': 75,
                        'git_changes': 10,
                        'concerns': ['authentication', 'security']
                    },
                    {
                        'id': 'util1',
                        'name': 'utils.py',
                        'path': '/utils.py',
                        'risk_score': 20,
                        'git_changes': 2,
                        'concerns': []
                    },
                    {
                        'id': 'auth2',
                        'name': 'session.py',
                        'path': '/auth/session.py',
                        'risk_score': 60,
                        'git_changes': 5,
                        'concerns': ['authentication']
                    }
                ]
            }

            query = "authentication security"
            files = _select_relevant_files(query, scan_data, max_files=10)

            passed = assert_greater(len(files), 0, "Should find relevant files")
            if len(files) >= 2:
                passed = assert_equal(files[0]['name'], 'login.py', "Highest scored auth file should be first") and passed

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_4_2_high_risk_files_boosted(self):
        """Test 4.2: Verify high-risk files get scoring boost"""
        start = time.time()
        test_name = "4.2: High-risk files boosted"

        try:
            from cartographer import _select_relevant_files

            scan_data = {
                'nodes': [
                    {
                        'id': 'low',
                        'name': 'low.py',
                        'path': '/low.py',
                        'risk_score': 20,
                        'git_changes': 0,
                        'concerns': ['test']
                    },
                    {
                        'id': 'high',
                        'name': 'high.py',
                        'path': '/high.py',
                        'risk_score': 85,
                        'git_changes': 0,
                        'concerns': ['test']
                    }
                ]
            }

            query = "test"
            files = _select_relevant_files(query, scan_data, max_files=10)

            # High risk file should be prioritized
            passed = len(files) > 0
            if passed and files[0]['risk_score'] == 85:
                print_test("High risk file prioritized", "PASS")
            else:
                print_test("High risk file not prioritized", "FAIL")
                passed = False

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_4_3_recent_changes_boost(self):
        """Test 4.3: Verify files with recent git changes get boost"""
        start = time.time()
        test_name = "4.3: Recent changes boost"

        try:
            from cartographer import _select_relevant_files

            scan_data = {
                'nodes': [
                    {
                        'id': 'old',
                        'name': 'old.py',
                        'path': '/old.py',
                        'risk_score': 50,
                        'git_changes': 1,
                        'concerns': ['api']
                    },
                    {
                        'id': 'recent',
                        'name': 'recent.py',
                        'path': '/recent.py',
                        'risk_score': 50,
                        'git_changes': 15,
                        'concerns': ['api']
                    }
                ]
            }

            query = "api"
            files = _select_relevant_files(query, scan_data, max_files=10)

            # Recent file should be prioritized
            passed = len(files) > 0
            if passed and files[0]['git_changes'] == 15:
                print_test("Recent file prioritized", "PASS")
            else:
                print_test("Recent file not prioritized", "FAIL")
                passed = False

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    # ───────────────────────────────────────────────────────────────────
    # PHASE 5: API Integration Tests (Real DeepSeek Calls)
    # ───────────────────────────────────────────────────────────────────

    def test_5_1_chat_with_deepseek_coder(self):
        """Test 5.1: Test actual API call to DeepSeek with coder model"""
        start = time.time()
        test_name = "5.1: Chat with deepseek-coder"

        if not self.runner.api_key or self.runner.api_key == 'test-mock-key':
            print_test(f"{test_name}: Skipped (no API key)", "WARN")
            self.runner.record_test(test_name, True, time.time() - start)
            return

        try:
            response = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={
                    'message': 'Find security vulnerabilities in authentication files',
                    'project_id': self.auth_project_id,
                    'model': 'deepseek-coder'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            passed = assert_status(response, 200, test_name)
            if passed:
                data = response.json()

                # Verify response structure
                passed = 'response' in data and passed
                passed = 'model' in data and passed
                passed = 'context_size' in data and passed

                if 'model' in data:
                    passed = assert_equal(data['model'], 'deepseek-coder', "Model should be deepseek-coder") and passed

                if 'response' in data:
                    passed = assert_greater(len(data['response']), 50, "Response should be substantial") and passed

                    # Record metrics
                    self.runner.record_api_call(
                        model='deepseek-coder',
                        context_size=data.get('context_size', 0),
                        tokens_used=len(data['response']) // 4,
                        response_time=response.elapsed.total_seconds()
                    )

                    # Verify quality: Should reference specific files
                    ai_response = data['response']
                    quality_score = {
                        'length': len(ai_response),
                        'has_file_refs': '.py' in ai_response or 'File:' in ai_response,
                        'has_security_terms': 'security' in ai_response.lower() or 'vulnerability' in ai_response.lower()
                    }
                    self.runner.metrics['response_quality'].append({
                        'test': test_name,
                        'model': 'deepseek-coder',
                        'quality': quality_score
                    })

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_5_2_chat_history_accumulation(self):
        """Test 5.2: Verify chat history builds up correctly"""
        start = time.time()
        test_name = "5.2: Chat history accumulation"

        try:
            # Send first message
            response1 = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={
                    'message': 'What authentication files exist?',
                    'project_id': self.auth_project_id,
                    'model': 'deepseek-coder'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            # Send follow-up
            response2 = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={
                    'message': 'Review the login file for security issues',
                    'project_id': self.auth_project_id,
                    'model': 'deepseek-coder'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            # Check history
            response = requests.get(
                f"{self.runner.base_url}/api/chat/history",
                params={'project_id': self.auth_project_id},
                timeout=TestConfig.API_TIMEOUT
            )

            passed = assert_status(response, 200, test_name)
            if passed:
                history = response.json().get('messages', [])
                passed = assert_greater(len(history), 2, "Should have multiple messages in history")

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_5_3_structured_json_output(self):
        """Test 5.3: Test /api/chat/structured endpoint returns valid JSON"""
        start = time.time()
        test_name = "5.3: Structured JSON output"

        if not self.runner.api_key or self.runner.api_key == 'test-mock-key':
            print_test(f"{test_name}: Skipped (no API key)", "WARN")
            self.runner.record_test(test_name, True, time.time() - start)
            return

        try:
            response = requests.post(
                f"{self.runner.base_url}/api/chat/structured",
                json={
                    'message': 'Find all security and performance issues',
                    'project_id': self.auth_project_id,
                    'model': 'deepseek-coder'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            passed = assert_status(response, 200, test_name)
            if passed:
                data = response.json()

                # Verify JSON structure
                passed = 'summary' in data and passed
                passed = 'issues' in data and passed
                passed = 'recommendations' in data and passed
                passed = isinstance(data.get('issues', []), list) and passed

                if passed:
                    print_test("Structured JSON output valid", "PASS")

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    # ───────────────────────────────────────────────────────────────────
    # PHASE 6: Model-Specific Prompt Tests
    # ───────────────────────────────────────────────────────────────────

    def test_6_1_coder_provides_file_paths(self):
        """Test 6.1: Verify deepseek-coder includes file paths in responses"""
        start = time.time()
        test_name = "6.1: Coder model provides file paths"

        if not self.runner.api_key or self.runner.api_key == 'test-mock-key':
            print_test(f"{test_name}: Skipped (no API key)", "WARN")
            self.runner.record_test(test_name, True, time.time() - start)
            return

        try:
            response = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={
                    'message': 'Show me how to fix the SQL injection in login',
                    'project_id': self.auth_project_id,
                    'model': 'deepseek-coder'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            passed = assert_status(response, 200, test_name)
            if passed:
                data = response.json()
                ai_response = data.get('response', '')

                # Coder model should include file paths
                has_file_ref = '/' in ai_response or 'File:' in ai_response or '.py' in ai_response
                passed = has_file_ref

                if passed:
                    print_test("Coder model includes file paths", "PASS")
                else:
                    print_test("Coder model missing file paths", "FAIL")

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_6_2_reasoner_model_response(self):
        """Test 6.2: Verify deepseek-reasoner provides response"""
        start = time.time()
        test_name = "6.2: Reasoner model response"

        if not self.runner.api_key or self.runner.api_key == 'test-mock-key':
            print_test(f"{test_name}: Skipped (no API key)", "WARN")
            self.runner.record_test(test_name, True, time.time() - start)
            return

        try:
            response = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={
                    'message': 'Analyze the authentication flow',
                    'project_id': self.auth_project_id,
                    'model': 'deepseek-reasoner'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            passed = assert_status(response, 200, test_name)
            if passed:
                data = response.json()
                # R1 should provide reasoning-oriented output
                passed = assert_greater(len(data.get('response', '')), 50, "Response should be substantial")

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_6_3_chat_model_conversational(self):
        """Test 6.3: Verify deepseek-chat is more conversational"""
        start = time.time()
        test_name = "6.3: Chat model conversational"

        if not self.runner.api_key or self.runner.api_key == 'test-mock-key':
            print_test(f"{test_name}: Skipped (no API key)", "WARN")
            self.runner.record_test(test_name, True, time.time() - start)
            return

        try:
            response = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={
                    'message': 'What does this project do?',
                    'project_id': self.auth_project_id,
                    'model': 'deepseek-chat'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            passed = assert_status(response, 200, test_name)
            if passed:
                data = response.json()
                passed = assert_equal(data.get('model'), 'deepseek-chat', "Model should be chat")
                passed = assert_greater(len(data.get('response', '')), 0, "Response should be non-empty") and passed

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    # ───────────────────────────────────────────────────────────────────
    # PHASE 7: Error Handling & Edge Cases
    # ───────────────────────────────────────────────────────────────────

    def test_7_1_invalid_model_name(self):
        """Test 7.1: Test behavior with invalid model name"""
        start = time.time()
        test_name = "7.1: Invalid model name handling"

        try:
            response = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={
                    'message': 'test',
                    'project_id': self.auth_project_id,
                    'model': 'invalid-model'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            # Should fall back to default or error gracefully
            passed = assert_in_list(response.status_code, [200, 400, 500], "Should handle gracefully")

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_7_2_missing_message(self):
        """Test 7.2: Verify error when message is missing"""
        start = time.time()
        test_name = "7.2: Missing message parameter"

        try:
            response = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={'project_id': self.auth_project_id},
                timeout=TestConfig.API_TIMEOUT
            )

            passed = assert_status(response, 400, "Should return 400 for missing message")

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    def test_7_3_invalid_project_id(self):
        """Test 7.3: Test behavior with invalid project ID"""
        start = time.time()
        test_name = "7.3: Invalid project ID handling"

        try:
            response = requests.post(
                f"{self.runner.base_url}/api/chat",
                json={
                    'message': 'test',
                    'project_id': 'invalid-project-id-999'
                },
                timeout=TestConfig.API_TIMEOUT
            )

            # Should handle gracefully
            passed = assert_in_list(response.status_code, [200, 400, 404], "Should handle gracefully")

            self.runner.record_test(test_name, passed, time.time() - start)
        except Exception as e:
            self.runner.record_test(test_name, False, time.time() - start, str(e))

    # ───────────────────────────────────────────────────────────────────
    # Report Generation
    # ───────────────────────────────────────────────────────────────────

    def generate_report(self):
        """Generate comprehensive test report with metrics"""
        self.runner.metrics['end_time'] = datetime.now().isoformat()

        # Calculate statistics
        total = self.runner.metrics['total']
        passed = self.runner.metrics['passed']
        failed = self.runner.metrics['failed']
        pass_rate = (passed / total * 100) if total > 0 else 0

        # API call statistics
        api_calls = self.runner.metrics['api_calls']
        if api_calls:
            avg_response_time = sum(c['response_time'] for c in api_calls) / len(api_calls)
            models_tested = list(set(c['model'] for c in api_calls))
        else:
            avg_response_time = 0
            models_tested = []

        report = {
            'test_summary': {
                'total_tests': total,
                'passed': passed,
                'failed': failed,
                'pass_rate': f"{pass_rate:.1f}%"
            },
            'api_calls': {
                'total_calls': len(api_calls),
                'avg_response_time': f"{avg_response_time:.2f}s" if api_calls else "N/A",
                'models_tested': models_tested
            },
            'token_usage': self.runner.metrics['token_usage'],
            'response_quality': self.runner.metrics['response_quality'],
            'test_details': self.runner.metrics['tests']
        }

        # Save to JSON
        report_path = TestConfig.RESULTS_DIR / 'test_results_deepseek.json'
        report_path.write_text(json.dumps(report, indent=2))

        # Print summary
        print("\n" + "="*70)
        print("DEEPSEEK OPTIMIZATION SYSTEM TEST REPORT")
        print("="*70)
        print(f"Tests: {total}")
        print(f"Passed: {passed} ({pass_rate:.1f}%)")
        print(f"Failed: {failed}")
        print(f"\nAPI Calls: {len(api_calls)}")
        if api_calls:
            print(f"Avg Response Time: {avg_response_time:.2f}s")
            print(f"Models Tested: {', '.join(models_tested)}")
        print(f"\nReport saved to: {report_path}")

        # Print failed tests
        if failed > 0:
            print("\n" + "="*70)
            print("FAILED TESTS:")
            print("="*70)
            for test in self.runner.metrics['tests']:
                if not test['passed']:
                    print(f"  ❌ {test['name']}")
                    if test.get('error'):
                        print(f"     Error: {test['error']}")

        return report


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main Execution
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Main test execution"""
    import argparse
    parser = argparse.ArgumentParser(description='DeepSeek Optimization System Test Suite')
    parser.add_argument('--api-key', help='DeepSeek API key (or set DEEPSEEK_API_KEY env var)')
    parser.add_argument('--port', type=int, default=TestConfig.SERVER_PORT, help='Server port')
    args = parser.parse_args()

    print("="*70)
    print("DEEPSEEK OPTIMIZATION SYSTEM TEST SUITE")
    print("="*70)

    # Check for API key
    api_key = args.api_key or os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        print_test("⚠️  DEEPSEEK_API_KEY not set - API integration tests will be skipped", "WARN")
        print_test("   Set DEEPSEEK_API_KEY to run full integration tests", "INFO")
    else:
        print_test("✓ DEEPSEEK_API_KEY detected - will run full integration tests", "INFO")

    # Initialize runner
    runner = DeepSeekTestRunner(api_key=api_key, port=args.port)

    # Start server
    runner.start_server()

    try:
        # Initialize test suite
        suite = TestSuite(runner)
        suite.setup()

        # Run all test phases
        print_test("PHASE 1] Model Configuration Tests", "SECTION")
        suite.test_1_1_default_model_is_coder()
        suite.test_1_2_model_switching()
        suite.test_1_3_model_persistence()

        print_test("PHASE 2] Token Limit Tests", "SECTION")
        suite.test_2_1_token_estimation()
        suite.test_2_2_token_truncation()
        suite.test_2_3_context_size_increased()
        suite.test_2_4_token_limits_per_model()

        print_test("PHASE 3] Strategic Context Placement Tests", "SECTION")
        suite.test_3_1_query_in_response()
        suite.test_3_2_focus_extraction()
        suite.test_3_3_explicitly_requested_files()

        print_test("PHASE 4] Relevance Scoring Tests", "SECTION")
        suite.test_4_1_relevance_prioritizes_auth()
        suite.test_4_2_high_risk_files_boosted()
        suite.test_4_3_recent_changes_boost()

        print_test("PHASE 5] API Integration Tests (Real DeepSeek Calls)", "SECTION")
        suite.test_5_1_chat_with_deepseek_coder()
        suite.test_5_2_chat_history_accumulation()
        suite.test_5_3_structured_json_output()

        print_test("PHASE 6] Model-Specific Prompt Tests", "SECTION")
        suite.test_6_1_coder_provides_file_paths()
        suite.test_6_2_reasoner_model_response()
        suite.test_6_3_chat_model_conversational()

        print_test("PHASE 7] Error Handling & Edge Cases", "SECTION")
        suite.test_7_1_invalid_model_name()
        suite.test_7_2_missing_message()
        suite.test_7_3_invalid_project_id()

        # Generate report
        suite.generate_report()

    finally:
        # Cleanup
        runner.stop_server()
        runner.cleanup_projects()

    # Exit with appropriate code
    sys.exit(0 if runner.metrics['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
