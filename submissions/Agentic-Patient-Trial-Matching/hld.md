**High-Level Design Document: AI-Powered Clinical Trial Matching**

**1. Introduction**

This document outlines the high-level design for an AI-powered Clinical Trial Matching system. The goal is to provide clinicians with an integrated tool within their existing workflow (e.g., EHR or clinical dashboard) that leverages agentic AI and Generative AI (via Langchain) to automatically identify potentially relevant clinical trials for a specific patient. The system will present ranked matches, rationale for the match, and links to further details, significantly reducing manual search effort and improving access to research opportunities.

**2. Goals**

*   Provide an automated mechanism for clinicians to initiate clinical trial searches for specific patients (CTM-F01).
*   Leverage AI agents to fetch and process patient data and clinical trial protocols.
*   Utilize AI (specifically NLP and reasoning capabilities via Langchain) to match patient profiles against trial eligibility criteria (CTM-F04).
*   Display a clear, ranked list of potential, actively recruiting trial matches within the clinician's workflow (CTM-F03).
*   Present concise reasons why a trial is suggested and highlight potential uncertainties (CTM-F04).
*   Provide easy access to full trial details (e.g., links to ClinicalTrials.gov) (CTM-F05).
*   Inform the clinician clearly if no matches are found or if an error occurs (CTM-F06, CTM-F07).
*   Ensure the system is performant, reliable, secure (HIPAA compliant), and accurate enough to be clinically useful (CTM-NF01, NF02, NF04, NF05).
*   Integrate seamlessly into the existing clinical application (CTM-NF03, NF06).

**3. Non-Goals**

*   Patient enrollment into trials.
*   Replacing the clinician's final judgment on trial suitability.
*   Providing medical advice.
*   Real-time trial status updates beyond what's available in source databases at the time of query.
*   Managing trial logistics or patient communication post-identification.

**4. Actors**

*   **Clinician:** The primary user who interacts with the system via the frontend interface to find trials for their patient.

**5. System Architecture**

```mermaid
graph LR
    subgraph "Clinical Workflow System "
        A[Clinician UI] --> B[React Frontend Component];
    end

    subgraph "AI Trial Matching Service Backend"
        C[Backend API Gateway Python: FastAPI Flask];
        D[AI Orchestration Layer PythonLangchain];
        E[Patient Data Agent];
        F[Trial Discovery Agent];
        G[Matching & Eligibility Agent];
        H{Cache Optional: Redis Memcached};
    end

    subgraph "External Systems"
        I[EHRPatient Data Store API DB];
        J[ClinicalTrials.gov API];
        K[Other Trial Databases API DB];
        L[LLM Provider];
    end

    B -- 1. Initiate Search PatientID --> C;
    C -- 2. Request Patient Data --> E;
    E -- 3. Fetch Data --> I;
    I -- 4. Return Patient Data --> E;
    E -- 5. Processed Patient Profile --> D;
    C -- 6. Request Trial Discovery --> F;
    F -- 7. Query Trials --> J;
    F -- 8. Query Trials --> K;
    J -- 9. Trial List --> F;
    K -- 10. Trial List --> F;
    F -- 11. Potential Trials & Protocols --> D;
    D -- 12. Request Matching Profile and Trials --> G;
    G -- 13. Parse Analyze Protocols using LLM --> L;
    L -- 14. Analysis Results --> G;
    G -- 15. Perform Matching Logic --> D;
    D -- 16. Check or Store or Retrieve Cache --> H;
    H -- 17. Cached Data - Optional --> D;
    D -- 18. Formatted Results or Status --> C;
    C -- 19. Results or Status Response --> B;

    %% Styling
    style A fill:#f9f,stroke:#333,stroke-width:2px;
    style B fill:#ccf,stroke:#333,stroke-width:2px;
    style C fill:#9cf,stroke:#333,stroke-width:2px;
    style D fill:#f96,stroke:#333,stroke-width:2px;
    style E fill:#f96,stroke:#333,stroke-width:1px;
    style F fill:#f96,stroke:#333,stroke-width:1px;
    style G fill:#f96,stroke:#333,stroke-width:1px;
    style H fill:#ddd,stroke:#333,stroke-width:1px;
    style I fill:#ff9,stroke:#333,stroke-width:2px;
    style J fill:#ff9,stroke:#333,stroke-width:2px;
    style K fill:#ff9,stroke:#333,stroke-width:2px;
    style L fill:#ff9,stroke:#333,stroke-width:2px;

```

**6. Component Breakdown**

*   **React Frontend Component (B):**
    *   Embedded within the host clinical system.
    *   Renders the "Find Trials" button/trigger (CTM-F01).
    *   Manages UI state (idle, loading, results, no results, error) (CTM-F02, F03, F06, F07).
    *   Makes asynchronous API calls to the Backend API Gateway (C).
    *   Displays formatted trial results, match rationale, flags, and links (CTM-F03, F04, F05).
    *   Ensures UI responsiveness and clarity (CTM-NF03).
*   **Backend API Gateway (C):**
    *   Built with Python (FastAPI/Flask recommended for async handling).
    *   Provides RESTful endpoints (e.g., `/findTrials`).
    *   Authenticates/Authorizes requests (likely leveraging host system's auth).
    *   Validates incoming requests.
    *   Orchestrates calls to the AI Orchestration Layer (D).
    *   Formats responses for the frontend.
    *   Handles system-level error responses (CTM-F07).
*   **AI Orchestration Layer (D):**
    *   Manages the workflow involving different Langchain agents.
    *   Receives patient identifier/context from the API Gateway.
    *   Invokes Patient Data Agent (E), Trial Discovery Agent (F), and Matching Agent (G) in sequence or parallel where applicable.
    *   Aggregates results from agents.
    *   Interacts with Cache (H) if implemented.
    *   Contains the core logic flow for the matching process.
*   **Patient Data Agent (E):**
    *   Responsible for securely fetching relevant structured and unstructured patient data from the EHR/Data Store (I) based on the patient ID.
    *   Uses NLP (potentially via LLM) to parse notes and extract key information.
    *   Creates a standardized patient profile summary for matching.
    *   Adheres strictly to data access permissions and privacy rules (CTM-NF02).
*   **Trial Discovery Agent (F):**
    *   Queries external (J) and internal (K) trial databases based on core patient conditions (e.g., diagnosis, location).
    *   Filters for actively recruiting trials.
    *   Retrieves detailed trial protocol information, focusing on eligibility criteria.
*   **Matching & Eligibility Agent (G):**
    *   The core AI component using Langchain.
    *   Takes the standardized patient profile (from E) and trial protocols (from F).
    *   Uses LLMs (L) via Langchain chains/tools to parse complex, natural language eligibility criteria (inclusion/exclusion).
    *   Performs logical comparison/reasoning between patient data and parsed criteria.
    *   Generates ranked matches, rationale, and identifies uncertainties/flags (CTM-F04, NF04).
*   **Cache (H) (Optional):**
    *   Stores frequently accessed, non-sensitive data like parsed trial protocols or intermediate results to improve performance (CTM-NF01). Redis or Memcached could be used. Needs careful consideration regarding data staleness.
*   **External Systems (I, J, K, L):**
    *   EHR/Patient Data Store: Source of truth for patient info. Requires secure API/DB access.
    *   Trial Databases: ClinicalTrials.gov, potentially EudraCT, institutional DBs. Accessed via APIs or direct DB query where available/permitted.
    *   LLM Provider: The service providing the core language understanding and generation capabilities used by the Langchain agents.

**7. Data Flow (Primary Success Scenario - CTM-F03)**

1.  Clinician clicks "Find Trials" in React component (B).
2.  React component sends patient ID to Backend API (C).
3.  API Gateway (C) validates and forwards request to AI Orchestrator (D).
4.  Orchestrator (D) invokes Patient Data Agent (E).
5.  Agent (E) securely fetches data from EHR (I) and creates patient profile.
6.  Orchestrator (D) invokes Trial Discovery Agent (F).
7.  Agent (F) queries Trial DBs (J, K) and retrieves relevant protocols.
8.  Orchestrator (D) invokes Matching Agent (G) with profile and protocols.
9.  Agent (G) uses Langchain and LLM (L) to parse criteria and compare against profile.
10. Agent (G) returns ranked list, rationale, and flags to Orchestrator (D).
11. Orchestrator (D) formats results (potentially using Cache H).
12. Orchestrator (D) sends formatted results to API Gateway (C).
13. API Gateway (C) sends successful JSON response to React component (B).
14. React component (B) displays the results list to the clinician.

**8. API Design (High-Level)**

*   **Endpoint:** `POST /api/v1/trials/find`
*   **Request Body:**
    ```json
    {
      "patientId": "unique-patient-identifier",
      "context": { // Optional: Additional context if needed
        "requestingClinicianId": "clinician-xyz",
        "searchRadiusKm": 50
      }
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "status": "success",
      "matches": [
        {
          "trialId": "NCT12345678",
          "title": "Trial for Advanced Widgetitis",
          "status": "Recruiting",
          "phase": "Phase 3",
          "condition": "Widgetitis",
          "locations": ["City Hospital", "Regional Clinic"],
          "matchRationale": [
            "Matches diagnosis: Widgetitis Stage IV",
            "Meets age criteria (55)",
            "Acceptable prior therapy"
          ],
          "flags": ["Requires confirmation of eGFR > 60 within last 30 days"],
          "detailsUrl": "https://clinicaltrials.gov/ct2/show/NCT12345678",
          "contactInfo": "Dr. Smith, 555-1234"
        },
        // ... other matches
      ],
      "searchTimestamp": "2023-10-27T10:30:00Z"
    }
    ```
*   **No Matches Response (200 OK):**
    ```json
    {
      "status": "no_matches_found",
      "matches": [],
      "message": "No suitable recruiting trials found based on current criteria.",
      "searchTimestamp": "2023-10-27T10:30:00Z"
    }
    ```
*   **Error Response (e.g., 500 Internal Server Error, 400 Bad Request, 403 Forbidden):**
    ```json
    {
      "status": "error",
      "message": "Failed to complete trial search due to an internal error.",
      "errorDetails": "Optional: Internal error code/ref (not sensitive details)"
    }
    ```

**9. Data Management**

*   **Patient Data (PHI):** Handled with utmost care. Access via secure APIs/mechanisms provided by the EHR. Data processed in memory or temporary storage during request lifecycle. No persistent storage of PHI within the trial matching service unless explicitly required, architected, and secured according to HIPAA standards. Anonymization/Tokenization to be used where feasible.
*   **Trial Data:** Fetched from public/private sources. Can be cached (H) to improve performance, considering data freshness requirements.
*   **Log Data:** System logs should not contain PHI unless strictly necessary for debugging and secured appropriately.

**10. Security Considerations (CTM-NF02)**

*   **Authentication:** Leverage the host clinical system's authentication mechanism. The Backend API must validate user sessions/tokens passed from the frontend.
*   **Authorization:** Implement Role-Based Access Control (RBAC) if necessary, ensuring only authorized clinicians can initiate searches. Check patient access permissions via EHR integration.
*   **Data Encryption:** TLS for data in transit between all components (Frontend <-> Backend, Backend <-> External Systems). Encryption at rest for any sensitive configuration or cached data.
*   **HIPAA Compliance:** All aspects of data handling, storage (if any), access logging, and processing must be HIPAA compliant. Conduct Privacy Impact Assessment (PIA). Secure access to LLM Provider (e.g., private endpoints, data processing agreements).
*   **Input Sanitization:** Protect against injection attacks at the API layer.
*   **Dependency Security:** Regularly scan dependencies (React, Python libraries) for vulnerabilities.

**11. Scalability & Performance (CTM-NF01)**

*   **Backend API:** Deploy as scalable containerized services (e.g., Docker/Kubernetes) or serverless functions. Use asynchronous processing (e.g., `asyncio` in Python with FastAPI/Uvicorn) to handle concurrent requests efficiently.
*   **AI Processing:** The Langchain/LLM calls are likely the bottleneck. Optimize prompts, potentially use smaller/faster models if acceptable, parallelize independent tasks (e.g., fetching patient data while fetching trial data).
*   **Caching:** Implement caching (H) for trial protocols and potentially intermediate LLM results where appropriate.
*   **Database Access:** Optimize queries to EHR and trial databases.

**12. Reliability & Availability (CTM-NF05)**

*   **Error Handling:** Implement robust error handling at each layer (Frontend, API, AI Agents). Provide clear feedback to the user (CTM-F07).
*   **Monitoring & Logging:** Implement comprehensive logging (excluding PHI where possible) and monitoring (uptime, performance metrics, error rates) using tools like Prometheus/Grafana, Datadog, etc.
*   **Health Checks:** Implement health check endpoints for the backend service for load balancers and monitoring.
*   **Redundancy:** Deploy backend services across multiple availability zones/instances.

**13. Deployment Strategy**

*   **Frontend:** The React component will be bundled and integrated into the deployment pipeline of the host clinical workflow system.
*   **Backend:** Deployed as containerized services (e.g., Kubernetes cluster) or serverless functions in a secure cloud (e.g., AWS, Azure, GCP) or on-premise environment, adhering to organizational policies. CI/CD pipelines for automated testing and deployment.

**14. Assumptions & Dependencies**

*   Reliable and secure API/access mechanism to the EHR/Patient Data Store (I).
*   Availability and reliability of external trial database APIs (J, K).
*   Availability, reliability, and acceptable performance of the chosen LLM Provider (L).
*   The host clinical system allows embedding of the React component and communication with the backend API.
*   Clinicians have appropriate training on the tool's capabilities and limitations.

**15. Future Considerations**

*   User feedback mechanism for inaccurate matches.
*   More granular filtering options (e.g., specific biomarkers, advanced exclusion criteria).
*   Integration with clinical trial management systems (CTMS).
*   Proactive alerting based on patient data changes.
*   Support for different languages.
