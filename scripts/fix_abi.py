#!/usr/bin/env python3
"""
Fix ABI boolean values from JavaScript to Python format
"""

import json

def fix_abi_booleans(abi):
    """Convert JavaScript boolean values to Python boolean values"""
    if isinstance(abi, list):
        return [fix_abi_booleans(item) for item in abi]
    elif isinstance(abi, dict):
        fixed_dict = {}
        for key, value in abi.items():
            if value == "false":
                fixed_dict[key] = False
            elif value == "true":
                fixed_dict[key] = True
            else:
                fixed_dict[key] = fix_abi_booleans(value)
        return fixed_dict
    else:
        return abi

# Read the contract constants file
with open('compiled_contracts/contract_constants.py', 'r') as f:
    content = f.read()

# Extract the ABI strings and fix them
import re

# Find all ABI definitions
abi_pattern = r'(SIMPLEERC20_ABI|SIMPLEESCROW_ABI)\s*=\s*(\[.*?\])'
matches = re.findall(abi_pattern, content, re.DOTALL)

for match in matches:
    abi_name, abi_str = match
    try:
        # Parse the ABI
        abi = eval(abi_str)
        # Fix the booleans
        fixed_abi = fix_abi_booleans(abi)
        # Replace in content
        content = content.replace(abi_str, json.dumps(fixed_abi, indent=2))
    except Exception as e:
        print(f"Error fixing {abi_name}: {e}")

# Write back the fixed content
with open('compiled_contracts/contract_constants.py', 'w') as f:
    f.write(content)

print("✅ Fixed ABI boolean values in contract_constants.py") 