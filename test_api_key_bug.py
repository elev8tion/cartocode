#!/usr/bin/env python3
"""Test script to reproduce the API key configuration bug"""

# Simulate the global variable setup
DEEPSEEK_API_KEY = ''

def call_deepseek_test():
    """Simulates call_deepseek function"""
    print(f"[call_deepseek] DEEPSEEK_API_KEY value: '{DEEPSEEK_API_KEY}'")
    print(f"[call_deepseek] Is empty? {not DEEPSEEK_API_KEY}")

    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY not set")

    print("[call_deepseek] API key is set!")
    return "Success"

def configure_api_key(new_key):
    """Simulates the /api/chat/config endpoint"""
    global DEEPSEEK_API_KEY

    print(f"[configure] Received key: '{new_key}'")

    if new_key:
        DEEPSEEK_API_KEY = new_key
        print(f"[configure] Set DEEPSEEK_API_KEY to: '{DEEPSEEK_API_KEY}'")

    return {"success": True}

# Test the flow
print("=== Initial State ===")
try:
    call_deepseek_test()
except ValueError as e:
    print(f"Expected error: {e}")

print("\n=== Configure API Key ===")
result = configure_api_key("sk-test-key-12345")
print(f"Config result: {result}")

print("\n=== Try to use API key after configuration ===")
try:
    result = call_deepseek_test()
    print(f"Success! Result: {result}")
except ValueError as e:
    print(f"ERROR: {e}")
    print("BUG REPRODUCED!")
