from agno.tools.duckduckgo import DuckDuckGoTools
from platformdirs import (
    user_documents_dir,
    user_desktop_dir,
    user_downloads_dir,
    user_pictures_dir,
    user_videos_dir,
    user_music_dir,
    user_data_dir,
    user_cache_dir,
    user_runtime_dir,
)
import subprocess
import os
import platform


class AgentTools:
    @staticmethod
    def searchWeb():
        return DuckDuckGoTools()
    
    @staticmethod
    def getOS():
        return platform.system()

    @staticmethod
    def runMacTerminalCommand(command: str) -> str:
        """
            Executes a terminal command on macOS and returns its output.

            This function uses the subprocess module to run the given shell command,
            capture its standard output, and return it as a string. If the command
            produces no output, an empty string is returned.

            Parameters:
                command (str): The shell command to execute (e.g., 'ls -la ~/Documents').

            Returns:
                str: The standard output of the executed command, stripped of leading/trailing whitespace.

            Note:
                - This function uses `shell=True`, so avoid passing untrusted user input directly to it,
                as it can lead to shell injection vulnerabilities.
                - If you need to capture standard error, use `result.stderr` instead of `result.stdout`.
        """

        shell_path = os.environ.get("SHELL", "/bin/zsh")
        

        full_command = f'''
        source ~/.zshrc >/dev/null 2>&1;
        source ~/.zprofile >/dev/null 2>&1;
        {command}
        '''
        result = subprocess.run(
            [shell_path, "-i", "-c", full_command],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    @staticmethod
    def runWindowsTerminalCommand(command: str) -> str:
        """
        Executes a PowerShell command on Windows and returns its output.

        This function uses the subprocess module to run the given PowerShell command,
        capture its standard output, and return it as a string. If the command
        produces no output, an empty string is returned.

        Parameters:
            command (str): The PowerShell command to execute (e.g., 'Get-ChildItem "C:\\Users\\Public\\Desktop"').

        Returns:
            str: The standard output of the executed command, stripped of leading/trailing whitespace.

        Note:
            - Avoid passing untrusted user input directly, as PowerShell supports powerful shell expressions.
            - If you need to capture standard error, use result.stderr.
        """
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                shell=True  # Required for Windows PowerShell to launch correctly in some environments
            )
            return result.stdout.strip()
        except Exception as e:
            return f"PowerShell execution error: {str(e)}"

    @staticmethod
    def getFolderLocation(system_folder: str):
        """
        Returns the full path to a standard user folder such as Documents, Desktop, Downloads, etc.

        Supported values (case-insensitive):
        - "documents"
        - "desktop"
        - "downloads"
        - "pictures"
        - "videos"
        - "music"
        - "appdata"      → User's application data/config directory
        - "cache"        → User's cache directory
        - "runtime"      → User's runtime directory

        Returns:
            str: Full path to the specified folder, or None if invalid input.
        """
        match system_folder.lower():
            case "documents":
                return user_documents_dir()
            case "desktop":
                return user_desktop_dir()
            case "downloads":
                return user_downloads_dir()
            case "pictures":
                return user_pictures_dir()
            case "videos":
                return user_videos_dir()
            case "music":
                return user_music_dir()
            case "appdata":
                return user_data_dir()
            case "cache":
                return user_cache_dir()
            case "runtime":
                return user_runtime_dir()
            case _:
                return None
