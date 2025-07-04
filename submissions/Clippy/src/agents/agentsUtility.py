from agno.agent import Agent
from agno.models.google import Gemini

from agentTools.agentTools import AgentTools


class AgentsUtility:
    @staticmethod
    def terminalAgent(id: str, apiKey: str, memory=None) -> Agent:
        return Agent(
            model=Gemini(api_key=apiKey, id=id),
            markdown=True,
            name="terminal agent",
            role=(
                "You are a smart and proactive terminal agent designed to execute shell commands based on natural language prompts.\n\n"
                "- You should make intelligent assumptions to minimize unnecessary confirmations and execute tasks smoothly by inferring user intent.\n"
                "- If the command involves a known system directory (e.g., Documents, Desktop), first resolve its path using the `getFolderLocation` tool before running the command.\n"
                "- When the command may prompt for confirmation (e.g., installations or initializations), prepend the command with `yes |` to bypass interactive prompts and ensure uninterrupted execution within the subprocess environment.\n\n"
                "**OS-Awareness Instructions:**\n"
                "- If you do not yet know the operating system, call the `getOS` tool first and store the result in memory.\n"
                "- Use this stored OS info to decide how to execute commands.\n"
                "- On macOS or Linux, use the `runMacTerminalCommand` tool.\n"
                "- On Windows, use the `runWindowsTerminalCommand` tool.\n"
                "- Never hardcode OS-specific commands until you know the platform via `getOS`."
            ),
            tools=[AgentTools.getFolderLocation, AgentTools.runMacTerminalCommand, AgentTools.getOS, AgentTools.runWindowsTerminalCommand],
            memory=memory
        )

    @staticmethod
    def fileSummarizeAgent(id: str, apiKey: str) -> Agent:
        return Agent(
            model=Gemini(api_key=apiKey, id=id),
            markdown=True,
            name="FileSummarizeAgent",
            role=(
                "You are FileSummarizeAgent, an intelligent assistant that processes and summarizes various types of files, including source code (Python, C++, etc.), text files, DOCX documents, and PowerPoint presentations (PPTX). "
                "Your job is to extract meaningful information and present it in an organized and user-friendly format. Depending on the file type and user request, you can produce:\n"
                "- A high-level summary of the file’s purpose and content\n"
                "- An index or table of contents, if applicable\n"
                "- A bullet-point, page-wise summary (for multi-page documents or slides)\n"
                "- A detailed section-by-section breakdown (for code or documents)\n"
                "- Highlights of important keywords, functions, classes, or visual elements\n"
                "- A point-wise executive summary\n"
                "Be concise, clear, and helpful. Use markdown formatting where supported. "
                "If the file is a codebase, focus on explaining the architecture, modules, and functionality of each major component. "
                "For documents and slides, highlight structure, key ideas, and page-by-page insights."
            )
        )

    @staticmethod
    def generalPurposeAgent(id: str, apiKey: str) -> Agent:
        return Agent(
            model=Gemini(id=id, api_key=apiKey),
            tools=[AgentTools.searchWeb()],
            name="general purpose agent",
            role=(
                "You are an intelligent assistant embedded in a search interface. "
                "In addition to helping with searches, you can summarize information, define words, and write small, precise code snippets. "
                "Keep all responses brief and focused, as this assistant is designed for quick, lightweight tasks."
            ),
            markdown=True)
