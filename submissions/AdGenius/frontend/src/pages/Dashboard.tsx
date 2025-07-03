import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import Sidebar from "../components/Sidebar";
import ChatPanel from "../components/ChatPanel";
import { Sparkles, Menu, X, ChevronLeft, ChevronRight } from "lucide-react";
import { useParams, useLocation } from "react-router-dom";

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [currentView, setCurrentView] = useState<"chat" | "metrics">("chat");
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [selectedConversationId, setSelectedConversationId] = useState<
    string | null
  >(null);
  const { conversationId } = useParams<{ conversationId?: string }>();

  // Reset selectedConversationId when navigating to the root path
  const location = useLocation();
  useEffect(() => {
    if (location.pathname === "/") {
      setSelectedConversationId(null);
    }
  }, [location.pathname]);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setIsMobileSidebarOpen(true)}
                className="md:hidden p-2 rounded-md text-gray-700 hover:bg-gray-100"
              >
                <Menu className="h-6 w-6" />
              </button>
              <div className="flex items-center">
                <Sparkles className="h-8 w-8 text-primary-600 mr-2" />
                <span className="font-bold text-xl text-primary-700">
                  AdGenius
                </span>
              </div>
            </div>

            <div className="flex items-center">
              {user && (
                <div className="flex items-center space-x-4">
                  <div className="hidden md:flex flex-col items-end">
                    <span className="text-sm font-medium">{user.name}</span>
                    <span className="text-xs text-gray-500">{user.email}</span>
                  </div>
                  <img
                    src={user.photoURL}
                    alt={user.name}
                    className="h-10 w-10 rounded-full border-2 border-gray-200"
                  />
                  <button
                    onClick={logout}
                    className="hidden md:block text-sm text-gray-700 hover:text-red-600"
                  >
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Sidebar */}
      <div
        className={`fixed inset-0 z-40 md:hidden bg-black bg-opacity-50 transition-opacity duration-300 ease-in-out ${
          isMobileSidebarOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        }`}
        onClick={() => setIsMobileSidebarOpen(false)}
      />

      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out md:hidden ${
          isMobileSidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center">
            <Sparkles className="h-6 w-6 text-primary-600 mr-2" />
            <span className="font-bold text-lg text-primary-700">AdGenius</span>
          </div>
          <button
            onClick={() => setIsMobileSidebarOpen(false)}
            className="p-2 rounded-md text-gray-600 hover:bg-gray-100"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <Sidebar
          onToggleView={(view) => {
            setCurrentView(view);
            setIsMobileSidebarOpen(false);
          }}
          currentView={currentView}
          onSelectConversation={(conversationId) => {
            setSelectedConversationId(conversationId);
            setIsMobileSidebarOpen(false);
          }}
        />
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop Sidebar */}
        <div className="relative hidden md:block">
          <div
            className={`h-full transition-all duration-300 ${
              isSidebarOpen ? "w-80" : "w-20"
            } overflow-hidden border-r border-gray-200 bg-white`}
          >
            <Sidebar
              onToggleView={setCurrentView}
              currentView={currentView}
              isCollapsed={!isSidebarOpen}
              onSelectConversation={setSelectedConversationId}
            />
          </div>
          <button
            onClick={toggleSidebar}
            className="absolute -right-3 top-4 bg-white rounded-full p-1 shadow-soft border border-gray-200/50"
          >
            {isSidebarOpen ? (
              <ChevronLeft className="h-4 w-4 text-gray-600" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-600" />
            )}
          </button>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-hidden">
            <ChatPanel
              key={
                location.pathname === "/"
                  ? "new-conversation"
                  : conversationId || selectedConversationId
              }
              conversationId={conversationId || selectedConversationId}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
