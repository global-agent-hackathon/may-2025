import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import CompanyAnalysisPage from './pages/CompanyAnalysisPage';
import IntersectXChatPage from './pages/IntersectXChatPage';
import Auth from './pages/Auth';
import FounderSignup from './pages/FounderSignup';
import ColorPalette from './components/styleguide/ColorPalette';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ChatProvider } from './providers/ChatProvider';
import type { ReactElement } from 'react';

function ProtectedRoute({ children }: { children: ReactElement }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return null;
  if (!user) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }
  return children;
}

function AppContent() {
  const location = useLocation();
  const isAuthPage = location.pathname === '/auth' || location.pathname === '/founder-signup';



  return (
    <div className={`min-h-screen flex flex-col ${isAuthPage ? 'bg-gradient-to-b from-purple-light/10 to-off-white' : 'bg-gray-50'}`}>
      {!isAuthPage && <Navbar />}
      <main className={`container-fluid mx-auto flex-1 overflow-hidden ${!isAuthPage ? 'px-0 pt-16' : ''}`}>
        <Routes>
          <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/companies/:companyName/analysis" element={<CompanyAnalysisPage />} />
          <Route path="/intersectx-chat" element={<IntersectXChatPage />} />
          <Route path="/intersectx-chat/t/:threadId" element={<ProtectedRoute><IntersectXChatPage /></ProtectedRoute>} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/founder-signup" element={<FounderSignup />} />
          <Route path="/styleguide/colors" element={<ColorPalette />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ChatProvider>
        <Router>
          <AppContent />
        </Router>
      </ChatProvider>
    </AuthProvider>
  );
}
