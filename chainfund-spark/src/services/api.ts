// API Service Layer for ChainFund Spark
// Handles all backend communication with proper TypeScript types and error handling

const API_BASE_URL = 'http://localhost:8000/api/v1';

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface User {
  id: string;
  wallet_address: string;
  username?: string;
  email?: string;
  created_at: string;
}

export interface AuthRequest {
  wallet_address: string;
  signature: string;
  message: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Campaign {
  id: string;
  title: string;
  description: string;
  goal_amount: number;
  total_backed: number;
  status: 'active' | 'funded' | 'completed';
  creator_wallet: string;
  milestones: Milestone[];
  backers: Backer[];
  created_at: string;
  updated_at: string;
  category?: string;
  end_date?: string;
}

export interface Milestone {
  id: string;
  title: string;
  description: string;
  amount: number;
  status: 'pending' | 'active' | 'completed' | 'approved';
  votes_for: number;
  votes_against: number;
  total_votes: number;
}

export interface Backer {
  id: string;
  wallet_address: string;
  amount: number;
  timestamp: string;
}

export interface CreateCampaignRequest {
  title: string;
  description: string;
  goal_amount: number;
  category: string;
  duration_days: number;
  milestones: Omit<Milestone, 'id' | 'status' | 'votes_for' | 'votes_against' | 'total_votes'>[];
}

export interface FundCampaignRequest {
  amount: number;
  campaign_id: string;
}

export interface VoteRequest {
  milestone_id: string;
  vote: 'for' | 'against';
}

export interface Category {
  name: string;
  count: number;
  description: string;
}

export interface SkillHistory {
  campaign_id: string;
  milestone_id: string;
  milestone_title: string;
  score_earned: number;
  completed_at: string;
  difficulty_rating: string;
  on_time_completion: boolean;
  peer_reviews: number[];
}

export interface SkillScoreData {
  wallet_address: string;
  skill_score: number;
  skill_level: string;
  skill_nft_token_id?: number;
  total_milestones_completed: number;
  total_campaigns_participated: number;
  average_completion_time?: number;
  skill_breakdown: Record<string, number>;
  recent_achievements: Array<{
    campaign_id: string;
    milestone_title: string;
    score_earned: number;
    completed_at: string;
    difficulty: string;
    on_time: boolean;
  }>;
  next_level_threshold: number;
}

export interface SkillActivityRequest {
  campaign_id: string;
  milestone_id: string;
  milestone_title: string;
  score_earned: number;
  difficulty?: string;
  on_time?: boolean;
  peer_reviews?: number[];
}

export interface SkillNFTData {
  nft_id: string;
  token_id: number;
  skill_level: string;
  skill_score: number;
  color: string;
  description: string;
  updated?: boolean;
}

export interface SkillLeaderboardEntry {
  wallet_address: string;
  username?: string;
  skill_score: number;
  skill_level: string;
  total_milestones_completed: number;
  total_campaigns_participated: number;
  rank: number;
}

export interface CampaignsResponse {
  campaigns: Campaign[];
  total: number;
  page: number;
  limit: number;
}

// API Error class
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Generic API request function
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Add auth token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers = {
      ...config.headers,
      'Authorization': `Bearer ${token}`,
    };
  }

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData.code
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    // Network or other errors
    throw new ApiError(
      error instanceof Error ? error.message : 'Network error',
      0
    );
  }
}

// Authentication API
export const authApi = {
  async authenticate(authRequest: AuthRequest): Promise<AuthResponse> {
    return apiRequest<AuthResponse>('/users/auth', {
      method: 'POST',
      body: JSON.stringify(authRequest),
    });
  },

  async getCurrentUser(): Promise<User> {
    return apiRequest<User>('/users/me');
  },
};

// Campaigns API
export const campaignsApi = {
  async getCampaigns(
    page: number = 1,
    limit: number = 10,
    status?: string,
    category?: string
  ): Promise<CampaignsResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });

    if (status) {
      params.append('status', status);
    }

    if (category && category !== 'all') {
      params.append('category', category);
    }

    return apiRequest<CampaignsResponse>(`/campaigns?${params}`);
  },

  async getCampaign(campaignId: string): Promise<Campaign> {
    return apiRequest<Campaign>(`/campaigns/${campaignId}`);
  },

  async createCampaign(campaignData: CreateCampaignRequest): Promise<Campaign> {
    return apiRequest<Campaign>('/campaigns', {
      method: 'POST',
      body: JSON.stringify(campaignData),
    });
  },

  async fundCampaign(fundData: FundCampaignRequest): Promise<{ transaction_hash: string }> {
    return apiRequest<{ transaction_hash: string }>('/funding', {
      method: 'POST',
      body: JSON.stringify(fundData),
    });
  },

  async voteOnMilestone(voteData: VoteRequest): Promise<{ success: boolean }> {
    return apiRequest<{ success: boolean }>('/votes', {
      method: 'POST',
      body: JSON.stringify(voteData),
    });
  },

  async getCategories(): Promise<{ categories: Category[] }> {
    return apiRequest<{ categories: Category[] }>('/campaigns/categories');
  },
};

// Skill API
export const skillApi = {
  async getSkillScore(walletAddress: string): Promise<SkillScoreData> {
    return apiRequest<SkillScoreData>(`/users/skill-score/${walletAddress}`);
  },

  async addSkillActivity(walletAddress: string, activity: SkillActivityRequest): Promise<{ message: string; new_skill_score: number; new_skill_level: string }> {
    return apiRequest<{ message: string; new_skill_score: number; new_skill_level: string }>(`/users/skill-activity/${walletAddress}`, {
      method: 'POST',
      body: JSON.stringify(activity),
    });
  },

  async mintSkillNFT(walletAddress: string): Promise<{ message: string; nft_data: SkillNFTData }> {
    return apiRequest<{ message: string; nft_data: SkillNFTData }>(`/users/mint-skill-nft/${walletAddress}`, {
      method: 'POST',
    });
  },

  async getSkillNFT(walletAddress: string): Promise<{ skill_nft: SkillNFTData } | { message: string }> {
    return apiRequest<{ skill_nft: SkillNFTData } | { message: string }>(`/users/skill-nft/${walletAddress}`);
  },

  async updateSkillScore(walletAddress: string): Promise<{ message: string; skill_score: number; skill_level: string }> {
    return apiRequest<{ message: string; skill_score: number; skill_level: string }>(`/users/skill-score/update/${walletAddress}`, {
      method: 'PUT',
    });
  },

  async getSkillLeaderboard(limit: number = 50): Promise<{ leaderboard: SkillLeaderboardEntry[] }> {
    return apiRequest<{ leaderboard: SkillLeaderboardEntry[] }>(`/users/skill-leaderboard?limit=${limit}`);
  },
};

// Utility functions
export const apiUtils = {
  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  },

  getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  setAuthToken(token: string): void {
    localStorage.setItem('auth_token', token);
  },

  clearAuthToken(): void {
    localStorage.removeItem('auth_token');
  },

  formatApiError(error: unknown): string {
    if (error instanceof ApiError) {
      return error.message;
    }
    return 'An unexpected error occurred';
  },
};