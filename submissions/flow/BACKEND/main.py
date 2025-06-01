import asyncio
import base64
import os
import re
import json
from dotenv import load_dotenv  # Add this import
from flask import Flask, request, jsonify
from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.url import UrlKnowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.tools.duckduckgo import DuckDuckGoTools
from pathlib import Path
from flask_cors import CORS
import requests
from browser_toolkit import BrowserUseToolkit
from razorpay_toolkit import RazorpayPaymentLink
from razorpay_toolkit import RazorpayTrackerToolkit
from agno.tools.resend import ResendTools
from analyze_toolkit import AnalyzeToolkit  # Add this import
from agno.tools.website import WebsiteTools

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize browser toolkit (persistent session)
browseruse_toolkit = BrowserUseToolkit()
# Initialize parallel browser toolkit

# Initialize Razorpay toolkit
razorpaypayment_toolkit = RazorpayPaymentLink()
razorpay_tracker_toolkit = RazorpayTrackerToolkit()


# Design specialists
visual_agent = Agent(
    name="Visual Designer",
    role="Expert in color theory and visual composition.",
    model=OpenAIChat("gpt-4o"),
)

typography_agent = Agent(
    name="Typography Expert",
    role="Handles questions about fonts and layout typography.",
    model=OpenAIChat("gpt-4o"),
)

ux_agent = Agent(
    name="UX Writer",
    role="Provides microcopy and UX content guidance.",
    model=OpenAIChat("gpt-4o"),
)

image_agent = Agent(
    name="Image Analysis Agent",
    role="Analyze images and extract visual insights or design inspiration.",
    model=OpenAIChat(id="gpt-4o"),
    tools=[AnalyzeToolkit()],  # Replace DuckDuckGoTools with AnalyzeToolkit
    markdown=True,
    instructions="""
    IMAGE ANALYSIS PROTOCOL:
    1. When analyzing images, use the analyze_current_tab tool to:
       - Get detailed descriptions of all images on the page
       - Extract visual insights and design inspiration
       - Identify key elements and subjects
    2. Ensure Chrome browser has the target page open
    3. Provide comprehensive analysis of visual content
    """,
)

accessibility_agent = Agent(
    name="Accessibility Expert",
    role="Ensures designs meet WCAG guidelines and accessibility standards.",
    model=OpenAIChat("gpt-4o"),
    instructions="""
    ACCESSIBILITY PROTOCOL:
    1. Evaluate color contrast ratios
    2. Check text readability and sizing
    3. Ensure proper heading hierarchy
    4. Verify keyboard navigation support
    5. Recommend ARIA attributes when needed
    """,
    show_tool_calls=True,
)

animation_agent = Agent(
    name="Animation Specialist",
    role="Creates and optimizes motion design and micro-interactions.",
    model=OpenAIChat("gpt-4o"),
    instructions="""
    ANIMATION PROTOCOL:
    1. Design smooth transitions
    2. Create engaging micro-interactions
    3. Optimize performance
    4. Ensure motion accessibility
    5. Provide animation code examples
    """,
    show_tool_calls=True,
)

brand_agent = Agent(
    name="Brand Strategist",
    role="Maintains brand consistency and voice across all designs.",
    model=OpenAIChat("gpt-4o"),
    instructions="""
    BRAND PROTOCOL:
    1. Ensure brand color consistency
    2. Maintain typography hierarchy
    3. Verify brand voice in copy
    4. Check logo usage guidelines
    5. Recommend brand-aligned imagery
    """,
    show_tool_calls=True,
)

# Add Language Expert Agent
language_agent = Agent(
    name="Language Expert",
    role="Expert in translation and language nuances",
    model=OpenAIChat("gpt-4o"),
    instructions="""
    TRANSLATION PROTOCOL:
    1. Provide accurate translations that maintain the original meaning
    2. Consider cultural context and nuances
    3. Ensure natural language flow in the target language
    4. Avoid literal translations that may sound awkward
    5. Preserve any technical terms or proper nouns appropriately
    6. Return only the translated text without additional explanations
    """,
    show_tool_calls=True,
)

browser_agent = Agent(
    name="Browser Automation Agent",
    role="Handles all web browsing, automation, and data extraction tasks.",
    model=OpenAIChat(id="gpt-4o"),
    tools=[browseruse_toolkit],
    show_tool_calls=True,
    markdown=True,
    instructions="""
    BROWSER AUTOMATION PROTOCOL:

    1. WEB SCRAPING & DATA EXTRACTION:
       - Extract structured data from websites
       - Scrape product information
       - Collect pricing data
       - Gather competitor information
       - Monitor website changes

    2. FORM AUTOMATION:
       - Fill out web forms
       - Submit data automatically
       - Handle file uploads
       - Process multi-step forms
       - Validate form submissions

    3. CONTENT MONITORING:
       - Track price changes
       - Monitor stock availability
       - Check for content updates
       - Track social media feeds
       - Monitor news sources

    4. TESTING & VALIDATION:
       - Test website functionality
       - Validate links and forms
       - Check responsive design
       - Verify accessibility
       - Test cross-browser compatibility

    5. INTERACTION AUTOMATION:
       - Click buttons and links
       - Navigate through pages
       - Handle popups and alerts
       - Manage cookies and sessions
       - Execute JavaScript actions

    6. DATA COLLECTION:
       - Gather market research data
       - Collect user reviews
       - Extract contact information
       - Monitor SEO metrics
       - Track analytics data

    EXECUTION GUIDELINES:
    1. Always maintain session state between requests
    2. Handle errors gracefully with retry mechanisms
    3. Respect website robots.txt and rate limits
    4. Use appropriate delays between actions
    5. Implement proper error handling
    6. Document all automation steps
    7. Provide clear success/failure status
    """,
)

razorpay_agent = Agent(
    name="PaymentLinkGenerator",
    role="Generates valid Razorpay payment links",
    model=OpenAIChat("gpt-4o"),
    tools=[razorpaypayment_toolkit],
    instructions="""
    STRICT PAYMENT GENERATION PROTOCOL:

    1. INPUT REQUIREMENTS:
       - api_key (provided)
       - api_secret (provided)
       - amount (in INR)
       - description
       - customer_name
       - customer_email

    2. EXECUTION STEPS:
       a. Immediately use razorpay_toolkit.generate_payment_link with:
          - All provided parameters exactly as received
          - amount converted to paise (amount × 100)
          - currency defaulting to INR
       b. NEVER ask for confirmation or additional details
       c. If API fails, return exact error message

    3. OUTPUT REQUIREMENTS:
       - Return ONLY the payment link (https://rzp.io/l/...)
       - Never return dummy/example links
       - Never modify or reveal the api_secret

    FAILURE CONDITIONS:
    - If missing any required field: "ERROR: Missing required field: [field]"
    - If API error: "ERROR: Razorpay API failed: [details]"
    """,
    show_tool_calls=True,
)

from_email = "onboarding@resend.dev"

mail_agent = Agent(
    name="PaymentEmailSender",
    role="Sends payment links via email",
    model=OpenAIChat("gpt-4o"),
    tools=[ResendTools(from_email=from_email)],
    instructions="""
    EMAIL PROTOCOL:
    1. Compose email with:
       - Subject: "Payment Link: {description}"
       - Body: Payment details and link
       - To: customer_email
    2. MUST include actual payment link
    3. Verify all details before sending
    """,
    show_tool_calls=True,
)


# Coordinated Team
payment_team = Team(
    name="PaymentProcessingTeam",
    mode="coordinate",
    model=OpenAIChat("gpt-4o"),
    members=[razorpay_agent, mail_agent],
    description="Handles end-to-end payment processing",
    instructions="""
    COORDINATION WORKFLOW:

    1. PAYMENT GENERATION PHASE:
       a. Delegate to PaymentLinkGenerator with all required parameters
       b. Validate response is a proper Razorpay link

    2. EMAIL SENDING PHASE:
       a. Compose email with EXACT format:
          Subject: "Payment Link: {description}"
          Body: |
            Dear {customer_name},

            Your payment link for {amount} INR:
            {payment_link}

            Description: {description}
          To: {customer_email}
       b. Send using ResendTools

    3. VALIDATION:
       - Verify payment link starts with https://rzp.io/l/
       - Confirm email contains the exact payment link
    """,
    success_criteria="""
    - Valid Razorpay link generated
    - Email sent with correct payment details
    - No placeholder text in final output
    """,
    show_members_responses=True,
)

# Creative Design Team with enhanced capabilities
creative_team = Team(
    name="Creative Design Team",
    mode="route",
    model=OpenAIChat("gpt-4o"),
    members=[
        visual_agent, 
        typography_agent, 
        ux_agent, 
        image_agent,
        accessibility_agent,
        animation_agent,
        brand_agent,
        language_agent,  # Add language agent
    ],
    show_members_responses=True,
    markdown=True,
    instructions=[
        "If prompt includes an image or asks for visual evaluation, use Image Analysis Agent.",
        "Use Visual Designer for colors and layout advice.",
        "Typography Expert handles font or layout text questions.",
        "UX Writer covers microcopy and UX writing.",
        "Route todo-related tasks to the Todoist Agent.",
        "For web browsing, automation, or data extraction, use Browser Automation Agent.",
        "Use Accessibility Expert for WCAG compliance and accessibility checks.",
        "Animation Specialist handles motion design and micro-interactions.",
        "Brand Strategist ensures brand consistency across all elements.",
        "Responsive Design Expert manages cross-device compatibility.",
        "Use Language Expert for all translation tasks.",
        "Route all other requests to the most appropriate specialist.",
        "For complex projects, coordinate multiple specialists to provide comprehensive solutions.",
        "Always consider accessibility, brand consistency, and responsive design in all recommendations."
    ],
    success_criteria="""
    - All designs meet accessibility standards
    - Brand consistency is maintained
    - Responsive design principles are followed
    - Animations enhance user experience
    - Typography is readable and accessible
    - Color schemes are accessible and on-brand
    - Microcopy is clear and user-friendly
    - Translations are accurate and natural
    - All recommendations include implementation guidance
    """
)

# Create Razorpay Tracking Agent
razorpay_tracking_agent = Agent(
    name="PaymentTrackingAgent",
    role="Tracks and manages Razorpay payment links",
    model=OpenAIChat("gpt-4o"),
    tools=[razorpay_tracker_toolkit],
    instructions="""
    PAYMENT TRACKING PROTOCOL:

    1. INPUT REQUIREMENTS:
       - api_key (required)
       - api_secret (required)
       - limit (optional, default: 10)
       - status (optional)

    2. EXECUTION STEPS:
       a. Use razorpay_tracker_toolkit.get_payment_links with provided parameters
       b. The toolkit will return a JSON string with payment links
       c. Return the JSON string directly without modification

    3. OUTPUT FORMAT:
       - Return the JSON string exactly as received from the toolkit
       - Do not modify or parse the response
    """,
    show_tool_calls=True,
)

# Add Flashcard Agent
flashcard_agent = Agent(
    name="FlashcardGenerator",
    role="Generates educational flashcards from web content",
    model=OpenAIChat("gpt-4o"),
    tools=[WebsiteTools()],
    instructions="""
    FLASHCARD GENERATION PROTOCOL:

    1. CONTENT EXTRACTION & ORGANIZATION:
       - Extract key concepts and main ideas from the content
       - Group related concepts together
       - Create a logical flow of information
       - Focus on important facts and relationships

    2. FLASHCARD STRUCTURE:
       Each flashcard must follow this exact format:
       ```
       # Front: [Clear, concise question or concept]
       
       ## Back
       ### Definition
       [Clear and concise definition or explanation]
       
       ### Key Points
       - [Point 1]
       - [Point 2]
       - [Point 3]
       
       ### Examples
       - [Example 1]
       - [Example 2]
       
       ### Additional Context
       [Any relevant context or connections to other concepts]
       ```

    3. QUALITY REQUIREMENTS:
       - Front must be a clear, specific question or concept
       - Back must contain comprehensive but concise information
       - Include real-world examples
       - Use bullet points for better readability
       - Maintain consistent formatting
       - Ensure each card is self-contained
       - Number each card (e.g., "Card 1:", "Card 2:", etc.)

    4. CONTENT GUIDELINES:
       - Use active voice
       - Keep language simple and clear
       - Include practical applications
       - Add relevant context
       - Connect related concepts
       - Use markdown formatting for structure

    5. OUTPUT FORMAT:
       - Each card must start with "Card X:" followed by the front
       - Front must be prefixed with "Front:"
       - Back must be prefixed with "Back:"
       - Use ### for subsections within the back
       - Use bullet points for lists
       - Separate cards with blank lines
       - Include at least 5-10 cards per topic
       - Ensure proper markdown formatting

    6. EXAMPLE FORMAT:
       ```
       Card 1:
       Front: What is photosynthesis?
       
       Back:
       ### Definition
       The process by which plants convert light energy into chemical energy
       
       ### Key Points
       - Occurs in chloroplasts
       - Requires sunlight, water, and CO2
       - Produces glucose and oxygen
       
       ### Examples
       - Green leaves in sunlight
       - Algae in water
       
       ### Additional Context
       Essential for life on Earth as it produces oxygen and food
       ```
    """,
    show_tool_calls=True,
    markdown=True
)

@app.route("/api/ai-response", methods=["POST"])
def design():
    prompt = request.json.get("prompt", "")
    image_url = request.json.get("image_url")
    element = request.json.get("element")
    page_content = request.json.get("pageContent")

    # If element is present, build a prompt with its content
    if element:
        text = element.get('text', '').strip()
        src = element.get('src', '').strip()
        if text:
            prompt = f"{prompt}\nElement text: {text}"
        elif src:
            # Use the image source URL directly
            image_url = src
            prompt = f"{prompt}\nAnalyze this image: {src}"
        else:
            return jsonify({"response": "No text or image found in the selected element."})

    # If page content is present, add it to the context
    if page_content:
        context = f"""
        Current page information:
        - Title: {page_content.get('title', '')}
        - URL: {page_content.get('url', '')}
        - Content: {page_content.get('text', '')[:2000]}  # Limit content length
        
        User question: {prompt}
        
        Please provide a helpful response based on the page content and the user's question.
        If the question is about the page content, use the provided information to answer.
        If the question is about navigation or actions, provide clear instructions.
        If the question is about forms or data extraction, explain how to accomplish the task.
        """
        prompt = context

    # Create image list with either the direct image_url or the element's src
    images = [Image(url=image_url)] if image_url else []

    try:
        result = creative_team.run(prompt, images=images)
        return jsonify({"response": result.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/browser/execute", methods=["POST"])
async def handle_browser_task():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400
    
    try:
        # Directly await the agent call
        result = await browser_agent.arun(data['prompt'])
        response = str(result.content) if hasattr(result, 'content') else str(result)
        return jsonify({"result": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

    required_fields = [
        "api_key",
        "api_secret",
        "description",
        "customer_name",
        "customer_email"
    ]
    
    data = request.get_json()
    
    # Validate required fields
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "Missing required fields",
            "required": required_fields
        }), 400

    try:
        result = await razorpaypayment_toolkit.generate_payment_link(
            api_key=data["api_key"],
            api_secret=data["api_secret"],
            description=data["description"],
            customer_name=data["customer_name"],
            customer_email=data["customer_email"],
            amount=data.get("amount"),
            currency=data.get("currency", "INR")
        )
        
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/send-payment-link", methods=["POST"])
def send_payment_link():
    data = request.get_json()

    required_fields = ["api_key", "api_secret", "description",
                       "customer_name", "customer_email", "amount"]
    missing = [field for field in required_fields if field not in data]

    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400


    try:
        task = f"""
        Process payment request with these EXACT parameters:
        - api_key: {data['api_key']}
        - api_secret: {data['api_secret']}
        - amount: {data['amount']}
        - currency: INR
        - description: {data['description']}
        - customer_name: {data['customer_name']}
        - customer_email: {data['customer_email']}

        REQUIREMENTS:
        - Generate real Razorpay link
        - Send email with actual link
        - Return payment URL
        """

        result = payment_team.run(task)  # use .run, not .arun

        content = result.content

        # 🔥 Extract first link from the response
        match = re.search(r"https:\/\/rzp\.io\/[^\s\)\]]+", content)
        
        if not match:
            return jsonify({
                "status": "error",
                "message": "Invalid payment link generated",
                "response": str(content)
            }), 400

        payment_link = match.group(0)

        return jsonify({
            "status": "success",
            "payment_link": payment_link,
            "email": data["customer_email"]
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "email": data.get("customer_email", "unknown")
        }), 500
    
@app.route("/api/track-payments", methods=["POST"])
def track_payments():
    data = request.get_json()

    # Validate required fields
    if not data or "api_key" not in data or "api_secret" not in data:
        return jsonify({"error": "API key and secret are required"}), 400

    try:
        # Create task for the agent
        task = f"""
        Track payments with these parameters:
        - api_key: {data['api_key']}
        - api_secret: {data['api_secret']}
        - limit: {data.get('limit', 10)}
        - status: {data.get('status')}

        REQUIREMENTS:
        - Fetch payment links using the toolkit
        - Return the JSON string response directly
        """

        # Run the agent
        result = razorpay_tracking_agent.run(task)
        
        # Parse the response string back to JSON
        try:
            response_data = json.loads(result.content)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid response format from agent"}), 500
        
        if isinstance(response_data, dict) and "error" in response_data:
            return jsonify(response_data), 400

        return jsonify({
            "status": "success",
            "payment_links": response_data.get("payment_links", [])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze-images", methods=["POST"])
async def analyze_images():
    """
    Analyze images in the currently active Chrome tab.
    Requires Chrome to be running with remote debugging enabled.
    """
    try:
        # Get the prompt from the request
        data = request.get_json()
        prompt = data.get('prompt', "Look at each image on the current page and describe what you see in detail.")
        
        # Initialize the toolkit
        toolkit = AnalyzeToolkit()
        
        # Run the analysis and await the result
        result = await toolkit.analyze_current_tab(prompt)
        
        if result.get("success"):
            return jsonify({
                "status": "success",
                "analysis": result.get("data"),
                "message": result.get("message")
            })
        else:
            return jsonify({
                "status": "error",
                "message": result.get("message")
            }), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error during image analysis: {str(e)}"
        }), 500
    
@app.route("/api/analyze-tab", methods=["POST"])
async def analyze_tab():
    """
    Analyze Everything in the currently active Chrome tab.
    Requires Chrome to be running with remote debugging enabled.
    """
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400
    
    prompt = data.get('prompt')

    try:
        # Initialize the toolkit
        toolkit = AnalyzeToolkit()
        
        # Run the analysis with the dynamic prompt and await the result
        result = await toolkit.analyze_current_tab(prompt)
        
        if result.get("success"):
            return jsonify({
                "status": "success",
                "analysis": result.get("data"),
                "message": result.get("message")
            })
        else:
            # Ensure error response format is consistent
            return jsonify({
                "status": "error",
                "message": result.get("message") or "Image analysis failed"
            }), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    data = request.get_json()
    if not data or 'tasks' not in data or not isinstance(data['tasks'], list):
        return jsonify({"error": "Request must include a 'tasks' list."}), 400
    try:
        results = await parallel_browser_toolkit.run_parallel_tasks(data['tasks'])
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/translate", methods=["POST"])
def translate():
    element = request.json.get("element")
    prompt = request.json.get("prompt", "")
    
    if not element or not element.get('text'):
        return jsonify({"error": "No text to translate"}), 400

    text = element.get('text', '').strip()
    if not text:
        return jsonify({"error": "Empty text"}), 400

    # Extract target language from prompt
    target_language = None
    if "Translate this text to" in prompt:
        target_language = prompt.split("Translate this text to")[1].split(".")[0].strip()

    if not target_language:
        return jsonify({"error": "Target language not specified"}), 400

    try:
        # Create a task for the language expert to handle translation
        task = f"""
        Translate the following text to {target_language}. 
        Focus on providing a natural, accurate translation that maintains the original meaning.
        Return only the translated text without any additional context or explanation.

        Text to translate: {text}
        Target language: {target_language}
        """

        result = language_agent.run(task)
        
        # Return the translation directly
        return jsonify({
            "translations": [{
                "language": target_language,
                "text": result.content.strip(),
                "meaning": None
            }]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate-flashcards", methods=["POST"])
async def generate_flashcards():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Create task for the agent
        task = f"""
        Generate comprehensive educational flashcards from this URL: {data['url']}
        
        Requirements:
        1. Extract key concepts and main ideas
        2. Create clear, engaging questions
        3. Provide detailed, well-structured answers
        4. Include practical examples
        5. Use proper markdown formatting
        6. Generate at least 5-10 cards
        7. Ensure each card follows the exact format:
           # Question
           
           ## Definition
           [Clear definition]
           
           ## Key Points
           - [Point 1]
           - [Point 2]
           
           ## Examples
           - [Example 1]
           - [Example 2]
           
           ## Additional Context
           [Relevant context]
        """

        # Run the agent
        result = await flashcard_agent.arun(task)
        
        return jsonify({
            "status": "success",
            "flashcards": result.content
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)