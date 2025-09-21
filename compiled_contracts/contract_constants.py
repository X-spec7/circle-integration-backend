"""Compiled Smart Contract Constants"""

FUNDRAISINGTOKEN_ABI = [
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "name_",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "symbol_",
        "type": "string"
      },
      {
        "internalType": "uint8",
        "name": "decimals_",
        "type": "uint8"
      },
      {
        "internalType": "uint256",
        "name": "initialSupply",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [],
    "name": "CallerNotOwner",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "CallerNotWhitelisted",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "CannotWhitelistZeroAddress",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "allowance",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "needed",
        "type": "uint256"
      }
    ],
    "name": "ERC20InsufficientAllowance",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "sender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "balance",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "needed",
        "type": "uint256"
      }
    ],
    "name": "ERC20InsufficientBalance",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "approver",
        "type": "address"
      }
    ],
    "name": "ERC20InvalidApprover",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      }
    ],
    "name": "ERC20InvalidReceiver",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "sender",
        "type": "address"
      }
    ],
    "name": "ERC20InvalidSender",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      }
    ],
    "name": "ERC20InvalidSpender",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MintAuthorityFrozen",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NewOwnerIsZeroAddress",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "RecipientMustBeWhitelisted",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "RecipientNotWhitelisted",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ReentrantCallBlocked",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SenderNotWhitelisted",
    "type": "error"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "AddressRemovedFromWhitelist",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "AddressWhitelisted",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "owner",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "Approval",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [],
    "name": "MintAuthorityFrozen",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "OwnershipTransferred",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "newAddress",
        "type": "address"
      }
    ],
    "name": "RewardTrackingAddressUpdated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "bool",
        "name": "enabled",
        "type": "bool"
      }
    ],
    "name": "RewardTrackingEnabled",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "Transfer",
    "type": "event"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "addToWhitelist",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      }
    ],
    "name": "allowance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "approve",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "balanceOf",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address[]",
        "name": "accounts",
        "type": "address[]"
      }
    ],
    "name": "batchAddToWhitelist",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address[]",
        "name": "accounts",
        "type": "address[]"
      }
    ],
    "name": "batchRemoveFromWhitelist",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "burn",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "decimals",
    "outputs": [
      {
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isMintAuthorityFrozen",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isRewardTrackingEnabled",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "isWhitelisted",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "mint",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "name",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "removeFromWhitelist",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "rewardTrackingAddress",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_rewardTrackingAddress",
        "type": "address"
      }
    ],
    "name": "setRewardTrackingAddress",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "symbol",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalSupply",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "transfer",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "transferFrom",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "transferOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]

FUNDRAISINGTOKEN_BYTECODE = "608060405234801562000010575f80fd5b5060405162001ac838038062001ac8833981016040819052620000339162000433565b338484600362000044838262000542565b50600462000053828262000542565b5050506001600160a01b0381166200007e57604051633a247dd760e11b815260040160405180910390fd5b620000898162000176565b506008805460ff191660ff8416179055600680546001600160a01b0319169055600160075f620000b63390565b6001600160a01b0316815260208101919091526040015f20805460ff1916911515919091179055620000e53390565b6001600160a01b03167f4f783c179409b4127238bc9c990bc99b9a651666a0d20b51d6c42849eb88466d60405160405180910390a2620001263382620001c7565b6005805460ff60a01b1916600160a01b1790556040517f90d02b784227cf3640052f8e41e0bfba1b781199a9ca01d26c4966083bbf26d5905f90a16200016c5f62000207565b5050505062000634565b600580546001600160a01b038381166001600160a01b0319831681179093556040519116919082907f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0905f90a35050565b6001600160a01b038216620001f65760405163ec442f0560e01b81525f60048201526024015b60405180910390fd5b620002035f838362000243565b5050565b7f6d2b42ea8ea68279786cfbfa61adeb8dae2aeed7b08f233fdd601b54283376315f8262000236575f62000239565b60015b60ff169091555050565b6001600160a01b03831662000271578060025f8282546200026591906200060e565b90915550620002e39050565b6001600160a01b0383165f9081526020819052604090205481811015620002c55760405163391434e360e21b81526001600160a01b03851660048201526024810182905260448101839052606401620001ed565b6001600160a01b0384165f9081526020819052604090209082900390555b6001600160a01b03821662000301576002805482900390556200031f565b6001600160a01b0382165f9081526020819052604090208054820190555b816001600160a01b0316836001600160a01b03167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef836040516200036591815260200190565b60405180910390a3505050565b634e487b7160e01b5f52604160045260245ffd5b5f82601f83011262000396575f80fd5b81516001600160401b0380821115620003b357620003b362000372565b604051601f8301601f19908116603f01168101908282118183101715620003de57620003de62000372565b8160405283815260209250866020858801011115620003fb575f80fd5b5f91505b838210156200041e5785820183015181830184015290820190620003ff565b5f602085830101528094505050505092915050565b5f805f806080858703121562000447575f80fd5b84516001600160401b03808211156200045e575f80fd5b6200046c8883890162000386565b9550602087015191508082111562000482575f80fd5b50620004918782880162000386565b935050604085015160ff81168114620004a8575f80fd5b6060959095015193969295505050565b600181811c90821680620004cd57607f821691505b602082108103620004ec57634e487b7160e01b5f52602260045260245ffd5b50919050565b601f8211156200053d57805f5260205f20601f840160051c81016020851015620005195750805b601f840160051c820191505b818110156200053a575f815560010162000525565b50505b505050565b81516001600160401b038111156200055e576200055e62000372565b62000576816200056f8454620004b8565b84620004f2565b602080601f831160018114620005ac575f8415620005945750858301515b5f19600386901b1c1916600185901b17855562000606565b5f85815260208120601f198616915b82811015620005dc57888601518255948401946001909101908401620005bb565b5085821015620005fa57878501515f19600388901b60f8161c191681555b505060018460011b0185555b505050505050565b808201808211156200062e57634e487b7160e01b5f52601160045260245ffd5b92915050565b61148680620006425f395ff3fe608060405234801561000f575f80fd5b5060043610610148575f3560e01c80635d53bdf3116100bf57806395d89b411161007957806395d89b41146102ce578063a9059cbb146102d6578063dd62ed3e146102e9578063e43252d7146102fc578063ecb40af91461030f578063f2fde38b14610322575f80fd5b80635d53bdf31461025b57806370a082311461026d578063715018a6146102805780638ab1d681146102885780638da5cb5b1461029b578063924a80cc146102bb575f80fd5b80632db6fa36116101105780632db6fa36146101cb578063313ce567146101de5780633af32abf146101f35780633d8d30b61461021e57806340c10f191461023557806342966c6814610248575f80fd5b8063045fb8881461014c57806306fdde0314610161578063095ea7b31461017f57806318160ddd146101a257806323b872dd146101b8575b5f80fd5b61015f61015a3660046111f7565b610335565b005b610169610451565b60405161017691906112b7565b60405180910390f35b61019261018d366004611303565b610460565b6040519015158152602001610176565b6101aa6104a2565b604051908152602001610176565b6101926101c636600461132b565b6104ac565b61015f6101d93660046111f7565b610636565b60085460405160ff9091168152602001610176565b610192610201366004611364565b6001600160a01b03165f9081526007602052604090205460ff1690565b5f8051602061143183398151915254600114610192565b61015f610243366004611303565b61074f565b61015f61025636600461137d565b6107ec565b600554600160a01b900460ff16610192565b6101aa61027b366004611364565b610828565b61015f610845565b61015f610296366004611364565b61084f565b6102a36108ee565b6040516001600160a01b039091168152602001610176565b61015f6102c9366004611364565b610901565b6101696109e7565b6101926102e4366004611303565b6109f1565b6101aa6102f7366004611394565b610b7a565b61015f61030a366004611364565b610ba6565b6006546102a3906001600160a01b031681565b61015f610330366004611364565b610c48565b3361033e6108ee565b6001600160a01b03161461036557604051632e6c18c960e11b815260040160405180910390fd5b5f5b815181101561044d575f6001600160a01b031682828151811061038c5761038c6113c5565b60200260200101516001600160a01b031614610445575f60075f8484815181106103b8576103b86113c5565b60200260200101516001600160a01b03166001600160a01b031681526020019081526020015f205f6101000a81548160ff021916908315150217905550818181518110610407576104076113c5565b60200260200101516001600160a01b03167f535611fb62fa2a833988f283b779e417e996813e44046f521d76c17b5943b08c60405160405180910390a25b600101610367565b5050565b606061045b610c51565b905090565b335f9081526007602052604081205460ff1661048f57604051638c6e5d7160e01b815260040160405180910390fd5b6104998383610ce1565b90505b92915050565b5f61045b60025490565b335f9081526007602052604081205460ff166104db57604051638c6e5d7160e01b815260040160405180910390fd5b6001600160a01b0384165f908152600760205260409020548490849060ff1661051757604051637ed449a960e01b815260040160405180910390fd5b6001600160a01b0381165f9081526007602052604090205460ff1661054f576040516317b4cc9360e21b815260040160405180910390fd5b610557610cf8565b5f610563878787610d44565b905061057d5f805160206114318339815191525460011490565b801561059357506006546001600160a01b031615155b156106025760065460405163677ba3d360e01b81526001600160a01b0389811660048301528881166024830152604482018890529091169063677ba3d3906064015f604051808303815f87803b1580156105eb575f80fd5b505af11580156105fd573d5f803e3d5ffd5b505050505b925061062d60017fb781d8a1ba627211bdb7127bc33569e32c3687cf3e7f96a45864ae48ddcbd09d55565b50509392505050565b3361063f6108ee565b6001600160a01b03161461066657604051632e6c18c960e11b815260040160405180910390fd5b5f5b815181101561044d575f6001600160a01b031682828151811061068d5761068d6113c5565b60200260200101516001600160a01b03161461074757600160075f8484815181106106ba576106ba6113c5565b60200260200101516001600160a01b03166001600160a01b031681526020019081526020015f205f6101000a81548160ff021916908315150217905550818181518110610709576107096113c5565b60200260200101516001600160a01b03167f4f783c179409b4127238bc9c990bc99b9a651666a0d20b51d6c42849eb88466d60405160405180910390a25b600101610668565b336107586108ee565b6001600160a01b03161461077f57604051632e6c18c960e11b815260040160405180910390fd5b600554600160a01b900460ff16156107aa5760405163121a056f60e31b815260040160405180910390fd5b6001600160a01b0382165f9081526007602052604090205460ff166107e257604051633eab307560e01b815260040160405180910390fd5b61044d8282610d67565b335f9081526007602052604090205460ff1661081b57604051638c6e5d7160e01b815260040160405180910390fd5b6108253382610da0565b50565b6001600160a01b0381165f9081526020819052604081205461049c565b61084d610dd4565b565b336108586108ee565b6001600160a01b03161461087f57604051632e6c18c960e11b815260040160405180910390fd5b6001600160a01b0381166108a657604051633756244d60e01b815260040160405180910390fd5b6001600160a01b0381165f81815260076020526040808220805460ff19169055517f535611fb62fa2a833988f283b779e417e996813e44046f521d76c17b5943b08c9190a250565b5f61045b6005546001600160a01b031690565b3361090a6108ee565b6001600160a01b03161461093157604051632e6c18c960e11b815260040160405180910390fd5b6001600160a01b03811661095857604051633756244d60e01b815260040160405180910390fd5b600680546001600160a01b0319166001600160a01b03831617905561097d6001610e0d565b6040516001600160a01b038216907f9962f0fa162172ba3dc3e0912f2526f2c9041edead2f56b562415cabc9356aff905f90a2604051600181527fd5aec850d69a1d40917d707745a75fa581809b43d331005cec287da0faf3c80d9060200160405180910390a150565b606061045b610e34565b335f9081526007602052604081205460ff16610a2057604051638c6e5d7160e01b815260040160405180910390fd5b335f81815260076020526040902054849060ff16610a5157604051637ed449a960e01b815260040160405180910390fd5b6001600160a01b0381165f9081526007602052604090205460ff16610a89576040516317b4cc9360e21b815260040160405180910390fd5b610a91610cf8565b5f610a9c8686610e43565b9050610ab65f805160206114318339815191525460011490565b8015610acc57506006546001600160a01b031615155b15610b47576006546001600160a01b031663677ba3d3336040516001600160e01b031960e084901b1681526001600160a01b0391821660048201529089166024820152604481018890526064015f604051808303815f87803b158015610b30575f80fd5b505af1158015610b42573d5f803e3d5ffd5b505050505b9250610b7260017fb781d8a1ba627211bdb7127bc33569e32c3687cf3e7f96a45864ae48ddcbd09d55565b505092915050565b6001600160a01b038083165f908152600160209081526040808320938516835292905290812054610499565b33610baf6108ee565b6001600160a01b031614610bd657604051632e6c18c960e11b815260040160405180910390fd5b6001600160a01b038116610bfd57604051633756244d60e01b815260040160405180910390fd5b6001600160a01b0381165f81815260076020526040808220805460ff19166001179055517f4f783c179409b4127238bc9c990bc99b9a651666a0d20b51d6c42849eb88466d9190a250565b61082581610e50565b606060038054610c60906113d9565b80601f0160208091040260200160405190810160405280929190818152602001828054610c8c906113d9565b8015610cd75780601f10610cae57610100808354040283529160200191610cd7565b820191905f5260205f20905b815481529060010190602001808311610cba57829003601f168201915b5050505050905090565b5f33610cee818585610eb0565b5060019392505050565b7fb781d8a1ba627211bdb7127bc33569e32c3687cf3e7f96a45864ae48ddcbd09d80546001198101610d3d5760405163139b643560e21b815260040160405180910390fd5b5060029055565b5f33610d51858285610ec2565b610d5c858585610f26565b506001949350505050565b6001600160a01b038216610d955760405163ec442f0560e01b81525f60048201526024015b60405180910390fd5b61044d5f8383610f7f565b6001600160a01b038216610dc957604051634b637e8f60e11b81525f6004820152602401610d8c565b61044d825f83610f7f565b33610ddd6108ee565b6001600160a01b031614610e0457604051632e6c18c960e11b815260040160405180910390fd5b61084d5f6110a5565b5f805160206114318339815191525f82610e27575f610e2a565b60015b60ff169091555050565b606060048054610c60906113d9565b5f33610cee818585610f26565b33610e596108ee565b6001600160a01b031614610e8057604051632e6c18c960e11b815260040160405180910390fd5b6001600160a01b038116610ea757604051633a247dd760e11b815260040160405180910390fd5b610825816110a5565b610ebd83838360016110f6565b505050565b5f610ecd8484610b7a565b90505f19811015610f205781811015610f1257604051637dc7a0d960e11b81526001600160a01b03841660048201526024810182905260448101839052606401610d8c565b610f2084848484035f6110f6565b50505050565b6001600160a01b038316610f4f57604051634b637e8f60e11b81525f6004820152602401610d8c565b6001600160a01b038216610f785760405163ec442f0560e01b81525f6004820152602401610d8c565b610ebd8383835b6001600160a01b038316610fa9578060025f828254610f9e9190611411565b909155506110199050565b6001600160a01b0383165f9081526020819052604090205481811015610ffb5760405163391434e360e21b81526001600160a01b03851660048201526024810182905260448101839052606401610d8c565b6001600160a01b0384165f9081526020819052604090209082900390555b6001600160a01b03821661103557600280548290039055611053565b6001600160a01b0382165f9081526020819052604090208054820190555b816001600160a01b0316836001600160a01b03167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef8360405161109891815260200190565b60405180910390a3505050565b600580546001600160a01b038381166001600160a01b0319831681179093556040519116919082907f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0905f90a35050565b6001600160a01b03841661111f5760405163e602df0560e01b81525f6004820152602401610d8c565b6001600160a01b03831661114857604051634a1406b160e11b81525f6004820152602401610d8c565b6001600160a01b038085165f9081526001602090815260408083209387168352929052208290558015610f2057826001600160a01b0316846001600160a01b03167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040516111ba91815260200190565b60405180910390a350505050565b634e487b7160e01b5f52604160045260245ffd5b80356001600160a01b03811681146111f2575f80fd5b919050565b5f6020808385031215611208575f80fd5b823567ffffffffffffffff8082111561121f575f80fd5b818501915085601f830112611232575f80fd5b813581811115611244576112446111c8565b8060051b604051601f19603f83011681018181108582111715611269576112696111c8565b604052918252848201925083810185019188831115611286575f80fd5b938501935b828510156112ab5761129c856111dc565b8452938501939285019261128b565b98975050505050505050565b5f602080835283518060208501525f5b818110156112e3578581018301518582016040015282016112c7565b505f604082860101526040601f19601f8301168501019250505092915050565b5f8060408385031215611314575f80fd5b61131d836111dc565b946020939093013593505050565b5f805f6060848603121561133d575f80fd5b611346846111dc565b9250611354602085016111dc565b9150604084013590509250925092565b5f60208284031215611374575f80fd5b610499826111dc565b5f6020828403121561138d575f80fd5b5035919050565b5f80604083850312156113a5575f80fd5b6113ae836111dc565b91506113bc602084016111dc565b90509250929050565b634e487b7160e01b5f52603260045260245ffd5b600181811c908216806113ed57607f821691505b60208210810361140b57634e487b7160e01b5f52602260045260245ffd5b50919050565b8082018082111561049c57634e487b7160e01b5f52601160045260245ffdfe6d2b42ea8ea68279786cfbfa61adeb8dae2aeed7b08f233fdd601b5428337631a2646970667358221220ddbbd37f77b394bdbb52f67a50ff0d7177119e8a277970a32ff7a02880d6ae7e64736f6c63430008180033"

IEO_ABI = [
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_tokenAddress",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_admin",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_businessAdmin",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_delayDays",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "_minInvestment",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "_maxInvestment",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [],
    "name": "CallerNotOwner",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "CircuitBreakerTriggered",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ClaimPeriodNotStarted",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InvalidDelayDays",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InvalidInvestmentAmount",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InvalidInvestmentRange",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InvalidMinInvestment",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InvalidPrice",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NewOwnerIsZeroAddress",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NotAdmin",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NotInvestor",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ReentrantCallBlocked",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "RefundPeriodEnded",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ZeroAddress",
    "type": "error"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "newAdmin",
        "type": "address"
      }
    ],
    "name": "AdminUpdated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "oldBusinessAdmin",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "newBusinessAdmin",
        "type": "address"
      }
    ],
    "name": "BusinessAdminUpdated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "bool",
        "name": "enabled",
        "type": "bool"
      }
    ],
    "name": "CircuitBreakerEnabled",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [],
    "name": "CircuitBreakerReset",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "string",
        "name": "reason",
        "type": "string"
      }
    ],
    "name": "CircuitBreakerTriggered",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "stalenessThreshold",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "maxDeviation",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "bool",
        "name": "enabled",
        "type": "bool"
      }
    ],
    "name": "CircuitBreakerUpdated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "totalRaised",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "totalTokensSold",
        "type": "uint256"
      }
    ],
    "name": "IEOEnded",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "startTime",
        "type": "uint256"
      }
    ],
    "name": "IEOStarted",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [],
    "name": "IEOpaused",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [],
    "name": "IEOunpaused",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "investor",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "usdcAmount",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "tokenAmount",
        "type": "uint256"
      }
    ],
    "name": "InvestmentMade",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "investor",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "usdcAmount",
        "type": "uint256"
      }
    ],
    "name": "InvestmentRefunded",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "OwnershipTransferred",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "newOracle",
        "type": "address"
      }
    ],
    "name": "PriceOracleUpdated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "minPrice",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "maxPrice",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "bool",
        "name": "enabled",
        "type": "bool"
      }
    ],
    "name": "PriceValidationUpdated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "newAddress",
        "type": "address"
      }
    ],
    "name": "RewardTrackingAddressUpdated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "bool",
        "name": "enabled",
        "type": "bool"
      }
    ],
    "name": "RewardTrackingEnabled",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "investor",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "tokenAmount",
        "type": "uint256"
      }
    ],
    "name": "TokensClaimed",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "businessAdmin",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "USDCWithdrawn",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "CLAIM_DELAY",
    "outputs": [
      {
        "internalType": "uint32",
        "name": "",
        "type": "uint32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "MAX_INVESTMENT",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "MAX_PRICE_DECIMALS",
    "outputs": [
      {
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "MIN_INVESTMENT",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "REFUND_PERIOD",
    "outputs": [
      {
        "internalType": "uint32",
        "name": "",
        "type": "uint32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "USDC_ADDRESS",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "WITHDRAWAL_DELAY",
    "outputs": [
      {
        "internalType": "uint32",
        "name": "",
        "type": "uint32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "admin",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "businessAdmin",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "circuitBreakerEnabled",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "circuitBreakerTriggered",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "claimTokens",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "disableCircuitBreaker",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "emergencyWithdrawUSDC",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "enableCircuitBreaker",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "endIEO",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getBusinessAdmin",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "investor",
        "type": "address"
      }
    ],
    "name": "getClaimableInvestments",
    "outputs": [
      {
        "internalType": "uint256[]",
        "name": "claimableIndices",
        "type": "uint256[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getIEOStatus",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "investor",
        "type": "address"
      }
    ],
    "name": "getInvestment",
    "outputs": [
      {
        "components": [
          {
            "internalType": "uint128",
            "name": "usdcAmount",
            "type": "uint128"
          },
          {
            "internalType": "uint128",
            "name": "tokenAmount",
            "type": "uint128"
          },
          {
            "internalType": "uint64",
            "name": "investmentTime",
            "type": "uint64"
          },
          {
            "internalType": "bool",
            "name": "claimed",
            "type": "bool"
          },
          {
            "internalType": "bool",
            "name": "refunded",
            "type": "bool"
          }
        ],
        "internalType": "struct IIEO.Investment",
        "name": "",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "index",
        "type": "uint256"
      }
    ],
    "name": "getInvestor",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getInvestorCount",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "investor",
        "type": "address"
      }
    ],
    "name": "getInvestorWithdrawableAmount",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getLastValidPrice",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getMaxPriceDeviation",
    "outputs": [
      {
        "internalType": "uint16",
        "name": "",
        "type": "uint16"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getMaxTokenPrice",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getMinTokenPrice",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getPriceStalenessThreshold",
    "outputs": [
      {
        "internalType": "uint32",
        "name": "",
        "type": "uint32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "investor",
        "type": "address"
      }
    ],
    "name": "getRefundableInvestments",
    "outputs": [
      {
        "internalType": "uint256[]",
        "name": "refundableIndices",
        "type": "uint256[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getTotalDeposited",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getTotalWithdrawn",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getUSDCBalance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "investor",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "index",
        "type": "uint256"
      }
    ],
    "name": "getUserInvestmentByIndex",
    "outputs": [
      {
        "components": [
          {
            "internalType": "uint128",
            "name": "usdcAmount",
            "type": "uint128"
          },
          {
            "internalType": "uint128",
            "name": "tokenAmount",
            "type": "uint128"
          },
          {
            "internalType": "uint64",
            "name": "investmentTime",
            "type": "uint64"
          },
          {
            "internalType": "bool",
            "name": "claimed",
            "type": "bool"
          },
          {
            "internalType": "bool",
            "name": "refunded",
            "type": "bool"
          }
        ],
        "internalType": "struct IIEO.Investment",
        "name": "",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "investor",
        "type": "address"
      }
    ],
    "name": "getUserInvestmentCount",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "investor",
        "type": "address"
      }
    ],
    "name": "getUserInvestments",
    "outputs": [
      {
        "components": [
          {
            "internalType": "uint128",
            "name": "usdcAmount",
            "type": "uint128"
          },
          {
            "internalType": "uint128",
            "name": "tokenAmount",
            "type": "uint128"
          },
          {
            "internalType": "uint64",
            "name": "investmentTime",
            "type": "uint64"
          },
          {
            "internalType": "bool",
            "name": "claimed",
            "type": "bool"
          },
          {
            "internalType": "bool",
            "name": "refunded",
            "type": "bool"
          }
        ],
        "internalType": "struct IIEO.Investment[]",
        "name": "",
        "type": "tuple[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getWithdrawableAmount",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getWithdrawalDelay",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "ieoStartTime",
    "outputs": [
      {
        "internalType": "uint64",
        "name": "",
        "type": "uint64"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "usdcAmount",
        "type": "uint256"
      }
    ],
    "name": "invest",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "investmentCounter",
    "outputs": [
      {
        "internalType": "uint32",
        "name": "",
        "type": "uint32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "name": "investors",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isCircuitBreakerEnabled",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isCircuitBreakerTriggered",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isIEOActive",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "isInvestor",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isPaused",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isPriceValidationEnabled",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isRewardTrackingEnabled",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "lastValidPrice",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "maxPriceDeviation",
    "outputs": [
      {
        "internalType": "uint16",
        "name": "",
        "type": "uint16"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "maxTokenPrice",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "minTokenPrice",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "pauseIEO",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "priceOracle",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "priceStalenessThreshold",
    "outputs": [
      {
        "internalType": "uint32",
        "name": "",
        "type": "uint32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "refundInvestment",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "investmentIndex",
        "type": "uint256"
      }
    ],
    "name": "refundInvestmentByIndex",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "resetCircuitBreaker",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "rewardTrackingAddress",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_businessAdmin",
        "type": "address"
      }
    ],
    "name": "setBusinessAdmin",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint32",
        "name": "_priceStalenessThreshold",
        "type": "uint32"
      },
      {
        "internalType": "uint16",
        "name": "_maxPriceDeviation",
        "type": "uint16"
      },
      {
        "internalType": "bool",
        "name": "_enabled",
        "type": "bool"
      }
    ],
    "name": "setCircuitBreaker",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_priceOracle",
        "type": "address"
      }
    ],
    "name": "setPriceOracle",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint128",
        "name": "_minTokenPrice",
        "type": "uint128"
      },
      {
        "internalType": "uint128",
        "name": "_maxTokenPrice",
        "type": "uint128"
      }
    ],
    "name": "setPriceValidation",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_rewardTrackingAddress",
        "type": "address"
      }
    ],
    "name": "setRewardTrackingAddress",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "startIEO",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "tokenAddress",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalDeposited",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalRaised",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalTokensSold",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalWithdrawn",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "",
        "type": "uint128"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "transferOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "unpauseIEO",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "name": "userInvestments",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "usdcAmount",
        "type": "uint128"
      },
      {
        "internalType": "uint128",
        "name": "tokenAmount",
        "type": "uint128"
      },
      {
        "internalType": "uint64",
        "name": "investmentTime",
        "type": "uint64"
      },
      {
        "internalType": "bool",
        "name": "claimed",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "refunded",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "withdrawAllUSDC",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint128",
        "name": "amount",
        "type": "uint128"
      }
    ],
    "name": "withdrawUSDC",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]

IEO_BYTECODE = "61016060405234801562000011575f80fd5b50604051620042b3380380620042b3833981016040819052620000349162000350565b33806200005457604051633a247dd760e11b815260040160405180910390fd5b6200005f816200024b565b506001600160a01b038616620000885760405163d92e233d60e01b815260040160405180910390fd5b6001600160a01b038516620000b05760405163d92e233d60e01b815260040160405180910390fd5b6001600160a01b038416620000d85760405163d92e233d60e01b815260040160405180910390fd5b825f03620000f957604051632a31921560e11b815260040160405180910390fd5b815f036200011a5760405163d35f18fd60e01b815260040160405180910390fd5b8181116200013b5760405163237f41b560e01b815260040160405180910390fd5b6001600160a01b0386811660805285811660a052600380546001600160a01b031916918616919091179055620001758362015180620003b2565b63ffffffff1660c0526200018d8362015180620003b2565b63ffffffff1660e0526001600160801b0380831661010052811661012052620001ba8362015180620003b2565b63ffffffff1661014052600180546001600160a01b03191690555f6006819055600780547fffffffff00000000ffffffff0000000000000000000000000000000000000000167903e80000000000000e100000000000000000000000000000000017905562000229906200029a565b620002345f620002d6565b6200023f5f62000305565b505050505050620003dc565b5f80546001600160a01b038381166001600160a01b0319831681178455604051919092169283917f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e09190a35050565b7f2d3996652885557ed57cfc94ac2c251fe5d04a1c8a5f6b32b7507118673771dd5f82620002c9575f620002cc565b60015b60ff169091555050565b7f3269ffed2b18a39abd6a644fc796888eaaf9ff1251aa3ad897a0a560d34ec6c35f82620002c9575f620002cc565b7fea7662f213c1e365ff55c50b7d32910320875afda2fa69e210c9167a2d7da1d35f82620002c9575f620002cc565b80516001600160a01b03811681146200034b575f80fd5b919050565b5f805f805f8060c0878903121562000366575f80fd5b620003718762000334565b9550620003816020880162000334565b9450620003916040880162000334565b9350606087015192506080870151915060a087015190509295509295509295565b8082028115828204841417620003d657634e487b7160e01b5f52601160045260245ffd5b92915050565b60805160a05160c05160e051610100516101205161014051613e1c620004975f395f818161047d015281816104e0015281816128f70152612d9f01525f81816106a001526112d101525f81816106c7015261129f01525f81816107ba01528181611eb001528181612106015281816121ee01526124eb01525f8181610a8a01528181610c7401528181610d5c0152611b2201525f8181610b34015261237401525f8181610916015281816113340152611be00152613e1c5ff3fe608060405234801561000f575f80fd5b506004361061044d575f3560e01c806387d280cd11610242578063bb09d9b711610140578063de5f8d93116100bf578063ecb40af911610084578063ecb40af914610aef578063f2fde38b14610b02578063f31b10ef14610b15578063f851a44014610b2f578063ff50abdc14610b56575f80fd5b8063de5f8d9314610a7d578063e18132c414610a85578063e337e23614610aac578063e7967c1614610ab4578063e8171a0f14610ac7575f80fd5b8063c5a0afda11610105578063c5a0afda14610a11578063c5c4744c14610a22578063c99dccf914610a35578063cee2a9cf14610a48578063ddcbc51614610a6a575f80fd5b8063bb09d9b714610997578063bd111870146109b2578063c34f548a146109c9578063c3520788146109de578063c52c5c88146109f1575f80fd5b8063960524e3116101cc578063a7c782a011610191578063a7c782a014610940578063ab9068fa14610953578063ad90af7a14610967578063b187bd261461096f578063b68ef55914610986575f80fd5b8063960524e3146108ce578063975b8662146108d65780639b7d7be8146108fe5780639d76ea5814610911578063a64254c314610938575f80fd5b80638da5cb5b116102125780638da5cb5b1461083a5780638e25e3e31461084a57806390be10cc1461085d5780639244adcd14610865578063924a80cc146108bb575f80fd5b806387d280cd146107ef57806389404a79146108075780638957ce541461081f5780638b3e161c14610827575f80fd5b806346a611351161034f5780635d7339f4116102d95780637994c1a11161029e5780637994c1a11461078557806379ade3831461079c5780637a266cfc146107a45780637f6578d3146107b557806385f288f2146107dc575f80fd5b80635d7339f4146107235780635dabb20e1461073657806363b2011714610749578063715018a61461076357806377e5c4a81461076b575f80fd5b80634c76361e1161031f5780634c76361e1461069b5780634ef8ff33146106c257806351108cac146106e9578063530e784f146106fd5780635bab47d914610710575f80fd5b806346a611351461065457806348c54b9d146106675780634b3197131461066f5780634c2b118014610689575f80fd5b806321208fa2116103db5780633a67cb1c116103a05780633a67cb1c146105f05780633cfd1ccc146105f85780633d8d30b6146106005780633feb5f2b1461062a57806343c8a8d41461063d575f80fd5b806321208fa21461059a5780632630c12f146105a257806326df6e91146105cd5780632afcf480146105d55780632de7722f146105e8575f80fd5b80630ebb172a116104215780630ebb172a146104db57806311ce305914610517578063146b58df1461053557806316871f0f146105555780631aef1aa114610568575f80fd5b80626059a014610451578063031609401461047b57806306faa6f3146104b1578063076628e1146104d1575b5f80fd5b6007546001600160801b03165b6040516001600160801b0390911681526020015b60405180910390f35b7f000000000000000000000000000000000000000000000000000000000000000063ffffffff165b604051908152602001610472565b6104c46104bf366004613921565b610b69565b6040516104729190613941565b6104d9610de1565b005b6105027f000000000000000000000000000000000000000000000000000000000000000081565b60405163ffffffff9091168152602001610472565b600754600160d01b900460ff165b6040519015158152602001610472565b610548610543366004613921565b610ebf565b60405161047291906139ce565b60075461045e906001600160801b031681565b60035461058290600160a01b90046001600160401b031681565b6040516001600160401b039091168152602001610472565b6104d961100d565b6002546105b5906001600160a01b031681565b6040516001600160a01b039091168152602001610472565b6104d961108e565b6104d96105e33660046139dc565b611255565b610525611819565b610525611855565b6104a3611884565b7f2d3996652885557ed57cfc94ac2c251fe5d04a1c8a5f6b32b7507118673771dd54600114610525565b6105b56106383660046139dc565b6118f7565b5f80516020613d8783398151915254600114610525565b6105486106623660046139f3565b61191f565b6104d9611a79565b60055461045e90600160801b90046001600160801b031681565b600754600160d81b900460ff16610525565b61045e7f000000000000000000000000000000000000000000000000000000000000000081565b61045e7f000000000000000000000000000000000000000000000000000000000000000081565b60075461052590600160d81b900460ff1681565b6104d961070b366004613921565b611ca2565b6104d961071e3660046139dc565b611d3c565b6104c4610731366004613921565b611ffb565b60065461045e906001600160801b031681565b60045461045e90600160801b90046001600160801b031681565b6104d9612269565b60065461045e90600160801b90046001600160801b031681565b60075461050290600160a01b900463ffffffff1681565b6104d9612271565b6003546001600160a01b03166105b5565b6105027f000000000000000000000000000000000000000000000000000000000000000081565b6104d96107ea366004613921565b612369565b600654600160801b90046001600160801b031661045e565b600554600160801b90046001600160801b03166104a3565b6104d9612442565b6104d9610835366004613a28565b61262d565b5f546001600160a01b03166105b5565b6003546105b5906001600160a01b031681565b6104a36127cd565b6108786108733660046139f3565b6129ab565b604080516001600160801b0396871681529590941660208601526001600160401b039092169284019290925290151560608301521515608082015260a001610472565b6104d96108c9366004613921565b612a17565b600a546104a3565b6007546108eb90600160c01b900461ffff1681565b60405161ffff9091168152602001610472565b6104d961090c366004613a94565b612af6565b6105b57f000000000000000000000000000000000000000000000000000000000000000081565b6104d9612c19565b6104a361094e366004613921565b612ca1565b60075461052590600160d01b900460ff1681565b6104d9612e0e565b5f80516020613da783398151915254600114610525565b6005546001600160801b03166104a3565b6105b573966c69ae5b4fb4744e976eb058cfe7592bd935d281565b60075461050290600160801b900463ffffffff1681565b600754600160801b900463ffffffff16610502565b6104d96109ec3660046139dc565b612f01565b610a046109ff366004613921565b612fc8565b6040516104729190613ac5565b6006546001600160801b031661045e565b60045461045e906001600160801b031681565b6105b5610a433660046139dc565b613091565b610525610a56366004613921565b60096020525f908152604090205460ff1681565b600754600160c01b900461ffff166108eb565b6104d96130bf565b6105027f000000000000000000000000000000000000000000000000000000000000000081565b6104d9613139565b6104d9610ac2366004613b06565b61324a565b6104a3610ad5366004613921565b6001600160a01b03165f9081526008602052604090205490565b6001546105b5906001600160a01b031681565b6104d9610b10366004613921565b613486565b610b1d601281565b60405160ff9091168152602001610472565b6105b57f000000000000000000000000000000000000000000000000000000000000000081565b60055461045e906001600160801b031681565b6001600160a01b0381165f908152600860209081526040808320805482518185028101850190935280835260609493849084015b82821015610c24575f8481526020908190206040805160a0810182526002860290920180546001600160801b038082168552600160801b90910416838501526001908101546001600160401b0381169284019290925260ff600160401b8304811615156060850152600160481b909204909116151560808301529083529092019101610b9d565b5050505090505f4290505f805b8351811015610cd1575f848281518110610c4d57610c4d613b1f565b602002602001015190508060600151158015610c6b57508060800151155b8015610cb557507f000000000000000000000000000000000000000000000000000000000000000063ffffffff168160400151610ca89190613b47565b6001600160401b03168410155b15610cc85782610cc481613b6e565b9350505b50600101610c31565b50806001600160401b03811115610cea57610cea613b86565b604051908082528060200260200182016040528015610d13578160200160208202803683370190505b5093505f805b8451811015610dd7575f858281518110610d3557610d35613b1f565b602002602001015190508060600151158015610d5357508060800151155b8015610d9d57507f000000000000000000000000000000000000000000000000000000000000000063ffffffff168160400151610d909190613b47565b6001600160401b03168510155b15610dce5781878481518110610db557610db5613b1f565b602090810291909101015282610dca81613b6e565b9350505b50600101610d19565b5050505050919050565b6003546001600160a01b03163314801590610e0657505f546001600160a01b03163314155b15610e2457604051637bfa4b9f60e01b815260040160405180910390fd5b5f80516020613d8783398151915254600114610e5b5760405162461bcd60e51b8152600401610e5290613b9a565b60405180910390fd5b610e645f61348f565b610e6d5f6134b6565b600454604080516001600160801b038084168252600160801b90930490921660208301527fd28ade5316d9a9cb5c641d1a2242187eb34afbc6cc14f16992d7a3d233f60b2f91015b60405180910390a1565b6040805160a0810182525f808252602080830182905282840182905260608301829052608083018290526001600160a01b0385168252600881528382208054855181840281018401909652808652939492939091849084015b82821015610f9f575f8481526020908190206040805160a0810182526002860290920180546001600160801b038082168552600160801b90910416838501526001908101546001600160401b0381169284019290925260ff600160401b8304811615156060850152600160481b909204909116151560808301529083529092019101610f18565b50505050905080515f03610fde5750506040805160a0810182525f80825260208201819052918101829052606081018290526080810191909152919050565b8060018251610fed9190613bc2565b81518110610ffd57610ffd613b1f565b6020026020010151915050919050565b6003546001600160a01b0316331480159061103257505f546001600160a01b03163314155b1561105057604051637bfa4b9f60e01b815260040160405180910390fd5b6007805461ffff60d01b191690556040515f81527f558abc8e44db5b5d1d9fa5ad99dd7c1978a8fd793ca5c6cb2e7c202c4049ca8090602001610eb5565b6003546001600160a01b031633148015906110b357505f546001600160a01b03163314155b156110d157604051637bfa4b9f60e01b815260040160405180910390fd5b6110d96134d0565b5f6110e26127cd565b90505f811161112c5760405162461bcd60e51b8152602060048201526016602482015275139bc81dda5d1a191c985dd8589b1948185b5bdd5b9d60521b6044820152606401610e52565b80600560108282829054906101000a90046001600160801b03166111509190613bd5565b82546001600160801b039182166101009390930a92830291909202199091161790555060035460405163a9059cbb60e01b81526001600160a01b0390911660048201526024810182905273966c69ae5b4fb4744e976eb058cfe7592bd935d29063a9059cbb906044016020604051808303815f875af11580156111d5573d5f803e3d5ffd5b505050506040513d601f19601f820116820180604052508101906111f99190613bf5565b506003546040518281526001600160a01b03909116907f2aa7fb97600ea702b454359fc3d02ae9fa48367e7155505d38cee896e5b5aae79060200160405180910390a25061125360015f80516020613dc783398151915255565b565b61125d6134d0565b600754600160d01b900460ff16801561127f5750600754600160d81b900460ff165b1561129d57604051630552b01360e31b815260040160405180910390fd5b7f00000000000000000000000000000000000000000000000000000000000000006001600160801b03168110806112fc57507f00000000000000000000000000000000000000000000000000000000000000006001600160801b031681115b1561131a57604051631bf1f55760e11b815260040160405180910390fd5b6002546040516341976e0960e01b81526001600160a01b037f0000000000000000000000000000000000000000000000000000000000000000811660048301525f9283928392909116906341976e0990602401606060405180830381865afa158015611388573d5f803e3d5ffd5b505050506040513d601f19601f820116820180604052508101906113ac9190613c10565b925092509250825f036113d15760405162bfc92160e01b815260040160405180910390fd5b6113db8382613509565b6006546001600160801b03161515806114055750600654600160801b90046001600160801b031615155b1561149a576006546001600160801b03161580159061142e57506006546001600160801b031683105b1561144b5760405162bfc92160e01b815260040160405180910390fd5b600654600160801b90046001600160801b03161580159061147d5750600654600160801b90046001600160801b031683115b1561149a5760405162bfc92160e01b815260040160405180910390fd5b5f6114a6858585613702565b6040516323b872dd60e01b81523360048201523060248201526044810187905290915073966c69ae5b4fb4744e976eb058cfe7592bd935d2906323b872dd906064016020604051808303815f875af1158015611504573d5f803e3d5ffd5b505050506040513d601f19601f820116820180604052508101906115289190613bf5565b50600580548691905f906115469084906001600160801b0316613bd5565b82546001600160801b039182166101009390930a9283029282021916919091179091556040805160a081018252888316815284831660208083019182526001600160401b034281168486019081525f606086018181526080870182815233808452600887528984208054600181810183559186528886208b519a518e16600160801b029a909d16999099176002909902909b019788559351969099018054915199511515600160481b0260ff60481b199a1515600160401b0268ffffffffffffffffff1990931697909516969096171797909716919091179092559084526009905291205490915060ff1661169157335f818152600960205260408120805460ff19166001908117909155600a805491820181559091527fc65a7bb8d6351c1cf70c95a316cc6a92839c986682d98bc35f958f4883f9d2a80180546001600160a01b03191690911790555b600480548791905f906116ae9084906001600160801b0316613bd5565b92506101000a8154816001600160801b0302191690836001600160801b0316021790555081600460108282829054906101000a90046001600160801b03166116f69190613bd5565b92506101000a8154816001600160801b0302191690836001600160801b031602179055506117457f2d3996652885557ed57cfc94ac2c251fe5d04a1c8a5f6b32b7507118673771dd5460011490565b801561175b57506001546001600160a01b031615155b156117c057600154604051631235a0df60e31b8152336004820152602481018490526001600160a01b03909116906391ad06f8906044015f604051808303815f87803b1580156117a9575f80fd5b505af11580156117bb573d5f803e3d5ffd5b505050505b604080518781526020810184905233917f0a9bd546b0677820e552855be50bea4847cd782448e9f00d2543ceb3b91c2c5b910160405180910390a2505050505061181660015f80516020613dc783398151915255565b50565b5f6118325f80516020613d878339815191525460011490565b80156118505750600354600160a01b90046001600160401b03164210155b905090565b6006545f906001600160801b0316151580611850575050600654600160801b90046001600160801b0316151590565b6040516370a0823160e01b81523060048201525f9073966c69ae5b4fb4744e976eb058cfe7592bd935d2906370a0823190602401602060405180830381865afa1580156118d3573d5f803e3d5ffd5b505050506040513d601f19601f820116820180604052508101906118509190613c3b565b600a8181548110611906575f80fd5b5f918252602090912001546001600160a01b0316905081565b6040805160a0810182525f808252602080830182905282840182905260608301829052608083018290526001600160a01b0386168252600881528382208054855181840281018401909652808652939492939091849084015b828210156119ff575f8481526020908190206040805160a0810182526002860290920180546001600160801b038082168552600160801b90910416838501526001908101546001600160401b0381169284019290925260ff600160401b8304811615156060850152600160481b909204909116151560808301529083529092019101611978565b50505050905080518310611a555760405162461bcd60e51b815260206004820152601e60248201527f496e766573746d656e7420696e646578206f7574206f6620626f756e647300006044820152606401610e52565b808381518110611a6757611a67613b1f565b60200260200101519150505b92915050565b611a816134d0565b335f9081526008602052604081208054909103611ab157604051633ab272c160e01b815260040160405180910390fd5b5f42815b8354811015611ba3575f848281548110611ad157611ad1613b1f565b905f5260205f20906002020190508060010160089054906101000a900460ff1680611b0757506001810154600160481b900460ff165b15611b125750611b9b565b6001810154611b519063ffffffff7f000000000000000000000000000000000000000000000000000000000000000016906001600160401b0316613b47565b6001600160401b03168310611b99578054611b7c90600160801b90046001600160801b031685613c52565b60018201805468ff00000000000000001916600160401b17905593505b505b600101611ab5565b50815f03611bc45760405163916da0d160e01b815260040160405180910390fd5b60405163a9059cbb60e01b8152336004820152602481018390527f00000000000000000000000000000000000000000000000000000000000000006001600160a01b03169063a9059cbb906044016020604051808303815f875af1158015611c2e573d5f803e3d5ffd5b505050506040513d601f19601f82011682018060405250810190611c529190613bf5565b5060405182815233907f896e034966eaaf1adc54acc0f257056febbd300c9e47182cf761982cf1f5e430906020015b60405180910390a250505061125360015f80516020613dc783398151915255565b5f546001600160a01b03163314611ccc57604051632e6c18c960e11b815260040160405180910390fd5b6001600160a01b038116611cf35760405163d92e233d60e01b815260040160405180910390fd5b600280546001600160a01b0319166001600160a01b0383169081179091556040517fefe8ab924ca486283a79dc604baa67add51afb82af1db8ac386ebbba643cdffd905f90a250565b611d446134d0565b335f9081526008602052604081208054909103611d7457604051633ab272c160e01b815260040160405180910390fd5b80548210611dc45760405162461bcd60e51b815260206004820152601e60248201527f496e766573746d656e7420696e646578206f7574206f6620626f756e647300006044820152606401610e52565b5f818381548110611dd757611dd7613b1f565b905f5260205f20906002020190508060010160089054906101000a900460ff1615611e445760405162461bcd60e51b815260206004820152601a60248201527f496e766573746d656e7420616c726561647920636c61696d65640000000000006044820152606401610e52565b6001810154600160481b900460ff1615611ea05760405162461bcd60e51b815260206004820152601b60248201527f496e766573746d656e7420616c726561647920726566756e64656400000000006044820152606401610e52565b6001810154611edf9063ffffffff7f000000000000000000000000000000000000000000000000000000000000000016906001600160401b0316613b47565b6001600160401b0316421115611f0857604051632127579d60e21b815260040160405180910390fd5b60018101805460ff60481b1916600160481b179055805460405163a9059cbb60e01b81523360048201526001600160801b03909116602482015273966c69ae5b4fb4744e976eb058cfe7592bd935d29063a9059cbb906044016020604051808303815f875af1158015611f7d573d5f803e3d5ffd5b505050506040513d601f19601f82011682018060405250810190611fa19190613bf5565b5080546040516001600160801b03909116815233907f36223d67e276b82c1b7ba6855d656a2b8071564264666ef7977022c5d8a644029060200160405180910390a2505061181660015f80516020613dc783398151915255565b6001600160a01b0381165f908152600860209081526040808320805482518185028101850190935280835260609493849084015b828210156120b6575f8481526020908190206040805160a0810182526002860290920180546001600160801b038082168552600160801b90910416838501526001908101546001600160401b0381169284019290925260ff600160401b8304811615156060850152600160481b90920490911615156080830152908352909201910161202f565b5050505090505f4290505f805b8351811015612163575f8482815181106120df576120df613b1f565b6020026020010151905080606001511580156120fd57508060800151155b801561214757507f000000000000000000000000000000000000000000000000000000000000000063ffffffff16816040015161213a9190613b47565b6001600160401b03168411155b1561215a578261215681613b6e565b9350505b506001016120c3565b50806001600160401b0381111561217c5761217c613b86565b6040519080825280602002602001820160405280156121a5578160200160208202803683370190505b5093505f805b8451811015610dd7575f8582815181106121c7576121c7613b1f565b6020026020010151905080606001511580156121e557508060800151155b801561222f57507f000000000000000000000000000000000000000000000000000000000000000063ffffffff1681604001516122229190613b47565b6001600160401b03168511155b15612260578187848151811061224757612247613b1f565b60209081029190910101528261225c81613b6e565b9350505b506001016121ab565b611253613801565b6003546001600160a01b0316331480159061229657505f546001600160a01b03163314155b156122b457604051637bfa4b9f60e01b815260040160405180910390fd5b5f80516020613d87833981519152546001146122e25760405162461bcd60e51b8152600401610e5290613b9a565b5f80516020613da7833981519152546001036123355760405162461bcd60e51b8152602060048201526012602482015271125153c8185b1c9958591e481c185d5cd95960721b6044820152606401610e52565b61233f60016134b6565b6040517f4b8df69b03c1b4f9352f415f774c6738325eb0855dfcff15d9b9bfe8fe3efd3f905f90a1565b336001600160a01b037f000000000000000000000000000000000000000000000000000000000000000016148015906123ac57505f546001600160a01b03163314155b156123ca57604051637bfa4b9f60e01b815260040160405180910390fd5b6001600160a01b0381166123f15760405163d92e233d60e01b815260040160405180910390fd5b600380546001600160a01b038381166001600160a01b0319831681179093556040519116919082907f19b780f6e09d47d54c68aac72ed1d9228f0e78ef5f03e2c74418a2b68978939a905f90a35050565b61244a6134d0565b335f908152600860205260408120805490910361247a57604051633ab272c160e01b815260040160405180910390fd5b5f42815b8354811015612560575f84828154811061249a5761249a613b1f565b905f5260205f20906002020190508060010160089054906101000a900460ff16806124d057506001810154600160481b900460ff165b156124db5750612558565b600181015461251a9063ffffffff7f000000000000000000000000000000000000000000000000000000000000000016906001600160401b0316613b47565b6001600160401b0316831161255657805461253e906001600160801b031685613c52565b60018201805460ff60481b1916600160481b17905593505b505b60010161247e565b50815f0361258157604051632127579d60e21b815260040160405180910390fd5b60405163a9059cbb60e01b81523360048201526024810183905273966c69ae5b4fb4744e976eb058cfe7592bd935d29063a9059cbb906044016020604051808303815f875af11580156125d6573d5f803e3d5ffd5b505050506040513d601f19601f820116820180604052508101906125fa9190613bf5565b5060405182815233907f36223d67e276b82c1b7ba6855d656a2b8071564264666ef7977022c5d8a6440290602001611c81565b6003546001600160a01b0316331480159061265257505f546001600160a01b03163314155b1561267057604051637bfa4b9f60e01b815260040160405180910390fd5b5f8363ffffffff16116126c55760405162461bcd60e51b815260206004820152601b60248201527f496e76616c6964207374616c656e657373207468726573686f6c6400000000006044820152606401610e52565b6127108261ffff16111561271b5760405162461bcd60e51b815260206004820152601c60248201527f496e76616c696420646576696174696f6e2070657263656e74616765000000006044820152606401610e52565b6007805469ffff00000000ffffffff60801b1916600160801b63ffffffff86160261ffff60c01b191617600160c01b61ffff8516021760ff60d01b1916600160d01b83158015919091029190911790915561277e576007805460ff60d81b191690555b6040805163ffffffff8516815261ffff841660208201528215158183015290517f5cedba746cf3c1de98d00cf7ebf27545192185471c5a1ad549548e0fd051beec9181900360600190a1505050565b5f8042815b600a54811015612967575f600a82815481106127f0576127f0613b1f565b5f9182526020808320909101546001600160a01b031680835260088252604080842080548251818602810186019093528083529295509092909190849084015b828210156128b7575f8481526020908190206040805160a0810182526002860290920180546001600160801b038082168552600160801b90910416838501526001908101546001600160401b0381169284019290925260ff600160401b8304811615156060850152600160481b909204909116151560808301529083529092019101612830565b5050505090505f5b815181101561295c575f8282815181106128db576128db613b1f565b602002602001015190508060800151156128f55750612954565b7f000000000000000000000000000000000000000000000000000000000000000063ffffffff16816040015161292b9190613b47565b6001600160401b0316861061295257805161294f906001600160801b031688613c52565b96505b505b6001016128bf565b5050506001016127d2565b50600554600160801b90046001600160801b03168211612987575f6129a4565b6005546129a490600160801b90046001600160801b031683613bc2565b9250505090565b6008602052815f5260405f2081815481106129c4575f80fd5b5f918252602090912060029091020180546001909101546001600160801b038083169450600160801b90920490911691506001600160401b0381169060ff600160401b8204811691600160481b90041685565b5f546001600160a01b03163314612a4157604051632e6c18c960e11b815260040160405180910390fd5b6001600160a01b038116612a685760405163d92e233d60e01b815260040160405180910390fd5b600180546001600160a01b0319166001600160a01b038316178155612a8c90613834565b6040516001600160a01b038216907f9962f0fa162172ba3dc3e0912f2526f2c9041edead2f56b562415cabc9356aff905f90a2604051600181527fd5aec850d69a1d40917d707745a75fa581809b43d331005cec287da0faf3c80d9060200160405180910390a150565b6003546001600160a01b03163314801590612b1b57505f546001600160a01b03163314155b15612b3957604051637bfa4b9f60e01b815260040160405180910390fd5b5f826001600160801b0316118015612b5957505f816001600160801b0316115b8015612b775750806001600160801b0316826001600160801b031610155b15612b955760405163237f41b560e01b815260040160405180910390fd5b6001600160801b03818116600160801b029083169081176006557fad9175a0aa9809642815bb2292ed3d05636eaf20c54571b1ccc6341e011ae63a9083908390151580612bea57505f846001600160801b0316115b604080516001600160801b03948516815293909216602084015215159082015260600160405180910390a15050565b6003546001600160a01b03163314801590612c3e57505f546001600160a01b03163314155b15612c5c57604051637bfa4b9f60e01b815260040160405180910390fd5b6007805461ffff60d01b1916600160d01b179055604051600181527f558abc8e44db5b5d1d9fa5ad99dd7c1978a8fd793ca5c6cb2e7c202c4049ca8090602001610eb5565b6001600160a01b0381165f90815260086020908152604080832080548251818502810185019093528083528493849084015b82821015612d5a575f8481526020908190206040805160a0810182526002860290920180546001600160801b038082168552600160801b90910416838501526001908101546001600160401b0381169284019290925260ff600160401b8304811615156060850152600160481b909204909116151560808301529083529092019101612cd3565b5050505090505f804290505f5b8351811015612e04575f848281518110612d8357612d83613b1f565b60200260200101519050806080015115612d9d5750612dfc565b7f000000000000000000000000000000000000000000000000000000000000000063ffffffff168160400151612dd39190613b47565b6001600160401b03168310612dfa578051612df7906001600160801b031685613c52565b93505b505b600101612d67565b5090949350505050565b6003546001600160a01b03163314801590612e3357505f546001600160a01b03163314155b15612e5157604051637bfa4b9f60e01b815260040160405180910390fd5b5f80516020613d8783398151915254600114612e7f5760405162461bcd60e51b8152600401610e5290613b9a565b5f80516020613da783398151915254600114612ece5760405162461bcd60e51b815260206004820152600e60248201526d125153c81b9bdd081c185d5cd95960921b6044820152606401610e52565b612ed75f6134b6565b6040517f466ddd10824c213c892808c6cb14556be36b4a4b5121627a1b848fed589a18b6905f90a1565b5f546001600160a01b03163314612f2b57604051632e6c18c960e11b815260040160405180910390fd5b73966c69ae5b4fb4744e976eb058cfe7592bd935d263a9059cbb612f565f546001600160a01b031690565b6040516001600160e01b031960e084901b1681526001600160a01b039091166004820152602481018490526044016020604051808303815f875af1158015612fa0573d5f803e3d5ffd5b505050506040513d601f19601f82011682018060405250810190612fc49190613bf5565b5050565b6001600160a01b0381165f908152600860209081526040808320805482518185028101850190935280835260609492939192909184015b82821015613086575f8481526020908190206040805160a0810182526002860290920180546001600160801b038082168552600160801b90910416838501526001908101546001600160401b0381169284019290925260ff600160401b8304811615156060850152600160481b909204909116151560808301529083529092019101612fff565b505050509050919050565b5f600a82815481106130a5576130a5613b1f565b5f918252602090912001546001600160a01b031692915050565b6003546001600160a01b031633148015906130e457505f546001600160a01b03163314155b1561310257604051637bfa4b9f60e01b815260040160405180910390fd5b6007805460ff60d81b191690556040517f749ce304ab81145be90b787a7777d030c801b4cfd19e6b30df21973a54ec004c905f90a1565b6003546001600160a01b0316331480159061315e57505f546001600160a01b03163314155b1561317c57604051637bfa4b9f60e01b815260040160405180910390fd5b5f80516020613d87833981519152546001036131cf5760405162461bcd60e51b815260206004820152601260248201527149454f20616c72656164792061637469766560701b6044820152606401610e52565b6003805467ffffffffffffffff60a01b1916600160a01b426001600160401b0316021790556131fe600161348f565b6132075f6134b6565b600354604051600160a01b9091046001600160401b031681527fed4b8508c6db02c23ec5358d0d937c123ddf9ae484265dc3155a22d5f408e18690602001610eb5565b6003546001600160a01b0316331480159061326f57505f546001600160a01b03163314155b1561328d57604051637bfa4b9f60e01b815260040160405180910390fd5b6132956134d0565b5f816001600160801b0316116132ed5760405162461bcd60e51b815260206004820152601d60248201527f416d6f756e74206d7573742062652067726561746572207468616e20300000006044820152606401610e52565b6132f56127cd565b816001600160801b031611156133585760405162461bcd60e51b815260206004820152602260248201527f416d6f756e74206578636565647320776974686472617761626c6520616d6f756044820152611b9d60f21b6064820152608401610e52565b80600560108282829054906101000a90046001600160801b031661337c9190613bd5565b82546101009290920a6001600160801b0381810219909316918316021790915560035460405163a9059cbb60e01b81526001600160a01b039091166004820152908316602482015273966c69ae5b4fb4744e976eb058cfe7592bd935d2915063a9059cbb906044016020604051808303815f875af1158015613400573d5f803e3d5ffd5b505050506040513d601f19601f820116820180604052508101906134249190613bf5565b506003546040516001600160801b03831681526001600160a01b03909116907f2aa7fb97600ea702b454359fc3d02ae9fa48367e7155505d38cee896e5b5aae79060200160405180910390a261181660015f80516020613dc783398151915255565b61181681613861565b5f80516020613d878339815191525f826134a9575f6134ac565b60015b60ff169091555050565b5f80516020613da78339815191525f826134a9575f6134ac565b5f80516020613dc7833981519152805460011981016135025760405163139b643560e21b815260040160405180910390fd5b5060029055565b600754600160d01b900460ff1661351e575050565b6007544290600160801b900463ffffffff1661353a8383613bc2565b11156135c6576007805460ff60d81b1916600160d81b1790556040517f955ab0bdc02be6b79ebc0fd3b6cf87b6d751525a0220e904b25323ad2544645d906135a5906020808252600f908201526e507269636520746f6f207374616c6560881b604082015260600190565b60405180910390a1604051630552b01360e31b815260040160405180910390fd5b6007546001600160801b0316156136d5576007545f906001600160801b0316841161361c576007546001600160801b03166136018582613bc2565b61360d90612710613c65565b6136179190613c7c565b613648565b6007546001600160801b03166136328186613bc2565b61363e90612710613c65565b6136489190613c7c565b600754909150600160c01b900461ffff168111156136d3576007805460ff60d81b1916600160d81b1790556040517f955ab0bdc02be6b79ebc0fd3b6cf87b6d751525a0220e904b25323ad2544645d906135a59060208082526018908201527f507269636520646576696174696f6e20746f6f20686967680000000000000000604082015260600190565b505b5050600780546fffffffffffffffffffffffffffffffff19166001600160801b0392909216919091179055565b5f60128211156137545760405162461bcd60e51b815260206004820152601760248201527f507269636520646563696d616c7320746f6f20686967680000000000000000006044820152606401610e52565b5f61376083600a613d7b565b90505f8161377687670de0b6b3a7640000613c65565b6137809190613c65565b905081670de0b6b3a76400006137968884613c7c565b6137a09190613c7c565b146137ed5760405162461bcd60e51b815260206004820152601d60248201527f4f766572666c6f7720696e20746f6b656e2063616c63756c6174696f6e0000006044820152606401610e52565b6137f78582613c7c565b9695505050505050565b5f546001600160a01b0316331461382b57604051632e6c18c960e11b815260040160405180910390fd5b6112535f6138b7565b7f2d3996652885557ed57cfc94ac2c251fe5d04a1c8a5f6b32b7507118673771dd5f826134a9575f6134ac565b5f546001600160a01b0316331461388b57604051632e6c18c960e11b815260040160405180910390fd5b6001600160a01b0381166138b257604051633a247dd760e11b815260040160405180910390fd5b611816815b5f80546001600160a01b038381166001600160a01b0319831681178455604051919092169283917f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e09190a35050565b80356001600160a01b038116811461391c575f80fd5b919050565b5f60208284031215613931575f80fd5b61393a82613906565b9392505050565b602080825282518282018190525f9190848201906040850190845b818110156139785783518352928401929184019160010161395c565b50909695505050505050565b6001600160801b03808251168352806020830151166020840152506001600160401b0360408201511660408301526060810151151560608301526080810151151560808301525050565b60a08101611a738284613984565b5f602082840312156139ec575f80fd5b5035919050565b5f8060408385031215613a04575f80fd5b613a0d83613906565b946020939093013593505050565b8015158114611816575f80fd5b5f805f60608486031215613a3a575f80fd5b833563ffffffff81168114613a4d575f80fd5b9250602084013561ffff81168114613a63575f80fd5b91506040840135613a7381613a1b565b809150509250925092565b80356001600160801b038116811461391c575f80fd5b5f8060408385031215613aa5575f80fd5b613aae83613a7e565b9150613abc60208401613a7e565b90509250929050565b602080825282518282018190525f9190848201906040850190845b8181101561397857613af3838551613984565b9284019260a09290920191600101613ae0565b5f60208284031215613b16575f80fd5b61393a82613a7e565b634e487b7160e01b5f52603260045260245ffd5b634e487b7160e01b5f52601160045260245ffd5b6001600160401b03818116838216019080821115613b6757613b67613b33565b5092915050565b5f60018201613b7f57613b7f613b33565b5060010190565b634e487b7160e01b5f52604160045260245ffd5b6020808252600e908201526d49454f206e6f742061637469766560901b604082015260600190565b81810381811115611a7357611a73613b33565b6001600160801b03818116838216019080821115613b6757613b67613b33565b5f60208284031215613c05575f80fd5b815161393a81613a1b565b5f805f60608486031215613c22575f80fd5b8351925060208401519150604084015190509250925092565b5f60208284031215613c4b575f80fd5b5051919050565b80820180821115611a7357611a73613b33565b8082028115828204841417611a7357611a73613b33565b5f82613c9657634e487b7160e01b5f52601260045260245ffd5b500490565b600181815b80851115613cd557815f1904821115613cbb57613cbb613b33565b80851615613cc857918102915b93841c9390800290613ca0565b509250929050565b5f82613ceb57506001611a73565b81613cf757505f611a73565b8160018114613d0d5760028114613d1757613d33565b6001915050611a73565b60ff841115613d2857613d28613b33565b50506001821b611a73565b5060208310610133831016604e8410600b8410161715613d56575081810a611a73565b613d608383613c9b565b805f1904821115613d7357613d73613b33565b029392505050565b5f61393a8383613cdd56fe3269ffed2b18a39abd6a644fc796888eaaf9ff1251aa3ad897a0a560d34ec6c3ea7662f213c1e365ff55c50b7d32910320875afda2fa69e210c9167a2d7da1d38e1d5467d66a605ed83ea1e24e51ca4184aad2d9131649bbd3f106303265c8b2a264697066735822122084027014b3d2bbdfc1a6b1e7e2d469594a533fa5939eeef9a7a9a0bebba3eab364736f6c63430008180033"

REWARDTRACKING_ABI = [
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_tokenAddress",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_ieoContract",
        "type": "address"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [],
    "name": "CallerNotOwner",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NewOwnerIsZeroAddress",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NoRewardsToClaim",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NoTokensSold",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NotIEOContract",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ReentrantCallBlocked",
    "type": "error"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "newIEOContract",
        "type": "address"
      }
    ],
    "name": "IEOContractUpdated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "OwnershipTransferred",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "user",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "RewardClaimed",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "newAccumulatedRewardPerToken",
        "type": "uint256"
      }
    ],
    "name": "RewardDeposited",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "newTotalTokenSold",
        "type": "uint256"
      }
    ],
    "name": "TokensSoldUpdated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "user",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "newBalance",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "newRewardDebt",
        "type": "uint256"
      }
    ],
    "name": "UserBalanceUpdated",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "PRECISION",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "USDC_ADDRESS",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "claimReward",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "depositUSDC",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "emergencyWithdrawUSDC",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "getPendingReward",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getPoolInfo",
    "outputs": [
      {
        "components": [
          {
            "internalType": "uint128",
            "name": "totalTokenSold",
            "type": "uint128"
          },
          {
            "internalType": "uint256",
            "name": "accumulatedRewardPerToken",
            "type": "uint256"
          },
          {
            "internalType": "uint128",
            "name": "totalUSDCDeposited",
            "type": "uint128"
          },
          {
            "internalType": "uint64",
            "name": "lastRewardBlock",
            "type": "uint64"
          }
        ],
        "internalType": "struct IRewardTracking.PoolInfo",
        "name": "",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "getUserRewardTracking",
    "outputs": [
      {
        "components": [
          {
            "internalType": "uint128",
            "name": "balance",
            "type": "uint128"
          },
          {
            "internalType": "uint256",
            "name": "rewardDebt",
            "type": "uint256"
          }
        ],
        "internalType": "struct IRewardTracking.UserRewardTracking",
        "name": "",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "ieoContract",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "onTokenSold",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "onTokenTransfer",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "poolInfo",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "totalTokenSold",
        "type": "uint128"
      },
      {
        "internalType": "uint256",
        "name": "accumulatedRewardPerToken",
        "type": "uint256"
      },
      {
        "internalType": "uint128",
        "name": "totalUSDCDeposited",
        "type": "uint128"
      },
      {
        "internalType": "uint64",
        "name": "lastRewardBlock",
        "type": "uint64"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "tokenAddress",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "transferOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "userRewardTrackings",
    "outputs": [
      {
        "internalType": "uint128",
        "name": "balance",
        "type": "uint128"
      },
      {
        "internalType": "uint256",
        "name": "rewardDebt",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]

REWARDTRACKING_BYTECODE = "60c060405234801561000f575f80fd5b50604051620012da380380620012da83398101604081905261003091610138565b338061004f57604051633a247dd760e11b815260040160405180910390fd5b610058816100ce565b506001600160a01b039182166080908152911660a0526040805191820181525f80835260208301819052908201819052436001600160401b03166060909201829052600180546001600160801b0319169055600255600380546001600160c01b031916600160801b909202919091179055610169565b5f80546001600160a01b038381166001600160a01b0319831681178455604051919092169283917f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e09190a35050565b80516001600160a01b0381168114610133575f80fd5b919050565b5f8060408385031215610149575f80fd5b6101528361011d565b91506101606020840161011d565b90509250929050565b60805160a051611141620001995f395f8181610164015261081401525f81816103a801526104bc01526111415ff3fe608060405234801561000f575f80fd5b5060043610610105575f3560e01c80638da5cb5b1161009e578063b88a802f1161006e578063b88a802f146103d9578063bb09d9b7146103e1578063c3520788146103fc578063f2fde38b1461040f578063f688bcfb14610422575f80fd5b80638da5cb5b1461038057806391ad06f8146103905780639d76ea58146103a3578063aaf5eb68146103ca575f80fd5b80635a2f3d09116100d95780635a2f3d091461023f57806360246c88146102ab578063677ba3d314610363578063715018a614610378575f80fd5b8062291f5b1461010957806302801f041461015f57806343a078f51461019e5780634df9d6ba1461021e575b5f80fd5b61013b610117366004610f97565b60046020525f9081526040902080546001909101546001600160801b039091169082565b604080516001600160801b0390931683526020830191909152015b60405180910390f35b6101867f000000000000000000000000000000000000000000000000000000000000000081565b6040516001600160a01b039091168152602001610156565b6101fa6101ac366004610f97565b604080518082019091525f8082526020820152506001600160a01b03165f90815260046020908152604091829020825180840190935280546001600160801b03168352600101549082015290565b6040805182516001600160801b031681526020928301519281019290925201610156565b61023161022c366004610f97565b610435565b604051908152602001610156565b600154600254600354610271926001600160801b03908116929190811690600160801b900467ffffffffffffffff1684565b604080516001600160801b0395861681526020810194909452919093169082015267ffffffffffffffff9091166060820152608001610156565b61031b604080516080810182525f80825260208201819052918101829052606081019190915250604080516080810182526001546001600160801b039081168252600254602083015260035490811692820192909252600160801b90910467ffffffffffffffff16606082015290565b6040805182516001600160801b0390811682526020808501519083015283830151169181019190915260609182015167ffffffffffffffff1691810191909152608001610156565b610376610371366004610fb7565b6104b1565b005b6103766107ff565b5f546001600160a01b0316610186565b61037661039e366004610ff0565b610809565b6101867f000000000000000000000000000000000000000000000000000000000000000081565b610231670de0b6b3a764000081565b6103766109ba565b61018673966c69ae5b4fb4744e976eb058cfe7592bd935d281565b61037661040a366004611018565b610b3e565b61037661041d366004610f97565b610c05565b610376610430366004611018565b610c11565b6001600160a01b0381165f908152600460209081526040808320815180830190925280546001600160801b03168083526001909101549282019290925260025490918391670de0b6b3a76400009161048d9190611043565b6104979190611060565b90508160200151816104a9919061107f565b949350505050565b336001600160a01b037f000000000000000000000000000000000000000000000000000000000000000016146105385760405162461bcd60e51b815260206004820152602160248201527f4f6e6c7920746f6b656e20636f6e74726163742063616e2063616c6c207468696044820152607360f81b60648201526084015b60405180910390fd5b6001600160a01b038316156106fc576001600160a01b0383165f90815260046020526040902080546001600160801b03168211156105c25760405162461bcd60e51b815260206004820152602160248201527f496e73756666696369656e742062616c616e636520666f72207472616e7366656044820152603960f91b606482015260840161052f565b8054829082905f906105de9084906001600160801b0316611092565b92506101000a8154816001600160801b0302191690836001600160801b031602179055505f670de0b6b3a764000060018001548461061c9190611043565b6106269190611060565b9050808260010154101561068b5760405162461bcd60e51b815260206004820152602660248201527f496e73756666696369656e7420726577617264206465627420666f72207265646044820152653ab1ba34b7b760d11b606482015260840161052f565b80826001015f82825461069e919061107f565b909155505081546001830154604080516001600160801b03909316835260208301919091526001600160a01b038716917fef88868e7a1bd2fac29f7b777f32f9d8ea2ac5e10c2d23234d4715ab11c84890910160405180910390a250505b6001600160a01b038216156107fa576001600160a01b0382165f90815260046020526040812080549091839183919061073f9084906001600160801b03166110b9565b92506101000a8154816001600160801b0302191690836001600160801b031602179055505f670de0b6b3a764000060018001548461077d9190611043565b6107879190611060565b905080826001015f82825461079c91906110d9565b909155505081546001830154604080516001600160801b03909316835260208301919091526001600160a01b038616917fef88868e7a1bd2fac29f7b777f32f9d8ea2ac5e10c2d23234d4715ab11c84890910160405180910390a250505b505050565b610807610d20565b565b336001600160a01b037f0000000000000000000000000000000000000000000000000000000000000000161461085257604051630d5b7f3760e41b815260040160405180910390fd5b600180548291905f9061086f9084906001600160801b03166110b9565b82546101009290920a6001600160801b038181021990931691831602179091556001600160a01b0384165f908152600460205260408120805490935084928492916108bc918591166110b9565b92506101000a8154816001600160801b0302191690836001600160801b031602179055505f670de0b6b3a76400006001800154846108fa9190611043565b6109049190611060565b905080826001015f82825461091991906110d9565b909155505081546001830154604080516001600160801b03909316835260208301919091526001600160a01b038616917fef88868e7a1bd2fac29f7b777f32f9d8ea2ac5e10c2d23234d4715ab11c84890910160405180910390a26001546040516001600160801b0390911681527f90194823427294393575be3dad28fc355c5c5b64ef5fe241f87389f91d44a3c69060200160405180910390a150505050565b6109c2610d53565b335f9081526004602052604081206002548154919291670de0b6b3a7640000916109f4916001600160801b0316611043565b6109fe9190611060565b90505f826001015482610a11919061107f565b9050805f03610a33576040516373380d9960e01b815260040160405180910390fd5b6002548354670de0b6b3a764000091610a54916001600160801b0316611043565b610a5e9190611060565b600184015560405163a9059cbb60e01b81523360048201526024810182905273966c69ae5b4fb4744e976eb058cfe7592bd935d29063a9059cbb906044016020604051808303815f875af1158015610ab8573d5f803e3d5ffd5b505050506040513d601f19601f82011682018060405250810190610adc91906110ec565b5060405181815233907f106f923f993c2149d49b4255ff723acafa1f2d94393f561d3eda32ae348f72419060200160405180910390a250505061080760017facb42c6d5ca45bacd796d0d2d88a45f24a2c84adedbb2715f73454a68493167255565b5f546001600160a01b03163314610b6857604051632e6c18c960e11b815260040160405180910390fd5b73966c69ae5b4fb4744e976eb058cfe7592bd935d263a9059cbb610b935f546001600160a01b031690565b6040516001600160e01b031960e084901b1681526001600160a01b039091166004820152602481018490526044016020604051808303815f875af1158015610bdd573d5f803e3d5ffd5b505050506040513d601f19601f82011682018060405250810190610c0191906110ec565b5050565b610c0e81610d9f565b50565b5f546001600160a01b03163314610c3b57604051632e6c18c960e11b815260040160405180910390fd5b610c43610d53565b6001546001600160801b03165f03610c6e5760405163138ef2bf60e31b815260040160405180910390fd5b6040516323b872dd60e01b81523360048201523060248201526044810182905273966c69ae5b4fb4744e976eb058cfe7592bd935d2906323b872dd906064016020604051808303815f875af1158015610cc9573d5f803e3d5ffd5b505050506040513d601f19601f82011682018060405250810190610ced91906110ec565b50610cf781610df9565b610c0e60017facb42c6d5ca45bacd796d0d2d88a45f24a2c84adedbb2715f73454a68493167255565b5f546001600160a01b03163314610d4a57604051632e6c18c960e11b815260040160405180910390fd5b6108075f610f2d565b7facb42c6d5ca45bacd796d0d2d88a45f24a2c84adedbb2715f73454a68493167280546001198101610d985760405163139b643560e21b815260040160405180910390fd5b5060029055565b5f546001600160a01b03163314610dc957604051632e6c18c960e11b815260040160405180910390fd5b6001600160a01b038116610df057604051633a247dd760e11b815260040160405180910390fd5b610c0e81610f2d565b8015610c0e576001546001600160801b0316610e4c5760405162461bcd60e51b8152602060048201526012602482015271139bc81d1bdad95b9cc81cdbdb19081e595d60721b604482015260640161052f565b600380548291905f90610e699084906001600160801b03166110b9565b82546101009290920a6001600160801b038181021990931691831602179091556001545f925016610ea2670de0b6b3a764000084611043565b610eac9190611060565b905080600180015f828254610ec191906110d9565b90915550506003805467ffffffffffffffff60801b1916600160801b4367ffffffffffffffff16021790556002546040805184815260208101929092527fbf2ebcc991369bcf488ef5738352a5d8998bd7a2c138128ca91ec96afe123fd6910160405180910390a15050565b5f80546001600160a01b038381166001600160a01b0319831681178455604051919092169283917f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e09190a35050565b80356001600160a01b0381168114610f92575f80fd5b919050565b5f60208284031215610fa7575f80fd5b610fb082610f7c565b9392505050565b5f805f60608486031215610fc9575f80fd5b610fd284610f7c565b9250610fe060208501610f7c565b9150604084013590509250925092565b5f8060408385031215611001575f80fd5b61100a83610f7c565b946020939093013593505050565b5f60208284031215611028575f80fd5b5035919050565b634e487b7160e01b5f52601160045260245ffd5b808202811582820484141761105a5761105a61102f565b92915050565b5f8261107a57634e487b7160e01b5f52601260045260245ffd5b500490565b8181038181111561105a5761105a61102f565b6001600160801b038281168282160390808211156110b2576110b261102f565b5092915050565b6001600160801b038181168382160190808211156110b2576110b261102f565b8082018082111561105a5761105a61102f565b5f602082840312156110fc575f80fd5b81518015158114610fb0575f80fdfea2646970667358221220bcef8952a1af8a79abb44c86b4c6627f43814646001374d34355804aac89b58d64736f6c63430008180033"

