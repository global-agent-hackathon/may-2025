from typing import List
import os
import base64
import io
from tempfile import TemporaryDirectory
import requests

from dotenv import load_dotenv
from pptx import Presentation
from PIL import Image
from PIL.PpmImagePlugin import PpmImageFile
from pdf2image import convert_from_path
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
import cloudinary
import cloudinary.uploader

from backend.models.response.files import DoucmentParseResponse
from backend.settings import StorageConfig, get_app_settings
from backend.utils.llm import get_model
from agno.document import Document

from backend.utils.logger import get_logger

LOG = get_logger("DocProcessingEngine")


class DocumentProcessingEngine:
    """
    Engine to extract text from PDF or PPTX files using an LLM with vision (e.g., GPT-4o via phidata).
    """

    def __init__(self, model: AzureOpenAI, storage_config: StorageConfig):
        self.model = model
        self.agent = Agent(
            model=model,
            markdown=True,
            instructions="""
            You are a document parser engine. For the given page, output strictly:
            - A heading for the page which you must generate based on the contents of the page, use the company name passed in all headings along with the title
            - A detailed description of all content and data points on the page. Don't put details like this slide shows and just the description is enough
            Only maintain headings and descriptions. Do not include anything else in the output.
            """,
            response_model=DoucmentParseResponse,
        )
        self.storage_config = storage_config
        # Set Cloudinary config for upload/download
        cloudinary.config(
            cloud_name=self.storage_config.cloud_name,
            api_key=self.storage_config.api_key,
            api_secret=self.storage_config.api_secret,
        )

    def extract_text(
        self, file_path: str, file_name: str = None, company_name: str = None
    ) -> List[Document]:
        file_ext = os.path.splitext(file_path)[1].lower()
        images = []
        if not file_name:
            file_name = os.path.basename(file_path)
        with TemporaryDirectory() as tmpdir:
            if file_ext == ".pdf":
                images = convert_from_path(file_path, dpi=300, output_folder=tmpdir)
            elif file_ext in [".ppt", ".pptx"]:
                prs = Presentation(file_path)
                for i, slide in enumerate(prs.slides):
                    width = prs.slide_width
                    height = prs.slide_height
                    img = Image.new("RGB", (width, height), "white")
                    img_path = os.path.join(tmpdir, f"slide_{i + 1}.png")
                    img.save(img_path)
                    images.append(Image.open(img_path))
            else:
                raise ValueError(
                    "Unsupported file type. Only PDF and PPTX are supported."
                )

            documents = []
            for i, img in enumerate(images):
                if isinstance(img, PpmImageFile):
                    img = img.convert("RGB")
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                img_data_url = f"data:image/png;base64,{img_base64}"

                prompt = [
                    {
                        "type": "text",
                        "text": f"Extract text from this slide for the company {company_name}",
                    },
                    {"type": "image_url", "image_url": {"url": img_data_url}},
                ]
                response = self.agent.run(prompt)
                text = f"Heading: {response.content.heading}\nContent: {response.content.content}"
                LOG.info(f"Parsed page {i + 1} text")
                text = text.strip()
                if text:
                    doc = Document(
                        content=text,
                        name=file_name,
                        meta_data={
                            "company": company_name,
                            "file_name": file_name,
                            "page_number": i + 1,
                        },
                    )
                    documents.append(doc)
            return documents

    @staticmethod
    def upload_to_cloudinary(file_path: str, public_id: str = None) -> str:
        """
        Uploads a file to Cloudinary and returns the public URL.
        """
        result = cloudinary.uploader.upload(
            file_path, resource_type="raw", public_id=public_id
        )
        return result["secure_url"]

    @staticmethod
    def download_from_cloudinary(url: str, save_path: str) -> None:
        """
        Downloads a file from a Cloudinary public URL and saves it to the specified local path.
        """
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


if __name__ == "__main__":
    load_dotenv()
    app_settings = get_app_settings()
    model = get_model(app_settings.llm_config)
    document_processing_engine = DocumentProcessingEngine(
        model, app_settings.storage_config
    )
    print(app_settings.storage_config)
    result = document_processing_engine.extract_text(
        "/Users/ashish_kumar/Downloads/OIX Lab 2 Hackathon Slides.pdf",
        "OIX Lab 2 Hackathon Slides.pdf",
    )
    print(result)
