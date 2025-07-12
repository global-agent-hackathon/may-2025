// src/components/SdkGeneratorForm.tsx
"use client";

import React, { useState } from "react";
import { generateSdk, GenerateSdkResponse } from "@/lib/api";

// Define the type for the SDK configuration
export interface SdkConfig {
  sdkName: string;
  version: string;
  baseUrl: string;
}

// Props for the SdkGeneratorForm component
interface SdkGeneratorFormProps {
  onSdkGenerated: (response: GenerateSdkResponse) => void;
  onLoading: (isLoading: boolean) => void;
  onError: (error: string | null) => void;
  isLoading: boolean; // <--- ADDED THIS PROP
}

// --- NEW: Define interface for example data ---
interface ExampleData {
  name: string; // Display name for the button
  sdkName: string; // Prefills the SDK Name input
  docUrl: string; // Prefills the Documentation URL input
  baseUrl: string; // Prefills the Base URL input
}

// --- UPDATED: Predefined example data - now only JSONPlaceholder ---
const predefinedExamples: ExampleData[] = [
  {
    name: "JSONPlaceholder API",
    sdkName: "JsonPlaceholder",
    docUrl: "https://jsonplaceholder.typicode.com/",
    baseUrl: "https://jsonplaceholder.typicode.com/",
  },
];

export default function SdkGeneratorForm({
  onSdkGenerated,
  onLoading,
  onError,
  isLoading, // <--- ADDED TO DESTRUCTURING
}: SdkGeneratorFormProps) {
  const [sdkName, setSdkName] = useState<string>("");
  const [version, setVersion] = useState<string>("1.0.0");
  const [baseUrl, setBaseUrl] = useState<string>("");
  const [docUrl, setDocUrl] = useState<string>("");
  const [docFile, setDocFile] = useState<File | null>(null);

  // --- NEW: handlePrefill function ---
  const handlePrefill = (example: ExampleData) => {
    setSdkName(example.sdkName);
    setDocUrl(example.docUrl);
    setBaseUrl(example.baseUrl);
    setDocFile(null); // Clear any previously selected file input
    onError(null); // Clear any previous error messages
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    onLoading(true); // Signal parent to start loading
    onError(null); // Clear previous errors

    try {
      if (!sdkName || !version || !baseUrl) {
        throw new Error("Please fill in all SDK configuration fields.");
      }
      if (!docUrl && !docFile) {
        throw new Error(
          "Please provide either a documentation URL or upload a file."
        );
      }

      let docSource:
        | { type: "url"; value: string }
        | { type: "file"; value: File };
      if (docFile) {
        docSource = { type: "file", value: docFile };
      } else if (docUrl) {
        docSource = { type: "url", value: docUrl };
      } else {
        // This case should ideally not happen due to the check above
        throw new Error("No documentation source provided.");
      }

      const config: SdkConfig = { sdkName, version, baseUrl };
      const response = await generateSdk(config, docSource);
      onSdkGenerated(response);
    } catch (error) {
      console.error("SDK generation failed:", error);
      onError((error as Error).message);
    } finally {
      onLoading(false); // Signal parent to stop loading
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-6 bg-gray-800 rounded-lg shadow-md max-w-3xl mx-auto space-y-4"
    >
      <h2 className="text-2xl font-bold text-white mb-4">
        Generate TypeScript SDK
      </h2>

      {/* --- NEW: Quick Try Out Section --- */}
      {/* Checks if there are any predefined examples to display the section */}
      {predefinedExamples.length > 0 && (
        <div className="mb-6 bg-gray-700 p-4 rounded-md">
          <h3 className="text-xl font-semibold text-white mb-3">
            Quick Try Out
          </h3>
          <p className="text-gray-300 text-sm mb-3">
            Effortlessly test Type-Scribe AI by pre-filling the form with
            example API documentation sources.
          </p>
          <div className="flex flex-wrap gap-3">
            {predefinedExamples.map((example, index) => (
              <button
                key={index}
                type="button" // Important: Prevent form submission
                onClick={() => handlePrefill(example)}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md text-sm font-medium transition duration-200 flex-grow sm:flex-grow-0 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isLoading} // Disable while loading
              >
                Try {example.name}
              </button>
            ))}
          </div>
        </div>
      )}
      {/* End Quick Try Out Section */}

      {/* SDK Configuration fields... (existing code) */}
      <div className="space-y-2">
        <label
          htmlFor="sdkName"
          className="block text-sm font-medium text-gray-300"
        >
          SDK Name:
        </label>
        <input
          type="text"
          id="sdkName"
          value={sdkName}
          onChange={(e) => setSdkName(e.target.value)}
          placeholder="e.g., UserServiceSdk"
          className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required
          // MERGED DISABLED LOGIC: Disable if already loading OR docFile is selected from a prior action or a preset
          disabled={isLoading || !!docFile}
        />
      </div>

      <div className="space-y-2">
        <label
          htmlFor="version"
          className="block text-sm font-medium text-gray-300"
        >
          Version:
        </label>
        <input
          type="text"
          id="version"
          value={version}
          onChange={(e) => setVersion(e.target.value)}
          placeholder="e.g., 1.0.0"
          className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required
          // MERGED DISABLED LOGIC
          disabled={isLoading || !!docFile}
        />
      </div>

      <div className="space-y-2">
        <label
          htmlFor="baseUrl"
          className="block text-sm font-medium text-gray-300"
        >
          Base URL:
        </label>
        <input
          type="url"
          id="baseUrl"
          value={baseUrl}
          onChange={(e) => setBaseUrl(e.target.value)}
          placeholder="e.g., https://api.example.com"
          className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required
          // MERGED DISABLED LOGIC
          disabled={isLoading || !!docFile}
        />
      </div>
      {/* Documentation Source */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">
          API Documentation Source:
        </label>
        <div className="flex flex-col md:flex-row md:space-x-4 space-y-4 md:space-y-0">
          <div className="flex-1 space-y-2">
            <label
              htmlFor="docUrl"
              className="block text-xs font-medium text-gray-400"
            >
              Documentation URL (e.g., GitHub README, API docs page):
            </label>
            <input
              type="url"
              id="docUrl"
              value={docUrl}
              onChange={(e) => {
                setDocUrl(e.target.value);
                setDocFile(null); // Clear file selection if URL is used
              }}
              placeholder="https://example.com/api/docs"
              className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              // MERGED DISABLED LOGIC: Disable if loading OR if file is selected
              disabled={isLoading || !!docFile}
            />
          </div>
          <p className="text-gray-400 md:self-center">OR</p>
          <div className="flex-1 space-y-2">
            <label
              htmlFor="docFile"
              className="block text-xs font-medium text-gray-400"
            >
              Upload Documentation File (.md, .pdf, .docx,):
            </label>
            <input
              type="file"
              id="docFile"
              onChange={(e) => {
                setDocFile(e.target.files ? e.target.files[0] : null);
                setDocUrl(""); // Clear URL if file is uploaded
              }}
              accept=".pdf,.docx,.md,"
              className="mt-1 block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-500 file:text-white hover:file:bg-blue-600 cursor-pointer"
              // MERGED DISABLED LOGIC: Disable if loading OR if URL is entered
              disabled={isLoading || !!docUrl}
            />
          </div>
        </div>
      </div>

      {/* Submit button - MODIFIED */}
      <button
        type="submit"
        className={`w-full py-3 px-6 rounded-md text-lg font-semibold transition duration-300 ${
          isLoading
            ? "bg-gray-600 text-gray-400 cursor-not-allowed" // Greyed out when loading
            : "bg-blue-600 hover:bg-blue-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
        }`}
        disabled={isLoading} // <--- USE isLoading PROP TO DISABLE
      >
        {isLoading ? ( // <--- Conditional text based on loading state
          <span className="flex items-center justify-center">
            Generating SDK...
            {/* Simple spinner for visual feedback, customize as needed */}
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </span>
        ) : (
          "Generate SDK"
        )}
      </button>
    </form>
  );
}
