import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from tools.nmkr_toolkit import NMKRToolkit
import logging
import json
# Set up logging - more verbose to help with debugging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

"""Create an agent specialized for NMKR NFT operations in the preprod environment"""

# Try to get a specific preprod key first, fall back to regular key if not available
nmkr_preprod_api_key = os.environ.get("NMKR_PREPROD_API_KEY")

# Create NMKR toolkit with preprod environment
nmkr_toolkit = NMKRToolkit(api_key=nmkr_preprod_api_key, environment="preprod")

nft_agent = Agent(
    name="NMKR NFT Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[nmkr_toolkit],
    description="You are an AI agent that can create, mint, and manage NFTs using the NMKR Studio API in both preprod (testnet) and mainnet environments.",
    instructions=[
        "When the user asks about NFT operations, use the appropriate NMKR tool.",
        "For project creation, ask for name, description, and wallet address if not provided.",
        
        # Updated NFT upload instructions
        "For NFT uploading, the toolkit supports multiple upload methods:",
        "  - Local file upload: Use file_path parameter for local files",
        "  - Remote URL upload: Use preview_image parameter with fileFromsUrl",
        "  - IPFS hash: Use preview_image parameter with fileFromIPFS",
        "  - Base64 content: Use preview_image parameter with fileFromBase64",
        
        # Metadata handling instructions
        "For metadata handling, the toolkit supports:",
        "  - Token details: token_name, display_name, description parameters for basic info",
        "  - Complete metadata: Use metadata parameter to provide a full metadata object",
        "  - Metadata override: Use metadata_override parameter for custom 721 metadata format",
        "  - Placeholder fields: Use metadata_placeholder parameter for template-based metadata",
        
        "When uploading NFTs, do not expect both file_path and metadata as the only parameters.",
        "Instead, identify which upload method the user wants to use (file, URL, IPFS) and use the appropriate parameters.",
        
        # Original instructions continued
        "For minting, ask for necessary details like project ID and token UIDs.",
        "Provide clear responses about transaction status and any errors that occur.",
        "Format responses in a user-friendly way, especially when displaying project or token details.",
        "Note that the API key is used as a Bearer token in the Authorization header.",
        "When a response contains 'error' or 'Error', format it as an error message to the user.",
        "Convert all dictionary responses to formatted strings before returning them to the user.",
        "You can work with both preprod (testnet) and mainnet environments based on the toolkit configuration.",
        "If authentication fails, suggest to the user that they might need a separate API key for the specific environment.",
        "For preprod environment, remind users that it uses test ADA (tADA), not real funds.",
        "Preprod API operations should be done at studio-preprod.nmkr.io, while mainnet operations use studio.nmkr.io.",
        "Always inform the user which environment (preprod or mainnet) you're currently operating in.",
        "Be cautious with mainnet operations as they involve real assets and funds.",
        "For URL-based image uploads, the agent should use either:",
        "  - image_url parameter directly, or",
        "  - preview_image parameter with a dictionary: {'mimetype': 'image/jpeg', 'fileFromsUrl': 'https://example.com/image.jpg'}",
        "Example usage for URL uploads:",
        "  upload_file_and_metadata(",
        "    project_uid='project-id-here',",
        "    token_name='TOKEN_NAME',",
        "    display_name='Display Name',",
        "    description='Description',",
        "    preview_image={",
        "      'mimetype': 'image/jpeg',",
        "      'fileFromsUrl': 'https://example.com/image.jpg'",
        "    }",
        "  )",
        
        # IPFS workflow instructions
        "For uploading to IPFS first, then creating NFTs with IPFS hash:",
        "  1. First use upload_to_ipfs(customer_id, file_from_url=url, mimetype=mimetype)",
        "  2. Then extract the ipfsHash from the response",
        "  3. Then use upload_file_and_metadata with preview_image={'mimetype': mimetype, 'fileFromIPFS': ipfs_hash}",
        
        # Minting instructions
        "For minting and sending NFTs, use the mint_and_send_specific method with the correct parameters:",
        "  - project_uid: The project UID",
        "  - nft_uid: Single NFT UID as a string (not a list of token_uids)",
        "  - token_count: Number of tokens to mint (typically 1)",
        "  - receiver_address: The wallet address to receive the NFT",
        "Example:",
        "  mint_and_send_specific(",
        "    project_uid='project-id-here',", 
        "    nft_uid='nft-uid-here',", 
        "    token_count=1,",
        "    receiver_address='addr_test1...'", 
        "  )"
    ],
    markdown=True,
    debug_mode=True,
    show_tool_calls=True,
)

# Test creating a project with additional parameters
test_command = """
Create a project with the following details:
- Environment: preprod
- Project Name: TestAgno
- Description: A small testing project for the NMKR toolkit
- Wallet Address: addr_test1qz47ranxl4p5l97hwtd6793tavxqzzn6mtgmg6ztwf7356x6cluln4vc579dv335axeyk9a9fg9seql3h2d230vve5wscmmu9h
- Max Token Supply: 1
- Token Prefix: AGNO
- Project URL: https://agno.com
- Address Expire Time: 30
- NFT 
"""

# Test uploading a file to an existing project
test_upload_command = """
Upload an NFT to the project with the following details use the URL to upload to IPFS first and then use the IPFS hash to upload to the project
- Project UID: f0cc6560-4ec4-41e1-908d-174d4eea656c
- USER ID: 190328
- Token Name: AGNO_TEST_03
- Display Name: Agno Test NFT
- Description: This is a test NFT uploaded via the NMKR toolkit
- Upload Method: URL
- Image URL: https://replicate.delivery/xezq/nz1cZdX3UDKgBR1beXPNtmwW5oB47lfVVkeQEKU8Z7PMRvMpA/tmpswo95zwd.jpg
- Image MIME Type: image/jpeg
- After this mint and send the NFT to the following address: addr_test1qz47ranxl4p5l97hwtd6793tavxqzzn6mtgmg6ztwf7356x6cluln4vc579dv335axeyk9a9fg9seql3h2d230vve5wscmmu9h
"""

# Run the test
nft_agent.print_response(test_upload_command)
