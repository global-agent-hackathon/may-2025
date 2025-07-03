from textwrap import dedent
from typing import Dict, Any, Iterator, Optional
import os
import json
import time
from logging_config import get_logger

from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.workflow import Workflow
from agno.utils.log import logger
from tools.nmkr_toolkit import NMKRToolkit
from agno.tools.replicate import ReplicateTools
from dotenv import load_dotenv

# Load environment variables and configure logging
load_dotenv()
logger = get_logger(__name__)

class ContentToNFTWorkflow(Workflow):
    """Workflow for generating content (image/video) and minting it as an NFT"""
    
    description: str = (
        "Generate AI content (image or video) based on user description and mint it as an NFT"
    )
    
    # Image generation agent using Replicate's Luma API
    image_generator = Agent(
        name="Image Generator",
        model=OpenAIChat(id="gpt-4o"),
        tools=[ReplicateTools(model="luma/photon-flash")],
        description="Generate high-quality images based on text descriptions",
        instructions=[
            "You are an AI image generation specialist.",
            "Create high-quality, detailed images from text descriptions.",
            "Ensure images are suitable for being minted as NFTs.",
            "Always return a direct link to the generated image.",
            "Do not add any formatting to the URL in the response.",
        ],
        markdown=True,
        debug_mode=True,
        show_tool_calls=True,
    )
    
    # Video generation agent using Replicate's Kling API
    video_generator = Agent(
        name="Video Generator",
        model=OpenAIChat(id="gpt-4o"),
        tools=[ReplicateTools(model="kwaivgi/kling-v1.6-standard")],
        description="Generate high-quality videos based on text descriptions",
        instructions=[
            "You are an AI video generation specialist.",
            "Create high-quality, detailed videos from text descriptions.",
            "Ensure videos are suitable for being minted as NFTs.",
            "Always return a direct link to the generated video.",
            "Do not add any formatting to the URL in the response.",
        ],
        markdown=True,
        debug_mode=True,
        show_tool_calls=True,
    )
    
    # Create NMKR toolkit 
    nmkr_toolkit = NMKRToolkit(
        api_key=os.environ.get("NMKR_API_KEY"),
        environment=os.environ.get("NMKR_ENVIRONMENT")
    )
    
    # NFT minting agent using NMKR API
    nft_minter = Agent(
        name="NFT Minter",
        model=OpenAIChat(id="gpt-4o"),
        tools=[nmkr_toolkit],
        description="Mint NFTs from digital content using NMKR Studio",
        instructions=[
            "You are an NFT minting specialist using NMKR Studio.",
            "Your job is to mint digital content (images/videos) as NFTs.",
            f"Use the existing project with UID '{os.environ.get('NMKR_PROJECT_UID')}' for all NFT operations.",
            "When you need to upload the NFT content, you MUST use the 'upload_file_and_metadata' function.",
            "The 'upload_file_and_metadata' function requires several arguments, including 'image_url' and 'preview_image'.",
            "For the 'image_url' argument, use the 'Image URL' provided in the task.",
            "For the 'preview_image' argument, you MUST construct a dictionary with two keys: 'mimetype' and 'fileFromsUrl'.",
            "   - Populate the 'mimetype' key in the 'preview_image' dictionary with the 'Image MIME Type' provided in the task (e.g., 'image/jpeg' or 'video/mp4').",
            "   - Populate the 'fileFromsUrl' key in the 'preview_image' dictionary with the 'Image URL' provided in the task.",
            "Ensure all other required arguments for 'upload_file_and_metadata' like 'project_uid', 'token_name', 'display_name', and 'description' are also correctly passed.",
            "Do NOT use the 'upload_to_ipfs' method.",
            f"Always use the {os.environ.get('NMKR_ENVIRONMENT')} environment unless explicitly instructed otherwise.",
            "After successfully calling 'upload_file_and_metadata', you will receive an 'nft_uid'. You MUST then use this 'nft_uid' to call the 'mint_and_send_specific' function to mint and send the NFT to the provided wallet address.",
            "Return clear success/failure messages with transaction details, including IPFS links if available from the tool responses.",
        ],
        markdown=True,
        debug_mode=True,
        show_tool_calls=True,
    )
    
    # Store the input parameters as instance variables
    def __init__(self, debug_mode: bool = False, **kwargs):
        super().__init__(debug_mode=debug_mode)
        self.prompt = kwargs.get("prompt", "")
        self.content_type = kwargs.get("content_type", "image")
        self.wallet_address = kwargs.get("wallet_address", "")
        self.display_name = kwargs.get("display_name", "Agno Test NFT")
        self.project_name = kwargs.get("project_name", "Agno NFT Project")
        # Get project UID from environment with fallback to default
        self.project_uid = os.environ.get("NMKR_PROJECT_UID")
    
    def run(self) -> Iterator[RunResponse]:
        """
        Execute the content generation and NFT minting workflow
        
        Returns:
            Iterator of RunResponse objects with results of each step
        """
        # Validate input data
        if not self.prompt:
            yield RunResponse(
                run_id=self.run_id, 
                content="Error: Content description (prompt) is required."
            )
            return
        
        if not self.wallet_address:
            yield RunResponse(
                run_id=self.run_id, 
                content="Error: Wallet address is required to mint and transfer the NFT."
            )
            return
            
        # Generate content based on type
        logger.info(f"Generating {self.content_type} content from prompt: {self.prompt[:50]}...")
        
        try:
            if self.content_type == "image":
                # Generate image
                generation_prompt = f"Generate a high-quality image for an NFT with the following description: {self.prompt}"
                content_response = self.image_generator.run(generation_prompt)
                content_type_display = "Image"
                mime_type = "image/jpeg"
            else:  # video
                # Generate video
                generation_prompt = f"Generate a high-quality video for an NFT with the following description: {self.prompt}"
                content_response = self.video_generator.run(generation_prompt)
                content_type_display = "Video"
                mime_type = "video/mp4"
            
            if not content_response or not content_response.content:
                yield RunResponse(
                    run_id=self.run_id, 
                    content=f"Failed to generate {self.content_type} content."
                )
                return
                
            # Extract just the URL from the content response
            content_url = self._extract_url(content_response.content)
            if not content_url:
                yield RunResponse(
                    run_id=self.run_id, 
                    content=f"Failed to extract URL from content generation response."
                )
                return
                
            logger.info(f"{content_type_display} generated successfully: {content_url[:50]}...")
            
            # Create NFT metadata
            timestamp = int(time.time())
            nft_name = f"AGNO_{timestamp}"
            
            # Mint NFT with the generated content - use the working approach
            mint_prompt = f"""
            Upload an NFT to the project with the following details:
            - Project UID: {self.project_uid}
            - Token Name: {nft_name}
            - Display Name: {self.display_name}
            - Description: AI-generated {content_type_display.lower()} NFT with the description: {self.prompt}
            - Upload Method: URL
            - Image URL: {content_url}
            - Image MIME Type: {mime_type}
            - After this mint and send the NFT to the following address: {self.wallet_address}
            """
            
            logger.info(f"Minting NFT and sending to wallet: {self.wallet_address[:15]}...")
            mint_response = self.nft_minter.run(mint_prompt)
            
            if not mint_response or not mint_response.content:
                yield RunResponse(
                    run_id=self.run_id, 
                    content=f"Failed to mint NFT with the generated {self.content_type}."
                )
                return
                
            # Return successful result with all details
            result = {
                "status": "success",
                "content_type": self.content_type,
                "content_url": content_url,
                "display_name": self.display_name,
                "nft_details": mint_response.content,
                "wallet_address": self.wallet_address
            }
            
            # Format the result as markdown
            markdown_result = f"""### NFT Creation Status

- **Overall Status:** {result['status']}
- **Content Type:** {result['content_type']}
- **Display Name:** {result['display_name']}
- **Target Wallet Address:** {result['wallet_address']}
- **Generated Content URL:** [View Content]({result['content_url']})

---
#### NFT Minting Agent Response:
{result['nft_details']}
"""
            yield RunResponse(run_id=self.run_id, content=markdown_result)
            
        except Exception as e:
            logger.error(f"Error in ContentToNFTWorkflow: {str(e)}")
            yield RunResponse(
                run_id=self.run_id, 
                content=f"Error: Failed to complete the NFT creation process. {str(e)}"
            )
    
    def _extract_url(self, content: str) -> Optional[str]:
        """Extract a URL from content text that might contain markdown or other formatting"""
        # First check if it's already a clean URL
        if content.startswith(("http://", "https://")):
            return content.strip()
            
        # Try to extract from markdown image syntax
        import re
        url_match = re.search(r'\bhttps?://\S+\.\S+\b', content)
        if url_match:
            url = url_match.group(0)
            # Remove trailing characters that might not be part of the URL
            for char in ['.', ',', ')', ']', '"', "'"]:
                if url.endswith(char):
                    url = url[:-1]
            return url
            
        # If no URL found, return the original content
        return content.strip()


# Function to run the workflow with specified parameters
def run_workflow(prompt: str, content_type: str, wallet_address: str, 
                display_name: str = "Agno Test NFT") -> Iterator[RunResponse]:
    """
    Run the ContentToNFTWorkflow with the given parameters.
    
    Args:
        prompt: Text description of desired content
        content_type: "image" or "video"
        wallet_address: Cardano wallet address to receive the NFT
        display_name: Display name for the NFT (defaults to "Agno Test NFT")
        
    Returns:
        Iterator of RunResponse objects
    """
    workflow = ContentToNFTWorkflow(
        debug_mode=True,
        prompt=prompt,
        content_type=content_type,
        wallet_address=wallet_address,
        display_name=display_name
    )
    return workflow.run()


# Updated execute_agno_task function to use our workflow
async def execute_agno_task(input_data: Dict[str, str]) -> Dict[str, Any]:
    """Execute the AI content-to-NFT workflow with the provided input data"""
    logger.info(f"Starting Content-to-NFT workflow with input: {input_data}")
    
    # Extract parameters from input data
    prompt = input_data.get("prompt", "")
    content_type = input_data.get("content_type", "image")
    wallet_address = input_data.get("wallet_address", "")
    display_name = input_data.get("display_name", "Agno Test NFT")
    
    # Run the workflow with the parameters
    responses = list(run_workflow(
        prompt=prompt,
        content_type=content_type,
        wallet_address=wallet_address,
        display_name=display_name
    ))
    
    # Get the final response
    final_response = responses[-1] if responses else None
    
    if final_response and final_response.content:
        # Return the content as markdown
        return {"result": final_response.content, "format": "markdown"}
    else:
        return {"error": "No response from workflow"}


# Agent definition for API integration
nft_agent = Agent(
    name="Content to NFT Agent",
    model=OpenAIChat(id="gpt-4o"),
    description="An agent that generates AI content and mints it as an NFT on Cardano",
    instructions=[
        "You use AI to generate images or videos and mint them as NFTs on the Cardano blockchain.",
        "You'll generate content based on a text description, then mint it as an NFT.",
        "The NFT will be sent to the user's provided wallet address.",
        f"All operations are performed in the {os.environ.get('NMKR_ENVIRONMENT')} environment.",
        "Provide clear status updates and transaction details throughout the process.",
    ],
    markdown=True,
    debug_mode=True,
    show_tool_calls=True,
)


if __name__ == "__main__":
    # For testing purposes
    import time
    import asyncio
    
    # Test data
    test_data = {
        "prompt": "A digital painting of a futuristic city with floating islands",
        "content_type": "image",
        "wallet_address": "addr_test1qz47ranxl4p5l97hwtd6793tavxqzzn6mtgmg6ztwf7356x6cluln4vc579dv335axeyk9a9fg9seql3h2d230vve5wscmmu9h",
        "display_name": "Agno Test NFT"
    }
    
    # Run the workflow directly (synchronous)
    print("Starting workflow test...")
    responses = run_workflow(
        prompt=test_data["prompt"],
        content_type=test_data["content_type"],
        wallet_address=test_data["wallet_address"],
        display_name=test_data["display_name"]
    )
    
    for response in responses:
        print(f"Response: {response.content}")
    
    print("Workflow test completed.")