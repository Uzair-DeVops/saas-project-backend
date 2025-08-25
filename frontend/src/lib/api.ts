import axios, { AxiosInstance, AxiosResponse } from "axios";
import {
  AuthResponse,
  User,
  Video,
  Playlist,
  VideoAnalytics,
  DashboardOverview,
  PlaylistAnalytics,
  ApiResponse,
  LoginFormData,
  SignupFormData,
  UploadFormData,
  GenerateContentRequest,
  YouTubeToken,
  GeminiKey,
} from "@/types";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: "/api",
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add request interceptor to include Bearer token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem("access_token");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Clear token and redirect to login
          localStorage.removeItem("access_token");
          localStorage.removeItem("user");
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(data: LoginFormData): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.client.post(
      "/auth/login",
      data
    );
    return response.data;
  }

  async signup(data: SignupFormData): Promise<User> {
    const response: AxiosResponse<User> = await this.client.post(
      "/auth/signup",
      data
    );
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.client.get("/auth/me");
    return response.data;
  }

  // Video endpoints - using Bearer token for authentication
  async uploadVideo(data: FormData): Promise<Video> {
    const response: AxiosResponse<Video> = await this.client.post(
      "/videos/upload",
      data,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  }

  async downloadVideo(videoUrl: string): Promise<Video> {
    const response: AxiosResponse<Video> = await this.client.post(
      "/videos/download",
      {
        video_url: videoUrl,
      }
    );
    return response.data;
  }

  async getMyVideos(): Promise<Video[]> {
    const response: AxiosResponse<Video[]> = await this.client.get(
      "/videos/my-videos"
    );
    return response.data;
  }

  async getVideo(videoId: string): Promise<Video> {
    const response: AxiosResponse<Video> = await this.client.get(
      `/videos/${videoId}`
    );
    return response.data;
  }

  async cancelVideoCleanup(videoId: string): Promise<void> {
    await this.client.post(`/videos/${videoId}/cancel-cleanup`);
  }

  // Dashboard endpoints - using Bearer token for authentication
  async getDashboardOverview(): Promise<DashboardOverview> {
    const response: AxiosResponse<ApiResponse<DashboardOverview>> =
      await this.client.get("/dashboard/overview");
    return response.data.data;
  }

  async getDashboardPlaylists(): Promise<Playlist[]> {
    const response: AxiosResponse<ApiResponse<Playlist[]>> =
      await this.client.get("/dashboard/playlists");
    return response.data.data;
  }

  async getDashboardVideos(): Promise<VideoAnalytics[]> {
    const response: AxiosResponse<ApiResponse<VideoAnalytics[]>> =
      await this.client.get("/dashboard/videos");
    return response.data.data;
  }

  async getDashboardVideoDetails(videoId: string): Promise<VideoAnalytics> {
    const response: AxiosResponse<ApiResponse<VideoAnalytics>> =
      await this.client.get(`/dashboard/videos/${videoId}`);
    return response.data.data;
  }

  async getDashboardPlaylistVideos(
    playlistId: string
  ): Promise<VideoAnalytics[]> {
    const response: AxiosResponse<ApiResponse<VideoAnalytics[]>> =
      await this.client.get(`/dashboard/playlists/${playlistId}/videos`);
    return response.data.data;
  }

  async getDashboardPlaylistAnalytics(
    playlistId: string
  ): Promise<PlaylistAnalytics> {
    const response: AxiosResponse<ApiResponse<PlaylistAnalytics>> =
      await this.client.get(`/dashboard/playlists/${playlistId}/analytics`);
    return response.data.data;
  }

  async getCompleteChannelStats(): Promise<any> {
    const response: AxiosResponse<ApiResponse<any>> = await this.client.get(
      "/dashboard/channel-stats"
    );
    return response.data.data;
  }

  // YouTube Upload endpoints - using Bearer token for authentication
  async uploadToYouTube(videoId: string): Promise<any> {
    const response: AxiosResponse<ApiResponse<any>> = await this.client.post(
      `/youtube-upload/${videoId}/upload`
    );
    return response.data.data;
  }

  // Content Generation endpoints - using Bearer token for authentication
  async generateTitle(videoId: string, prompt?: string): Promise<any> {
    const response: AxiosResponse<ApiResponse<any>> = await this.client.post(
      "/title-generator/generate",
      {
        video_id: videoId,
        prompt,
      }
    );
    return response.data.data;
  }

  async generateDescription(videoId: string, prompt?: string): Promise<any> {
    const response: AxiosResponse<ApiResponse<any>> = await this.client.post(
      "/description-generator/generate",
      {
        video_id: videoId,
        prompt,
      }
    );
    return response.data.data;
  }

  async generateThumbnail(videoId: string, prompt?: string): Promise<any> {
    const response: AxiosResponse<ApiResponse<any>> = await this.client.post(
      "/thumbnail-generator/generate",
      {
        video_id: videoId,
        prompt,
      }
    );
    return response.data.data;
  }

  async generateTimestamps(videoId: string, prompt?: string): Promise<any> {
    const response: AxiosResponse<ApiResponse<any>> = await this.client.post(
      "/time-stamps-generator/generate",
      {
        video_id: videoId,
        prompt,
      }
    );
    return response.data.data;
  }

  // Playlist endpoints - using Bearer token for authentication
  async getPlaylists(): Promise<Playlist[]> {
    const response: AxiosResponse<ApiResponse<Playlist[]>> =
      await this.client.get("/playlists");
    return response.data.data;
  }

  async createPlaylist(data: any): Promise<Playlist> {
    const response: AxiosResponse<ApiResponse<Playlist>> =
      await this.client.post("/playlists", data);
    return response.data.data;
  }

  async updatePlaylist(playlistId: string, data: any): Promise<Playlist> {
    const response: AxiosResponse<ApiResponse<Playlist>> =
      await this.client.put(`/playlists/${playlistId}`, data);
    return response.data.data;
  }

  async deletePlaylist(playlistId: string): Promise<void> {
    await this.client.delete(`/playlists/${playlistId}`);
  }

  // Privacy Status endpoints - using Bearer token for authentication
  async getPrivacyStatuses(): Promise<string[]> {
    const response: AxiosResponse<ApiResponse<string[]>> =
      await this.client.get("/privacy-status");
    return response.data.data;
  }

  // Schedule endpoints - using Bearer token for authentication
  async getSchedules(): Promise<any[]> {
    const response: AxiosResponse<ApiResponse<any[]>> = await this.client.get(
      "/schedule"
    );
    return response.data.data;
  }

  async createSchedule(data: any): Promise<any> {
    const response: AxiosResponse<ApiResponse<any>> = await this.client.post(
      "/schedule",
      data
    );
    return response.data.data;
  }

  async updateSchedule(scheduleId: string, data: any): Promise<any> {
    const response: AxiosResponse<ApiResponse<any>> = await this.client.put(
      `/schedule/${scheduleId}`,
      data
    );
    return response.data.data;
  }

  async deleteSchedule(scheduleId: string): Promise<void> {
    await this.client.delete(`/schedule/${scheduleId}`);
  }

  // YouTube Token endpoints - using Bearer token for authentication
  async getYouTubeToken(): Promise<YouTubeToken> {
    const response: AxiosResponse<ApiResponse<YouTubeToken>> =
      await this.client.get("/youtube-token");
    return response.data.data;
  }

  async createYouTubeToken(data: any): Promise<YouTubeToken> {
    const response: AxiosResponse<ApiResponse<YouTubeToken>> =
      await this.client.post("/youtube-token", data);
    return response.data.data;
  }

  async updateYouTubeToken(tokenId: string, data: any): Promise<YouTubeToken> {
    const response: AxiosResponse<ApiResponse<YouTubeToken>> =
      await this.client.put(`/youtube-token/${tokenId}`, data);
    return response.data.data;
  }

  async deleteYouTubeToken(tokenId: string): Promise<void> {
    await this.client.delete(`/youtube-token/${tokenId}`);
  }

  // Gemini Key endpoints - using Bearer token for authentication
  async getGeminiKey(): Promise<GeminiKey> {
    const response: AxiosResponse<ApiResponse<GeminiKey>> =
      await this.client.get("/gemini-key");
    return response.data.data;
  }

  async createGeminiKey(data: any): Promise<GeminiKey> {
    const response: AxiosResponse<ApiResponse<GeminiKey>> =
      await this.client.post("/gemini-key", data);
    return response.data.data;
  }

  async updateGeminiKey(keyId: string, data: any): Promise<GeminiKey> {
    const response: AxiosResponse<ApiResponse<GeminiKey>> =
      await this.client.put(`/gemini-key/${keyId}`, data);
    return response.data.data;
  }

  async deleteGeminiKey(keyId: string): Promise<void> {
    await this.client.delete(`/gemini-key/${keyId}`);
  }

  // Video Details endpoints - using Bearer token for authentication
  async getVideoDetails(videoId: string): Promise<any> {
    const response: AxiosResponse<ApiResponse<any>> = await this.client.get(
      `/video-details/${videoId}`
    );
    return response.data.data;
  }

  async updateVideoDetails(videoId: string, data: any): Promise<any> {
    const response: AxiosResponse<ApiResponse<any>> = await this.client.put(
      `/video-details/${videoId}`,
      data
    );
    return response.data.data;
  }

  // Utility method to check if user is authenticated
  isAuthenticated(): boolean {
    const token = localStorage.getItem("access_token");
    return !!token;
  }

  // Utility method to get token
  getToken(): string | null {
    return localStorage.getItem("access_token");
  }

  // Utility method to clear authentication
  clearAuth(): void {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
  }
}

export const apiClient = new ApiClient();
