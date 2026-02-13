# Quick Start: DeepSeek System Tests

Get started testing DeepSeek optimizations in under 5 minutes.

## 🚀 Quick Start

### 1. Set API Key
```bash
export DEEPSEEK_API_KEY='sk-579238474d3445dba343e2c780774bea'
```

### 2. Run Tests
```bash
cd /Users/kcdacre8tor/cartocode
python3 test_deepseek_system.py
```

### 3. Check Results
```bash
cat test_results_deepseek.json
```

## ✅ What Gets Tested

- ✅ Model switching (coder/reasoner/chat)
- ✅ Token limits (128K coder/reasoner, 64K chat)
- ✅ Strategic context placement
- ✅ Relevance scoring
- ✅ API integration
- ✅ Error handling

## 📊 Expected Output

```
======================================================================
DEEPSEEK OPTIMIZATION SYSTEM TEST SUITE
======================================================================
✓ DEEPSEEK_API_KEY detected - will run full integration tests
ℹ️  Starting test server on port 3002...
✅ Test server ready

═══ PHASE 1] Model Configuration Tests
✅ 1.1: Default model is deepseek-coder: Status 200
✅ 1.2: Model switching to deepseek-coder: Status 200
✅ 1.2: Model switching to deepseek-reasoner: Status 200
✅ 1.2: Model switching to deepseek-chat: Status 200
✅ 1.3: Model persistence in config: Status 200

═══ PHASE 2] Token Limit Tests
✅ 2.1: Token estimation
✅ 2.2: Token truncation
✅ 2.3: Context size increased (value: 87234)
✅ 2.4: Token limit for deepseek-coder
✅ 2.4: Token limit for deepseek-reasoner
✅ 2.4: Token limit for deepseek-chat

═══ PHASE 3] Strategic Context Placement Tests
✅ 3.1: Query terms in response
✅ 3.2: Focus area extraction
✅ 3.3: Explicitly requested files: Status 200

═══ PHASE 4] Relevance Scoring Tests
✅ 4.1: Relevance scoring prioritizes auth files
✅ 4.2: High-risk files boosted
✅ 4.3: Recent changes boost

═══ PHASE 5] API Integration Tests (Real DeepSeek Calls)
✅ 5.1: Chat with deepseek-coder: Status 200
✅ 5.2: Chat history accumulation: Status 200
✅ 5.3: Structured JSON output: Status 200

═══ PHASE 6] Model-Specific Prompt Tests
✅ 6.1: Coder model provides file paths: Status 200
✅ 6.2: Reasoner model response: Status 200
✅ 6.3: Chat model conversational: Status 200

═══ PHASE 7] Error Handling & Edge Cases
✅ 7.1: Invalid model name handling
✅ 7.2: Missing message parameter: Status 400
✅ 7.3: Invalid project ID handling

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

## ⏱️ Test Duration

- **With API key:** ~60-120 seconds (includes real API calls)
- **Without API key:** ~10-20 seconds (unit tests only)

## 🔍 Validate Before Running

```bash
python3 validate_test_suite.py
```

This checks:
- ✅ Test file structure
- ✅ All 22 test methods present
- ✅ Helper functions available
- ✅ Classes correctly defined

## 📝 Test Report

The test generates `test_results_deepseek.json` with:

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
  }
}
```

## 🛠️ Troubleshooting

### No API Key?
Tests will skip API integration tests but run unit tests:
```bash
python3 test_deepseek_system.py
# Output: "⚠️  DEEPSEEK_API_KEY not set - API integration tests will be skipped"
```

### Port Already in Use?
```bash
python3 test_deepseek_system.py --port 3003
```

### Server Won't Start?
```bash
# Kill existing process
lsof -i :3002
kill -9 <PID>
```

## 📚 Full Documentation

See [TEST_DEEPSEEK_README.md](TEST_DEEPSEEK_README.md) for complete documentation.

## 🎯 What's Being Tested?

### 1. Model Configuration (3 tests)
Verifies default model, model switching, and config persistence

### 2. Token Limits (4 tests)
Verifies token estimation, truncation, and model-specific limits

### 3. Strategic Context (3 tests)
Verifies top/middle/bottom context placement effectiveness

### 4. Relevance Scoring (3 tests)
Verifies file prioritization based on relevance, risk, and recency

### 5. API Integration (3 tests)
Real DeepSeek API calls testing chat, history, and structured output

### 6. Model Prompts (3 tests)
Verifies model-specific behavior (coder file paths, reasoner logic, chat conversational)

### 7. Error Handling (3 tests)
Verifies graceful handling of invalid inputs and edge cases

## 🏆 Success Criteria

**Pass Rate: 100%** (22/22 tests)

All tests must pass to verify DeepSeek optimizations are working correctly.
