#!/usr/bin/env python3
"""
Quick verification script for DeepSeek optimizations
"""

import sys
sys.path.insert(0, '.')
from cartographer import (
    MODEL_DEEPSEEK_CODER,
    MODEL_DEEPSEEK_REASONER,
    MODEL_DEEPSEEK_CHAT,
    TOKEN_LIMITS,
    OPTIMAL_TEMPS,
    SELECTED_MODEL,
    estimate_tokens,
    _truncate_to_tokens,
    _extract_focus_areas,
    _select_relevant_files
)

def test_model_constants():
    """Test that model constants are defined"""
    print("Testing model constants...")
    assert MODEL_DEEPSEEK_CODER == 'deepseek-coder', "Coder model constant incorrect"
    assert MODEL_DEEPSEEK_REASONER == 'deepseek-reasoner', "Reasoner model constant incorrect"
    assert MODEL_DEEPSEEK_CHAT == 'deepseek-chat', "Chat model constant incorrect"
    print("  ✅ Model constants defined correctly")

def test_default_model():
    """Test that default model is deepseek-coder"""
    print("Testing default model...")
    assert SELECTED_MODEL == MODEL_DEEPSEEK_CODER, f"Default model should be deepseek-coder, got {SELECTED_MODEL}"
    print("  ✅ Default model is deepseek-coder")

def test_token_limits():
    """Test token limits configuration"""
    print("Testing token limits...")
    assert TOKEN_LIMITS[MODEL_DEEPSEEK_CODER] == 128000, "Coder token limit incorrect"
    assert TOKEN_LIMITS[MODEL_DEEPSEEK_REASONER] == 128000, "Reasoner token limit incorrect"
    assert TOKEN_LIMITS[MODEL_DEEPSEEK_CHAT] == 64000, "Chat token limit incorrect"
    print("  ✅ Token limits configured correctly")

def test_optimal_temps():
    """Test optimal temperatures configuration"""
    print("Testing optimal temperatures...")
    assert OPTIMAL_TEMPS[MODEL_DEEPSEEK_CODER] == 0.7, "Coder temp incorrect"
    assert OPTIMAL_TEMPS[MODEL_DEEPSEEK_REASONER] == 0.6, "Reasoner temp incorrect"
    assert OPTIMAL_TEMPS[MODEL_DEEPSEEK_CHAT] == 0.7, "Chat temp incorrect"
    print("  ✅ Optimal temperatures configured correctly")

def test_token_estimation():
    """Test token estimation utilities"""
    print("Testing token estimation...")
    test_text = "a" * 1000  # 1000 chars
    tokens = estimate_tokens(test_text)
    assert tokens == 250, f"Expected 250 tokens, got {tokens}"

    # Test truncation
    large_text = "a" * 10000  # 10,000 chars = ~2,500 tokens
    truncated = _truncate_to_tokens(large_text, max_tokens=1000)
    assert len(truncated) == 4000, f"Expected 4000 chars, got {len(truncated)}"
    print("  ✅ Token estimation working correctly")

def test_focus_extraction():
    """Test focus area extraction"""
    print("Testing focus area extraction...")

    # Create mock scan data with CONCERN_KEYWORDS available
    from cartographer import CONCERN_KEYWORDS
    scan_data = {'nodes': []}

    query = "Find security vulnerabilities in authentication files"
    focus = _extract_focus_areas(query, scan_data)
    assert 'security' in focus.lower(), "Should detect security focus"
    assert 'authentication' in focus.lower(), "Should detect authentication domain"
    print("  ✅ Focus area extraction working")

def test_file_selection():
    """Test relevance-based file selection"""
    print("Testing file selection...")

    # Create mock scan data
    scan_data = {
        'nodes': [
            {
                'id': 'file1',
                'name': 'auth.py',
                'path': '/src/auth.py',
                'risk_score': 60,
                'git_changes': 10,
                'concerns': ['authentication', 'security']
            },
            {
                'id': 'file2',
                'name': 'utils.py',
                'path': '/src/utils.py',
                'risk_score': 20,
                'git_changes': 2,
                'concerns': []
            }
        ]
    }

    query = "authentication security"
    files = _select_relevant_files(query, scan_data, max_files=5)

    assert len(files) > 0, "Should find relevant files"
    assert files[0]['name'] == 'auth.py', "Should prioritize auth.py"
    print("  ✅ File selection working correctly")

def main():
    print("\n🔍 DeepSeek Optimization Verification\n")
    print("=" * 50)

    try:
        test_model_constants()
        test_default_model()
        test_token_limits()
        test_optimal_temps()
        test_token_estimation()
        test_focus_extraction()
        test_file_selection()

        print("\n" + "=" * 50)
        print("✅ All verification tests passed!")
        print("\nKey optimizations implemented:")
        print("  • Default model: deepseek-coder")
        print("  • Token limits: 128K (coder/reasoner), 64K (chat)")
        print("  • Strategic context placement (top/middle/bottom)")
        print("  • Relevance-based file selection")
        print("  • Model-specific system prompts")
        print("  • Token-based truncation (vs char-based)")
        print("  • Structured JSON output support")
        print("\n🎯 Ready for testing!")

        return 0
    except AssertionError as e:
        print(f"\n❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
