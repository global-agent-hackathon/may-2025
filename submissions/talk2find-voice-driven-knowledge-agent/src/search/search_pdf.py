import logging
import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional

import pdf2image
import pypandoc  # type: ignore
from agno.embedder.google import GeminiEmbedder  
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv 
from PIL import Image

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)


class PDFSearcher:
    def __init__(self, search_directory: str, recreate_knowledge_base: bool = False):
        """Class for searching PDF files (also handles DOCX by converting to temporary PDF)

        Args:
            search_directory: Target directory for search (containing PDF and DOCX files)
            recreate_knowledge_base: If True, delete existing knowledge base and rebuild
        """

        self.search_directory = os.path.abspath(search_directory)  # Normalize search_directory
        self.recreate_knowledge_base = recreate_knowledge_base
        self.temporary_pdf_files: List[str] = []  # Initialize temporary PDF file list
        self.source_mapping: Dict[str, Dict[str, Any]] = {}  # Map temporary PDF to original DOCX info

        if not os.path.isdir(self.search_directory):
            raise ValueError(
                f"Specified search directory not found: {self.search_directory}"
            )

        self.knowledge_base = self._initialize_knowledge_base(
            recreate=self.recreate_knowledge_base
        )

    def _initialize_knowledge_base(self, recreate: bool) -> Optional[PDFKnowledgeBase]:
        """Initialize agno Knowledge Base and load data
        Targets PDF and DOCX files (converted to temporary PDF) in the specified directory.
        """
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.error("Environment variable GOOGLE_API_KEY is not set.")
            # Handle errors in main or calling function when needed
            raise ValueError("Environment variable GOOGLE_API_KEY is not set.")

        # Remove old temporary directories if they exist
        for item in os.listdir(self.search_directory):
            item_path = os.path.join(self.search_directory, item)
            if os.path.isdir(item_path) and item.startswith("_temp_docx_conv_"):
                try:
                    shutil.rmtree(item_path)
                    logger.info(f"Removed old temporary directory: {item_path}")
                except Exception as e:
                    logger.error(f"Failed to remove old temporary directory ({item_path}): {e}")

        vector_db = LanceDb(
            uri="tmp/lancedb_pdf_and_docx",
            table_name="docs_gemini_hybrid",
            search_type=SearchType.hybrid,
            embedder=GeminiEmbedder(api_key=google_api_key),
        )

        # Explore files in the search target directory
        all_files_to_load: List[str] = []  # List of PDF paths to actually load into KnowledgeBase
        self.temporary_pdf_files = []  # Initialize
        self.source_mapping = {}  # Initialize
        self.temp_docx_pdf_subdir: str | None = None

        # Create temporary directory to save PDFs converted from DOCX
        # Exists only while PDFSearcher instance is alive
        # Delete the temporary subdirectory when `PDFSearcher` ends
        self.temp_docx_pdf_subdir = tempfile.mkdtemp(
            dir=self.search_directory, prefix="_temp_docx_conv_"
        )
        logger.info(f"Created temporary subdirectory for DOCX conversion: {self.temp_docx_pdf_subdir}")

        # PDFKnowledgeBase only looks at one directory, so we have to specify the original directory

        for root, _, files in os.walk(self.search_directory):
            if (
                self.temp_docx_pdf_subdir in root
            ):  # Exclude temporary subdirectory itself from scan (prevent infinite loop)
                continue
            for file in files:
                original_file_path = os.path.join(root, file)
                if file.lower().endswith(".pdf"):
                    # PDF files as-is. Register in source_mapping
                    stem_filename = os.path.splitext(os.path.basename(file))[0]
                    self.source_mapping[stem_filename] = {
                        "original_path": original_file_path,
                        "original_type": "pdf",
                        "is_temporary": False,
                        "display_path": original_file_path,  # Path for display
                        "kb_source_path": original_file_path,  # Path recognized by KB
                    }
                elif file.lower().endswith(".docx"):
                    try:
                        # Convert DOCX to PDF in temporary subdirectory
                        # Ensure uniqueness by adding suffix to original filename
                        relative_docx_path = os.path.relpath(
                            original_file_path, self.search_directory
                        )
                        safe_pdf_filename = relative_docx_path.replace(os.sep, "-").replace(
                            ".docx", ".pdf"
                        )
                        temp_pdf_path = os.path.join(self.temp_docx_pdf_subdir, safe_pdf_filename)

                        os.makedirs(
                            os.path.dirname(temp_pdf_path), exist_ok=True
                        )  # Maintain subdirectory structure

                        logger.info(
                            f"Converting DOCX to temporary PDF: {original_file_path} -> {temp_pdf_path}"
                        )

                        try:
                            # Determine the absolute path to the latex_header_for_lists.tex file
                            current_script_dir = os.path.dirname(os.path.abspath(__file__))
                            header_file_path = os.path.join(
                                current_script_dir, "latex_header_for_lists.tex"
                            )

                            pypandoc.convert_file(
                                original_file_path,
                                "pdf",
                                outputfile=temp_pdf_path,
                                extra_args=[
                                    "--pdf-engine=xelatex",
                                    "-V",
                                    "mainfont=Times New Roman",  # English font
                                    "-V",
                                    "CJKmainfont=Hiragino Sans",  # Japanese font
                                    f"--include-in-header={header_file_path}",
                                ],
                            )
                            logger.info(
                                f"Successfully converted DOCX to temporary PDF (via pypandoc): {temp_pdf_path}"
                            )
                        except RuntimeError as e_runtime_pandoc:
                            # pypandoc.exceptions.PandocNotFoundError may be
                            # a subclass of RuntimeError, so catch RuntimeError
                            logger.error(
                                f"pypandoc runtime error ({original_file_path}):"
                                + f"{e_runtime_pandoc}."
                                + "Please check if pandoc is installed and in PATH."
                            )
                            continue
                        except Exception as e_pandoc:
                            logger.error(
                                "Failed to convert DOCX to PDF with pypandoc"
                                + f"({original_file_path}): {e_pandoc}"
                            )
                            continue  # Continue to next file

                        all_files_to_load.append(temp_pdf_path)
                        self.temporary_pdf_files.append(temp_pdf_path)
                        stem_filename = os.path.splitext(os.path.basename(safe_pdf_filename))[0]
                        self.source_mapping[stem_filename] = {
                            "original_path": original_file_path,  # Original DOCX path
                            "original_type": "docx",
                            "is_temporary": True,
                            "display_path": temp_pdf_path,  # User change: display converted PDF path
                            "kb_source_path": temp_pdf_path,  # Path recognized by KB
                            "is_temporary_source": True,  # Whether this result is from temporary file
                        }
                    except Exception as e:
                        logger.error(f"Failed to convert DOCX to temporary PDF ({original_file_path}): {e}")

        knowledge_base = PDFKnowledgeBase(
            path=self.search_directory,  # Use normalized search_directory
            vector_db=vector_db,
        )
        logger.info(
            f"Agno Knowledge Base (Gemini Embedder, PDF+temporary DOCX) instance creation completed "
            f"({self.search_directory})"
        )

        try:
            knowledge_base.load(
                recreate=recreate
            )  # Load PDFs in search_directory here (including temporary PDFs)
        except Exception as e:
            logger.error(f"Error occurred while loading knowledge base: {e}")
            self.cleanup_temporary_files()  # Clean up temporary files on error
            raise  # Re-raise error

        return knowledge_base

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        logger.info(f"Searching knowledge base for '{query}' (retrieving {top_k} results)...")

        if self.knowledge_base is None:
            logger.warning("Knowledge base is not initialized. Returning empty results.")
            return []

        try:
            search_results = self.knowledge_base.search(query, top_k)
        except Exception as e:
            logger.error(f"Error during knowledge base search: {e}")
            return []

        logger.info(f"Retrieved {len(search_results)} search results")
        formatted_results = []
        for doc in search_results:
            meta_data = getattr(doc, "meta_data", {})
            page_number = meta_data.get("page", None)
            doc_name = getattr(doc, "name", None)

            raw_source_path = None
            if doc_name:
                source_entry = self.source_mapping.get(doc_name)
                if source_entry:
                    raw_source_path = source_entry.get("kb_source_path")
                    display_path = source_entry.get("display_path", raw_source_path)
                    original_type = source_entry.get("original_type", "unknown")
                    original_path = source_entry.get("original_path", raw_source_path)
                    is_temporary_source = source_entry.get("is_temporary", False)
                else:
                    logger.warning(f"Key not found in source_mapping (doc_name: {doc_name}")

            formatted_results.append(
                {
                    "text": doc.content or "",
                    "page": page_number,
                    "file_path": display_path,
                    "original_type": original_type,
                    "original_absolute_path": original_path,
                    "doc_name": doc_name,
                    "score": getattr(doc, "score", None),
                    "is_temporary_source": is_temporary_source,
                }
            )
        return formatted_results

    def get_page_image(self, file_path: str, page_index: int) -> Image.Image | None:
        """Get image of specified page from specified file.
        If file_path is DOCX, get image via temporary PDF.
        """

        if not file_path or not os.path.exists(file_path):
            logger.error(
                "get_page_image: Specified PDF file not found:"
                + f"{file_path} (original file: {file_path})"
            )
            return None

        logger.info(
            f"get_page_image: Getting image of page {page_index + 1} from {file_path} "
            + f"(original file: {file_path})"
        )
        with tempfile.TemporaryDirectory() as temp_image_dir:
            try:
                images = pdf2image.convert_from_path(
                    file_path,
                    first_page=page_index + 1,
                    last_page=page_index + 1,
                    dpi=150,
                    output_folder=temp_image_dir,
                    fmt="png",
                )
                return images[0] if images else None
            except Exception as e:
                logger.error(f"Error during image conversion from PDF ({file_path}): {e}")
                return None

    def cleanup_temporary_files(self) -> None:
        """Delete temporary PDF files converted from DOCX and the temporary subdirectory that contained them"""
        logger.info("Starting cleanup of temporary files...")
        # Cleanup temporary directory (TemporaryDirectory object)

        # Delete temporary subdirectory created in search_directory
        if (
            hasattr(self, "temp_docx_pdf_subdir")
            and self.temp_docx_pdf_subdir
            and os.path.exists(self.temp_docx_pdf_subdir)
        ):
            try:
                shutil.rmtree(self.temp_docx_pdf_subdir)
                logger.info(f"Deleted temporary subdirectory: {self.temp_docx_pdf_subdir}")
            except Exception as e:
                logger.error(
                    f"Failed to delete temporary subdirectory ({self.temp_docx_pdf_subdir}): {e}"
                )
        self.temp_docx_pdf_subdirs = None
        self.temporary_pdf_files = []  # Clear list as well
        self.source_mapping = {}  # Clear mapping as well

    def __del__(self) -> None:
        """Clean up temporary files when PDFSearcher instance is destroyed"""
        self.cleanup_temporary_files()
