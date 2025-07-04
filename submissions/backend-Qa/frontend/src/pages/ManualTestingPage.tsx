
import React from "react";
import TabsContainer from "@/components/tabs/TabsContainer";
import FeaturePanel from "@/components/shared/FeaturePanel";

const TestPlanningHelp = () => (
  <div className="space-y-4">
    <p>Test planning is the process of defining the testing approach, resources, and schedule for testing a software application.</p>
    <h4 className="font-semibold">Tips:</h4>
    <ul className="list-disc pl-5 space-y-1">
      <li>Upload existing test plans or requirements</li>
      <li>Include project scope and testing objectives</li>
      <li>Define test schedule and resources</li>
      <li>Include risk assessment in your planning</li>
    </ul>
  </div>
);

const TestCasesHelp = () => (
  <div className="space-y-4">
    <p>Manual test cases are step-by-step instructions for testing application functionality without automation.</p>
    <h4 className="font-semibold">Tips:</h4>
    <ul className="list-disc pl-5 space-y-1">
      <li>Include clear prerequisites</li>
      <li>Write specific, detailed steps</li>
      <li>Define expected results for each step</li>
      <li>Include test data requirements</li>
      <li>Describe your user story or requirements in detail</li>
    </ul>
  </div>
);

const ManualTestingPage = () => {
  // The generation is now handled directly in the FeaturePanel component
  // This is just for logging purposes
  const handleGenerate = (text: string, file?: File) => {
    console.log('Manual testing generation requested with:', text, file);
  };

  const tabs = [
    {
      id: "test-planning",
      label: "Test Planning",
      content: (
        <FeaturePanel
          title="Test Planning Generator"
          description="Generate comprehensive test plans based on project requirements and specifications"
          acceptedFileTypes=".docx,.pdf,.txt"
          onGenerate={handleGenerate}
          helpContent={<TestPlanningHelp />}
          agentType="manual_planning"
        />
      ),
    },
    {
      id: "test-cases",
      label: "Manual Test Cases",
      content: (
        <FeaturePanel
          title="Test Case Generator"
          description="Create detailed manual test cases with step-by-step instructions"
          acceptedFileTypes=".docx,.pdf,.txt,.xlsx"
          onGenerate={handleGenerate}
          helpContent={<TestCasesHelp />}
          agentType="manual_testcases"
        />
      ),
    },
  ];

  return (
    <div>
      <TabsContainer tabs={tabs} defaultTab="test-planning" />
    </div>
  );
};

export default ManualTestingPage;
