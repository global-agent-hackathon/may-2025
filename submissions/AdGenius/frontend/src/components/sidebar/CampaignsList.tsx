import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ChevronDown, ChevronUp, Clock, Loader2 } from 'lucide-react';
import { Conversation } from '../../types';
import { chatService } from '../../services/chatService';
import { useNavigate } from 'react-router-dom';

interface CampaignsListProps {
  activeCampaign: string | null;
  setActiveCampaign: (id: string | null) => void;
  isExpanded: boolean;
  toggleExpanded: () => void;
  currentView: 'chat' | 'metrics';
  onSelectConversation?: (conversationId: string) => void;
}

const CampaignsList: React.FC<CampaignsListProps> = ({
  activeCampaign,
  setActiveCampaign,
  isExpanded,
  toggleExpanded,
  currentView,
  onSelectConversation
}) => {
  const [campaigns, setCampaigns] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const observer = useRef<IntersectionObserver | null>(null);
  const LIMIT = 10;
  const navigate = useNavigate();
  
  // Function to fetch conversations as campaigns
  const fetchCampaigns = useCallback(async (isInitialFetch = false) => {
    if (currentView !== 'chat') return;
    
    try {
      setIsLoading(true);
      const newOffset = isInitialFetch ? 0 : offset;
      const response = await chatService.getConversations(LIMIT, newOffset);
      
      // If we get fewer items than the limit, we've reached the end
      if (response.length < LIMIT) {
        setHasMore(false);
      }
      
      // For initial fetch, replace campaigns; for pagination, append
      if (isInitialFetch) {
        setCampaigns(response);
      } else {
        // Deduplicate by ID when appending
        setCampaigns((prev: Conversation[]) => {
          const existingIds = new Set(prev.map((campaign: Conversation) => campaign.id));
          const newCampaigns = response.filter((campaign: Conversation) => !existingIds.has(campaign.id));
          return [...prev, ...newCampaigns];
        });
      }
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    } finally {
      setIsLoading(false);
    }
  }, [offset, currentView]);
  
  // Reset when changing views
  useEffect(() => {
    setCampaigns([]);
    setOffset(0);
    setHasMore(true);
  }, [currentView]);
  
  // Initial load - only when expanded or view changes
  useEffect(() => {
    if (isExpanded) {
      // Reset offset and fetch from beginning
      setOffset(0);
      fetchCampaigns(true);
    }
  }, [isExpanded, currentView]);
  
  // Handle pagination - separate from initial load
  useEffect(() => {
    if (isExpanded && offset > 0) {
      fetchCampaigns(false);
    }
  }, [offset, isExpanded, fetchCampaigns]);
  
  // Setup the intersection observer for infinite scrolling
  const lastCampaignRef = useCallback((node: HTMLDivElement | null) => {
    // If already loading, don't observe
    if (isLoading) return;
    
    // Disconnect previous observer
    if (observer.current) observer.current.disconnect();
    
    // Create new observer
    observer.current = new IntersectionObserver(entries => {
      // If the last item is visible and we have more items to load
      if (entries[0]?.isIntersecting && hasMore) {
        setOffset(prev => prev + LIMIT);
      }
    });
    
    // Observe the last item if it exists
    if (node) observer.current.observe(node);
  }, [isLoading, hasMore]);
  
  // Handle campaign selection
  const handleCampaignSelect = (campaignId: string) => {
    setActiveCampaign(campaignId === activeCampaign ? null : campaignId);
    if (onSelectConversation) {
      onSelectConversation(campaignId);
    }
    // Update the URL to /campaigns/xxx_conversation
    if (campaignId) {
      navigate(`/campaigns/${campaignId}`);
    }
  };
  
  return (
    <div className="flex flex-col h-full">
      <div className="px-3 mb-2 flex-shrink-0">
        <button 
          onClick={toggleExpanded}
          className="flex items-center justify-between w-full px-3 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50 rounded-md"
        >
          <div className="flex items-center">
            <Clock className="h-4 w-4 mr-2" />
            Recent Campaigns
          </div>
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>
      
      {isExpanded && (
        <div className="space-y-1 px-3 flex-1 overflow-y-auto message-list-scrollbar">
          {campaigns.length === 0 && !isLoading ? (
            <div className="text-sm text-gray-500 px-3 py-2">
              No campaigns yet
            </div>
          ) : (
            campaigns.map((campaign, index) => {
              // Apply ref to last item for infinite scrolling
              const isLastItem = index === campaigns.length - 1;
              
              return (
                <div 
                  key={campaign.id}
                  ref={isLastItem ? lastCampaignRef : null}
                >
                  <button
                    onClick={() => handleCampaignSelect(campaign.id)}
                    className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                      campaign.id === activeCampaign
                        ? 'bg-gray-100 text-gray-900'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="truncate">{campaign.title}</div>
                  </button>
                </div>
              );
            })
          )}
          
          {/* Loading indicator at the bottom */}
          {isLoading && (
            <div className="flex justify-center py-2">
              <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CampaignsList;