
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Upload, Download, HelpCircle, X } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { generateContent, generateWithFile, downloadFeatureFile, isAgentAvailable } from '@/lib/api';

interface FeaturePanelProps {
  title: string;
  description: string;
  acceptedFileTypes: string;
  onGenerate?: (text: string, file?: File) => void;
  helpContent: React.ReactNode;
  agentType: string;
  language?: string;
}

const FeaturePanel: React.FC<FeaturePanelProps> = ({
  title,
  description,
  acceptedFileTypes,
  onGenerate,
  helpContent,
  agentType,
  language
}) => {
  const [inputText, setInputText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [showHelp, setShowHelp] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadFilename, setDownloadFilename] = useState<string | null>(null);
  
  // Create a ref for the result container to scroll to it
  const resultContainerRef = React.useRef<HTMLDivElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleGenerate = async () => {
    if (!inputText.trim() && !file) {
      toast.error("Please enter text or upload a file");
      return;
    }
    
    // Check if the agent is available
    if (!isAgentAvailable(agentType, language)) {
      let message = "";
      
      if (agentType === "selenium" && language === "java") {
        message = "Java Selenium Script Generator is currently under development. Please use Python for Selenium scripts for now.";
      } else if (agentType === "api") {
        message = "API Test Generator is currently under development. Please check back later.";
      } else {
        message = `This agent is still under construction. Currently, only the Gherkin Generator and Python Selenium Script Generator are available.`;
      }
      
      setResult(message);
      toast.info("This feature is coming soon!");
      return;
    }
    
    setIsGenerating(true);
    setDownloadFilename(null);
    
    try {
      let response;
      
      if (file) {
        // Use file upload endpoint
        response = await generateWithFile(
          file,
          agentType,
          inputText,
          undefined, // featureName
          undefined, // testName
          language
        );
      } else {
        // Use text-only endpoint
        response = await generateContent({
          requirement: inputText,
          agentType: agentType,
          language: language
        });
      }
      
      setResult(response.content);
      
      if (response.filename) {
        setDownloadFilename(response.filename);
      }
      
      toast.success(response.message || "Generated successfully!");
      
      if (onGenerate) {
        onGenerate(inputText, file || undefined);
      }
      
      // Scroll to the result container after a short delay to ensure rendering is complete
      setTimeout(() => {
        if (resultContainerRef.current) {
          resultContainerRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to generate content");
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!result) {
      toast.error("No content to download");
      return;
    }
    
    try {
      if (downloadFilename) {
        // Download the file from the server if we have a filename
        const blob = await downloadFeatureFile(downloadFilename);
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = downloadFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        // Otherwise create a file from the content
        let extension = '.txt';
        
        // Set appropriate file extension based on agent type
        if (agentType === 'gherkin') {
          extension = '.feature';
        } else if (agentType === 'selenium' && language === 'python') {
          extension = '.py';
        } else if (agentType === 'selenium' && language === 'java') {
          extension = '.java';
        } else if (agentType === 'api') {
          extension = '.js';
        }
        
        const blob = new Blob([result], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${title.toLowerCase().replace(/\s+/g, '-')}-result${extension}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
      
      toast.success("Downloaded file successfully");
    } catch (error) {
      toast.error("Failed to download file");
      console.error(error);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2">
        <div className="flex flex-col h-full">
          <div className="mb-6">
            <h2 className="text-2xl font-bold tracking-tight">{title}</h2>
            <p className="text-muted-foreground">{description}</p>
          </div>

          <Card className="mb-6">
            <CardContent className="p-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="file-upload">Upload File</Label>
                  <div className="mt-2 flex items-center gap-2">
                    <Label 
                      htmlFor="file-upload" 
                      className="flex-1 border-2 border-dashed rounded-lg p-4 text-center cursor-pointer hover:border-primary/50 transition-colors"
                    >
                      <Upload className="h-5 w-5 mx-auto mb-2" />
                      <span className="text-sm text-muted-foreground block">
                        {file ? file.name : `Click to upload ${acceptedFileTypes}`}
                      </span>
                      <input
                        id="file-upload"
                        type="file"
                        accept={acceptedFileTypes}
                        className="hidden"
                        onChange={handleFileChange}
                      />
                    </Label>
                    {file && (
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        onClick={() => setFile(null)}
                        aria-label="Remove file"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>

                <div>
                  <Label htmlFor="input-text">Input Text (Optional)</Label>
                  <Textarea
                    id="input-text"
                    className="min-h-32 mt-2"
                    placeholder="Enter your text here..."
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                  />
                </div>

                <Button 
                  onClick={handleGenerate} 
                  className="w-full" 
                  disabled={isGenerating || (!inputText.trim() && !file)}
                >
                  {isGenerating ? "Generating..." : "Generate"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {result && (
            <Card className="flex-1" ref={resultContainerRef}>
              <CardContent className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-medium">Generated Result</h3>
                  <Button variant="outline" size="sm" onClick={handleDownload}>
                    <Download className="h-4 w-4 mr-2" />
                    Download Result
                  </Button>
                </div>
                <div className="bg-muted rounded-lg p-4 h-64 overflow-auto whitespace-pre-wrap">
                  {result}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
      
      {/* Help panel */}
      <div className="md:col-span-1 relative">
        <Card className="sticky top-4">
          <CardContent className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-medium flex items-center gap-2">
                <HelpCircle className="h-5 w-5" />
                <span>Help & Tips</span>
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHelp(!showHelp)}
                className="md:hidden"
              >
                {showHelp ? 'Hide' : 'Show'}
              </Button>
            </div>
            <div className={`space-y-4 ${showHelp ? '' : 'hidden md:block'}`}>
              {helpContent}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default FeaturePanel;
