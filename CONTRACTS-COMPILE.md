## Smart Contracts: Compile and Integration Guide

This project compiles Solidity contracts in `app/contracts` using the system `solc` compiler and generates:
- JSON artifacts per contract under `compiled_contracts/*.json` (ABI + bytecode)
- A Python module `compiled_contracts/contract_constants.py` exporting `<CONTRACT>_ABI` and `<CONTRACT>_BYTECODE` symbols for direct import in the backend

### Prerequisites
- Python 3.10+ and a virtualenv (see `Makefile install`)
- `solc` compiler matching the contracts’ pragma (currently `pragma solidity ^0.8.24;`)

Install `solc` (pick one):
- Ubuntu APT:

```bash
sudo add-apt-repository -y ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install -y solc
solc --version   # verify (should be 0.8.x; prefer 0.8.24 for this repo)
```

- solc-select (easiest for pinning exact version):

```bash
pipx install solc-select || pip install --user solc-select
solc-select install 0.8.24
solc-select use 0.8.24
solc --version
```

- Direct binary (Linux):

```bash
VERSION=0.8.24
wget https://github.com/ethereum/solidity/releases/download/v${VERSION}/solc-static-linux
chmod +x solc-static-linux
sudo mv solc-static-linux /usr/local/bin/solc
solc --version
```

### Compile the contracts
The compilation script is already set up for the repo.

```bash
# from repo root, inside your venv (optional but recommended)
python3 scripts/compile_contracts.py
```

What it does:
- Compiles the contracts listed in `scripts/compile_contracts.py` (array named `contracts`)
- Writes JSON artifacts to `compiled_contracts/<name>.json`
- Regenerates `compiled_contracts/contract_constants.py` with Python constants:
  - `<NAME>_ABI` (list[dict]) and `<NAME>_BYTECODE` (hex string)

If you add/rename a contract file in `app/contracts`, update the `contracts` list in `scripts/compile_contracts.py` (name and path) and rerun the script.

### Using the generated constants
Import ABIs directly from the generated module and pass them to web3:

```11:13:app/services/blockchain_events/event_listener.py
from compiled_contracts.contract_constants import IEO_ABI
from web3 import Web3
from web3.providers.websocket import WebsocketProvider
```

```51:55:app/services/blockchain_events/event_listener.py
async def _listen_project_investments(self, project_id: str, ieo_address: str):
    contract = self.w3.eth.contract(address=ieo_address, abi=IEO_ABI)
    event = contract.events.InvestmentMade
```

Common imports after compilation (examples):

```python
from compiled_contracts.contract_constants import (
    IEO_ABI, IEO_BYTECODE,
    FUNDRAISINGTOKEN_ABI, FUNDRAISINGTOKEN_BYTECODE,
    REWARDTRACKING_ABI, REWARDTRACKING_BYTECODE,
    MOCKPRICEORACLE_ABI, MOCKPRICEORACLE_BYTECODE,
)
```

### Contract addresses
- Production/live listening uses addresses stored in the database (see model `Project.ieo_contract_address`). Ensure your deployment step persists the deployed address there.
- RPC URLs are configured via settings (see `app/core/config.py` and environment). The live event listener uses `settings.ws_rpc_url` for WebSocket subscriptions.

### JSON artifacts
Each file under `compiled_contracts/*.json` contains:
- `abi`: standard ABI list
- `bytecode`: hex string for deployment

You can also load ABIs directly from these JSONs if you prefer not to import from the constants module.

### Troubleshooting
- solc not found:
  - Ensure `solc --version` works in your shell. Reopen the terminal or adjust `PATH` if needed.
- Version mismatch or “pragma” errors:
  - Use `solc-select use 0.8.24` (or install that exact version) to match `pragma solidity ^0.8.24;` in the contracts.
- “No contract data found for <Name>” from the script:
  - The `name` in `scripts/compile_contracts.py` must match the Solidity contract’s name.
  - The script ignores test files (`*.t.sol`). Ensure you reference the main contract file.
- Boolean or JSON formatting issues in older constants:
  - A helper `scripts/fix_abi.py` exists to normalize boolean values if needed.

### Optional: Make it a Makefile target
If you want a shortcut, add this to `Makefile`:

```makefile
compile:
	. venv/bin/activate && python3 scripts/compile_contracts.py
```

Then run:

```bash
make compile
```

### Quick checklist after modifying contracts
- Update `scripts/compile_contracts.py` if you added/renamed contracts
- Ensure `solc` is at 0.8.24 (or a compatible 0.8.x)
- Run the compile script
- Commit updated files in `compiled_contracts/` (JSON + `contract_constants.py`) if your workflow requires checked-in artifacts

