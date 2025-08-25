export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Video {
  id: string;
  filename: string;
  original_filename?: string;
  file_path: string;
  file_size: number;
  duration: number;
  status: "uploading" | "processing" | "ready" | "error";
  user_id: string;
  created_at: string;
  updated_at: string;
  title?: string;
  description?: string;
  thumbnail_path?: string;
  youtube_video_id?: string;
  privacy_status?: string;
  scheduled_time?: string;
}

export interface Playlist {
  id: string;
  title: string;
  description: string;
  playlist_id: string;
  channel_id: string;
  published_at: string;
  thumbnail_url: string;
  total_videos: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  last_updated: string;
}

export interface VideoAnalytics {
  video_id: string;
  title: string;
  views: number;
  likes: number;
  comments: number;
  engagement_rate: number;
  performance_score: number;
  published_at: string;
  duration: string;
  thumbnail_url: string;
}

export interface DashboardOverview {
  total_playlists: number;
  total_videos: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  average_views_per_playlist: number;
  average_videos_per_playlist: number;
  top_playlists: Playlist[];
  recent_playlists: Playlist[];
}

export interface PlaylistAnalytics {
  total_videos: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  average_engagement_rate: number;
  top_performing_videos: VideoAnalytics[];
  worst_performing_videos: VideoAnalytics[];
  performance_summary: {
    best_video: VideoAnalytics;
    worst_video: VideoAnalytics;
    average_views: number;
    average_likes: number;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  count?: number;
}

export interface LoginFormData {
  email: string;
  password: string;
}

export interface SignupFormData {
  email: string;
  username: string;
  full_name: string;
  password: string;
  confirm_password: string;
}

export interface UploadFormData {
  file: File;
  title?: string;
  description?: string;
  privacy_status?: string;
  scheduled_time?: string;
}

export interface GenerateContentRequest {
  video_id: string;
  prompt?: string;
  type: "title" | "description" | "thumbnail" | "timestamps";
}

export interface YouTubeToken {
  id: string;
  user_id: string;
  access_token: string;
  refresh_token: string;
  expires_at: string;
  created_at: string;
  updated_at: string;
}

export interface GeminiKey {
  id: string;
  user_id: string;
  api_key: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Backend specific types
export interface UserSignUp {
  id: string;
  email: string;
  username: string;
  full_name: string;
  password: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserSignIn {
  email: string;
  password: string;
}

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
