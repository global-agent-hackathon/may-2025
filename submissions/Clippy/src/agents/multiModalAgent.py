from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.file import FileTools
from agno.media import Image, Audio, Video, File


class MultiModalAgent:
    @staticmethod
    def create(apiKey: str, model: str = "gpt-4o"):
        import os

        class _MultiModalAgent:
            def __init__(self, apiKey, model):
                self.apiKey = apiKey
                self.model = model

            async def summarize(self, file_path: str):
                ext = os.path.splitext(file_path)[1].lower()
                if ext == ".pdf":
                    return await self.summarize_pdf(file_path)
                elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"]:
                    return await self.summarize_image(file_path)
                elif ext in [".mp3", ".wav", ".m4a", ".aac", ".ogg"]:
                    return await self.summarize_audio(file_path)
                elif ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
                    return await self.summarize_video(file_path)
                else:
                    # Try to read and summarize raw content for unsupported file types
                    import errno
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            raw_content = f.read()
                        # Use the same Gemini agent instance for raw content summarization
                        agent = Agent(
                            model=Gemini(api_key=self.apiKey, id=self.model),
                            markdown=True,
                        )
                        summary = await agent.arun(f"Summarize the following file content:\n\n{raw_content[:10000]}")
                        return getattr(summary, "content", str(summary))
                    except IsADirectoryError:
                        return "This is a directory or application bundle, not a file. Please select a regular file to summarize."
                    except PermissionError:
                        return "Permission denied. Please select a file you have access to."
                    except OSError as e:
                        if hasattr(e, 'errno') and e.errno == errno.EISDIR:
                            return "This is a directory or application bundle, not a file. Please select a regular file to summarize."
                        elif hasattr(e, 'errno') and e.errno == errno.EACCES:
                            return "Permission denied. Please select a file you have access to."
                        else:
                            return f"Could not read or summarize file: {e}"
                    except Exception as e:
                        return f"Could not read or summarize file: {e}"

            async def summarize_pdf(self, file_path: str):
                # Use Gemini model and FileTools for PDF summarization
                agent = Agent(
                    model=Gemini(api_key=self.apiKey, id=self.model),
                    tools=[FileTools()],
                    markdown=True,
                )
                return await agent.arun(
                    f"Summarize the content of this PDF file.",
                    files=[File(filepath=file_path)]
                )

            async def summarize_image(self, file_path: str):
                agent = Agent(
                    model=Gemini(api_key=self.apiKey, id=self.model),
                    markdown=True,
                )
                return await agent.arun(
                    "Tell me about this local image.",
                    images=[Image(filepath=file_path)]
                )

            async def summarize_audio(self, file_path: str):
                agent = Agent(
                    model=Gemini(api_key=self.apiKey, id=self.model),
                    markdown=True,
                )
                return await agent.arun(
                    "Summarize the content of this audio file.",
                    audios=[Audio(filepath=file_path)]
                )

            async def summarize_video(self, file_path: str):
                agent = Agent(
                    model=Gemini(api_key=self.apiKey, id=self.model),
                    markdown=True,
                )
                return await agent.arun(
                    "Summarize the content of this video file.",
                    videos=[Video(filepath=file_path)]
                )

        return _MultiModalAgent(apiKey, model)
