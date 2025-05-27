from youtube_transcript_api import YouTubeTranscriptApi
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.openai import OpenAIEmbedder
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from typing import List
from pytube import YouTube
from langdetect import detect
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class LanguageTutorRepository:
    """
    A repository for managing YouTube transcripts in LanceDB for language tutoring.

    This class allows ingestion of YouTube video transcripts (fetched via YouTubeTranscriptAPI),
    stores them into a LanceDB vector database, and provides search functionality.
    """

    def __init__(self, language_code: str = "fr") -> None:
        """
        Initialize the LanguageTutorRepository with the specified language code.

        Args:
            language_code (str): The target language code (e.g., "fr" for French). Default is "fr".
        """
        self.console = Console()
        self.language_code: str = language_code

        self.current_dir: Path = Path(__file__).parent.parent.parent.parent.resolve()
        self.tmp_dir: Path = self.current_dir / "tmp"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        self.vector_db: LanceDb = LanceDb(
            uri=str(self.tmp_dir / "lancedb"),
            table_name=f"lang_{language_code}_docs",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-large"),
        )

    def ingest_youtube_video(self, video_id: str) -> None:
        """
        Fetch the transcript of a YouTube video, detect its language, and store it in LanceDB.

        Args:
            video_id (str): The unique identifier of the YouTube video.
        """
        try:
            self.console.print(
                f"[bold blue]Starting ingestion for video: {video_id}[/bold blue]"
            )

            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            title = yt.title
            self.console.print(f"[bold cyan]Video Title:[/bold cyan] {title}")

            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            logger.info(f"Fetched {len(transcript)} transcript entries.")

            # Detect language from a sample of the transcript
            sample_text: str = " ".join([entry["text"] for entry in transcript[:10]])
            detected_lang: str = detect(sample_text)
            self.console.print(
                f"[bold green]Detected Language:[/bold green] {detected_lang}"
            )

            inserted_count: int = 0
            for entry in transcript:
                text: str = entry["text"].strip()
                if text:
                    self.vector_db.insert(
                        text=text,
                        metadata={
                            "start": entry["start"],
                            "video_id": video_id,
                            "video_title": title,
                            "language": detected_lang,
                        },
                    )
                    inserted_count += 1

            self.console.print(
                f"[bold green]Ingested {inserted_count} entries successfully.[/bold green]"
            )
            logger.info(f"Ingested {inserted_count} transcript chunks for {video_id}.")

        except Exception as e:
            logger.error(f"Failed to ingest YouTube video {video_id}: {str(e)}")
            self.console.print(
                f"[bold red]Failed to ingest YouTube video: {e}[/bold red]"
            )

    def search_knowledge(self, query: str) -> List[str]:
        """
        Search the LanceDB for content relevant to the given query.

        Args:
            query (str): The search query string.

        Returns:
            List[str]: A list of content previews matching the query.
                       If an error occurs, returns a list with an error message.
        """
        try:
            results = self.vector_db.search(query)
            formatted_results: List[str] = []
            for result in results:
                content: str = getattr(result, "content", "")
                content = " ".join(content.split())
                preview: str = content[:500] + "..." if len(content) > 500 else content
                formatted_results.append(preview)
            return formatted_results
        except Exception as e:
            logger.error(f"Error during search_knowledge: {str(e)}")
            return ["Error searching knowledge base"]

    def get_concept_explanation(self, query: str) -> str:
        """
        Retrieve the most relevant explanation for a given query.

        Args:
            query (str): The topic or question to explain.

        Returns:
            str: The top search result explanation or an error message.
        """
        try:
            results: List[str] = self.search_knowledge(query)
            if results:
                return results[0]
            return "No relevant information found."
        except Exception as e:
            logger.error(f"Error during get_concept_explanation: {str(e)}")
            return "Error retrieving concept explanation."
