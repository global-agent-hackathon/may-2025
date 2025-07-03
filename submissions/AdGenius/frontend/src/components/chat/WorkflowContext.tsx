import React, { createContext, useState, ReactNode, useEffect, useCallback } from "react";
import { WorkflowStep, WorkflowStatus, DraftCampaign } from "../../types/index";
import { chatService } from "../../services/chatService";

interface WorkflowContextProps {
  currentWorkflow: WorkflowStep[];
  setCurrentWorkflow: React.Dispatch<React.SetStateAction<WorkflowStep[]>>;
  currentStep: string;
  setCurrentStep: React.Dispatch<React.SetStateAction<string>>;
  generatedContent: {
    adCopyOptions: string[];
    selectedImage: string;
  };
  setGeneratedContent: React.Dispatch<
    React.SetStateAction<{
      adCopyOptions: string[];
      selectedImage: string;
    }>
  >;
  selectedAdCopy: number | null;
  setSelectedAdCopy: React.Dispatch<React.SetStateAction<number | null>>;
  handlePublish: () => Promise<void>;
  draftCampaigns: DraftCampaign[];
  fetchDraftCampaigns: (conversationId: string) => Promise<void>;
  currentConversationId: string | null;
  setCurrentConversationId: React.Dispatch<React.SetStateAction<string | null>>;
  publishedCampaign: DraftCampaign | null;
}

export const WorkflowContext = createContext<WorkflowContextProps | undefined>(
  undefined,
);

// Custom hook to use the workflow context

interface WorkflowProviderProps {
  children: ReactNode;
}

// Workflow provider component
export const WorkflowProvider: React.FC<WorkflowProviderProps> = ({
  children,
}) => {
  // Workflow state
  const [currentWorkflow, setCurrentWorkflow] = useState<WorkflowStep[]>([
    { id: "analysis", name: "Analysis", status: WorkflowStatus.Pending },
    { id: "content", name: "Ad Copy", status: WorkflowStatus.Pending },
    { id: "image", name: "Visual", status: WorkflowStatus.Pending },
    { id: "publish", name: "Publish", status: WorkflowStatus.Pending },
  ]);

  // Campaign content state
  const [currentStep, setCurrentStep] = useState(
    "Generating campaign requirements..."
  );
  const [selectedAdCopy, setSelectedAdCopy] = useState<number | null>(null);
  const [generatedContent, setGeneratedContent] = useState<{
    adCopyOptions: string[];
    selectedImage: string;
  }>({
    adCopyOptions: [],
    selectedImage: "",
  });
  
  // Draft campaigns state
  const [draftCampaigns, setDraftCampaigns] = useState<DraftCampaign[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);

  // Add published campaign state
  const [publishedCampaign, setPublishedCampaign] = useState<DraftCampaign | null>(null);

  // Update workflow status based on available data
  const updateWorkflowStatus = useCallback((campaigns: DraftCampaign[]) => {
    // Determine which steps are available
    const hasRequirements = campaigns.some(campaign => campaign.type === "requirements");
    const hasAdCopy = campaigns.some(campaign => campaign.type === "ad_copy");
    const hasVisual = campaigns.some(campaign => campaign.type === "ad_image");
    const hasPublished = campaigns.some(campaign => campaign.type === "published_campaign");

    // Find the current step index
    let currentStepIndex = 0;
    if (!hasRequirements) {
      setCurrentStep("Generating campaign requirements...");
      currentStepIndex = 0;
    } else if (!hasAdCopy) {
      setCurrentStep("Generating ad copy options...");
      currentStepIndex = 1;
    } else if (!hasVisual) {
      setCurrentStep("Generating visual content...");
      currentStepIndex = 2;
    } else if (!hasPublished) {
      setCurrentStep("Ready to publish your campaign");
      currentStepIndex = 3;
    } else {
      setCurrentStep("Campaign published successfully!");
      currentStepIndex = 4;
    }

    // Update workflow steps based on current step
    setCurrentWorkflow(prev =>
      prev.map((step, idx) => {
        if (idx < currentStepIndex) {
          return { ...step, status: WorkflowStatus.Completed };
        } else if (idx === currentStepIndex) {
          return { ...step, status: WorkflowStatus.InProgress };
        } else {
          return { ...step, status: WorkflowStatus.Pending };
        }
      })
    );

    // Update published campaign state
    const published = campaigns.find(campaign => campaign.type === "published_campaign");
    setPublishedCampaign(published || null);
  }, []);

  // Fetch draft campaigns for a conversation
  const fetchDraftCampaigns = async (conversationId: string) => {
    try {
      const campaigns = await chatService.getDraftCampaigns(conversationId);
      setDraftCampaigns(campaigns);
      
      // Process campaigns to update UI
      updateUIFromDraftCampaigns(campaigns);
    } catch (error) {
      console.error("Error fetching draft campaigns:", error);
    }
  };
  
  // Update UI components based on draft campaigns
  const updateUIFromDraftCampaigns = (campaigns: DraftCampaign[]) => {
    // Process ad copy options
    const adCopyOptions = campaigns
      .filter(campaign => campaign.type === "ad_copy")
      .map(campaign => {
        // Handle potential different formats for ad copy data
        if (typeof campaign.data === 'string') {
          return campaign.data;
        } else if (campaign.data && campaign.data.content) {
          return campaign.data.content;
        } else if (Array.isArray(campaign.data)) {
          return campaign.data.join('\n');
        }
        return "";
      });
    
    // Process image selection
    const imageData = campaigns.find(campaign => campaign.type === "ad_image");
    let selectedImage = generatedContent.selectedImage;
    
    // Handle potential different formats for image data
    if (imageData?.data) {
      if (typeof imageData.data === 'string') {
        selectedImage = imageData.data;
      } else if (imageData.data.url) {
        selectedImage = imageData.data.url;
      } else if (imageData.data.image_url) {
        selectedImage = imageData.data.image_url;
      }
    }
    
    // Update the generated content with new data if available
    if (adCopyOptions.length > 0 || imageData) {
      setGeneratedContent(prev => ({
        adCopyOptions: adCopyOptions.length > 0 ? adCopyOptions : prev.adCopyOptions,
        selectedImage: selectedImage,
      }));
    }
    
    // Update workflow status based on data availability
    updateWorkflowStatus(campaigns);
  };

  // Fetch draft campaigns when conversation ID changes
  useEffect(() => {
    if (currentConversationId) {
      fetchDraftCampaigns(currentConversationId);
    }
  }, [currentConversationId]);

  /**
   * Handles the publishing of a campaign
   */
  const handlePublish = async () => {
    if (selectedAdCopy === null) {
      setCurrentStep("Please select an ad copy option before publishing");
      return Promise.resolve();
    }

    setCurrentStep("Publishing your campaign...");

    return new Promise<void>((resolve) => {
      setTimeout(() => {
        setCurrentWorkflow((prev) =>
          prev.map((step) =>
            step.id === "publish"
              ? { ...step, status: WorkflowStatus.Completed }
              : step,
          ),
        );
        setCurrentStep("Campaign successfully published!");
        resolve();
      }, 3000);
    });
  };

  return (
    <WorkflowContext.Provider
      value={{
        currentWorkflow,
        setCurrentWorkflow,
        currentStep,
        setCurrentStep,
        generatedContent,
        setGeneratedContent,
        selectedAdCopy,
        setSelectedAdCopy,
        handlePublish,
        draftCampaigns,
        fetchDraftCampaigns,
        currentConversationId,
        setCurrentConversationId,
        publishedCampaign,
      }}
    >
      {children}
    </WorkflowContext.Provider>
  );
};
