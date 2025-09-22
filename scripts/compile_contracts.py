#!/usr/bin/env python3
"""
Smart Contract Compilation Script
Compiles Solidity contracts and generates Python constants
"""

import json
import subprocess
import sys
from pathlib import Path

def compile_contract(contract_path: Path, contract_name: str):
    """Compile a single Solidity contract"""
    try:
        # Change to contracts directory and run solc
        contracts_dir = contract_path.parent
        
        # Run solc compiler with proper include paths
        cmd = [
            "solc",
            "--optimize",
            "--optimize-runs", "200",
            "--combined-json", "abi,bin",
            str(contract_path.name)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=contracts_dir)
        
        if result.returncode != 0:
            print(f"Compilation failed for {contract_name}:")
            print(result.stderr)
            return None
        
        # Parse output
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON output: {e}")
            print(f"Output: {result.stdout}")
            return None
        
        # Extract contract data
        if 'contracts' in output:
            # Find the main contract (not test contracts)
            for contract_key, contract_data in output['contracts'].items():
                if contract_name in contract_key and '.t.sol' not in contract_key:
                    abi = contract_data['abi']
                    if isinstance(abi, str):
                        abi = json.loads(abi)
                    return {
                        'abi': abi,
                        'bytecode': contract_data['bin']
                    }
        
        print(f"No contract data found for {contract_name}")
        return None
        
    except Exception as e:
        print(f"Error compiling {contract_name}: {e}")
        return None

def convert_json_to_python(obj):
    """Convert JSON data to Python-compatible format"""
    if isinstance(obj, dict):
        return {key: convert_json_to_python(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_json_to_python(item) for item in obj]
    elif obj == "false":
        return False
    elif obj == "true":
        return True
    elif obj == "null":
        return None
    else:
        return obj

def create_python_constants(compiled_contracts, output_file):
    """Create Python constants file from compiled contracts"""
    with open(output_file, 'w') as f:
        f.write('"""\n')
        f.write('Compiled Contract Constants\n')
        f.write('Generated automatically by compile_contracts.py\n')
        f.write('"""\n\n')
        
        for contract_name, contract_data in compiled_contracts.items():
            f.write(f'{contract_name.upper()}_ABI = {repr(convert_json_to_python(contract_data["abi"]))}\n\n')
            f.write(f'{contract_name.upper()}_BYTECODE = {repr(contract_data["bytecode"])}\n\n')

def main():
    """Main compilation function"""
    print("Smart Contract Compilation Script")
    print("=" * 40)
    
    # Contract paths
    contracts_dir = Path("app/contracts")
    output_dir = Path("compiled_contracts")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Contracts to compile
    contracts = [
        {
            'name': 'FundraisingToken',
            'path': contracts_dir / 'FundraisingToken.sol',
        },
        {
            'name': 'IEO',
            'path': contracts_dir / 'IEO.sol',
        },
        {
            'name': 'RewardTracking',
            'path': contracts_dir / 'RewardTracking.sol',
        }
    ]
    
    compiled_contracts = {}
    
    for contract in contracts:
        print(f"\nCompiling {contract['name']}...")
        
        # Check if Solidity file exists
        if not contract['path'].exists():
            print(f"❌ Solidity file not found: {contract['path']}")
            continue
        
        # Compile contract
        result = compile_contract(contract['path'], contract['name'])
        
        if result:
            print(f"✓ {contract['name']} compiled successfully")
            print(f"  ABI: {len(result['abi'])} functions")
            print(f"  Bytecode: {len(result['bytecode'])} bytes")
            
            # Save individual contract files
            contract_file = output_dir / f"{contract['name'].lower()}.json"
            with open(contract_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"  Saved to: {contract_file}")
            
            # Store for Python constants
            compiled_contracts[contract['name']] = result
        else:
            print(f"❌ Failed to compile {contract['name']}")
    
    # Create Python constants file
    if compiled_contracts:
        constants_file = output_dir / "contract_constants.py"
        create_python_constants(compiled_contracts, constants_file)
        print(f"\nCreated Python constants file: {constants_file}")
    
    print(f"\n✓ Compilation complete! Check {output_dir} for results.")

if __name__ == "__main__":
    main()
