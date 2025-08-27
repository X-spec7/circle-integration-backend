"""
Escrow Smart Contract Template
This contract holds funds for a specific project and manages token distribution.
"""

ESCROW_CONTRACT_TEMPLATE = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract ProjectEscrow is ReentrancyGuard, Ownable, Pausable {
    IERC20 public projectToken;
    IERC20 public usdcToken;
    
    address public projectOwner;
    uint256 public targetAmount;
    uint256 public raisedAmount;
    uint256 public tokenPrice;
    uint256 public endDate;
    
    bool public isActive;
    bool public isCompleted;
    
    mapping(address => uint256) public investments;
    mapping(address => uint256) public tokenAllocations;
    
    event InvestmentReceived(address indexed investor, uint256 amount, uint256 tokens);
    event FundsReleased(address indexed projectOwner, uint256 amount);
    event RefundIssued(address indexed investor, uint256 amount);
    event EscrowCompleted(uint256 totalRaised, uint256 totalTokensDistributed);
    
    constructor(
        address _projectToken,
        address _usdcToken,
        address _projectOwner,
        uint256 _targetAmount,
        uint256 _tokenPrice,
        uint256 _endDate
    ) {
        require(_projectToken != address(0), "Invalid token address");
        require(_usdcToken != address(0), "Invalid USDC address");
        require(_projectOwner != address(0), "Invalid project owner");
        require(_targetAmount > 0, "Target amount must be greater than 0");
        require(_tokenPrice > 0, "Token price must be greater than 0");
        require(_endDate > block.timestamp, "End date must be in the future");
        
        projectToken = IERC20(_projectToken);
        usdcToken = IERC20(_usdcToken);
        projectOwner = _projectOwner;
        targetAmount = _targetAmount;
        tokenPrice = _tokenPrice;
        endDate = _endDate;
        isActive = true;
    }
    
    modifier onlyProjectOwner() {
        require(msg.sender == projectOwner, "Only project owner can call this");
        _;
    }
    
    modifier onlyActive() {
        require(isActive && !isCompleted, "Escrow is not active");
        _;
    }
    
    function invest(uint256 usdcAmount) external nonReentrant onlyActive {
        require(usdcAmount > 0, "Investment amount must be greater than 0");
        require(block.timestamp <= endDate, "Investment period has ended");
        require(raisedAmount + usdcAmount <= targetAmount, "Target amount exceeded");
        
        // Transfer USDC from investor to escrow
        require(usdcToken.transferFrom(msg.sender, address(this), usdcAmount), "USDC transfer failed");
        
        // Calculate tokens to allocate
        uint256 tokensToAllocate = (usdcAmount * 1e18) / tokenPrice;
        
        // Update state
        investments[msg.sender] += usdcAmount;
        tokenAllocations[msg.sender] += tokensToAllocate;
        raisedAmount += usdcAmount;
        
        emit InvestmentReceived(msg.sender, usdcAmount, tokensToAllocate);
        
        // Check if target reached
        if (raisedAmount >= targetAmount) {
            _completeEscrow();
        }
    }
    
    function claimTokens() external nonReentrant {
        require(isCompleted, "Escrow not completed");
        require(tokenAllocations[msg.sender] > 0, "No tokens to claim");
        
        uint256 tokensToClaim = tokenAllocations[msg.sender];
        tokenAllocations[msg.sender] = 0;
        
        require(projectToken.transfer(msg.sender, tokensToClaim), "Token transfer failed");
    }
    
    function releaseFunds() external onlyProjectOwner nonReentrant {
        require(isCompleted, "Escrow not completed");
        require(raisedAmount > 0, "No funds to release");
        
        uint256 amountToRelease = raisedAmount;
        raisedAmount = 0;
        
        require(usdcToken.transfer(projectOwner, amountToRelease), "Fund release failed");
        emit FundsReleased(projectOwner, amountToRelease);
    }
    
    function requestRefund() external nonReentrant {
        require(!isCompleted, "Escrow already completed");
        require(investments[msg.sender] > 0, "No investment to refund");
        
        uint256 refundAmount = investments[msg.sender];
        investments[msg.sender] = 0;
        tokenAllocations[msg.sender] = 0;
        raisedAmount -= refundAmount;
        
        require(usdcToken.transfer(msg.sender, refundAmount), "Refund failed");
        emit RefundIssued(msg.sender, refundAmount);
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function _completeEscrow() internal {
        isActive = false;
        isCompleted = true;
        emit EscrowCompleted(raisedAmount, projectToken.balanceOf(address(this)));
    }
    
    function getInvestmentInfo(address investor) external view returns (
        uint256 investmentAmount,
        uint256 allocatedTokens
    ) {
        return (investments[investor], tokenAllocations[investor]);
    }
    
    function getEscrowInfo() external view returns (
        uint256 _targetAmount,
        uint256 _raisedAmount,
        uint256 _tokenPrice,
        uint256 _endDate,
        bool _isActive,
        bool _isCompleted
    ) {
        return (targetAmount, raisedAmount, tokenPrice, endDate, isActive, isCompleted);
    }
}
""" 