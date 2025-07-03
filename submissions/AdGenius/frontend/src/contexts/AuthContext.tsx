import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';
import axios from 'axios';
import * as authUtils from '../utils/auth';

interface User {
  id: string;
  name: string;
  email: string;
  photoURL: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check for existing session via token validation
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check for token
        const token = authUtils.getToken();

        if (token) {
          // Set the token in axios headers
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

          // Validate the token
          const result = await authApi.validateToken();
          if (result.valid && result.user) {
            setUser(result.user);
          } else {
            // Token is invalid, clean up
            authUtils.removeToken();
            delete axios.defaults.headers.common['Authorization'];
          }
        }
      } catch (error) {
        console.error('Authentication validation failed:', error);
        authUtils.removeToken();
        delete axios.defaults.headers.common['Authorization'];
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async () => {
    setLoading(true);
    try {
      // Store the intended redirect path
      authUtils.storeRedirectPath();
      
      // Get Google authentication URL
      const redirectPath = authUtils.getSafeRedirectPath(authUtils.getCurrentUrlPath());
      const authUrl = await authApi.getGoogleAuthUrl(redirectPath);
      
      // Redirect to Google login
      window.location.href = authUrl;
    } catch (error) {
      console.error('Login failed:', error);
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await authApi.logout();
      // Clean up auth state
      authUtils.removeToken();
      delete axios.defaults.headers.common['Authorization'];
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
      // Still clean up even if API call fails
      authUtils.removeToken();
      delete axios.defaults.headers.common['Authorization'];
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};
