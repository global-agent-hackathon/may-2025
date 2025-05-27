from dotenv import load_dotenv
import os
from typing import List
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.openai import OpenAIEmbedder
from agno.utils.log import logger
from pathlib import Path
from rich.console import Console

# Load environment variables
load_dotenv()


class PhysicsTutorRepository:
    """
    Repository for managing physics knowledge base and search operations.

    Loads PDF documents into a vector database (LanceDB) for semantic search,
    using OpenAI embeddings for similarity. Provides search functionality and concept explanations.
    """

    def __init__(self) -> None:
        """
        Initialize the PhysicsTutorRepository by setting up the vector database,
        loading physics PDFs, and preparing the knowledge base for search operations.
        """
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. Please check your .env file."
            )

        self.console: Console = Console()
        self.current_dir: Path = Path(__file__).parent.parent.parent.parent.resolve()
        self.tmp_dir: Path = self.current_dir / "tmp"
        self.tmp_dir.mkdir(exist_ok=True)

        self.physics_knowledge: PDFKnowledgeBase = PDFKnowledgeBase(
            path=str(self.current_dir / "learn"),
            vector_db=LanceDb(
                uri=str(self.tmp_dir / "lancedb"),
                table_name="physics_docs",
                search_type=SearchType.hybrid,
                embedder=OpenAIEmbedder(id="text-embedding-3-large"),
            ),
            reader=PDFReader(chunk=True),
            chunk_size=1500,
            chunk_overlap=300,
        )

        try:
            self.console.print(
                "[bold blue]Loading knowledge base with improved embeddings...[/bold blue]"
            )
            self.physics_knowledge.load()
            self.console.print(
                "[bold green]Knowledge base loaded successfully![/bold green]"
            )
            self.console.print(
                "[bold blue]Using text-embedding-3-large model for better search results[/bold blue]"
            )
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            self.console.print("[bold red]Error loading knowledge base[/bold red]")

    def search_knowledge(self, query: str) -> List[str]:
        """
        Search the physics knowledge base for relevant content based on a user's query.

        Args:
            query (str): The search query string (e.g., "Newton's Laws").

        Returns:
            List[str]: A list of relevant content previews matching the query.
                       If an error occurs, a list with an error message is returned.
        """
        try:
            results = self.physics_knowledge.search(query)
            formatted_results: List[str] = []

            for i, result in enumerate(results, 1):
                try:
                    content = result.content
                    content = " ".join(content.split())
                    preview = content[:500] + "..." if len(content) > 500 else content
                    formatted_results.append(preview)
                except Exception as e:
                    logger.error(f"Error processing search result: {str(e)}")
                    formatted_results.append(f"Error processing result {i}")

            return formatted_results
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return ["Error searching knowledge base"]

    def get_concept_explanation(self, query: str) -> str:
        """
        Retrieve a concise explanation for a physics concept based on a search query.

        Args:
            query (str): The search query string (e.g., "Ohm's Law").

        Returns:
            str: The most relevant explanation found, or a fallback message if no match is found.
        """
        try:
            results = self.search_knowledge(query)
            if results:
                return results[0]
            return "No relevant information found."
        except Exception as e:
            logger.error(f"Error getting concept explanation: {str(e)}")
            return "Error retrieving concept explanation."
