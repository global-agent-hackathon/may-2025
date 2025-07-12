"use client";

import React, { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { dracula } from "react-syntax-highlighter/dist/esm/styles/prism";

interface GeneratedSdkDisplayProps {
  sdkCode: string;
  sdkName: string; // The name of the SDK to use for the file download
  sdkUsageExample: string; // ADDED: The usage example for the SDK
}

export default function GeneratedSdkDisplay({
  sdkCode,
  sdkName,
  sdkUsageExample, // Destructure the new prop
}: GeneratedSdkDisplayProps) {
  const [copiedCode, setCopiedCode] = useState(false); // Renamed for clarity
  const [copiedExample, setCopiedExample] = useState(false); // New state for example copy button

  const handleCopyCode = () => {
    navigator.clipboard.writeText(sdkCode);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000); // Reset "Copied!" message after 2 seconds
  };

  const handleCopyExample = () => {
    navigator.clipboard.writeText(sdkUsageExample);
    setCopiedExample(true);
    setTimeout(() => setCopiedExample(false), 2000); // Reset "Copied!" message after 2 seconds
  };

  const handleDownload = () => {
    const blob = new Blob([sdkCode], { type: "text/typescript" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url || ""; // Add fallback for older TS versions expecting url to be string
    link.download = `${sdkName.toLowerCase().replace(/\s/g, "-")}-sdk.ts`; // Sanitize name for filename
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url); // Clean up the URL object
  };

  if (!sdkCode) {
    return null; // Don't render if no code is provided yet
  }

  return (
    <>
      {" "}
      {/* Used React Fragment to return multiple top-level elements */}
      {/* Generated SDK Code Section */}
      <div className="p-6 bg-gray-900 rounded-lg shadow-md max-w-4xl mx-auto mt-8 w-full">
        <h2 className="text-2xl font-bold text-white mb-4">
          Generated SDK Code
        </h2>
        <div className="flex justify-end space-x-2 mb-4">
          <button
            onClick={handleCopyCode}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium transition duration-200"
          >
            {copiedCode ? "Copied!" : "Copy Code"}
          </button>
          <button
            onClick={handleDownload}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition duration-200"
          >
            Download .ts File
          </button>
        </div>
        <div className="overflow-auto max-h-[600px] rounded-md">
          <SyntaxHighlighter
            language="typescript"
            style={dracula}
            showLineNumbers
            className="!m-0 !p-4 !overflow-visible"
          >
            {sdkCode}
          </SyntaxHighlighter>
        </div>
      </div>
      {/* ADDED: SDK Usage Example Section */}
      {sdkUsageExample && ( // Only render if sdkUsageExample is provided
        <div className="p-6 bg-gray-900 rounded-lg shadow-md max-w-4xl mx-auto mt-8 w-full">
          <h2 className="text-2xl font-bold text-white mb-4">
            SDK Usage Example
          </h2>
          <div className="flex justify-end space-x-2 mb-4">
            <button
              onClick={handleCopyExample}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium transition duration-200"
            >
              {copiedExample ? "Copied!" : "Copy Example"}
            </button>
          </div>
          <div className="overflow-auto max-h-[600px] rounded-md">
            <SyntaxHighlighter
              language="typescript" // Assuming the example is also TypeScript
              style={dracula}
              showLineNumbers
              className="!m-0 !p-4 !overflow-visible"
            >
              {sdkUsageExample}
            </SyntaxHighlighter>
          </div>
        </div>
      )}
    </>
  );
}
