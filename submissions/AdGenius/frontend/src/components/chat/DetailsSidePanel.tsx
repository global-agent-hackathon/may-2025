import React, { useMemo } from "react";
import { ChevronRight } from "lucide-react";
import WorkflowProgress from "./WorkflowProgress";
import { useWorkflow } from "./useWorkflow";
import { PublishedCampaignData } from "../../types";

interface DetailsSidePanelProps {
  isDesktop: boolean;
  isDetailsPanelOpen: boolean;
  setIsDetailsPanelOpen: (isOpen: boolean) => void;
  handlePublish: () => Promise<void>;
  conversationId?: string;
  sendMessage?: (messageContent: string) => void;
}

// Helper type for requirements data
interface RequirementsData {
  product_or_service?: string;
  product_or_service_url?: string;
  campaign_name?: string;
  target_audience?: string;
  geography?: string;
  ad_format?: string;
  platform?: string;
  budget?: string;
  kpi?: string;
  time_period?: string;
  creative_direction?: string;
  other_details?: string[];
}

// Type guard to check if an object is RequirementsData
function isRequirementsData(data: any): data is RequirementsData {
  return typeof data === 'object' && data !== null;
}

const DetailsSidePanel: React.FC<DetailsSidePanelProps> = ({
  isDesktop,
  isDetailsPanelOpen,
  setIsDetailsPanelOpen,
  handlePublish,
  conversationId,
  sendMessage,
}) => {
  const {
    currentWorkflow,
    currentStep,
    generatedContent,
    selectedAdCopy,
    setSelectedAdCopy,
    draftCampaigns,
    setCurrentConversationId,
    publishedCampaign,
  } = useWorkflow();

  // Set conversation ID when it changes
  React.useEffect(() => {
    if (conversationId) {
      setCurrentConversationId(conversationId);
    }
  }, [conversationId, setCurrentConversationId]);

  // Parse requirements from draft campaigns
  const campaignRequirements = useMemo(() => {
    const requirementsCampaign = draftCampaigns.find(
      (campaign) => campaign.type === "requirements"
    );
    
    // If no requirements data found, return null to indicate no data
    if (!requirementsCampaign) {
      return null;
    }

    try {
      // Use the data field directly with the actual field names
      const data = requirementsCampaign.data;
      
      // Make sure data is the right type before accessing properties
      if (isRequirementsData(data)) {
        return {
          product: data.product_or_service || "",
          productUrl: data.product_or_service_url || "",
          campaignName: data.campaign_name || "",
          targetAudience: data.target_audience || "",
          geography: data.geography || "",
          adFormat: data.ad_format || "",
          platform: data.platform || "",
          budget: data.budget || "",
          kpi: data.kpi || "",
          timePeriod: data.time_period || "",
          creativeDirection: data.creative_direction || "",
          otherDetails: Array.isArray(data.other_details) ? data.other_details : [],
        };
      }
      return null;
    } catch (error) {
      console.error("Error processing requirements:", error);
      return null;
    }
  }, [draftCampaigns]);

  // Extract ad copy options from the ad_copy campaign
  const adCopyOptions = useMemo(() => {
    const adCopyCampaign = draftCampaigns.find(
      (campaign) => campaign.type === "ad_copy"
    );
    if (!adCopyCampaign || !adCopyCampaign.data) return [];
    // Get all values whose keys start with "ad_copy_"
    return Object.entries(adCopyCampaign.data)
      .filter(([key]) => key.startsWith("ad_copy_"))
      .map(([, value]) => value)
      .filter(Boolean);
  }, [draftCampaigns]);

  // Check if we have any requirements data
  const hasRequirements = campaignRequirements !== null;

  // Add published campaign section
  const renderPublishedCampaign = () => {
    if (!publishedCampaign) return null;

    const data = publishedCampaign.data;
    return (
      <div className="space-y-4">
        <h4 className="font-medium mb-2">Published Campaign</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Campaign ID</span>
            <span className="font-medium">{data.campaign_id}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Ad ID</span>
            <span className="font-medium">{data.ad_id}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Status</span>
            <span className="font-medium capitalize">{data.ad_status}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Publication Date</span>
            <span className="font-medium">{data.publication_date}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Ad URL</span>
            <a 
              href={`https://ads-publisher.feedmob.ai/dashboard/ads/${data.ad_id}`}
              target="_blank" 
              rel="noopener noreferrer"
              className="font-medium text-primary-600 hover:text-primary-700"
            >
              View Ad
            </a>
          </div>
          {data.ad_metrics && (
            <div className="py-2">
              <div className="text-gray-600 mb-2">Ad Metrics</div>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="p-2 bg-gray-50 rounded">
                  <div className="text-xs text-gray-500">Impressions</div>
                  <div className="font-medium">{data.ad_metrics.impressions}</div>
                </div>
                <div className="p-2 bg-gray-50 rounded">
                  <div className="text-xs text-gray-500">Clicks</div>
                  <div className="font-medium">{data.ad_metrics.clicks}</div>
                </div>
                <div className="p-2 bg-gray-50 rounded">
                  <div className="text-xs text-gray-500">Conversions</div>
                  <div className="font-medium">{data.ad_metrics.conversions}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Function to handle publish button click
  const handlePublishClick = () => {
    // Send the message to AI Assistant if the sendMessage function is provided
    if (sendMessage) {
      sendMessage("Please publish the campaign");
      // No need to call handlePublish separately, as sendMessage now properly
      // triggers the full message flow including handlePublish
    } else {
      // Fallback to direct publish if sendMessage is not available
      handlePublish();
    }
  };

  return (
    <div
      className={
        isDesktop
          ? "bg-white flex flex-col border-l border-gray-200/50 rounded-xl" // desktop: flex child
          : `bg-white fixed inset-y-0 right-0 w-full md:w-[400px] transform transition-transform duration-300 z-20 ${
              isDetailsPanelOpen ? "translate-x-0" : "translate-x-full"
            }` // mobile: overlay
      }
      style={
        isDesktop
          ? {
              flex: 1,
              minWidth: 320,
              maxHeight: "100vh", // Ensure it doesn't exceed viewport height
              display: "flex",
              flexDirection: "column",
            }
          : {
              maxHeight: "100vh", // Ensure it doesn't exceed viewport height
              display: "flex", 
              flexDirection: "column",
            }
      }
    >
      {/* Mobile Close Button */}
      <button
        onClick={() => setIsDetailsPanelOpen(false)}
        className="absolute top-4 -left-12 lg:hidden bg-white p-3 rounded-l-xl border border-r-0 border-gray-200/50 text-gray-400 hover:text-gray-600"
      >
        <ChevronRight className="h-5 w-5" />
      </button>

      <div className="flex flex-col h-full">
        {/* Fixed Header */}
        <div className="flex-shrink-0 p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Campaign Details</h3>
            <button
              onClick={() => setIsDetailsPanelOpen(false)}
              className="lg:hidden p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100/80"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
          <div className="mt-4 hidden lg:block">
            <WorkflowProgress steps={currentWorkflow} />
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto message-list-scrollbar">
          <div className="p-6 space-y-8">
            {/* Current Step */}
            <div>
              <h4 className="font-medium mb-2">Current Step</h4>
              <div className="p-4 bg-primary-50 rounded-lg border border-primary-100">
                <p className="text-primary-700 text-sm">{currentStep}</p>
              </div>
            </div>

            {/* Published Campaign Section */}
            {renderPublishedCampaign()}

            {/* Campaign Preview */}
            <div>
              <h4 className="font-medium mb-3">Campaign Preview</h4>
              <div className="space-y-4">
                {/* Ad Copy Options - only show if data exists */}
                {adCopyOptions.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">
                      Ad Copy Options
                    </h5>
                    <div className="space-y-2">
                      {adCopyOptions.map((copy, index) => (
                        <button
                          key={index}
                          onClick={() => setSelectedAdCopy(index)}
                          className={`w-full p-3 text-left text-sm rounded-lg border transition-colors ${
                            selectedAdCopy === index
                              ? "border-primary-200 bg-primary-50 text-primary-900"
                              : "border-gray-200 hover:border-primary-200 hover:bg-primary-50/50"
                          }`}
                        >
                          {copy}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Ad Visual - only show if image exists */}
                {generatedContent.selectedImage && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">
                      Ad Visual
                    </h5>
                    <div className="rounded-lg border border-gray-200 overflow-hidden">
                      <img
                        src={generatedContent.selectedImage}
                        alt="Selected ad visual"
                        className="w-full h-auto"
                      />
                    </div>
                  </div>
                )}
                
                {/* Show message if no content available */}
                {adCopyOptions.length === 0 && !generatedContent.selectedImage && (
                  <p className="text-gray-500 text-sm italic">
                    Campaign content will appear here as it's generated
                  </p>
                )}
              </div>
            </div>

            {/* Campaign Details - only show if we have real data */}
            {hasRequirements ? (
              <div>
                <h4 className="font-medium mb-2">Campaign Details</h4>
                <div className="space-y-2 text-sm">
                  {campaignRequirements.campaignName && (
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Campaign Name</span>
                      <span className="font-medium">{campaignRequirements.campaignName}</span>
                    </div>
                  )}
                  {campaignRequirements.product && (
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Product</span>
                      <span className="font-medium">{campaignRequirements.product}</span>
                    </div>
                  )}
                  {campaignRequirements.productUrl && (
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Product URL</span>
                      <span className="font-medium">{campaignRequirements.productUrl}</span>
                    </div>
                  )}
                  {campaignRequirements.targetAudience && (
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Target Audience</span>
                      <span className="font-medium">{campaignRequirements.targetAudience}</span>
                    </div>
                  )}
                  {campaignRequirements.geography && (
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Geography</span>
                      <span className="font-medium">{campaignRequirements.geography}</span>
                    </div>
                  )}
                  {campaignRequirements.adFormat && (
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Ad Format</span>
                      <span className="font-medium">{campaignRequirements.adFormat}</span>
                    </div>
                  )}
                  {campaignRequirements.platform && (
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Platform</span>
                      <span className="font-medium">{campaignRequirements.platform}</span>
                    </div>
                  )}
                  {campaignRequirements.budget && (
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Budget</span>
                      <span className="font-medium">{campaignRequirements.budget}</span>
                    </div>
                  )}
                  {campaignRequirements.kpi && (
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">KPI</span>
                      <span className="font-medium">{campaignRequirements.kpi}</span>
                    </div>
                  )}
                  {campaignRequirements.timePeriod && (
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Time Period</span>
                      <span className="font-medium">{campaignRequirements.timePeriod}</span>
                    </div>
                  )}
                  {campaignRequirements.creativeDirection && (
                    <div className="py-2 border-b border-gray-100">
                      <div className="text-gray-600 mb-1">Creative Direction</div>
                      <div className="font-medium text-sm">{campaignRequirements.creativeDirection}</div>
                    </div>
                  )}
                  {campaignRequirements.otherDetails && campaignRequirements.otherDetails.length > 0 && (
                    <div className="py-2">
                      <div className="text-gray-600 mb-1">Other Details</div>
                      <ul className="list-disc pl-5 text-sm space-y-1">
                        {campaignRequirements.otherDetails.map((detail, index) => (
                          <li key={index} className="font-medium">{detail}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-sm italic">
                Campaign details will appear here once requirements are defined
              </p>
            )}
          </div>
        </div>

        {/* Fixed Footer */}
        <div className="flex-shrink-0 p-6 border-t border-gray-100">
          {publishedCampaign ? (
            <div className="text-center text-sm text-gray-600">
              Campaign published on {publishedCampaign.data.publication_date}
            </div>
          ) : (
            <button
              onClick={handlePublishClick}
              disabled={selectedAdCopy === null || adCopyOptions.length === 0}
              className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                selectedAdCopy !== null && adCopyOptions.length > 0
                  ? "bg-primary-600 hover:bg-primary-700 text-white"
                  : "bg-gray-100 text-gray-400 cursor-not-allowed"
              }`}
            >
              Publish Campaign
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default DetailsSidePanel;