# Frontend API Integration Guide

This guide explains how to integrate the new blockchain features into your frontend application via API calls.

## Overview

The backend now supports:
1. **ERC20 Token Deployment** - Automatic deployment of project tokens on Polygon mainnet
2. **Escrow Smart Contracts** - Project-specific escrow contracts for fund management
3. **EURC Integration** - Automatic transfer of on-ramped EURC to project escrows
4. **Enhanced Payment Flow** - Improved fiat and crypto payment processing

## Environment Setup

### Required Environment Variables

Add these to your frontend environment:

```env
# Backend API
REACT_APP_API_BASE_URL=http://localhost:8001/api/v1

# Blockchain
REACT_APP_POLYGON_RPC_URL=https://polygon-rpc.com
REACT_APP_POLYGON_SCAN_URL=https://polygonscan.com
REACT_APP_USDC_CONTRACT_ADDRESS=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
REACT_APP_EURC_CONTRACT_ADDRESS=0xE111178A87A3BFf0c8d18DECBa5798827539Ae99
```

## API Integration

### 1. Project Creation with Blockchain Deployment

#### Request
```javascript
const createProject = async (projectData) => {
  const response = await fetch(`${API_BASE_URL}/projects/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      name: "My Project",
      symbol: "MPT",
      description: "Project description",
      category: "Technology",
      target_amount: 10000.00,
      price_per_token: 1.00,
      total_supply: 1000000,
      end_date: "2025-12-31T23:59:59",
      risk_level: "Medium",
      image_url: "https://example.com/image.jpg",
      business_plan_url: "https://example.com/business-plan.pdf",
      whitepaper_url: "https://example.com/whitepaper.pdf"
    })
  });
  
  return response.json();
};
```

#### Response
```json
{
  "project_id": "uuid",
  "token_contract_address": "0x123...",
  "escrow_contract_address": "0x456...",
  "token_deployment_tx": "0x789...",
  "escrow_deployment_tx": "0xabc...",
  "deployment_status": "completed"
}
```

### 2. Enhanced Project Details

#### Request
```javascript
const getProject = async (projectId) => {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}`);
  return response.json();
};
```

#### Response
```json
{
  "id": "uuid",
  "name": "My Project",
  "symbol": "MPT",
  "description": "Project description",
  "category": "Technology",
  "target_amount": 10000.00,
  "price_per_token": 1.00,
  "total_supply": 1000000,
  "current_raised": 2500.00,
  "end_date": "2025-12-31T23:59:59",
  "risk_level": "Medium",
  "status": "active",
  "token_contract_address": "0x123...",
  "escrow_contract_address": "0x456...",
  "token_deployment_tx": "0x789...",
  "escrow_deployment_tx": "0xabc...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 3. Get Project Escrow Address

```javascript
const getEscrowAddress = async (projectId) => {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/escrow-address`);
  return response.json();
};
```

### 4. Initiate Payment

```javascript
const initiatePayment = async (paymentData) => {
  const response = await fetch(`${API_BASE_URL}/payments/initiate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      project_id: "project-uuid",
      amount: 100.00,
      payment_method: "fiat" // or "crypto"
    })
  });
  
  return response.json();
};
```

### 5. Get Payment Status

```javascript
const getPaymentStatus = async (paymentId) => {
  const response = await fetch(`${API_BASE_URL}/payments/${paymentId}/status`);
  return response.json();
};
```

## Error Handling

```javascript
const handleApiError = (error) => {
  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return `Bad Request: ${data.detail}`;
      case 403:
        return 'Access Denied: You do not have permission to perform this action';
      case 404:
        return 'Resource not found';
      case 500:
        return 'Server Error: Please try again later';
      default:
        return `Error ${status}: ${data.detail || 'Unknown error'}`;
    }
  }
  
  return 'Network error: Please check your connection';
};
```

## Testing

### Test Project Creation

```javascript
const testProjectCreation = async () => {
  const testData = {
    name: "Test Project",
    symbol: "TEST",
    description: "A test project for development",
    category: "Technology",
    target_amount: 1000.00,
    price_per_token: 0.50,
    total_supply: 100000,
    end_date: "2025-12-31T23:59:59",
    risk_level: "Low"
  };

  try {
    const result = await createProject(testData);
    console.log('Project created:', result);
  } catch (error) {
    console.error('Project creation failed:', error);
  }
};
```
