"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { User, AuthResponse } from "@/types";
import { apiClient } from "@/lib/api";
import { sessionManager } from "@/lib/session";
import toast from "react-hot-toast";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (
    email: string,
    username: string,
    fullName: string,
    password: string
  ) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthContextProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      setIsLoading(true);

      // Initialize session from stored data
      const session = sessionManager.initSession();

      if (session && sessionManager.isSessionValid()) {
        // Validate session with backend
        const isValid = await sessionManager.validateSession();

        if (isValid) {
          setUser(session.user);
          setIsAuthenticated(true);
        } else {
          // Session is invalid, clear it
          sessionManager.clearSession();
          setUser(null);
          setIsAuthenticated(false);
        }
      } else {
        // No valid session found
        sessionManager.clearSession();
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      sessionManager.clearSession();
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response: AuthResponse = await apiClient.login({ email, password });

      // Set session data
      sessionManager.setSession({
        access_token: response.access_token,
        user: response.user,
        expires_at: getTokenExpiration(response.access_token),
      });

      setUser(response.user);
      setIsAuthenticated(true);

      toast.success("Login successful!");
    } catch (error: any) {
      console.error("Login failed:", error);
      toast.error(error.response?.data?.detail || "Login failed");
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (
    email: string,
    username: string,
    fullName: string,
    password: string
  ) => {
    try {
      setIsLoading(true);
      const userData = await apiClient.signup({
        email,
        username,
        full_name: fullName,
        password,
        confirm_password: password,
      });

      toast.success("Account created successfully! Please log in.");
    } catch (error: any) {
      console.error("Signup failed:", error);
      toast.error(error.response?.data?.detail || "Signup failed");
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    // Clear session data
    sessionManager.clearSession();
    setUser(null);
    setIsAuthenticated(false);
    toast.success("Logged out successfully");
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);

      // Update session data
      const currentSession = sessionManager.initSession();
      if (currentSession) {
        sessionManager.setSession({
          ...currentSession,
          user: updatedUser,
        });
      }
    }
  };

  const refreshUser = async () => {
    try {
      if (sessionManager.isSessionValid()) {
        const userData = await apiClient.getCurrentUser();
        setUser(userData);

        // Update session data
        const currentSession = sessionManager.initSession();
        if (currentSession) {
          sessionManager.setSession({
            ...currentSession,
            user: userData,
          });
        }
      }
    } catch (error) {
      console.error("Failed to refresh user data:", error);
      logout();
    }
  };

  // Helper function to get token expiration
  const getTokenExpiration = (token: string): number | null => {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp * 1000; // Convert to milliseconds
    } catch (error) {
      console.error("Failed to decode token:", error);
      return null;
    }
  };

  const value = {
    user,
    isLoading,
    isAuthenticated,
    login,
    signup,
    logout,
    updateUser,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
 