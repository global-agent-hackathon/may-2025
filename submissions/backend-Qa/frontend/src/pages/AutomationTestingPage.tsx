
import React from "react";
import TabsContainer from "@/components/tabs/TabsContainer";
import FeaturePanel from "@/components/shared/FeaturePanel";

const GherkinHelp = () => (
  <div className="space-y-4">
    <p>Gherkin is a language that uses plain language to describe the behavior of software.</p>
    <h4 className="font-semibold">Tips:</h4>
    <ul className="list-disc pl-5 space-y-1">
      <li>Use "Given-When-Then" format</li>
      <li>Keep scenarios focused on one behavior</li>
      <li>Use consistent terminology</li>
      <li>Add examples for data-driven tests</li>
    </ul>
  </div>
);

const SeleniumHelp = () => (
  <div className="space-y-4">
    <p>Selenium is a framework for automated browser testing.</p>
    <h4 className="font-semibold">Tips:</h4>
    <ul className="list-disc pl-5 space-y-1">
      <li>Upload existing manual test cases</li>
      <li>Use specific selectors (IDs are best)</li>
      <li>Include waits for dynamic elements</li>
      <li>Structure tests using Page Object Model</li>
    </ul>
  </div>
);

const ApiTestHelp = () => (
  <div className="space-y-4">
    <p>API testing validates the functionality, reliability, and performance of APIs.</p>
    <h4 className="font-semibold">Tips:</h4>
    <ul className="list-disc pl-5 space-y-1">
      <li>Upload API documentation or swagger files</li>
      <li>Include authentication details if needed</li>
      <li>Test positive and negative scenarios</li>
      <li>Validate response data and status codes</li>
    </ul>
  </div>
);

const AutomationTestingPage = () => {
  const [language, setLanguage] = React.useState<"python" | "java">("python");

  // This function is handled directly in the FeaturePanel component
  // but we can use it for logging or future functionality
  const handleGenerate = (text: string, file?: File) => {
    console.log('Generate with:', text, file, language);
  };

  const tabs = [
    {
      id: "gherkin",
      label: "Gherkin Scenarios",
      content: (
        <FeaturePanel
          title="Gherkin Scenario Generator"
          description="Generate BDD-style Gherkin scenarios from requirements or manual test cases"
          acceptedFileTypes=".docx,.txt,.feature"
          onGenerate={handleGenerate}
          helpContent={<GherkinHelp />}
          agentType="gherkin"
        />
      ),
    },
    {
      id: "selenium",
      label: "Selenium Scripts",
      content: (
        <div>
          <div className="mb-6 flex items-center">
            <span className="mr-4">Output language:</span>
            <div className="flex rounded-md border">
              <button
                onClick={() => setLanguage("python")}
                className={`px-4 py-2 text-sm ${
                  language === "python"
                    ? "bg-primary text-primary-foreground"
                    : "bg-background"
                }`}
              >
                Python
              </button>
              <button
                onClick={() => setLanguage("java")}
                className={`px-4 py-2 text-sm ${
                  language === "java"
                    ? "bg-primary text-primary-foreground"
                    : "bg-background"
                }`}
              >
                Java
              </button>
            </div>
          </div>
          
          <FeaturePanel
            title={`Selenium Script Generator (${language === "python" ? "Python" : "Java"})`}
            description={`Generate ${language} Selenium scripts from manual test cases or Gherkin scenarios`}
            acceptedFileTypes=".docx,.txt,.feature"
            onGenerate={handleGenerate}
            helpContent={<SeleniumHelp />}
            agentType="selenium"
            language={language}
          />
        </div>
      ),
    },
    {
      id: "api-tests",
      label: "API Tests",
      content: (
        <FeaturePanel
          title="API Test Generator"
          description="Create API tests based on API specifications or documentation"
          acceptedFileTypes=".json,.yaml,.txt"
          onGenerate={handleGenerate}
          helpContent={<ApiTestHelp />}
          agentType="api"
        />
      ),
    },
  ];

  return (
    <div>
      <TabsContainer tabs={tabs} defaultTab="gherkin" />
    </div>
  );
};

export default AutomationTestingPage;
