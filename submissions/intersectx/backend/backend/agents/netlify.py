import hashlib
import requests
import uuid
from backend.settings import NetlifyConfig


class NetlifyAgent:
    """
    Agent to upload HTML files to Netlify via the Deploy API and return the public URL.
    """

    def __init__(self, netlify_config: NetlifyConfig):
        self.site_id = netlify_config.site_id
        self.auth_token = netlify_config.auth_token
        self.api_base = f"https://api.netlify.com/api/v1/sites/{self.site_id}"
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}

    async def upload_html(self, file_path: str) -> str:
        """
        Upload an HTML file to Netlify under the charts/ folder and return the public URL.
        """
        # Read file content and calculate SHA1
        with open(file_path, "rb") as f:
            content = f.read()
        sha1 = hashlib.sha1(content).hexdigest()
        unique_filename = f"{uuid.uuid4()}.html"
        netlify_path = f"charts/{unique_filename}"
        # Step 1: Create deploy with file hash
        deploy_url = f"{self.api_base}/deploys"
        data = {"files": {f"/{netlify_path}": sha1}}
        resp = requests.post(deploy_url, json=data, headers=self.headers)
        if not resp.ok:
            raise Exception(f"Netlify deploy creation failed: {resp.text}")
        deploy = resp.json()
        deploy_id = deploy["id"]
        # Step 2: Upload the file blob
        upload_url = (
            f"https://api.netlify.com/api/v1/deploys/{deploy_id}/files/{netlify_path}"
        )
        resp = requests.put(upload_url, data=content, headers=self.headers)
        if not resp.ok:
            raise Exception(f"Netlify file upload failed: {resp.text}")
        # Step 3: Get the public URL
        public_url = (
            f"https://{deploy['deploy_ssl_url'].replace('https://', '')}/{netlify_path}"
        )
        return public_url
