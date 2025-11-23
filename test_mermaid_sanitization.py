#!/usr/bin/env python3
"""Test script to verify Mermaid sanitization fixes."""

import re

def test_comma_separated_class_fix():
    """Test that comma-separated class assignments are split correctly."""
    
    test_cases = [
        {
            "input": "    class Product,ProductVariant,ProductAttribute coreEntity",
            "expected_count": 3,
            "class_name": "coreEntity"
        },
        {
            "input": "class Customer,CustomerProfile userEntity",
            "expected_count": 2,
            "class_name": "userEntity"
        },
        {
            "input": "    class Order,OrderItem,Payment txEntity",
            "expected_count": 3,
            "class_name": "txEntity"
        }
    ]
    
    for i, test in enumerate(test_cases):
        line = test["input"]
        match = re.match(r'^(\s*)class\s+([A-Za-z0-9_,]+)\s+([A-Za-z0-9_]+)\s*$', line)
        
        if match and ',' in match[2]:
            indent = match[1]
            nodes = match[2].split(',')
            class_name = match[3]
            
            assert len(nodes) == test["expected_count"], \
                f"Test {i+1} failed: Expected {test['expected_count']} nodes, got {len(nodes)}"
            assert class_name == test["class_name"], \
                f"Test {i+1} failed: Expected class '{test['class_name']}', got '{class_name}'"
            
            # Generate fixed lines
            fixed_lines = [f"{indent}class {node.strip()} {class_name}" for node in nodes if node.strip()]
            
            print(f"✅ Test {i+1} passed: Split {len(nodes)} nodes")
            print(f"   Input:  {line.strip()}")
            print(f"   Output: ({len(fixed_lines)} lines)")
            for fl in fixed_lines:
                print(f"           {fl}")
        else:
            print(f"❌ Test {i+1} failed: Pattern did not match")

def test_label_escape_fix():
    """Test that escaped quotes and backslashes are removed."""
    
    test_cases = [
        {
            "input": 'ProductDB["(\\"Customer Data Platform\\")"]',
            "expected": 'ProductDB["(\'Customer Data Platform\')"]'
        },
        {
            "input": 'Backend["API \\\\n Server"]',
            "expected": 'Backend["API n Server"]'
        },
        {
            "input": 'Node["Test \\"Quote\\" Here"]',
            "expected": 'Node["Test \'Quote\' Here"]'
        }
    ]
    
    for i, test in enumerate(test_cases):
        # Simulate the label cleaning logic
        # Use a more flexible pattern that handles escaped characters
        pattern = r'\["((?:[^"\\]|\\.)*)"\]'
        
        def clean_label(match):
            label = match[1]
            # Remove backslashes
            cleaned = label.replace('\\', '')
            # Replace quotes with single quotes
            cleaned = cleaned.replace('"', "'")
            return f'["{cleaned}"]'
        
        result = re.sub(pattern, clean_label, test["input"])
        
        if result == test["expected"]:
            print(f"✅ Test {i+1} passed:")
            print(f"   Input:    {test['input']}")
            print(f"   Expected: {test['expected']}")
            print(f"   Got:      {result}")
        else:
            print(f"❌ Test {i+1} failed:")
            print(f"   Input:    {test['input']}")
            print(f"   Expected: {test['expected']}")
            print(f"   Got:      {result}")

def test_truncated_property_fix():
    """Test that truncated properties are detected."""
    
    test_patterns = [
        (r'stroke-widt(?!h)', 'stroke-width'),
        (r'font-weigh(?!t)', 'font-weight'),
        (r'font-siz(?!e)', 'font-size'),
    ]
    
    test_lines = [
        ("classDef myClass stroke-widt:2px", True, "stroke-width"),
        ("style Node1 font-weigh:bold", True, "font-weight"),
        ("classDef x font-siz:14px", True, "font-size"),
        ("classDef good stroke-width:2px", False, None),
        ("style Node2 font-weight:bold", False, None),
    ]
    
    for i, (line, should_match, property_name) in enumerate(test_lines):
        matched = False
        detected_property = None
        
        for pattern_regex, prop_name in test_patterns:
            if re.search(pattern_regex, line):
                matched = True
                detected_property = prop_name
                break
        
        if matched == should_match:
            if should_match:
                print(f"✅ Test {i+1} passed: Detected truncated property '{detected_property}'")
                print(f"   Line: {line}")
            else:
                print(f"✅ Test {i+1} passed: No truncation detected (correct)")
                print(f"   Line: {line}")
        else:
            print(f"❌ Test {i+1} failed:")
            print(f"   Line: {line}")
            print(f"   Expected match: {should_match}, Got: {matched}")

if __name__ == "__main__":
    print("=" * 70)
    print("MERMAID SANITIZATION TEST SUITE")
    print("=" * 70)
    print()
    
    print("TEST 1: Comma-Separated Class Assignment Fix")
    print("-" * 70)
    test_comma_separated_class_fix()
    print()
    
    print("TEST 2: Label Escape Sequence Fix")
    print("-" * 70)
    test_label_escape_fix()
    print()
    
    print("TEST 3: Truncated Property Detection")
    print("-" * 70)
    test_truncated_property_fix()
    print()
    
    print("=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)

