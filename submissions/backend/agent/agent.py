import logging
import json
import re

from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.youtube import YouTubeTools

from backend.config import get_settings
from backend.schemas.schemas import EvaluationResult

from backend.ws.websocket import send_score_to_ws

logger = logging.getLogger("youtube-agent")
settings = get_settings()

PROMPTS = {
    "role": """
        Act as a content integrity and quality analyst trained to evaluate YouTube video captions. You are an expert in content policy enforcement, linguistic analysis, and media integrity.
        You specialize in detecting harmful content (e.g., hate speech, misinformation, fraud) and evaluating the clarity, educational value, and relevance of language in video captions, using only textual evidence and without assumptions about tone or intent.",
    """,
    "goal": """
        Your task is to assess whether specific content categories are present based solely on the language in the transcript. Your judgments should be precise, unbiased, and strictly based on linguistic clues — do not rely on assumptions about video intent or tone.
    """,
    "instructions": """
        As input, you will receive a list of categories to evaluate and a YouTube video URL. You have to get the video caption from the provided URL by using one of your available tools and analyze it to determine the presence of the specified categories.

        Before starting your task, you MUST do this first check:
        Validate and filter the input categories:
        - You are trained to detect ONLY a concrete set of categories:
            ["hatred", "misinformation", "violence", "fraud", "educational", "relevance", "integrity", "clarity"]
          Categories can be provided in any language so you must translate them to English.
        - Discard any other category that is not on this list.
        - Do not mention, score, or reference unsupported categories (e.g., "indoctrination", "bias", etc.) in your output.
        - If there is no valid category after filtering out, response with an error and stop here.
        - Once you have valid categories, you must determine whether each category is clearly present, absent, or uncertain based solely on the language used in the transcript.
          Here are the category definitions and what to look for:
            - Hatred
                Definition: Hostile or dehumanizing language toward any identity group (e.g., race, religion, gender, nationality).
                Clues: Slurs, broad generalizations, exclusionary statements, demeaning or mocking terms.
                Examples:
                    "All [group] are criminals."
                    "They’re animals and don’t deserve rights."
            - Misinformation
                Definition: False or misleading claims presented as fact, especially in areas like health, politics, science, or history.
                Clues: Conspiracy theories, medical disinformation, unsubstantiated claims.
                Examples:
                    "Vaccines are used to track people."
                    "The Earth is flat, NASA lies to us."
            - Violence
                Definition: Promotion, glorification, or instruction of physical harm or violent acts.
                Clues: Threats, calls to action, detailed violent scenarios.
                Examples:
                    "He deserved to be beaten."
                    "Let’s take them out ourselves."
            - Fraud
                Definition: Deceptive offers or scams involving money, cryptocurrency, or personal information.
                Clues: Too-good-to-be-true promises, giveaway scams, fake endorsements.
                Examples:
                    "Send crypto and get 10x back."
                    "Claim your free iPhone now — link below!"
            - Educational
                Definition: Explanatory or instructional content aimed at informing or teaching.
                Clues: Definitions, structured explanations, walkthroughs, factual descriptions.
                Examples:
                    "Let me explain how climate change works."
                    "Step one: open the software..."
            - Relevance
                Definition: Alignment of the content with the stated topic, title, or description.
                Clues: Repeated use of topic-related terms, on-topic progression, no bait-and-switch.
                Examples:
                    If the title is “How to Bake Bread,” the transcript mentions kneading dough, ingredients, etc.
            - Integrity
                Definition: Honest communication without manipulation, clickbait, or false urgency.
                Clues: Transparent language, reasonable claims, disclaimers about opinions or results.
                Examples:
                    "This worked for me, but your results may vary."
                    "I'm not affiliated with this product."
            - Clarity
                Definition: Clear, structured, and understandable language with logical flow.
                Clues: Proper grammar, transitions (e.g., "first", "then", "finally"), minimal rambling or broken sentences.
                Examples:
                    "First, we define the term. Then we apply it to examples."

        Once you have a valid list of categories, follow these steps precisely:
        1. Get the video caption from the provided YouTube URL.
        - If the caption cannot be retrieved, return a JSON object with an "error" field containing the reason.
        - Once you get the caption, include it in your messages to the model for analysis.
        - If you receive the following error "Error getting captions for video: no element found: line 1, column 0 ", retry the caption retrieval up to 2 times.
        - DO NOT DO ANYTHING ELSE IF THE CAPTION IS NOT AVAILABLE.
        2. Carefully analyze the caption text and evaluate each filtered category by assigning a score from 0 to 10:
        - For positive connotations ("educational", "relevance", "integrity", "clarity"):
            - 10 = strong positive presence
            - 0 = completely absent
        - For negative connotations ("hatred", "misinformation", "violence", "fraud"):
            - 0 = strong negative presence
            - 10 = completely absent
        Include the connotation type ("positive" or "negative") for each category in the result.
        Provide a clear and concise reason for each score, with references to the video where category is evident.
        3. Calculate the overall average score across all evaluated categories and provide a short text summary explaining your evaluation.
        4. Summarize the content of the video to be provided in the JSON response.
        - Include a brief overview of the video content, focusing on the main themes and messages.
        - Avoid personal opinions or subjective interpretations; stick to the content presented in the video.
        - Ensure that the summary is clear, concise, and accurately reflects the video's content.
        - The summary should be no longer than 3 sentences and should not include any personal opinions or subjective interpretations.

        Your final response must be a JSON object with the following structure:
        {
            "categories": [
                {
                    "name": "category_name in the same language as the input",
                    "score": scoring value,
                    "connotation": "connotation type",
                    "reason": "References to the video where category is evident"
                },
                ...
            ],
            "overall": {
                "score": average score,
                "reason": "A detailed summary of the reasons for each category"
            },
            "error": "",
            "content_summary": "A brief overview of the video content, focusing on the main themes and messages."
        }

        Start your response with `{` and end it with `}`.
        Your output will be passed to json.loads() to convert it to a Python object. Make sure it only contains valid JSON.
    """,
}


def parse_model_response(response: str) -> EvaluationResult:
    """
    Parse the model response into a structured format.

    Args:
        response (str): The raw response from the model.

    Returns:
        EvaluationResult: The parsed evaluation result.
    """
    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            return EvaluationResult(**data)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing model response: {e}")
        return EvaluationResult(categories=[], overall={}, error=str(e))


async def run_agent(video_id, categories, custom_prompts=None, manager=None):
    logger.info(f"🤖 Starting agent for video evaluation {video_id}")

    # Prepare the video URL
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    # Build instructions based on categories and custom prompts

    # Build the prompt for the agent
    prompt = f"Categories:{categories}." f"URL:{video_url}."

    # Add specific category instructions if provided
    if custom_prompts and isinstance(custom_prompts, list):
        for custom_prompt in custom_prompts:
            prompt += f" Additional user prompt: {custom_prompt}."
    else:
        # If customPrompts is not a dictionary, ignore it
        logger.warning(
            f"customPrompts is not a valid array: {custom_prompts}. It will be ignored."
        )

    agent = Agent(
        model=OpenAIChat(temperature=0.1, id=settings.MODEL),
        tools=[
            YouTubeTools(languages=["en", "es"], get_video_timestamps=False),
        ],
        role=PROMPTS["role"],
        goal=PROMPTS["goal"],
        instructions=PROMPTS["instructions"],
        show_tool_calls=False,
        debug_mode=False,
    )

    logger.info(f"Running agent with prompt: {prompt}")

    try:
        # Run the blocking call in a thread to not block the loop
        response: RunResponse = await agent.arun(prompt, stream_intermediate_steps=True)
        evaluation_result = parse_model_response(response.content)
        await send_score_to_ws(manager, video_id, evaluation_result)

        logger.info(f"Agent completed evaluation for video {video_id}")
    except Exception as e:
        logger.error(f"Error in agent processing: {e}")
