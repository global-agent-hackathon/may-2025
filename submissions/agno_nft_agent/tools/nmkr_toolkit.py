import requests
from typing import Dict, List, Optional, Union
import json
import datetime

from agno.agent import Agent
from agno.tools import Toolkit
from agno.utils.log import logger


class NMKRToolkit(Toolkit):
    def __init__(self, api_key: str, environment: str = "mainnet", base_url: str = None):
        """
        Initialize the NMKR toolkit for interacting with NMKR Studio API.
        
        Args:
            api_key (str): Your NMKR Studio API key (Bearer token)
            environment (str): Which environment to use - 'mainnet' or 'preprod' (default: 'mainnet')
            base_url (str): Override the base URL for the NMKR API (optional)
        """
        super().__init__(name="nmkr_tools")
        self.api_key = api_key
        self.environment = environment.lower()
        
        # Set the base URL based on environment or custom URL
        if base_url:
            self.base_url = base_url
        else:
            if self.environment == "preprod":
                self.base_url = "https://studio-api.preprod.nmkr.io"
                logger.info("Using NMKR Studio preprod environment")
            else:
                self.base_url = "https://studio-api.nmkr.io"
                logger.info("Using NMKR Studio mainnet environment")
        
        # Register all toolkit functions
        self.register(self.create_project)
        self.register(self.upload_file_and_metadata)
        self.register(self.mint_and_send_specific)
        self.register(self.get_project_details)
        self.register(self.get_payment_address)
        self.register(self.get_minted_tokens)
        self.register(self.list_projects)
        self.register(self.test_connection)
        self.register(self.upload_to_ipfs)
    
    def _format_response(self, response: Dict) -> str:
        """
        Formats a dictionary response as a string.
        
        Args:
            response (Dict): Response dictionary
            
        Returns:
            str: Formatted string representation
        """
        if not isinstance(response, dict):
            return str(response)
            
        if "status" in response and response["status"] == "error":
            return f"Error: {response.get('message', 'Unknown error')}"
            
        # Try to create a readable string from the dictionary
        try:
            return json.dumps(response, indent=2)
        except Exception:
            return str(response)
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, files: Dict = None) -> Dict:
        """
        Makes a request to the NMKR API.
        
        Args:
            endpoint (str): API endpoint to call
            method (str): HTTP method (GET, POST, etc.)
            params (Dict): URL parameters
            data (Dict): JSON data for POST requests
            files (Dict): Files to upload
            
        Returns:
            Dict: Response from the API or error message
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"Making {method} request to {url}")
        if data:
            logger.debug(f"Request data: {data}")
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                if files:
                    # Don't include Content-Type header for multipart/form-data requests
                    response = requests.post(url, headers=headers, data=data, files=files)
                else:
                    headers["Content-Type"] = "application/json"
                    response = requests.post(url, headers=headers, json=data)
            
            # Log response details for debugging
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            
            if response.status_code == 401:
                env_message = f" for the {self.environment} environment" if hasattr(self, 'environment') else ""
                error_msg = (
                    f"Authentication failed: Please check your API key and make sure it's valid{env_message}. "
                    f"Note that preprod and mainnet environments require different API keys."
                )
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "details": {
                        "environment": self.environment,
                        "api_url": self.base_url,
                        "status_code": response.status_code
                    }
                }
            
            # Try to get more detailed error information for non-200 responses
            if response.status_code >= 400:
                try:
                    error_detail = response.json()
                    error_msg = f"API Error: {response.status_code}"
                    if "title" in error_detail:
                        error_msg += f" - {error_detail.get('title')}"
                    if "detail" in error_detail:
                        error_msg += f": {error_detail['detail']}"
                    if "errors" in error_detail:
                        error_msg += f"\nValidation errors: {json.dumps(error_detail['errors'], indent=2)}"
                    logger.error(error_msg)
                    return {
                        "status": "error",
                        "message": error_msg,
                        "details": {
                            "environment": self.environment,
                            "api_url": self.base_url,
                            "status_code": response.status_code,
                            "response": error_detail
                        }
                    }
                except Exception:
                    error_msg = f"API Error: {response.status_code} - {response.text[:200]}"
                    logger.error(error_msg)
                    return {
                        "status": "error",
                        "message": error_msg,
                        "details": {
                            "environment": self.environment,
                            "api_url": self.base_url,
                            "status_code": response.status_code
                        }
                    }
            
            response.raise_for_status()
            
            try:
                return response.json()
            except json.JSONDecodeError:
                # Return text content if not JSON
                return {"status": "success", "content": response.text}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making request to NMKR API: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "details": {
                    "environment": self.environment,
                    "api_url": self.base_url,
                    "exception": str(e)
                }
            }
    
    def test_connection(self) -> str:
        """
        Tests the connection to the NMKR API and authentication.
        
        Returns:
            str: Connection test results as a string
        """
        # Try the simplest endpoint that requires authentication
        endpoint = "/v2/GetAdaRates"
        
        logger.info(f"Testing NMKR API connection to {self.base_url}")
        result = self._make_request(endpoint)
        
        if "status" in result and result["status"] == "error":
            error_message = result.get("message", "Unknown error")
            details = result.get("details", {})
            
            # Create a more detailed error message that includes troubleshooting tips
            detailed_error = (
                f"Error connecting to NMKR API: {error_message}\n\n"
                f"Environment: {details.get('environment', self.environment)}\n"
                f"API URL: {details.get('api_url', self.base_url)}\n"
                f"Status code: {details.get('status_code', 'N/A')}\n\n"
                f"Troubleshooting tips:\n"
                f"1. Verify your API key is correct for the {self.environment} environment\n"
                f"2. Preprod and mainnet environments require different API keys\n"
                f"3. Check if your API key has the necessary permissions\n"
                f"4. Verify the API service is available at {self.base_url}"
            )
            return detailed_error
        
        # Return a string instead of a dictionary to be compatible with the agent framework
        return f"Successfully connected to NMKR API at {self.base_url}. Connection test passed."
    
    def create_project(self, name: str, description: str, payout_wallet: str, max_token_supply: int, token_prefix: str = "", project_url: str = "", address_expire_time: int = 60, is_nft: bool = True, metadata_standard: str = "CIP25", twitter_handle: str = "", enable_fiat: bool = False, enable_decentral_payments: bool = False, enable_cross_sale: bool = False, activate_payin_address: bool = True, payment_gateway_sale_start: str = None, additional_payout_wallets: List[Dict] = None, sale_conditions: List[Dict] = None, policy_expires: bool = False, pricelist: List[Dict] = None, policy_locks_date_time: str = None) -> str:
        """
        Creates a new project in NMKR Studio.
        
        Args:
            name (str): Name of the project
            description (str): Description of the project
            payout_wallet (str): Cardano wallet address for payouts
            max_token_supply (int): Maximum number of tokens that can be minted
            token_prefix (str): Prefix for token names (default: "")
            project_url (str): URL for the project (default: "")
            address_expire_time (int): Time in minutes for address reservation expiration (5-60, default: 60)
            is_nft (bool): Whether this is an NFT project (True) or fungible token project (False) (default: True)
            metadata_standard (str): Metadata standard to use (default: "CIP25")
            twitter_handle (str): Twitter handle for the project (default: "")
            enable_fiat (bool): Enable fiat payments (default: False)
            enable_decentral_payments (bool): Enable decentralized payments (default: False)
            enable_cross_sale (bool): Enable cross-sale on payment gateway (default: False)
            activate_payin_address (bool): Activate pay-in address (default: True)
            payment_gateway_sale_start (str): ISO datetime for payment gateway sale start (default: None)
            additional_payout_wallets (List[Dict]): Additional payout wallets with percentages (default: None)
            sale_conditions (List[Dict]): Sale conditions for the project (default: None)
            policy_expires (bool): Whether the policy should expire (default: False)
            pricelist (List[Dict]): Custom price list for the project (default: None)
            policy_locks_date_time (str): Custom policy locks date time in ISO format (default: None)
            
        Returns:
            str: Project creation result as a formatted string
        """
        endpoint = "/v2/CreateProject"
        
        # Validate address_expire_time
        if address_expire_time and (address_expire_time < 5 or address_expire_time > 60):
            return f"Error: address_expire_time must be between 5 and 60 minutes, got {address_expire_time}"
        
        # Set locks date to 1 year from now if not provided
        locks_date = policy_locks_date_time if policy_locks_date_time else (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
        
        # Create a default price entry if not provided
        if pricelist is None:
            default_price = {
                "countNft": 1,
                "price": 10,  # 10 ADA default price
                "currency": "ADA",
                "isActive": True
            }
            price_list_to_use = [default_price]
        else:
            price_list_to_use = pricelist
        
        # The expected request structure based on API documentation
        data = {
            "projectname": name,
            "description": description,
            "projecturl": project_url,
            "tokennamePrefix": token_prefix,
            "twitterHandle": twitter_handle,
            "policyExpires": policy_expires,
            "policyLocksDateTime": locks_date,
            "payoutWalletaddress": payout_wallet,
            "maxNftSupply": max_token_supply,
            "enableCardano": True,
            "pricelist": price_list_to_use,
            "addressExpiretime": address_expire_time,
            "enableFiat": enable_fiat,
            "enableDecentralPayments": enable_decentral_payments,
            "enableCrossSaleOnPaymentgateway": enable_cross_sale,
            "activatePayinAddress": activate_payin_address
        }
        
        # Add payment gateway sale start if provided
        if payment_gateway_sale_start:
            data["paymentgatewaysalestart"] = payment_gateway_sale_start
            
        # Add additional payout wallets if provided
        if additional_payout_wallets:
            data["additionalPayoutWallets"] = additional_payout_wallets
            
        # Add sale conditions if provided
        if sale_conditions:
            data["saleConditions"] = sale_conditions
        
        # Add project type information based on is_nft parameter
        if not is_nft:
            logger.info(f"Creating fungible token project '{name}'")
            data["projectType"] = "fungibletoken"
            # For fungible tokens, we might need different metadata standards
            data["metadataStandard"] = metadata_standard
        else:
            logger.info(f"Creating NFT project '{name}'")
            # NFT is the default project type in NMKR Studio
            data["projectType"] = "standard"
            data["metadataStandard"] = metadata_standard
        
        # If we're in the preprod environment, make sure we're using a testnet wallet
        if self.environment == "preprod" and not payout_wallet.startswith(("addr_test", "stake_test")):
            return "Error: For preprod environment, you must use a testnet wallet address (starts with addr_test or stake_test)"
        
        logger.info(f"Creating project '{name}' with description '{description}' and max supply of {max_token_supply}")
        logger.info(f"Sending request to {endpoint} with project type: {data.get('projectType', 'standard')}")
        result = self._make_request(endpoint, method="POST", data=data)
        return self._format_response(result)
    
    def upload_file_and_metadata(
        self, 
        project_uid: str, 
        file_path: Optional[str] = None,
        image_url: Optional[str] = None,
        metadata: Optional[Dict] = None,
        token_name: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        preview_image: Optional[Dict] = None,
        subfiles: Optional[List[Dict]] = None,
        metadata_placeholder: Optional[List[Dict]] = None,
        metadata_override: Optional[str] = None,
        metadata_override_cip68: Optional[str] = None,
        price_in_lovelace: Optional[int] = None,
        is_blocked: Optional[bool] = None,
        upload_source: Optional[str] = None
    ) -> str:
        """
        Uploads a file and its metadata for an NFT.
        
        Args:
            project_uid (str): The project UID
            file_path (str, optional): Path to the NFT image/file (for local file upload)
            image_url (str, optional): URL to the NFT image/file (for remote file)
            metadata (Dict, optional): Complete metadata object to send in the request
            token_name (str, optional): The token name
            display_name (str, optional): Display name for the NFT
            description (str, optional): Description of the NFT
            preview_image (Dict, optional): Preview image data with format:
                {"mimetype": str, "fileFromBase64": str, "fileFromsUrl": str, "fileFromIPFS": str}
            subfiles (List[Dict], optional): Additional files for the NFT
            metadata_placeholder (List[Dict], optional): Metadata placeholders with format:
                [{"name": str, "value": str}]
            metadata_override (str, optional): Custom metadata JSON string (must be escaped)
            metadata_override_cip68 (str, optional): Custom CIP-68 metadata JSON string
            price_in_lovelace (int, optional): Price in lovelace
            is_blocked (bool, optional): Whether the NFT is blocked
            upload_source (str, optional): Source of the upload
            
        Returns:
            str: Upload response as a formatted string
        """
        endpoint = f"/v2/UploadNft/{project_uid}"
        
        # Build request data
        data = {}
        
        # If complete metadata object is provided, use it directly
        if metadata:
            data = metadata
        else:
            # Add optional parameters if provided
            if token_name:
                data["tokenname"] = token_name
            if display_name:
                data["displayname"] = display_name
            if description:
                data["description"] = description
            if preview_image:
                data["previewImageNft"] = preview_image
            if subfiles:
                data["subfiles"] = subfiles
            if metadata_placeholder:
                data["metadataPlaceholder"] = metadata_placeholder
            if metadata_override:
                data["metadataOverride"] = metadata_override
            if metadata_override_cip68:
                data["metadataOverrideCip68"] = metadata_override_cip68
            if price_in_lovelace is not None:
                data["priceInLovelace"] = price_in_lovelace
            if is_blocked is not None:
                data["isBlocked"] = is_blocked
            
            # Handle image URL if provided
            if image_url:
                if not preview_image:
                    data["previewImageNft"] = {"fileFromsUrl": image_url}
                logger.info(f"Using image URL for NFT: {image_url}")
            
        # Handle query parameters
        params = {}
        if upload_source:
            params["uploadsource"] = upload_source
            
        # Handle file upload (legacy method)
        files = None
        if file_path:
            logger.info(f"Using legacy file upload method with file: {file_path}")
            files = {"file": open(file_path, "rb")}
            
        logger.info(f"Uploading NFT to project {project_uid}")
        logger.debug(f"Upload data: {data}")
        result = self._make_request(
            endpoint, 
            method="POST", 
            data=data, 
            files=files,
            params=params
        )
        return self._format_response(result)
    
    def mint_and_send_specific(self, project_uid: str, nft_uid: str, token_count: int, receiver_address: str, blockchain: str = "Cardano") -> str:
        """
        Mints a specific NFT and sends it to an address.
        
        Args:
            project_uid (str): The project UID
            nft_uid (str): The NFT UID to mint
            token_count (int): Number of tokens to mint
            receiver_address (str): Receiver's wallet address
            blockchain (str, optional): Blockchain to use. Options: Cardano, Solana, Aptos, Hedara, Polygon, Ethereum. Defaults to "Cardano".
            
        Returns:
            str: Minting response as a formatted string
        """
        endpoint = f"/v2/MintAndSendSpecific/{project_uid}/{nft_uid}/{token_count}/{receiver_address}"
        params = {}
        if blockchain and blockchain != "Cardano":
            params["blockchain"] = blockchain
        
        result = self._make_request(endpoint, method="GET", params=params)
        return self._format_response(result)
    
    def get_project_details(self, project_uid: str) -> str:
        """
        Gets details about a project.
        
        Args:
            project_uid (str): The project UID
            
        Returns:
            str: Project details as a formatted string
        """
        endpoint = f"/v2/ProjectDetails/{project_uid}"
        result = self._make_request(endpoint)
        return self._format_response(result)
    
    def get_payment_address(self, project_uid: str, count_nft: int, customer_ip: str = "") -> str:
        """
        Gets a payment address for random NFT sales.
        
        Args:
            project_uid (str): The project UID
            count_nft (int): Number of NFTs to purchase
            customer_ip (str): Customer's IP address (optional)
            
        Returns:
            str: Payment address details as a formatted string
        """
        endpoint = f"/v2/GetPaymentAddressForRandomNftSale/{project_uid}/{count_nft}/{customer_ip}"
        result = self._make_request(endpoint)
        return self._format_response(result)
    
    def get_minted_tokens(self, project_uid: str) -> str:
        """
        Gets all minted tokens for a project.
        
        Args:
            project_uid (str): The project UID
            
        Returns:
            str: List of minted tokens as a formatted string
        """
        endpoint = f"/v2/GetNfts/{project_uid}/minted/100/1"
        result = self._make_request(endpoint)
        return self._format_response(result)
        
    def list_projects(self, count: int = 100, page: int = 1) -> str:
        """
        Lists all projects for the user with pagination.
        
        Args:
            count (int): Number of projects per page
            page (int): Page number
            
        Returns:
            str: List of projects as a formatted string
        """
        endpoint = f"/v2/ListProjects/{count}/{page}"
        result = self._make_request(endpoint)
        return self._format_response(result)

    def upload_to_ipfs(
        self,
        customer_id: int,
        mimetype: str = "image/jpeg",
        file_from_base64: Optional[str] = None,
        file_from_url: Optional[str] = None,
        name: Optional[str] = None
    ) -> str:
        """
        Upload a file to IPFS using either Base64 content or a URL.
        
        Args:
            customer_id (int): The customer ID
            mimetype (str): MIME type of the file (default: "image/jpeg")
            file_from_base64 (str, optional): Base64-encoded file content
            file_from_url (str, optional): URL to the file to upload
            name (str, optional): Name for the file
            
        Returns:
            str: IPFS upload response as a formatted string with the IPFS hash
        """
        endpoint = f"/v2/UploadToIpfs/{customer_id}"
        
        # Build request data
        data = {
            "mimetype": mimetype
        }
        
        if file_from_base64:
            data["fileFromBase64"] = file_from_base64
        elif file_from_url:
            data["fileFromsUrl"] = file_from_url
        else:
            return "Error: Either file_from_base64 or file_from_url must be provided"
        
        if name:
            data["name"] = name
        
        logger.info(f"Uploading file to IPFS for customer {customer_id}")
        logger.debug(f"Upload data: {data}")
        
        result = self._make_request(endpoint, method="POST", data=data)
        return self._format_response(result)