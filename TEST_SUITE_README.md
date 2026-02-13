# Multi-Project Chat Test Suite

Comprehensive HTTP-based integration tests for the multi-project chat functionality in Cartographer.

## Overview

This test suite validates:
- ✅ Backward compatibility with single-project mode
- ✅ Multi-project activation and management
- ✅ Context distribution (50/50 split)
- ✅ History management (unified vs per-project)
- ✅ Mode switching
- ✅ Project closure handling
- ✅ File selection with project-qualified IDs
- ✅ Edge cases and error handling

## Quick Start

### Basic Usage

```bash
# Run all tests (32 tests across 8 groups)
python3 test_multi_project_chat.py

# Run specific test group (1-8)
python3 test_multi_project_chat.py --group 3

# Verbose output
python3 test_multi_project_chat.py --verbose

# Custom output location
python3 test_multi_project_chat.py --output my_results.json
```

### With API Integration Testing

For full integration testing (including actual API calls):

```bash
# Set your DeepSeek API key
export DEEPSEEK_API_KEY='your-api-key-here'

# Run all tests
python3 test_multi_project_chat.py
```

**Without API key:** Chat-dependent tests will be gracefully skipped, but all HTTP API structure tests will run.

**With API key:** Full integration tests including actual DeepSeek API calls.

## Test Groups

### Group 1: Backward Compatibility (3 tests)
Ensures single-project mode works exactly as before.

- **1.1:** Load single project
- **1.2:** Send chat message (requires API key)
- **1.3:** Get project history

### Group 2: Multi-Project Activation (4 tests)
Tests enabling multi-project mode with 2 projects.

- **2.1:** Load second project
- **2.2:** List projects
- **2.3:** Send multi-project chat (requires API key)
- **2.4:** Verify context includes both projects

### Group 3: Context Distribution (2 tests)
Validates 50/50 split (5 files per project).

- **3.1:** Context size stays under limit (requires API key)
- **3.2:** Both projects represented in context

### Group 4: History Management (5 tests)
Tests unified vs per-project history storage.

- **4.1:** Send messages in multi-project mode (requires API key)
- **4.2:** Get unified multi-project history
- **4.3:** Verify per-project history independent
- **4.4:** Send single-project message (requires API key)
- **4.5:** Verify histories remain independent

### Group 5: Mode Switching (4 tests)
Tests switching between single and multi-project modes.

- **5.1:** Build up multi-project history (requires API key)
- **5.2:** Switch to single-project mode (requires API key)
- **5.3:** Switch back to multi-project mode (requires API key)
- **5.4:** Verify multi-project history preserved

### Group 6: Project Closure (4 tests)
Tests auto-disable when project count drops below 2.

- **6.1:** Chat in multi-project mode (requires API key)
- **6.2:** Unload project
- **6.3:** Verify only 1 project remains
- **6.4:** Chat still works with single project (requires API key)

### Group 7: File Selection (2 tests)
Tests project-qualified file IDs.

- **7.1:** Get scan data to extract file ID
- **7.2:** Send chat with project-qualified file ID (requires API key)

### Group 8: Edge Cases (8 tests)
Tests error handling and edge cases.

- **8.1:** Clear multi-project history
- **8.2:** Invalid project ID handling (requires API key)
- **8.3:** Missing message parameter
- **8.4:** Empty project_ids array (requires API key)
- **8.5:** Exceed MAX_PROJECTS (2 project limit)
- **8.6:** Malformed JSON
- **8.7:** Context overflow with huge query (requires API key)
- **8.8:** Clear per-project history

## Generated Files

After running tests, the following files are generated:

### `test_results_YYYYMMDD_HHMMSS.json`
Complete test results in JSON format:
- Timestamp
- Summary statistics (total, passed, failed)
- Individual test results with:
  - Test name
  - Pass/fail status
  - Duration
  - Error details (if failed)

### `MULTI_PROJECT_ISSUES.md`
Issue tracking document:
- Summary of test results
- Critical issues (HIGH severity)
- Detailed error information
- Recommended fixes

### `TEST_COVERAGE.md`
Feature coverage matrix:
- Table of all tests and their status (✓/✗)
- Overall coverage percentage
- Quick visual reference

## Architecture

### Test Components

```
test_multi_project_chat.py
├── TestConfig            # Configuration (ports, paths, timeouts)
├── TestServer            # Manages cartographer.py subprocess
├── TestProjects          # Creates temporary test project fixtures
├── TestRunner            # Orchestrates all test scenarios
│   ├── group_1_*         # 8 test group methods
│   ├── setup()           # Creates test projects
│   ├── teardown()        # Cleanup
│   └── generate_report() # Creates documentation files
└── Helper Functions      # Assertions (assert_status, assert_contains, etc.)
```

### Test Fixtures

Temporary test projects are created in `/tmp/cartographer_test_projects/`:

- **auth_service:** Authentication microservice (5 files)
  - auth/login.py
  - auth/middleware.py
  - auth/models.py
  - auth/config.py
  - tests/test_auth.py

- **api_gateway:** API gateway service (4 files)
  - api/routes.py
  - api/gateway.py
  - api/middleware.py
  - api/config.py

All fixtures are automatically cleaned up after test run.

### Server Management

- Starts cartographer.py on port **3001** (avoids conflict with default 3000)
- Runs as subprocess for isolation
- Waits for server readiness before running tests
- Graceful shutdown on test completion

## Expected Results

### Without API Key

```
Total Tests:  32
Passed:       19 ✓
Failed:       13 ✗
```

**Passed tests:** All HTTP API structure tests (project loading, history endpoints, error handling)

**Failed/Skipped tests:** Tests requiring actual DeepSeek API calls

### With API Key

```
Total Tests:  32
Passed:       32 ✓
Failed:       0 ✗
```

All tests pass including full integration tests with real API calls.

## Troubleshooting

### Server fails to start

**Symptom:** `Server failed to start ✗`

**Solutions:**
- Check if port 3001 is already in use: `lsof -i :3001`
- Kill existing process: `kill $(lsof -t -i :3001)`
- Increase `SERVER_START_TIMEOUT` in TestConfig

### Tests timing out

**Symptom:** Tests hang or timeout

**Solutions:**
- Increase `API_TIMEOUT` in TestConfig
- Check network connectivity for API calls
- Verify DeepSeek API is accessible

### Import errors

**Symptom:** `ModuleNotFoundError: No module named 'requests'`

**Solution:**
```bash
pip install requests
```

### Permission errors creating test projects

**Symptom:** `PermissionError` in `/tmp/cartographer_test_projects/`

**Solution:**
```bash
# Ensure /tmp is writable
chmod 755 /tmp

# Or change TEST_PROJECT_DIR in TestConfig
```

## Development

### Adding New Tests

1. Create a new test method in `TestRunner` class:
```python
def test_new_feature(self):
    start = time.time()
    try:
        response = requests.post(...)
        passed = assert_status(response, 200, "Test description")
        self.record_test("Test name", passed, time.time() - start)
    except Exception as e:
        self.record_test("Test name", False, time.time() - start, str(e))
```

2. Add to appropriate test group method

3. Update documentation

### Running Individual Tests

Modify `main()` to run specific tests:

```python
runner = TestRunner()
runner.setup()
runner.test_new_feature()  # Your test
runner.teardown()
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Multi-Project Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install requests

      - name: Run tests
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: python3 test_multi_project_chat.py

      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: |
            test_results_*.json
            MULTI_PROJECT_ISSUES.md
            TEST_COVERAGE.md
```

## Performance

**Test Duration:**
- Without API key: ~8-12 seconds (structure tests only)
- With API key: ~30-45 seconds (full integration)

**Resource Usage:**
- Minimal CPU/memory
- Temporary disk space: ~100KB (test projects)

## Best Practices

1. **Run tests before committing:** Ensure no regressions
2. **Check coverage report:** Verify all features tested
3. **Review issues document:** Address failures immediately
4. **Use API key for full testing:** Integration tests catch more bugs
5. **Clean test isolation:** Each test group is independent

## Known Limitations

1. **Subprocess server:** Cannot mock internal OpenAI calls
2. **API costs:** Full integration tests make real API calls (minimal cost)
3. **Port conflicts:** Requires port 3001 available
4. **Test order:** Groups run sequentially (not parallelized)

## Future Enhancements

- [ ] Parallel test execution
- [ ] Mock server for API calls (no key required)
- [ ] Performance benchmarking
- [ ] HTML test reports
- [ ] Test replay from JSON results

## Related Files

- `cartographer.py` - Main application being tested
- `MULTI_PROJECT_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `dashboard.html` - Frontend implementation

## Support

For issues or questions:
1. Check `MULTI_PROJECT_ISSUES.md` for known issues
2. Review test output in `test_results_*.json`
3. Run with `--verbose` for detailed output
4. Check server logs in subprocess output

---

**Status:** ✅ Production Ready

**Last Updated:** 2026-02-13

**Test Coverage:** 32 tests across 8 functional groups
