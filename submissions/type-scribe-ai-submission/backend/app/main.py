from typing import Optional  # FIX: Added import for Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import asyncio
import base64
import mimetypes
import logging

# Graphlit imports
from graphlit import Graphlit
from graphlit_api import input_types, enums, exceptions

# Agno imports
from agno.agent import Agent
from agno.models.google import Gemini  # Ensure Gemini is imported
from agno.team import Team

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Type-Scribe AI Backend",
    description="Generates TypeScript SDKs from API documentation using AI agents.",
)

origins = [
    "http://localhost:3000",
    "https://type-scribe-ai-frontend-407817572230.europe-west1.run.app",
    "https://-production-domain.oof",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Graphlit client instance
# Initialized on startup event, so it's ready for requests
graphlit_client_instance: Graphlit = None


@app.on_event("startup")
async def startup_event():
    """
    Initializes the Graphlit client when the FastAPI application starts up.
    This ensures the client is ready before any API requests are processed.
    """
    global graphlit_client_instance
    try:
        graphlit_client_instance = Graphlit(
            organization_id=os.getenv("GRAPHLIT_ORGANIZATION_ID"),
            environment_id=os.getenv("GRAPHLIT_ENVIRONMENT_ID"),
            jwt_secret=os.getenv("GRAPHLIT_JWT_SECRET"),
        )
        # Optional: Verify connection by making a small Graphlit API call
        # await graphlit_client_instance.client.query_whoami() # Uncomment for verbose startup check
        logger.info("Graphlit client initialized successfully on startup.")
    except Exception as e:
        logger.error(
            f"Failed to initialize Graphlit client: {str(e)}"
        )  # Using str(e) for broader compatibility
        raise RuntimeError(
            "Failed to initialize Graphlit client. Exiting."
        )  # Critical failure


# Pydantic models for API requests/responses
class SdkConfig(BaseModel):
    sdk_name: str = Field(
        ..., description="Name of the SDK to be generated (e.g., 'MyApiSdk')"
    )
    version: str = Field(..., description="Version of the SDK (e.g., '1.0.0')")
    base_url: str = Field(
        ..., description="Base URL of the API (e.g., 'https://api.example.com/v1')"
    )


class GenerateSdkResponse(BaseModel):
    sdk_code: str = Field(..., description="Generated TypeScript SDK code")
    sdk_usage_example: str = Field(
        ..., description="Example code demonstrating the usage of the generated SDK"
    )  # NEW FIELD!
    message: str = Field(
        ..., description="Status message for the SDK generation process"
    )


# --- Graphlit Helper Functions ---


async def get_graphlit_client():
    """
    Returns the initialized Graphlit API client.
    Raises HTTPException if the client is not properly initialized.
    """
    if not graphlit_client_instance or not graphlit_client_instance.client:
        raise HTTPException(
            status_code=500,
            detail="Graphlit client not initialized. Check backend logs for errors related to GRAPHLIT_ environment variables.",
        )
    return graphlit_client_instance.client


async def get_or_create_graphlit_workflow(client):
    """
    Ensures a Graphlit workflow for Azure AI Document Intelligence preparation exists or creates one.
    """
    workflow_name = "ApiDocTextExtractionWorkflow"
    try:
        workflows = await client.query_workflows(
            filter=input_types.WorkflowFilter(name=workflow_name)
        )
        if workflows and workflows.workflows and workflows.workflows.results:
            logger.info(
                f"Reusing existing Graphlit workflow: {workflow_name} (ID: {workflows.workflows.results[0].id})"
            )
            return workflows.workflows.results[0].id

        # If workflow doesn't exist, create it.
        # Directly define the FilePreparationConnectorInput for Azure Document Intelligence within the workflow.
        # No separate 'SpecificationInput' of type 'PREPARATION' for Azure Document Intelligence is needed here.
        workflow_input = input_types.WorkflowInput(
            name=workflow_name,
            preparation=input_types.PreparationWorkflowStageInput(
                jobs=[
                    input_types.PreparationWorkflowJobInput(
                        connector=input_types.FilePreparationConnectorInput(
                            type=enums.FilePreparationServiceTypes.AZURE_DOCUMENT_INTELLIGENCE,
                            azureDocument=input_types.AzureDocumentPreparationPropertiesInput(
                                model=enums.AzureDocumentIntelligenceModels.LAYOUT  # Standard model for layout extraction
                            ),
                        )
                    )
                ]
            ),
        )
        response = await client.create_workflow(workflow_input)
        logger.info(
            f"Created Graphlit workflow: {workflow_name} (ID: {response.create_workflow.id})"
        )
        return response.create_workflow.id
    except exceptions.GraphQLClientError as e:
        logger.error(
            f"Graphlit API error during workflow creation: {str(e.errors)}"
        )  # Access .errors attribute for multi-errors
        raise HTTPException(
            status_code=500,
            detail=f"Graphlit API error during workflow creation: {str(e.errors)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error during Graphlit workflow setup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Backend error during Graphlit workflow setup: {str(e)}",
        )


async def ingest_document_with_graphlit(
    client,
    doc_name: str,
    doc_uri: Optional[str] = None,
    file_content: Optional[bytes] = None,
    mime_type: Optional[str] = None,
):
    """
    Ingests documentation into Graphlit, either from a URL or an uploaded file.
    Applies a pre-configured workflow for text extraction.
    """
    workflow_id = await get_or_create_graphlit_workflow(client)

    try:
        content_id = None
        if doc_uri:
            logger.info(f"Ingesting URL document '{doc_uri}' into Graphlit...")
            response = await client.ingest_uri(
                uri=doc_uri,
                workflow=input_types.EntityReferenceInput(id=workflow_id),
                is_synchronous=True,
            )
            content_id = response.ingest_uri.id
        elif file_content:  # MIME type is now handled robustly before this call
            logger.info(
                f"Ingesting uploaded file '{doc_name}' (MIME: {mime_type}) into Graphlit..."
            )
            # FIX: Corrected typo from b64enocode to b64encode
            base64_content = base64.b64encode(file_content).decode("utf-8")
            response = await client.ingest_encoded_file(
                name=doc_name,
                data=base64_content,
                mime_type=mime_type,
                workflow=input_types.EntityReferenceInput(id=workflow_id),
                is_synchronous=True,
            )
            content_id = response.ingest_encoded_file.id
        else:
            raise HTTPException(
                status_code=400,
                detail="Either doc_url or uploaded file content is required for ingestion.",
            )

        if not content_id:
            raise HTTPException(
                status_code=500,
                detail="Graphlit ingestion failed to return a content ID.",
            )

        logger.info(
            f"Documentation ingested into Graphlit with content ID: {content_id}"
        )
        return content_id
    except exceptions.GraphQLClientError as e:
        # Access .errors attribute for GraphQLClientGraphQLMultiError to get details
        logger.error(
            f"Graphlit API error during ingestion: {str(e.errors) if hasattr(e, 'errors') else str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Graphlit API error during ingestion: {str(e.errors) if hasattr(e, 'errors') else str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error during Graphlit ingestion: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Backend error during ingestion: {str(e)}"
        )


async def get_content_markdown_from_graphlit(client, content_id: str):
    """
    Retrieves the markdown content of an ingested document from Graphlit.
    This content is generated as part of the ingestion workflow.
    """
    try:
        content_details = await client.get_content(content_id)
        if (
            not content_details
            or not content_details.content
            or not content_details.content.markdown
        ):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve markdown content for ID {content_id} from Graphlit. Content might not be processed yet, or is empty.",
            )
        return content_details.content.markdown
    except exceptions.GraphQLClientError as e:
        logger.error(
            f"Graphlit API error retrieving content: {str(e.errors) if hasattr(e, 'errors') else str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Graphlit API error retrieving content: {str(e.errors) if hasattr(e, 'errors') else str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving Graphlit content: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Backend error retrieving content: {str(e)}"
        )


# --- MODIFICATION START: New helper function for usage example generation (Optimized Prompt & Fixed Fallback String) ---
async def generate_sdk_usage_example(
    sdk_code: str, sdk_name: str, base_url: str
) -> str:
    """
    Generates a TypeScript usage example for the given SDK code using a dedicated Agno AI agent.
    """
    try:
        model = Gemini(id="gemini-2.0-flash-001")
        usage_agent = Agent(
            model=model,
            instructions="You are an expert TypeScript developer assistant. Your task is to provide a comprehensive, concise, and clear usage example for a given TypeScript SDK. The example should be pure TypeScript code, ready to run, and should not include the SDK class definition itself. Focus on demonstrating each method with appropriate error handling and console logging.",
        )

        # Optimized prompt for the usage agent
        prompt = f"""
        Generate a standalone, functional TypeScript usage example for the following SDK code, named '{sdk_name}' with base URL '{base_url}'.

        The example must:
        - Instantiate the SDK class (`const sdk = new {sdk_name}('{base_url}');`).
        - Demonstrate at least one GET method call (e.g., fetching all items or a specific item).
        - Demonstrate at least one POST/PUT/DELETE method call if applicable (creating/updating/deleting resources). If no such method is apparent, omit this part.
        - Use `async/await` for all asynchronous operations.
        - Implement basic `try...catch` for error handling around API calls.
        - Log results to the console (`console.log`).

        Output ONLY the TypeScript code, with no additional text, explanations, or markdown fences. The code should be ready to run in a typical Node.js or browser environment (assuming `fetch` API is available).

        SDK Code:
        ```typescript
        {sdk_code}
        ```

        Generate a standalone, functional TypeScript code snippet that clearly demonstrates the usage of **each distinct method** within this SDK class.

        For each method or a small logical group of interdependent methods:
        - Call the method with appropriate dummy/example arguments.
        - Wrap the method call in its **own, independent `try...catch` block** to demonstrate isolated error handling.
        - Log the successful result (or error) to the console using `console.log`.
        - Ensure all calls use `async/await` syntax.
        - Do NOT include the SDK class definition itself in your output; **only** the usage demonstration.
        - The code should be contained within a single `main` async function that is then called, similar to:
          ```typescript
          async function main() {{
            const sdk = new {sdk_name}('{base_url}');
            // Your method demonstrations here
          }}
          main();
          ```
        - Do NOT include any introductory or concluding conversational text, explanations, or markdown fences outside of the TypeScript code itself. The output must be pure, executable TypeScript.
        """
        logger.info("Generating SDK usage example using Agno agent...")
        # Get the response from the usage agent
        response = await usage_agent.arun(prompt)

        logger.info("SDK usage example generated successfully.")
        return response.content.strip()

    except Exception as e:
        logger.error(f"Error generating SDK usage example: {e}")
        # Optimized and fixed fallback f-string for simplicity
        return f"""Error generating usage example."""


# --- MODIFICATION END: New helper function for usage example generation (Optimized Prompt & Fixed Fallback String) ---


# --- Agno Agents and Orchestration ---

# API Understanding Agent: Gemini-powered to understand API docs
# This agent takes raw documentation and outputs structured API schema (JSON)
api_understanding_agent = Agent(
    name="API Understanding Agent",
    description="Analyzes API documentation content to meticulously extract endpoints, HTTP methods, route paths, request parameters (including their type, required status, and location like query/path/body), and detailed response schemas with explicit TypeScript-compatible data types. It infers types when not explicit, favoring 'string', 'number', 'boolean', 'array', or detailed nested structures. This agent's output is structured JSON, optimized for direct consumption by the SDK Generation Agent.",
    model=Gemini(
        id="gemini-2.0-flash-001"
    ),  # Powerful model for complex understanding and JSON formatting
    instructions=[
        "Your sole task is to process API documentation. Extract all API endpoints, their HTTP methods (GET, POST), their full route paths, request parameters (distinguishing between path, query, and request body parameters, specifying if they are required, and inferring precise data types like 'string', 'number', 'boolean', 'array of string', 'object' etc.), and detailed response structures.",
        "Represent complex data types and objects as nested JSON schemas within the response. For example, if a response contains a 'User' object, define its properties and their types within. If a parameter is an array, specify the type of items in the array (e.g., 'array of string', 'array of object (with ... properties)').",
        "If a data type is not explicitly stated, infer it based on naming conventions or common API patterns. For example, 'id' or 'count' often imply 'number', 'name' or 'description' imply 'string'.",
        "The output must be a single, valid, comprehensive JSON object that explicitly details the entire API structure. Do NOT include any conversational text, explanations, or extraneous characters outside the JSON.",
        "Example structured JSON output (simplified):",
        "```json",
        "{",
        '  "endpoints": [',
        "    {",
        '      "path": "/users/{userId}",',
        '      "method": "GET",',
        '      "summary": "Retrieve a user by ID.",',
        '      "parameters": [',
        '        {"name": "userId", "in": "path", "type": "string", "required": true, "description": "ID of the user to retrieve."}',
        "      ],",
        '      "response_schema": {',
        '        "id": "string",',
        '        "name": "string",',
        '        "email": "string"',
        "      }",
        "    },",
        "    {",
        '      "path": "/products",',
        '      "method": "POST",',
        '      "summary": "Create a new product.",',
        '      "parameters": [',
        '        {"name": "name", "in": "body", "type": "string", "required": true, "description": "Name of the product."},',
        '        {"name": "price", "in": "body", "type": "number", "required": true, "description": "Price of the product."}',
        "      ],",
        '      "response_schema": {',
        '        "id": "string",',
        '        "name": "string"',
        "      }",
        "    }",
        "  ]",
        "}",
        "```",
        "Strictly adhere to this JSON format and content. If a property like 'summary' is not inferable, omit it from the JSON. If the documentation is insufficient for an endpoint, return an empty `{\"endpoints\": []}`.",
        "Do not include any conversational text or setup instructions.",
    ],
)

# SDK Generation Agent: Gemini-powered to generate TypeScript SDK code
# This agent takes structured API schema (JSON) and converts it to TypeScript code
sdk_generation_agent = Agent(
    name="SDK Generation Agent",
    description="Generates a complete, functional, and type-safe TypeScript SDK from a provided structured API schema (JSON) and SDK configuration. Automatically includes necessary HTTP request logic using Fetch API, interface definitions, and client methods.",
    model=Gemini(id="gemini-2.0-flash-001"),  # Powerful model for code generation
    instructions=[
        "You are a highly skilled TypeScript SDK developer. Your task is to generate a full TypeScript SDK based on a JSON-formatted API schema and SDK configuration details. The SDK should be self-contained in a single `.ts` file.",
        "**Your entire response MUST consist ONLY of the TypeScript code.**",
        "DO NOT include any preparatory text, conversational remarks, or explanations outside of the code block.",
        """For example, do not say "Here is the code:" or "Okay, I have generated it.""",
        "It must include:",
        "1.  **TypeScript Interfaces:** Create interfaces for all request and response payloads based on the JSON schema. Use standard TypeScript types (`string`, `number`, `boolean`, `Date`, etc.). Represent nested objects and arrays correctly (`Array<Type>`, `key: Type`).",
        "2.  **Main SDK Class:** Create a class named dynamically (e.g., `MyApiSdk`) that encapsulates all API interactions. Its constructor should accept the `base_url` for the API.",
        "3.  **Client Methods:** For each API endpoint defined in the schema, create an asynchronous method within the SDK class. These methods should:",
        "    *   Use the `fetch` API for HTTP requests (`GET`, `POST`, `PUT`, `DELETE`, etc.).",
        "    *   Correctly handle path parameters (e.g., `/users/{userId}`), query parameters, and request body parameters.",
        "    *   Parse JSON responses. Handle success and potential error responses based on HTTP status codes.",
        "    *   Return a Promise resolving to the appropriate TypeScript interface for the response.",
        "    *   Have proper JSDoc comments explaining parameters and return types.",
        "4.  **No Boilerplate/Conversation:** Output ONLY the TypeScript `.ts` file content. Do NOT include any conversational text, explanations, markdown comments, or setup instructions outside of the TypeScript code itself. The output must be directly savable to a `.ts` file and compile without errors.",
        "5.  **SDK Configuration:** Integrate the provided `sdk_name` for class naming, `version` (optional, for comments if desired), and `base_url` for API calls.",
        "6.  **Example Template for a simple SDK:**",
        "```typescript",
        "// types.ts",
        "interface User {",
        "  id: string;",
        "  name: string;",
        "}",
        "// api.ts",
        "class MyApiSdk {",
        "  private baseUrl: string;",
        "  constructor(baseUrl: string) {",
        "    this.baseUrl = baseUrl;",
        "  }",
        "  async getUser(userId: string): Promise<User> {",
        "    const response = await fetch(`${this.baseUrl}/users/${userId}`);",
        "    if (!response.ok) {",
        "      throw new Error(`Error fetching user: ${response.statusText}`);",
        "    }",
        "    return response.json();",
        "  }",
        "}",
        "```",
        "Strictly adhere to this template and best practices for TypeScript. Ensure type safety and error handling with `try...catch` for network requests if applicable. Aim for an SDK that can be directly imported and used in a TypeScript project.",
    ],
)

# Orchestration Team: Coordinates API understanding and SDK generation
# This team acts as the central orchestrator of the entire SDK generation pipeline.
# It ensures sequential execution from documentation ingestion to final code output.
sdk_generation_team = Team(
    members=[api_understanding_agent, sdk_generation_agent],
    mode="coordinate",  # 'coordinate' mode is best for sequential task execution and delegation
    model=Gemini(
        id="gemini-2.0-flash-001"
    ),  # Team leader uses a powerful Gemini model for robust coordination.
    instructions=[
        "Your core objective is to generate a fully functional TypeScript SDK from provided raw API documentation.",
        "**Phase 1: API Schema Extraction.**",
        "  - Your first action is to delegate to the 'API Understanding Agent'.",
        "  - Provide the 'API Understanding Agent' with the raw API documentation content.",
        "  - It is critical that the 'API Understanding Agent' returns a **perfectly valid JSON string** representing the API schema. Do NOT proceed if the output is not valid JSON.",
        "**Phase 2: SDK Code Generation.**",
        "  - Once you have the validated JSON schema from the 'API Understanding Agent', immediately delegate to the 'SDK Generation Agent'.",
        "  - Provide the 'SDK Generation Agent' with the JSON API schema and the SDK configuration details (SDK Name, Version, Base URL).",
        "  - The 'SDK Generation Agent' MUST return the complete, ready-to-use TypeScript SDK code as a string. This will be your final output.",
        "Your final response to the user must ONLY be the generated TypeScript SDK code. Do not include any conversational text or setup instructions. The code must be directly usable.",
    ],
)

# --- FastAPI Endpoints ---


@app.post(
    "/generate-sdk", response_model=GenerateSdkResponse
)  # Ensure response_model is updated
async def generate_sdk_endpoint(
    # SDK Configuration details as Form data (for multipart/form-data support with files)
    sdk_name: str = Form(
        ..., description="Name of the SDK to be generated (e.g., 'MyApiSdk')"
    ),
    version: str = Form(..., description="Version of the SDK (e.g., '1.0.0')"),
    base_url: str = Form(
        ..., description="Base URL of the API (e.g., 'https://api.example.com/v1')"
    ),
    # API Documentation source
    doc_url: Optional[str] = Form(
        None,
        description="URL to the API documentation (e.g., a README.md on GitHub, or a web page)",
    ),
    doc_file: Optional[UploadFile] = File(
        None,
        description="Optional: Upload a documentation file (e.g., README.md, .docx, .pdf) directly.",
    ),
) -> GenerateSdkResponse:
    """
    Initiates the TypeScript SDK generation process using AI agents.
    Accepts API documentation via a URL or an uploaded file, along with SDK configuration details.
    """

    if not doc_url and not doc_file:
        raise HTTPException(
            status_code=400,
            detail="No API documentation provided. Please provide either a URL for the documentation or upload a file.",
        )

    client = await get_graphlit_client()
    content_id = None

    try:
        # Step 1: Ingest documentation using Graphlit
        if doc_url:
            logger.info(f"Received documentation URL for ingestion: {doc_url}")
            content_id = await ingest_document_with_graphlit(
                client, doc_name=sdk_name, doc_uri=doc_url
            )
        elif doc_file:  # MIME type is now handled robustly before this call
            # Read file content
            file_content = await doc_file.read()

            determined_mime_type = doc_file.content_type
            file_name_original = (
                doc_file.filename
            )  # Get the original filename to guess from

            # --- START of improved MIME type inference ---
            # If the content type is generic or missing, try to guess from the filename
            if (
                determined_mime_type == "application/octet-stream"
                or not determined_mime_type
            ):
                guessed_from_filename = mimetypes.guess_type(file_name_original)[0]
                if guessed_from_filename:
                    determined_mime_type = guessed_from_filename
                else:
                    # Fallback for common documentation types if mimetypes.guess_type fails
                    if file_name_original.lower().endswith(".md"):
                        determined_mime_type = "text/markdown"
                    elif file_name_original.lower().endswith(".txt"):
                        determined_mime_type = "text/plain"
                    elif file_name_original.lower().endswith(".pdf"):
                        determined_mime_type = "application/pdf"
                    elif file_name_original.lower().endswith(".docx"):
                        determined_mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    elif file_name_original.lower().endswith(".pptx"):
                        determined_mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    else:
                        logger.warning(
                            f"Could not determine specific MIME type for '{file_name_original}'. Falling back to application/octet-stream, which Graphlit might not infer directly. Consider adding this file type to inference logic."
                        )
                        determined_mime_type = (
                            "application/octet-stream"  # Last resort for unknown types
                        )
            # --- END of improved MIME type inference ---

            logger.info(
                f"Received uploaded file '{file_name_original}' (MIME: {determined_mime_type}) for ingestion."
            )
            content_id = await ingest_document_with_graphlit(
                client,
                doc_name=file_name_original,
                file_content=file_content,
                mime_type=determined_mime_type,
            )

        if not content_id:
            raise HTTPException(
                status_code=500,
                detail="Graphlit ingestion failed to return a content ID. This may indicate an issue with Graphlit service or provided credentials/document.",
            )

        # Step 2: Retrieve the processed markdown content from Graphlit
        # Graphlit's workflow will have processed the raw document into a readable markdown format.
        raw_doc_content = await get_content_markdown_from_graphlit(client, content_id)
        if not raw_doc_content.strip():
            raise HTTPException(
                status_code=500,
                detail="Retrieved empty or invalid documentation content from Graphlit. Ensure the document contains readable text.",
            )

        logger.info(
            "Raw documentation fetched from Graphlit. Starting Agno agent orchestration for SDK generation..."
        )

        # Prepare the initial prompt for the Agno team, including both the raw content and SDK config.
        # The team will then delegate to the API Understanding Agent.
        team_initial_input = f"""
        Below is the API documentation content and the desired SDK configuration.
        Your task is to first extract the API schema from this documentation, and then generate a TypeScript SDK.

        --- API Documentation Content ---
        {raw_doc_content}
        -------------------------------

        --- SDK Configuration ---
        SDK Name: {sdk_name}
        SDK Version: {version}
        API Base URL: {base_url}
        -------------------------

        Please begin by extracting the API schema.
        """

        # Run the Agno orchestration team asynchronously
        # The team's instructions will guide the flow between `api_understanding_agent` and `sdk_generation_agent`.
        team_result = await sdk_generation_team.arun(team_initial_input)
        generated_sdk_code = (
            team_result.content
        )  # The final content from the team should be the SDK code

        if not generated_sdk_code or not any(
            kw in generated_sdk_code for kw in ["interface", "class", "async", "fetch"]
        ):
            logger.error(
                f"Generated SDK code is empty or does not resemble TypeScript. Partial output: {generated_sdk_code[:1000]}..."
            )
            raise HTTPException(
                status_code=500,
                detail="SDK generation failed or returned invalid TypeScript code. This might indicate issues with the API documentation or the LLM's understanding/generation capabilities. Check backend logs for more details.",
            )

        logger.info("TypeScript SDK generated successfully by Agno agents.")

        # --- MODIFICATION START: Generate usage example after main SDK generation ---
        usage_example = await generate_sdk_usage_example(
            sdk_code=generated_sdk_code, sdk_name=sdk_name, base_url=base_url
        )
        logger.info("SDK usage example generated successfully.")
        # --- MODIFICATION END ---

        return GenerateSdkResponse(
            sdk_code=generated_sdk_code,
            sdk_usage_example=usage_example,
            message=f"TypeScript SDK generated successfully! SDK Name: {sdk_name}",
        )

    except HTTPException:
        raise  # Re-raise if it's already an HTTPException, no further handling needed here
    except Exception as e:
        logger.exception(
            f"An unexpected error occurred during SDK generation process: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected internal server error occurred: {str(e)}. Please check backend logs for more details.",
        )


@app.get("/")
async def root():
    """
    Root endpoint for health checks.
    """
    return {"message": "Type-Scribe AI Backend is running!"}
