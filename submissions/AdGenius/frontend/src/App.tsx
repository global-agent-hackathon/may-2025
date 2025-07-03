import React, { useEffect } from "react";
import {
  Routes,
  Route,
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import LoginPage from "./pages/LoginPage";
import Dashboard from "./pages/Dashboard";
import { authApi } from "./services/api";
import LoadingSpinner from "./components/LoadingSpinner";
import * as authUtils from "./utils/auth";
import AIAssistantPage from './pages/AIAssistantPage';

/**
 * Auth callback component to handle OAuth redirect
 */
function AuthCallback() {
  const { setUser, user, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleCallback = async () => {
      // Extract token from URL
      const urlParams = new URLSearchParams(location.search);
      const token = urlParams.get("token");
      
      // Get redirect path from URL params or session storage
      let redirectPath = urlParams.get("redirect");
      redirectPath = authUtils.retrieveAndClearRedirectPath(redirectPath || '/');
      
      // Process token if present
      if (token) {
        try {
          // Store token and update headers
          authUtils.setToken(token);
          
          // Validate token with backend
          const authResult = await authApi.validateToken();
          
          if (authResult.valid && authResult.user) {
            // Update auth state with user data
            setUser(authResult.user);
            
            // Brief delay to ensure state updates before navigation
            setTimeout(() => {
              console.log("Authentication successful, redirecting to:", redirectPath);
              navigate(redirectPath);
            }, 100);
          } else {
            console.error("Token validation failed");
            navigate("/login");
          }
        } catch (error) {
          console.error("Error processing auth callback:", error);
          navigate("/login");
        }
      } else {
        console.error("No token found in callback URL");
        navigate("/login");
      }
    };

    // Only process the callback if we're not authenticated yet
    if (!user && !loading) {
      handleCallback();
    } else if (user) {
      // Already authenticated, go to home
      navigate("/");
    }
  }, [location, navigate, user, loading, setUser]);

  // Show loading spinner while processing
  return (
    <div className="h-screen flex items-center justify-center">
      <LoadingSpinner size="lg" />
    </div>
  );
}

/**
 * Public route component
 */
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

/**
 * Protected route component
 */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  useEffect(() => {
    if (!loading && !user) {
      // Store the current path for redirect after login
      authUtils.storeRedirectPath(location.pathname);
    }
  }, [user, loading, location]);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

/**
 * Main App component with routing and authentication
 */
function App() {
  return (
    <AuthProvider>
      <div className="h-screen bg-gray-50 font-sans text-gray-900">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          
          {/* Protected routes */}
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/campaigns/:conversationId" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/assistant" element={<ProtectedRoute><AIAssistantPage /></ProtectedRoute>} />
          
          {/* Default redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </AuthProvider>
  );
}

export default App;
