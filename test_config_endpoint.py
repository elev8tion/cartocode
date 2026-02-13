#!/usr/bin/env python3
"""Test the config endpoint logic"""

DEEPSEEK_API_KEY = ''
SELECTED_MODEL = 'deepseek-chat'

def test_config(data):
    global DEEPSEEK_API_KEY, SELECTED_MODEL

    api_key = data.get('api_key', '').strip()
    model = data.get('model', '')

    print(f"Received api_key: '{api_key}' (length: {len(api_key)})")
    print(f"Received model: '{model}'")

    if api_key:
        DEEPSEEK_API_KEY = api_key
        print(f"Updated DEEPSEEK_API_KEY to: '{DEEPSEEK_API_KEY}'")
    else:
        print("Did NOT update DEEPSEEK_API_KEY (api_key was empty/falsy)")

    if model:
        SELECTED_MODEL = model
        print(f"Updated SELECTED_MODEL to: '{SELECTED_MODEL}'")

    print(f"\nFinal state:")
    print(f"  DEEPSEEK_API_KEY: '{DEEPSEEK_API_KEY}'")
    print(f"  SELECTED_MODEL: '{SELECTED_MODEL}'")

    return {'success': True, 'model': SELECTED_MODEL}

# Test 1: Valid API key
print("=== TEST 1: Valid API key ===")
result = test_config({'api_key': 'sk-valid-key', 'model': 'deepseek-chat'})
print(f"Response: {result}\n")

# Test 2: Empty string API key
print("=== TEST 2: Empty string API key ===")
DEEPSEEK_API_KEY = ''  # Reset
result = test_config({'api_key': '', 'model': 'deepseek-chat'})
print(f"Response: {result}\n")

# Test 3: Whitespace only API key
print("=== TEST 3: Whitespace only API key ===")
DEEPSEEK_API_KEY = ''  # Reset
result = test_config({'api_key': '   ', 'model': 'deepseek-chat'})
print(f"Response: {result}\n")

# Test 4: Missing api_key field
print("=== TEST 4: Missing api_key field ===")
DEEPSEEK_API_KEY = ''  # Reset
result = test_config({'model': 'deepseek-chat'})
print(f"Response: {result}\n")
