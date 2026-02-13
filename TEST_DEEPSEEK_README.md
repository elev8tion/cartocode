# DeepSeek Optimization System Test Suite

Comprehensive HTTP-based testing for DeepSeek optimizations with real API calls.

## Overview

This test suite validates all DeepSeek optimizations implemented in `cartographer.py`, including:

- ✅ **Model switching** (deepseek-coder, deepseek-reasoner, deepseek-chat)
- ✅ **Strategic context placement** (top/middle/bottom structure for improved AI attention)
- ✅ **Relevance-based file selection** (scoring algorithm vs simple keyword matching)
- ✅ **Token-based limits** (128K for coder/reasoner, 64K for chat)
- ✅ **Model-specific system prompts** (tailored to each model's strengths)
- ✅ **Structured JSON output** (`/api/chat/structured` endpoint)

## Test Coverage

**Total Tests:** 22 comprehensive system tests organized into 7 phases

### Phase 1: Model Configuration Tests (3 tests)
- `test_1_1_default_model_is_coder` - Verify default model is deepseek-coder
- `test_1_2_model_switching` - Test switching between coder/reasoner/chat models
- `test_1_3_model_persistence` - Test model selection persists to config

### Phase 2: Token Limit Tests (4 tests)
- `test_2_1_token_estimation` - Verify token estimation utility accuracy
- `test_2_2_token_truncation` - Verify truncation doesn't exceed limits
- `test_2_3_context_size_increased` - Verify context size is 15x larger than before
- `test_2_4_token_limits_per_model` - Verify different models respect their token limits

### Phase 3: Strategic Context Placement Tests (3 tests)
- `test_3_1_query_in_response` - Verify query terms appear in AI response (top section)
- `test_3_2_focus_extraction` - Verify focus areas are extracted from query
- `test_3_3_explicitly_requested_files` - Verify include_files appear in response

### Phase 4: Relevance Scoring Tests (3 tests)
- `test_4_1_relevance_prioritizes_auth` - Verify auth files are prioritized for auth query
- `test_4_2_high_risk_files_boosted` - Verify high-risk files get scoring boost
- `test_4_3_recent_changes_boost` - Verify files with recent git changes get boost

### Phase 5: API Integration Tests (3 tests - require API key)
- `test_5_1_chat_with_deepseek_coder` - Test actual API call to DeepSeek with coder model
- `test_5_2_chat_history_accumulation` - Verify chat history builds up correctly
- `test_5_3_structured_json_output` - Test `/api/chat/structured` endpoint

### Phase 6: Model-Specific Prompt Tests (3 tests - require API key)
- `test_6_1_coder_provides_file_paths` - Verify deepseek-coder includes file paths
- `test_6_2_reasoner_model_response` - Verify deepseek-reasoner provides response
- `test_6_3_chat_model_conversational` - Verify deepseek-chat is conversational

### Phase 7: Error Handling & Edge Cases (3 tests)
- `test_7_1_invalid_model_name` - Test behavior with invalid model name
- `test_7_2_missing_message` - Verify error when message is missing
- `test_7_3_invalid_project_id` - Test behavior with invalid project ID

## Prerequisites

### Required
- Python 3.8+
- `requests` library: `pip install requests`
- Running cartographer server (started automatically by test suite)

### Optional (for full integration tests)
- DeepSeek API key - Get from [platform.deepseek.com](https://platform.deepseek.com)

## Setup

1. **Clone or navigate to the cartocode directory:**
   ```bash
   cd /Users/kcdacre8tor/cartocode
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   pip install requests
   ```

3. **Set your DeepSeek API key** (for full integration tests):
   ```bash
   export DEEPSEEK_API_KEY='sk-579238474d3445dba343e2c780774bea'
   ```

   Or pass it as an argument:
   ```bash
   python3 test_deepseek_system.py --api-key='sk-579238474d3445dba343e2c780774bea'
   ```

## Running Tests

### Run All Tests
```bash
python3 test_deepseek_system.py
```

### Run with Custom Port
```bash
python3 test_deepseek_system.py --port 3003
```

### Validate Test Structure (without running tests)
```bash
python3 validate_test_suite.py
```

## Expected Output

### Successful Run
```
======================================================================
DEEPSEEK OPTIMIZATION SYSTEM TEST SUITE
======================================================================
✓ DEEPSEEK_API_KEY detected - will run full integration tests
ℹ️  Starting test server on port 3002...
ℹ️  Waiting for server to be ready...
✅ Test server ready

...

======================================================================
DEEPSEEK OPTIMIZATION SYSTEM TEST REPORT
======================================================================
Tests: 22
Passed: 22 (100.0%)
Failed: 0

API Calls: 12
Avg Response Time: 2.34s
Models Tested: deepseek-coder, deepseek-reasoner, deepseek-chat

Report saved to: /Users/kcdacre8tor/cartocode/test_results_deepseek.json
```

### Run Without API Key
If `DEEPSEEK_API_KEY` is not set, tests requiring API calls will be skipped:

```
======================================================================
DEEPSEEK OPTIMIZATION SYSTEM TEST SUITE
======================================================================
⚠️  DEEPSEEK_API_KEY not set - API integration tests will be skipped
   Set DEEPSEEK_API_KEY to run full integration tests
...
⚠️  5.1: Chat with deepseek-coder: Skipped (no API key)
⚠️  5.2: Chat history accumulation: Skipped (no API key)
...
```

## Test Artifacts

### Generated Files

1. **`test_results_deepseek.json`** - Comprehensive test report with:
   - Test summary (total, passed, failed, pass rate)
   - API call statistics (total calls, avg response time, models tested)
   - Token usage metrics
   - Response quality metrics
   - Detailed test results with timestamps and errors

2. **Test Projects** (temporary, cleaned up after tests):
   - `/tmp/deepseek_test_projects/auth_project/` - Authentication project with security issues
   - `/tmp/deepseek_test_projects/large_project/` - Large project with 50+ files
   - `/tmp/deepseek_test_projects/multi_lang_project/` - Multi-language project

### Report Structure

```json
{
  "test_summary": {
    "total_tests": 22,
    "passed": 22,
    "failed": 0,
    "pass_rate": "100.0%"
  },
  "api_calls": {
    "total_calls": 12,
    "avg_response_time": "2.34s",
    "models_tested": ["deepseek-coder", "deepseek-reasoner", "deepseek-chat"]
  },
  "token_usage": [...],
  "response_quality": [...],
  "test_details": [...]
}
```

## Test Projects

The suite automatically generates three test projects:

### 1. Authentication Project (`auth_project`)
- **Purpose:** Test security analysis and high-risk file detection
- **Contents:**
  - `auth/login.py` - SQL injection vulnerability
  - `auth/middleware.py` - Missing token validation
  - `auth/session.py` - Session management
  - `api/routes.py` - API endpoints
  - `database/models.py` - Database models
  - `tests/test_auth.py` - Test files

### 2. Large Project (`large_project`)
- **Purpose:** Test token limits and context truncation
- **Contents:** 50+ Python files with varying risk levels and content sizes

### 3. Multi-Language Project (`multi_lang_project`)
- **Purpose:** Test language detection across Python, TypeScript, Go
- **Contents:**
  - Python backend (FastAPI)
  - TypeScript frontend (React)
  - Go cache service

## Architecture

### Test Infrastructure

```python
DeepSeekTestRunner
├── Server management (start/stop)
├── Health checking
├── Metrics collection
│   ├── API call tracking
│   ├── Token usage tracking
│   └── Response quality tracking
└── Report generation

TestProjectGenerator
├── create_auth_project()
├── create_large_project()
└── create_multi_language_project()

TestSuite
├── setup()
├── 22 test methods (organized by phase)
└── generate_report()
```

### Helper Functions

- `print_test()` - Formatted test output
- `assert_status()` - HTTP status code assertions
- `assert_contains()` - Substring assertions
- `assert_equal()` - Equality assertions
- `assert_greater()` - Numeric comparison assertions
- `assert_less()` - Numeric comparison assertions
- `assert_in_list()` - List membership assertions

## Metrics Collected

### API Call Metrics
- Model used (coder/reasoner/chat)
- Context size sent
- Tokens used in response
- Response time (seconds)
- Timestamp

### Token Usage
- Query type (broad/specific/multi-file)
- Context tokens
- Response tokens
- Total tokens

### Response Quality
- Response length
- Presence of file references
- Presence of security terms
- Code block formatting

## Troubleshooting

### Server Won't Start
```bash
# Check if port is already in use
lsof -i :3002

# Kill existing process
kill -9 <PID>

# Or use a different port
python3 test_deepseek_system.py --port 3003
```

### API Key Issues
```bash
# Verify API key is set
echo $DEEPSEEK_API_KEY

# Test API key directly
curl https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-coder","messages":[{"role":"user","content":"test"}]}'
```

### Import Errors
```bash
# Ensure cartographer.py is in the same directory
ls -la cartographer.py

# Check Python path
python3 -c "import sys; print(sys.path)"
```

### Test Failures
1. Check `test_results_deepseek.json` for detailed error messages
2. Look for specific test output in the console
3. Verify test projects were created in `/tmp/deepseek_test_projects/`
4. Check server logs if available

## Performance Benchmarks

### Expected Performance (with API key)

- **Total test time:** ~60-120 seconds (depends on API response times)
- **API call average:** 2-5 seconds per call
- **Tests without API calls:** <1 second each
- **Project generation:** <2 seconds
- **Server startup:** ~3 seconds

### Token Usage Benchmarks

- **Coder model context:** 50K-400K chars (12.5K-100K tokens)
- **Chat model context:** 20K-250K chars (5K-62.5K tokens)
- **Response size:** 500-5000 tokens (typical)

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: DeepSeek Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install requests
      - name: Run tests
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: python3 test_deepseek_system.py
```

## Contributing

When adding new tests:

1. Add test method to `TestSuite` class
2. Follow naming convention: `test_<phase>_<number>_<description>`
3. Use helper assertions (`assert_status`, `assert_equal`, etc.)
4. Record test result with `self.runner.record_test()`
5. Update documentation in this README

## License

Same license as cartographer.py (MIT)

## Support

For issues or questions:
1. Check `test_results_deepseek.json` for detailed error information
2. Review test output for specific failure messages
3. Verify DeepSeek API key is valid and has credits
4. Ensure cartographer.py is up to date with latest optimizations

## Related Files

- `cartographer.py` - Main application being tested
- `test_optimizations.py` - Unit tests for DeepSeek optimizations
- `test_multi_project_chat.py` - Multi-project functionality tests
- `validate_test_suite.py` - Test structure validator

## Success Criteria

✅ All 22 tests pass with real DeepSeek API calls
✅ Model switching works (coder/reasoner/chat)
✅ Token limits respected (128K for coder/reasoner, 64K for chat)
✅ Strategic context placement verified (top/middle/bottom)
✅ Relevance scoring prioritizes correct files
✅ Structured JSON endpoint returns valid format
✅ Response quality metrics show improvement over baseline
✅ Error handling graceful for edge cases
✅ Report generated with comprehensive metrics
