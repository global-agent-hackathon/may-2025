# Add these imports at the top of your appF.py if not already present
from langchain_core.messages import AIMessage, HumanMessage # Import HumanMessage too
from langchain_google_genai import ChatGoogleGenerativeAI
from PIL import Image as PILImage # Rename to avoid conflict with agno.Image if any
from io import BytesIO
import base64
import os
import uuid
import json
import logging # Ensure logging is imported

# Ensure CONFIG dictionary is accessible and contains GEMINI_API_KEY and STORAGE_PATH
logger = logging.getLogger("blender_agents") # Ensure logger is configured
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"), "UVX_PATH": os.getenv("UVX_PATH"),
    "STORAGE_PATH": os.getenv("STORAGE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")),
    "MODEL_ID": os.getenv("MODEL_ID", "gemini-2.0-flash-lite"),
    "MEMORY_MODEL_ID": os.getenv("MEMORY_MODEL_ID", "gemini-1.5-flash-latest"),
    "MCP_PORT": int(os.getenv("MCP_PORT", "9876")), "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "3")),
    "RETRY_DELAY": int(os.getenv("RETRY_DELAY", "20")),
    "USE_DEBUG": os.getenv("USE_DEBUG", "True").lower() in ("true", "1", "yes"),
    "SESSION_TABLE": os.getenv("SESSION_TABLE", "blender_team_sessions"),
    "MEMORY_TABLE": os.getenv("MEMORY_TABLE", "blender_user_memories")
}
def generate_image_from_text_concept(prompt: str) -> str:
    """
    Generates an image from a text prompt using Gemini via Langchain.
    (For use as an Agent tool)

    Saves the image(s) to a subdirectory within the configured storage path
    and returns a JSON string listing the relative paths of the generated images,
    and any accompanying text.

    Args:
        prompt (str): The detailed text description of the image concept to generate.

    Returns:
        str: A JSON string containing a list of relative paths to the saved image files,
             and optionally any generated text, or an error message JSON.
    """
    api_key = CONFIG.get("GEMINI_API_KEY")
    storage_path = CONFIG.get("STORAGE_PATH")
    image_gen_model_id = CONFIG.get("IMAGE_GEN_MODEL_ID", "gemini-2.0-flash-preview-image-generation") # Use default if not in CONFIG

    if not api_key:
        logger.error("GEMINI_API_KEY not configured for image generation.")
        return json.dumps({"status": "error", "message": "GEMINI_API_KEY not configured."})
    if not storage_path:
        logger.error("STORAGE_PATH not configured for image generation tool.")
        return json.dumps({"status": "error", "message": "STORAGE_PATH not configured for tool."})

    concept_output_dir = os.path.join(storage_path, "concept_images")
    os.makedirs(concept_output_dir, exist_ok=True)

    try:
        # Initialize the Langchain ChatGoogleGenerativeAI model
        llm = ChatGoogleGenerativeAI(model=image_gen_model_id, api_key=api_key)

        # Create the message in the format Langchain expects for multimodal input
        # Langchain usually expects a list of content parts for HumanMessage
        human_message = HumanMessage(
            content=[
                {"type": "text", "text": prompt}
            ]
        )

        # Invoke the model
        response = llm.invoke(
            [human_message], # Pass the HumanMessage
            generation_config=dict(response_modalities=["TEXT", "IMAGE"]),
            # You might also need to set request_options for timeout if Langchain supports it directly here
            # or it might be handled differently by Langchain.
        )

        generated_relative_paths = []
        generated_text_parts = []

        # Process the Langchain AIMessage response
        if isinstance(response, AIMessage) and response.content:
            # Langchain's AIMessage.content can be a string or a list of dicts
            content_parts = response.content
            if isinstance(content_parts, str): # If only text is returned
                generated_text_parts.append(content_parts)
            elif isinstance(content_parts, list):
                for part in content_parts:
                    if isinstance(part, str): # Text part as a simple string
                        generated_text_parts.append(part)
                    elif isinstance(part, dict):
                        if part.get("type") == "text":
                            generated_text_parts.append(part.get("text", ""))
                        elif part.get("type") == "image_url" and part.get("image_url", {}).get("url"):
                            image_url_data = part["image_url"]["url"]
                            # image_url_data is expected to be "data:image/png;base64,LONG_BASE64_STRING"
                            if image_url_data.startswith("data:image/") and ";base64," in image_url_data:
                                try:
                                    base64_data = image_url_data.split(";base64,")[1]
                                    image_bytes = base64.b64decode(base64_data)
                                    image = PILImage.open(BytesIO(image_bytes))

                                    file_name = f"concept_lc_{uuid.uuid4().hex[:8]}.png"
                                    file_path = os.path.join(concept_output_dir, file_name)
                                    relative_file_path = os.path.relpath(file_path, storage_path)

                                    image.save(file_path)
                                    generated_relative_paths.append(relative_file_path)
                                    logger.info(f"Langchain: Generated image saved to: {file_path} (Relative: {relative_file_path})")
                                except Exception as img_proc_e:
                                    logger.error(f"Langchain: Error processing image_url data: {img_proc_e}")
                            else:
                                logger.warning(f"Langchain: Unrecognized image_url format: {image_url_data[:100]}") # Log first 100 chars


        if generated_relative_paths:
            return json.dumps({
                "status": "success",
                "image_paths": generated_relative_paths,
                "generated_text": " ".join(generated_text_parts).strip()
            })
        else:
            # Check for other indications of failure if Langchain provides them
            # This part might need adjustment based on how Langchain surfaces errors/blocks
            logger.warning("Langchain: Image generation failed or no image parts found in the response.")
            return json.dumps({
                "status": "error",
                "message": "Langchain: Image generation failed, no image parts found in response.",
                "generated_text": " ".join(generated_text_parts).strip() # Still return any text found
            })

    except Exception as e:
        logger.error(f"Langchain: An error occurred during image generation: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": f"Langchain: Image generation failed due to an unexpected error: {e}"})
    




# oh that was cool, so based on the flow now i was thinking to upgrde the agents , based on user task cordinator has to fist invoke these agents executive_producer, production_director, production_assistant since we are here to create a comple motion 3d adds, what do you think of it ? and then based on that the fisrt think is to invoke script_narrative, which can provide a detiled script in secene wise and based on script provided this agent should ask cordinator for each secene genarte a image and pass those images to get_storyboard_artist_instructions to get complete story for each senece and image passed to this agent and then invoke get_concept_artist_instructions agent to generte deatiled bpy mesh code for each senece and ask cordinator agent to invoke python code agent to verify all the basic code sniipts for each secene and tell python coding agent to execute each secene code in blender, and the rest dependes on these agents modeling_specialist, texturing_materials, rigging_animation, environment_scene, technical_director, lighting_specialist, camera_cinematography, rendering_compositing, technical_qa, artistic_qa where cordintor is resposible to get the sene info and ask these agents to adjust the patulure 3d asset to make it more attractive, since i have this plan what do you think of it ? and can you help me enhnace the utils.py with clear instructions to these agents especilly for cordinaot becuse its the router team leader with more prodcutive output as a result ? and please provide me complete code so that i can just copy paste for utils.py