// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract ProjectToken is ERC20, Ownable, Pausable {
    uint256 public pricePerToken;
    uint256 public maxSupply;
    bool public isInitialized;
    
    event TokensPurchased(address indexed buyer, uint256 amount, uint256 cost);
    event PriceUpdated(uint256 newPrice);
    
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply,
        uint256 _pricePerToken,
        address initialOwner
    ) ERC20(name, symbol) {
        require(initialSupply > 0, "Initial supply must be greater than 0");
        require(_pricePerToken > 0, "Price per token must be greater than 0");
        
        maxSupply = initialSupply;
        pricePerToken = _pricePerToken;
        isInitialized = true;
        
        // Transfer ownership to the project owner
        _transferOwnership(initialOwner);
        
        // Mint initial supply to the owner
        _mint(initialOwner, initialSupply);
    }
    
    function decimals() public view virtual override returns (uint8) {
        return 18;
    }
    
    function updatePrice(uint256 newPrice) external onlyOwner {
        require(newPrice > 0, "Price must be greater than 0");
        pricePerToken = newPrice;
        emit PriceUpdated(newPrice);
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual override {
        super._beforeTokenTransfer(from, to, amount);
        require(!paused(), "Token transfer paused");
    }
    
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
    
    function burnFrom(address account, uint256 amount) external onlyOwner {
        _burn(account, amount);
    }
} 