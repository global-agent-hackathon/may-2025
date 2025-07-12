// src/app/page.tsx
"use client";

import React, { useState } from "react";
import SdkGeneratorForm from "@/components/SdkGeneratorForm";
import GeneratedSdkDisplay from "@/components/GeneratedSdkDisplay";
import LoadingIndicator from "@/components/LoadingIndicator"; // <--- IMPORT NEW COMPONENT
import { GenerateSdkResponse } from "@/lib/api";

export default function HomePage() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedSdk, setGeneratedSdk] = useState<GenerateSdkResponse | null>(
    null
  );

  // Removed loadingMessageIndex, loadingMessages, didYouKnowIndex, didYouKnowFacts, useEffect related to these

  const handleSdkGenerated = (response: GenerateSdkResponse) => {
    setGeneratedSdk(response);
  };

  function sdkNameForDownload(initialName: string): string {
    return initialName.endsWith("Sdk") ? initialName : `${initialName}Sdk`;
  }

  const currentSdkName = generatedSdk
    ? sdkNameForDownload(
        generatedSdk.message.split("SDK Name: ")[1]?.split(" ")[0] ||
          "generated-sdk"
      )
    : "";

  return (
    <main className="container mx-auto p-4 md:p-8 min-h-screen flex flex-col justify-center items-center">
      <h1 className="text-4xl font-extrabold text-white mb-8 text-center">
        Type-Scribe AI
      </h1>
      <p className="text-xl text-gray-300 mb-10 text-center max-w-3xl">
        Automate the creation of TypeScript API SDKs from documentation using
        intelligent AI agents.
      </p>
      {/* Loading Indicator - Now a separate component */}
      <LoadingIndicator isLoading={loading} />{" "}
      {/* <--- USE NEW COMPONENT HERE */}
      {/* Error Message */}
      {error && (
        <div className="error-message">
          <p className="font-bold">Error:</p>
          <p className="text-sm break-words">{error}</p>
          <p className="text-xs mt-2">
            Please check your input or backend logs.
          </p>
        </div>
      )}
      {/* Success Message */}
      {generatedSdk?.message && !loading && !error && (
        <div className="success-message">
          <p className="font-bold">Success!</p>
          <p className="text-sm">{generatedSdk.message}</p>
        </div>
      )}
      {/* SDK Generator Form */}
      <SdkGeneratorForm
        onSdkGenerated={handleSdkGenerated}
        onLoading={setLoading}
        onError={setError}
        isLoading={loading}
      />
      {/* Display Generated SDK Code */}
      {generatedSdk && (
        <GeneratedSdkDisplay
          sdkCode={generatedSdk.sdk_code}
          sdkName={currentSdkName}
          sdkUsageExample={generatedSdk.sdk_usage_example || ""}
        />
      )}
    </main>
  );
}
