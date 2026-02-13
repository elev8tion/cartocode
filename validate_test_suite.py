#!/usr/bin/env python3
"""
Quick validation for test_deepseek_system.py
Verifies structure and imports without running full tests
"""

import sys
import importlib.util
from pathlib import Path

def validate_test_structure():
    """Validate test file structure"""
    print("\n🔍 Validating DeepSeek Test Suite Structure\n")
    print("="*60)

    test_file = Path(__file__).parent / 'test_deepseek_system.py'

    # Check file exists
    if not test_file.exists():
        print("❌ Test file not found")
        return False

    print("✅ Test file exists")

    # Load module
    try:
        spec = importlib.util.spec_from_file_location("test_deepseek_system", test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ Module loads successfully")
    except Exception as e:
        print(f"❌ Failed to load module: {e}")
        return False

    # Check classes exist
    classes_to_check = [
        'TestConfig',
        'DeepSeekTestRunner',
        'TestProjectGenerator',
        'TestSuite'
    ]

    for class_name in classes_to_check:
        if hasattr(module, class_name):
            print(f"✅ Class '{class_name}' exists")
        else:
            print(f"❌ Class '{class_name}' missing")
            return False

    # Check TestSuite has all test methods
    test_suite = module.TestSuite
    test_methods = [
        'test_1_1_default_model_is_coder',
        'test_1_2_model_switching',
        'test_1_3_model_persistence',
        'test_2_1_token_estimation',
        'test_2_2_token_truncation',
        'test_2_3_context_size_increased',
        'test_2_4_token_limits_per_model',
        'test_3_1_query_in_response',
        'test_3_2_focus_extraction',
        'test_3_3_explicitly_requested_files',
        'test_4_1_relevance_prioritizes_auth',
        'test_4_2_high_risk_files_boosted',
        'test_4_3_recent_changes_boost',
        'test_5_1_chat_with_deepseek_coder',
        'test_5_2_chat_history_accumulation',
        'test_5_3_structured_json_output',
        'test_6_1_coder_provides_file_paths',
        'test_6_2_reasoner_model_response',
        'test_6_3_chat_model_conversational',
        'test_7_1_invalid_model_name',
        'test_7_2_missing_message',
        'test_7_3_invalid_project_id',
        'setup',
        'generate_report'
    ]

    print(f"\n📋 Checking {len(test_methods)} test methods...")
    missing_methods = []
    for method_name in test_methods:
        if hasattr(test_suite, method_name):
            print(f"  ✅ {method_name}")
        else:
            print(f"  ❌ {method_name}")
            missing_methods.append(method_name)

    if missing_methods:
        print(f"\n❌ Missing methods: {', '.join(missing_methods)}")
        return False

    # Check helper functions exist
    helper_functions = [
        'print_test',
        'assert_status',
        'assert_contains',
        'assert_equal',
        'assert_greater',
        'assert_less',
        'assert_in_list'
    ]

    print(f"\n🛠️  Checking {len(helper_functions)} helper functions...")
    for func_name in helper_functions:
        if hasattr(module, func_name):
            print(f"  ✅ {func_name}")
        else:
            print(f"  ❌ {func_name}")
            return False

    # Summary
    print("\n" + "="*60)
    print("✅ ALL VALIDATION CHECKS PASSED")
    print("="*60)
    print("\n📊 Test Suite Statistics:")
    print(f"  • Total test methods: {len([m for m in test_methods if m.startswith('test_')])}")
    print(f"  • Test phases: 7")
    print(f"  • Helper functions: {len(helper_functions)}")
    print(f"  • Classes: {len(classes_to_check)}")

    print("\n🚀 Ready to run:")
    print("  python3 test_deepseek_system.py")
    print("\n💡 With API key:")
    print("  export DEEPSEEK_API_KEY='your-key-here'")
    print("  python3 test_deepseek_system.py")

    return True

if __name__ == '__main__':
    success = validate_test_structure()
    sys.exit(0 if success else 1)
