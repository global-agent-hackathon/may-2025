
import { Suspense, lazy } from 'react';
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider, RequireAuth } from "@/contexts/AuthContext";
import { WatchlistProvider } from "@/contexts/WatchlistContext";
import Layout from "./components/layout/Layout";

const Index = lazy(() => import("./pages/Index"));
const About = lazy(() => import("./pages/About"));
const Login = lazy(() => import("./pages/auth/Login"));
const Register = lazy(() => import("./pages/auth/Register"));
const ForgotPassword = lazy(() => import("./pages/auth/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/auth/ResetPassword"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Market = lazy(() => import("./pages/Market"));
const Profile = lazy(() => import("./pages/Profile"));
const Chat = lazy(() => import("./pages/Chat"));
const NotFound = lazy(() => import("./pages/NotFound"));

const queryClient = new QueryClient();

// Define metadata for the page
export const metadata = {
  title: 'SparkVest',
  description: 'View and track real-time market data and stock prices',
};

const App = () => (

    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <WatchlistProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <BrowserRouter>
              <Layout>
                <Suspense fallback={<div>Loading...</div>}>
                  <Routes>
                    <Route path="/" element={<Index />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/forgot-password" element={<ForgotPassword />} />
                    <Route path="/reset-password" element={<ResetPassword />} />
                    <Route 
                      path="/dashboard" 
                      element={
                        <RequireAuth>
                          <Dashboard />
                        </RequireAuth>
                      } 
                    />
                    <Route 
                      path="/market" 
                      element={
                        <RequireAuth>
                          <Market />
                        </RequireAuth>
                      } 
                    />
                    <Route 
                      path="/profile" 
                      element={
                        <RequireAuth>
                          <Profile />
                        </RequireAuth>
                      } 
                    />
                    <Route 
                      path="/chat" 
                      element={
                        <RequireAuth>
                          <Chat />
                        </RequireAuth>
                      } 
                    />
                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </Suspense>
              </Layout>
            </BrowserRouter>
          </TooltipProvider>
        </WatchlistProvider>
      </AuthProvider>
    </QueryClientProvider>
  
);

export default App;
