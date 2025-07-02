from typing import Dict, Any
import os
from backend.models.base.exceptions import NotFoundException
from backend.agents.document_processing import DocumentProcessingEngine
from backend.agents.vector_store import VectorStore
from backend.models.requests.auth import Documents
from backend.settings import MongoConnectionDetails, get_app_settings
from backend.database.mongo import MongoDBConnector
from cloudinary.utils import cloudinary_url
import uuid
import requests

from backend.utils.cache_decorator import cacheable


class FilesService:
    def __init__(
        self,
        doc_engine: DocumentProcessingEngine,
        vector_store: VectorStore,
        mongo_config: MongoConnectionDetails,
    ):
        self.doc_engine = doc_engine
        self.vector_store = vector_store
        self.mongo_config = mongo_config
        self.mongo_connector = MongoDBConnector(mongo_config)

    async def upload_file(self, file, company_name: str = None) -> Dict[str, Any]:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        cloud_url = self.doc_engine.upload_to_cloudinary(temp_path)
        documents = self.doc_engine.extract_text(temp_path, file.filename, company_name)
        await self.vector_store.add_documents(documents, company_name)
        os.remove(temp_path)
        # Add the public URL to the company_docs collection
        self.mongo_connector.update_records(
            "company_docs",
            {"company_name": company_name},
            {"$addToSet": {"document_urls": cloud_url}},
        )
        return {"cloud_url": cloud_url}

    @cacheable()
    async def get_company_docs(self, company_name: str) -> Documents:
        company_details = await self.mongo_connector.aquery(
            "companies", {"company_name": company_name}
        )
        if not company_details:
            raise NotFoundException("Company not found")
        documents = company_details[0]["documents"]
        return Documents(**documents)

    @cacheable()
    async def download_file(self, cloud_url: str) -> str:
        temp_path = "/tmp/downloaded_file"
        self.doc_engine.download_from_cloudinary(cloud_url, temp_path)
        return temp_path

    async def upload_iframe_obj(self, file_path: str) -> str:
        """
        Upload an HTML iframe file to Cloudinary, delete the local file, and return the public URL.
        The file will be renamed to a UUID for uniqueness.
        """
        unique_filename = f"{uuid.uuid4()}"
        # Optionally, you could copy/rename the file to a new path with the UUID, but Cloudinary upload can use the original path and just set the public_id if needed.
        cloud_url = self.doc_engine.upload_to_cloudinary(
            file_path, public_id=unique_filename
        )
        cloud_url, _ = cloudinary_url(
            f"{unique_filename}.html",  # Must include .html
            resource_type="raw",
            type="upload",
            sign_url=True,
            attachment=False,  # 🔑 Makes it inline instead of downloadable
        )
        os.remove(file_path)
        return cloud_url

    async def fetch_raw_file_from_cloudinary(self, public_id: str) -> bytes:
        """
        Download a raw file from Cloudinary by public_id and return its content as bytes.
        """
        app_settings = get_app_settings()
        cloud_name = app_settings.storage_config.cloud_name
        # Construct the raw file URL
        url = f"https://res.cloudinary.com/{cloud_name}/raw/upload/{public_id}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.content
