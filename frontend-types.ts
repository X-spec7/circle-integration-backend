// TypeScript interfaces for Project API integration

// Enums
export type RiskLevel = "Low" | "Medium" | "High";
export type ProjectStatus = "pending" | "active" | "completed" | "rejected";

// Request interfaces
export interface CreateProjectRequest {
  name: string;
  symbol: string;
  description: string;
  category: string;
  initial_supply: number;
  end_date: string; // ISO 8601 format
  risk_level: RiskLevel;
  delay_days?: number; // 1-365, default: 7
  min_investment?: number; // USDC (6 decimals), default: 100
  max_investment?: number; // USDC (6 decimals), default: 1000000
  image_url?: string;
  business_plan_url?: string;
  whitepaper_url?: string;
}

export interface UpdateProjectRequest {
  name?: string;
  symbol?: string;
  description?: string;
  category?: string;
  initial_supply?: number;
  end_date?: string;
  risk_level?: RiskLevel;
  delay_days?: number;
  min_investment?: number;
  max_investment?: number;
  image_url?: string;
  business_plan_url?: string;
  whitepaper_url?: string;
}

export interface ProjectFilters {
  status?: ProjectStatus;
  category?: string;
  risk_level?: RiskLevel;
  page?: number;
  limit?: number;
}

// Response interfaces
export interface ProjectResponse {
  id: string;
  owner_id: string;
  name: string;
  symbol: string;
  description: string;
  category: string;
  initial_supply: number;
  current_raised: string; // Decimal as string
  end_date: string;
  risk_level: RiskLevel;
  status: ProjectStatus;
  image_url?: string;
  business_plan_url?: string;
  whitepaper_url?: string;
  delay_days: number;
  min_investment: number;
  max_investment: number;
  token_contract_address?: string;
  ieo_contract_address?: string;
  reward_tracking_contract_address?: string;
  token_deployment_tx?: string;
  ieo_deployment_tx?: string;
  reward_tracking_deployment_tx?: string;
  created_at: string;
  updated_at?: string;
}

export interface ProjectDeploymentResponse {
  project_id: string;
  token_contract_address: string;
  ieo_contract_address: string;
  reward_tracking_contract_address: string;
  token_deployment_tx: string;
  ieo_deployment_tx: string;
  reward_tracking_deployment_tx: string;
  deployment_status: string;
}

export interface ProjectListResponse {
  items: ProjectResponse[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ProjectStatsResponse {
  total_projects: number;
  active_projects: number;
  total_raised: string;
  total_investors: number;
}

// Error interfaces
export interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}

export interface ErrorResponse {
  detail: string | ValidationError[];
}

// API Client interface
export interface ProjectAPIClient {
  createProject(data: CreateProjectRequest): Promise<ProjectDeploymentResponse>;
  getProjects(filters?: ProjectFilters): Promise<ProjectListResponse>;
  getProject(id: string): Promise<ProjectResponse>;
  updateProject(id: string, data: UpdateProjectRequest): Promise<ProjectResponse>;
  deleteProject(id: string): Promise<{ message: string }>;
  getProjectStats(): Promise<ProjectStatsResponse>;
}

// Utility types
export interface ProjectFormData extends Omit<CreateProjectRequest, 'end_date'> {
  end_date: Date; // For form handling
}

export interface ProjectDisplayData extends ProjectResponse {
  // Additional computed fields for display
  days_remaining?: number;
  progress_percentage?: number;
  formatted_raised?: string;
  formatted_supply?: string;
}

// Constants
export const PROJECT_CONSTANTS = {
  MIN_DELAY_DAYS: 1,
  MAX_DELAY_DAYS: 365,
  DEFAULT_DELAY_DAYS: 7,
  MIN_INVESTMENT: 1,
  DEFAULT_MIN_INVESTMENT: 100,
  MIN_MAX_INVESTMENT: 1000,
  DEFAULT_MAX_INVESTMENT: 1000000,
  MAX_NAME_LENGTH: 255,
  MAX_SYMBOL_LENGTH: 10,
  MIN_DESCRIPTION_LENGTH: 10,
  MAX_CATEGORY_LENGTH: 100,
  MAX_URL_LENGTH: 500,
  RISK_LEVELS: ['Low', 'Medium', 'High'] as const,
  PROJECT_STATUSES: ['pending', 'active', 'completed', 'rejected'] as const,
} as const;

// Validation helpers
export const validateProjectData = (data: CreateProjectRequest): string[] => {
  const errors: string[] = [];
  
  if (!data.name || data.name.length < 1 || data.name.length > PROJECT_CONSTANTS.MAX_NAME_LENGTH) {
    errors.push(`Name must be between 1 and ${PROJECT_CONSTANTS.MAX_NAME_LENGTH} characters`);
  }
  
  if (!data.symbol || data.symbol.length < 1 || data.symbol.length > PROJECT_CONSTANTS.MAX_SYMBOL_LENGTH) {
    errors.push(`Symbol must be between 1 and ${PROJECT_CONSTANTS.MAX_SYMBOL_LENGTH} characters`);
  }
  
  if (!data.description || data.description.length < PROJECT_CONSTANTS.MIN_DESCRIPTION_LENGTH) {
    errors.push(`Description must be at least ${PROJECT_CONSTANTS.MIN_DESCRIPTION_LENGTH} characters`);
  }
  
  if (!data.category || data.category.length < 1 || data.category.length > PROJECT_CONSTANTS.MAX_CATEGORY_LENGTH) {
    errors.push(`Category must be between 1 and ${PROJECT_CONSTANTS.MAX_CATEGORY_LENGTH} characters`);
  }
  
  if (!data.initial_supply || data.initial_supply <= 0) {
    errors.push('Initial supply must be greater than 0');
  }
  
  if (!data.end_date || new Date(data.end_date) <= new Date()) {
    errors.push('End date must be in the future');
  }
  
  if (!PROJECT_CONSTANTS.RISK_LEVELS.includes(data.risk_level)) {
    errors.push(`Risk level must be one of: ${PROJECT_CONSTANTS.RISK_LEVELS.join(', ')}`);
  }
  
  if (data.delay_days && (data.delay_days < PROJECT_CONSTANTS.MIN_DELAY_DAYS || data.delay_days > PROJECT_CONSTANTS.MAX_DELAY_DAYS)) {
    errors.push(`Delay days must be between ${PROJECT_CONSTANTS.MIN_DELAY_DAYS} and ${PROJECT_CONSTANTS.MAX_DELAY_DAYS}`);
  }
  
  if (data.min_investment && data.min_investment < PROJECT_CONSTANTS.MIN_INVESTMENT) {
    errors.push(`Minimum investment must be at least ${PROJECT_CONSTANTS.MIN_INVESTMENT}`);
  }
  
  if (data.max_investment && data.max_investment < PROJECT_CONSTANTS.MIN_MAX_INVESTMENT) {
    errors.push(`Maximum investment must be at least ${PROJECT_CONSTANTS.MIN_MAX_INVESTMENT}`);
  }
  
  if (data.min_investment && data.max_investment && data.min_investment >= data.max_investment) {
    errors.push('Maximum investment must be greater than minimum investment');
  }
  
  return errors;
};

// Format helpers
export const formatUSDCAmount = (amount: number): string => {
  return (amount / 1000000).toFixed(2); // Convert from 6 decimals to USD
};

export const formatTokenAmount = (amount: number): string => {
  return amount.toLocaleString();
};

export const calculateDaysRemaining = (endDate: string): number => {
  const end = new Date(endDate);
  const now = new Date();
  const diffTime = end.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};
