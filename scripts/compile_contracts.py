#!/usr/bin/env python3
"""
Smart Contract Compilation Script

This script helps compile the smart contracts for deployment.
Note: In production, you should use a proper Solidity compiler setup.
"""

import json
import os
import subprocess
from pathlib import Path

def check_solc():
    """Check if solc compiler is available"""
    try:
        result = subprocess.run(['solc', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def compile_contract(contract_path, contract_name):
    """Compile a Solidity contract"""
    if not check_solc():
        print("Error: solc compiler not found. Please install solc first.")
        print("Installation: https://docs.soliditylang.org/en/latest/installing-solidity.html")
        return None
    
    try:
        # Compile contract
        cmd = [
            'solc',
            '--optimize',
            '--combined-json', 'abi,bin',
            contract_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
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
        
        contract_key = f"{contract_path}:{contract_name}"
        
        if contract_key in output['contracts']:
            contract_data = output['contracts'][contract_key]
            # ABI is already a list, not a JSON string
            return {
                'abi': contract_data['abi'],
                'bytecode': contract_data['bin']
            }
        else:
            print(f"Contract {contract_name} not found in compilation output")
            print(f"Available contracts: {list(output['contracts'].keys())}")
            return None
            
    except Exception as e:
        print(f"Error compiling {contract_name}: {str(e)}")
        return None

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
            'name': 'SimpleERC20',
            'path': contracts_dir / 'simple_erc20.sol',
        },
        {
            'name': 'SimpleEscrow',
            'path': contracts_dir / 'simple_escrow.sol',
        }
    ]
    
    compiled_contracts = {}
    
    for contract in contracts:
        print(f"\nCompiling {contract['name']}...")
        
        # Check if Solidity file exists
        if not contract['path'].exists():
            print(f"Solidity file {contract['path']} not found.")
            continue
        
        # Compile contract
        result = compile_contract(str(contract['path']), contract['name'])
        
        if result:
            compiled_contracts[contract['name']] = result
            
            # Save compiled contract
            output_file = output_dir / f"{contract['name'].lower()}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"✓ {contract['name']} compiled successfully")
            print(f"  ABI: {len(result['abi'])} functions")
            print(f"  Bytecode: {len(result['bytecode'])} bytes")
            print(f"  Saved to: {output_file}")
        else:
            print(f"✗ Failed to compile {contract['name']}")
    
    # Create Python constants file
    if compiled_contracts:
        create_python_constants(compiled_contracts, output_dir)
        print(f"\n✓ Compilation complete! Check {output_dir} for results.")
    else:
        print("\n✗ No contracts were compiled successfully.")

def create_python_constants(compiled_contracts, output_dir):
    """Create Python constants file with compiled contract data"""
    constants_file = output_dir / "contract_constants.py"
    
    with open(constants_file, 'w') as f:
        f.write('"""Compiled Smart Contract Constants"""\n\n')
        
        for contract_name, contract_data in compiled_contracts.items():
            f.write(f'{contract_name.upper()}_ABI = {json.dumps(contract_data["abi"], indent=2)}\n\n')
            f.write(f'{contract_name.upper()}_BYTECODE = "{contract_data["bytecode"]}"\n\n')
    
    print(f"Created Python constants file: {constants_file}")

if __name__ == "__main__":
    main() 