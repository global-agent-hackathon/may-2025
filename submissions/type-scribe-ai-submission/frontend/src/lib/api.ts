import { SdkConfig } from "@/components/SdkGeneratorForm"; // Using @ alias for convenience
import { stripIndent } from "common-tags"; // Useful for formatting template literals

// Define the shape of the SDK generation response from the backend
export interface GenerateSdkResponse {
  sdk_code: string;
  message: string;
  sdk_usage_example?: string; // ADDED: New field for SDK usage example
}

// Function to call the backend and generate the SDK
export async function generateSdk(
  config: SdkConfig,
  docSource: { type: "url"; value: string } | { type: "file"; value: File }
): Promise<GenerateSdkResponse> {
  let backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!backendUrl) {
    backendUrl = "https://type-scribe-ai-407817572230.europe-west1.run.app/";
    // setting it this way because of cloud run NEXT_PUBLIC bug
  }
  if (!backendUrl) {
    throw new Error(
      "NEXT_PUBLIC_BACKEND_URL is not defined in environment variables."
    );
  }

  const formData = new FormData();
  formData.append("sdk_name", config.sdkName);
  formData.append("version", config.version);
  formData.append("base_url", config.baseUrl);

  if (docSource.type === "url") {
    formData.append("doc_url", docSource.value);
  } else {
    formData.append("doc_file", docSource.value);
  }

  try {
    const response = await fetch(`${backendUrl}/generate-sdk`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      // Attempt to parse JSON error message from backend
      const errorData = await response
        .json()
        .catch(() => ({ detail: "Unknown error" }));
      throw new Error(
        stripIndent`
          Backend error: ${response.status} ${response.statusText}
          Details: ${JSON.stringify(errorData, null, 2)}
        `
      );
    }

    const data: GenerateSdkResponse = await response.json();
    return data;
  } catch (error) {
    // Log more details for debugging internally
    console.error("API call failed:", error);
    // Re-throw a more user-friendly error
    throw new Error(`Failed to generate SDK: ${(error as Error).message}`);
  }
}
