import axios from "axios";
import * as authUtils from "../utils/auth";

// Create an axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false, // Not using cookies anymore, using JWT tokens
});

// Add request interceptor to add the token to every request
apiClient.interceptors.request.use((config) => {
  const token = authUtils.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authApi = {
  // Get Google OAuth URL
  getGoogleAuthUrl: async (redirectUrl?: string) => {
    const params = redirectUrl ? { redirect_url: redirectUrl } : {};
    const response = await apiClient.get("/api/v1/auth/login/google", {
      params,
    });
    return response.data.auth_url;
  },

  // Validate existing token
  validateToken: async () => {
    const token = authUtils.getToken();
    if (!token) {
      return { valid: false };
    }
    const response = await apiClient.get("/api/v1/auth/validate");
    return response.data;
  },

  // Get current user profile
  getCurrentUser: async () => {
    const response = await apiClient.get("/api/v1/auth/me");
    return response.data;
  },

  // Logout user
  logout: async () => {
    const response = await apiClient.post("/api/v1/auth/logout");
    return response.data;
  },
};

// Campaigns API
export const campaignsApi = {
  getAllCampaigns: async () => {
    const response = await apiClient.get("/api/v1/campaigns");
    return response.data;
  },

  getCampaign: async (id: string) => {
    const response = await apiClient.get(`/api/v1/campaign/${id}`);
    return response.data;
  },

  getCampaignMetrics: async (id: string) => {
    const response = await apiClient.get(`/api/v1/campaign-metrics/${id}`);
    return response.data;
  },
};

// Ad generation API
export const adsApi = {
  analyzeRequirement: async (requirementData: Record<string, unknown>) => {
    const response = await apiClient.post(
      "/api/v1/analyze-requirement",
      requirementData,
    );
    return response.data;
  },

  generateCreative: async (requirementId: string) => {
    const response = await apiClient.post("/api/v1/generate-creative", {
      requirement_id: requirementId,
    });
    return response.data;
  },

  publishCampaign: async (creativeId: string, campaignName: string) => {
    const response = await apiClient.post("/api/v1/publish-campaign", {
      creative_id: creativeId,
      campaign_name: campaignName,
    });
    return response.data;
  },
};

export default apiClient;
