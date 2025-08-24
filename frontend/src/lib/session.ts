import { apiClient } from "./api";

export interface SessionData {
  access_token: string;
  user: any;
  expires_at?: number;
}

class SessionManager {
  private static instance: SessionManager;
  private refreshTimeout: NodeJS.Timeout | null = null;

  private constructor() {}

  static getInstance(): SessionManager {
    if (!SessionManager.instance) {
      SessionManager.instance = new SessionManager();
    }
    return SessionManager.instance;
  }

  // Initialize session from stored data
  initSession(): SessionData | null {
    const token = localStorage.getItem("access_token");
    const userStr = localStorage.getItem("user");

    if (!token || !userStr) {
      return null;
    }

    try {
      const user = JSON.parse(userStr);
      return {
        access_token: token,
        user,
        expires_at: this.getTokenExpiration(token),
      };
    } catch (error) {
      console.error("Failed to parse session data:", error);
      this.clearSession();
      return null;
    }
  }

  // Set session data
  setSession(sessionData: SessionData): void {
    localStorage.setItem("access_token", sessionData.access_token);
    localStorage.setItem("user", JSON.stringify(sessionData.user));

    // Set up token refresh if expiration is available
    if (sessionData.expires_at) {
      this.scheduleTokenRefresh(sessionData.expires_at);
    }
  }

  // Clear session data
  clearSession(): void {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout);
      this.refreshTimeout = null;
    }
  }

  // Check if session is valid
  isSessionValid(): boolean {
    const token = localStorage.getItem("access_token");
    if (!token) return false;

    const expiresAt = this.getTokenExpiration(token);
    if (!expiresAt) return false;

    // Check if token is expired (with 5 minute buffer)
    const now = Date.now();
    const buffer = 5 * 60 * 1000; // 5 minutes
    return expiresAt > now + buffer;
  }

  // Get token expiration time
  private getTokenExpiration(token: string): number | null {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp * 1000; // Convert to milliseconds
    } catch (error) {
      console.error("Failed to decode token:", error);
      return null;
    }
  }

  // Schedule token refresh
  private scheduleTokenRefresh(expiresAt: number): void {
    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout);
    }

    const now = Date.now();
    const refreshTime = expiresAt - now - 5 * 60 * 1000; // Refresh 5 minutes before expiry

    if (refreshTime > 0) {
      this.refreshTimeout = setTimeout(() => {
        this.refreshToken();
      }, refreshTime);
    }
  }

  // Refresh token by calling backend
  private async refreshToken(): Promise<void> {
    try {
      // Call the current user endpoint to validate token
      const userData = await apiClient.getCurrentUser();

      // Update stored user data
      localStorage.setItem("user", JSON.stringify(userData));

      // Schedule next refresh
      const token = localStorage.getItem("access_token");
      if (token) {
        const expiresAt = this.getTokenExpiration(token);
        if (expiresAt) {
          this.scheduleTokenRefresh(expiresAt);
        }
      }
    } catch (error) {
      console.error("Token refresh failed:", error);
      // If refresh fails, clear session
      this.clearSession();
      window.location.href = "/login";
    }
  }

  // Validate session and refresh if needed
  async validateSession(): Promise<boolean> {
    if (!this.isSessionValid()) {
      this.clearSession();
      return false;
    }

    try {
      // Verify token with backend
      await apiClient.getCurrentUser();
      return true;
    } catch (error) {
      console.error("Session validation failed:", error);
      this.clearSession();
      return false;
    }
  }

  // Get current user data
  getCurrentUser(): any | null {
    const userStr = localStorage.getItem("user");
    if (!userStr) return null;

    try {
      return JSON.parse(userStr);
    } catch (error) {
      console.error("Failed to parse user data:", error);
      return null;
    }
  }

  // Get current token
  getToken(): string | null {
    return localStorage.getItem("access_token");
  }
}

export const sessionManager = SessionManager.getInstance();
 