#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Anthropic API credit balance and usage.
This script uses the Anthropic API to check your account status.
"""

import os
import sys
from anthropic import Anthropic

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_balance():
    """Check Anthropic API balance and display account info."""
    
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY environment variable not set")
        print("\nTo fix:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("  # Or on Windows:")
        print("  set ANTHROPIC_API_KEY=your-api-key-here")
        sys.exit(1)
    
    print("[INFO] Checking Anthropic API account status...")
    print(f"[INFO] API Key: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    try:
        client = Anthropic(api_key=api_key)
        
        # Make a minimal API call to test the key
        # We'll use the smallest possible request to minimize cost
        print("[INFO] Testing API key with minimal request...")
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Cheapest model
            max_tokens=10,  # Minimal tokens
            messages=[
                {"role": "user", "content": "Hi"}
            ]
        )
        
        print("[SUCCESS] API Key is VALID and has credits!")
        print()
        print("Test Request Results:")
        print(f"  - Model: claude-3-haiku-20240307")
        print(f"  - Input tokens: {response.usage.input_tokens}")
        print(f"  - Output tokens: {response.usage.output_tokens}")
        print(f"  - Response: {response.content[0].text}")
        print()
        
        # Calculate approximate cost (Haiku pricing)
        input_cost = (response.usage.input_tokens / 1_000_000) * 0.25
        output_cost = (response.usage.output_tokens / 1_000_000) * 1.25
        total_cost = input_cost + output_cost
        
        print(f"Cost of this test: ~${total_cost:.6f} USD")
        print()
        print("To see your full credit balance:")
        print("   >> https://console.anthropic.com/settings/billing")
        print()
        print("Common pricing (as of Nov 2024):")
        print("   Claude 3.5 Haiku:")
        print("     - Input:  $0.25 per million tokens")
        print("     - Output: $1.25 per million tokens")
        print()
        print("   Claude 3.5 Sonnet:")
        print("     - Input:  $3.00 per million tokens")
        print("     - Output: $15.00 per million tokens")
        
    except Exception as e:
        error_str = str(e)
        
        if "credit balance is too low" in error_str.lower():
            print("[ERROR] CREDIT BALANCE TOO LOW")
            print()
            print("Your Anthropic API key is valid, but you don't have enough credits.")
            print()
            print("To fix:")
            print("   1. Go to: https://console.anthropic.com/settings/billing")
            print("   2. Click 'Add Credits' or 'Upgrade Plan'")
            print("   3. Add at least $10 for testing")
            print("   4. Wait 2-3 minutes for credits to become available")
            print()
            
        elif "authentication" in error_str.lower() or "api key" in error_str.lower():
            print("[ERROR] INVALID API KEY")
            print()
            print("Your API key appears to be invalid or expired.")
            print()
            print("To fix:")
            print("   1. Go to: https://console.anthropic.com/settings/keys")
            print("   2. Create a new API key")
            print("   3. Update your ANTHROPIC_API_KEY environment variable")
            
        else:
            print(f"[ERROR] {error_str}")
            print()
            print("Check your account at: https://console.anthropic.com/")
        
        sys.exit(1)

if __name__ == "__main__":
    check_balance()

