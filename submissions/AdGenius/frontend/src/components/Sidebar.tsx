import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navigation from "./sidebar/Navigation";
import NewCampaignButton from "./sidebar/NewCampaignButton";
import CampaignsList from "./sidebar/CampaignsList";
import MobileSignOut from "./sidebar/MobileSignOut";

interface SidebarProps {
  onToggleView: (view: "chat" | "metrics") => void;
  currentView: "chat" | "metrics";
  isCollapsed?: boolean;
  onSelectConversation?: (conversationId: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  onToggleView,
  currentView,
  isCollapsed = false,
  onSelectConversation,
}) => {
  const navigate = useNavigate();
  const [activeCampaign, setActiveCampaign] = useState<string | null>(null);
  const [isRecentExpanded, setIsRecentExpanded] = useState(true);

  // Reset when navigating to home
  const handleNewCampaign = () => {
    // Reset active campaign
    setActiveCampaign(null);

    // If conversation selection handler is provided, reset it
    if (onSelectConversation) {
      onSelectConversation("");
    }

    // Navigate to home page
    navigate("/");
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Fixed Top Section */}
      <div className="flex-shrink-0">
        {/* New Campaign Button */}
        <NewCampaignButton
          isCollapsed={isCollapsed}
          onClick={handleNewCampaign}
        />

        {/* Navigation */}
        <Navigation
          onToggleView={onToggleView}
          currentView={currentView}
          isCollapsed={isCollapsed}
        />
      </div>

      {/* Scrollable Middle Section - Fills available space */}
      {!isCollapsed && currentView === "chat" && (
        <div className="flex-1 overflow-hidden flex flex-col">
          {/* Recent Campaigns - Takes all available height */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <CampaignsList
              activeCampaign={activeCampaign}
              setActiveCampaign={setActiveCampaign}
              isExpanded={isRecentExpanded}
              toggleExpanded={() => setIsRecentExpanded(!isRecentExpanded)}
              currentView={currentView}
              onSelectConversation={onSelectConversation}
            />
          </div>
        </div>
      )}

      {/* Fixed Bottom Section */}
      {!isCollapsed && (
        <div className="flex-shrink-0">
          <MobileSignOut />
        </div>
      )}
    </div>
  );
};

export default Sidebar;
