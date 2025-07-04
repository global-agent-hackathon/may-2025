import platform
import subprocess
import os
from utilities.getResourcePath import get_asset_path

class SearchUtils:
    @staticmethod
    def search_files(query: str) -> list[str]:
        system = platform.system()

        if system == "Darwin":
            res = SearchUtils.macos_search_files(query)
            return res
        elif system == "Windows":
            res = SearchUtils.windows_search_files(query)
            return res
        return []
    

    @staticmethod
    def macos_search_files(query: str):
        try:
            result = subprocess.run(
                [
                    "mdfind",
                    f'(kMDItemDisplayName == "*{query}*"cd) || (kMDItemPath == "*{query}*"cd)'
                ],
                capture_output=True,
                text=True
            )

            all_results = result.stdout.strip().splitlines()

            # Filter out paths that contain "/Library/"
            filtered_results = [
                path for path in all_results
                if "/Library/" not in path and not path.startswith("/Library/")
            ]

            if len(filtered_results) > 100:
                return filtered_results[:100]

            return filtered_results

        except Exception as e:
            return []
    @staticmethod
    def windows_search_files(query: str):
        es_path = get_asset_path(r"everything-cli\es.exe")
        max_results: int = 100

        # Forbidden directories (case-insensitive)
        forbidden_dirs = [
            r"C:\Windows",
            r"C:\Windows\System32",
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"C:\$Recycle.Bin",
            r"C:\ProgramData",
            r"C:\Users\Default",
            r"C:\Recovery",
            r"C:\System Volume Information",
            r"C:\AddData"
        ]

        # Exception: Start Menu paths (whitelist)
        allowed_exceptions = [
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")
        ]

        try:
            result = subprocess.run(
                [es_path, query, "-max-results", str(max_results)],
                capture_output=True,
                text=True,
                shell=True
            )
            raw_paths = result.stdout.strip().splitlines()

            safe_paths = []
            for path in raw_paths:
                lower_path = path.lower()

                # Allow if it's inside one of the exception paths
                if any(lower_path.startswith(exc.lower()) for exc in allowed_exceptions):
                    safe_paths.append(path)
                    continue

                # Otherwise, reject if it starts with a forbidden dir
                if any(lower_path.startswith(fbd.lower()) for fbd in forbidden_dirs):
                    continue

                # All other paths are safe
                safe_paths.append(path)

            return safe_paths

        except Exception as e:
            print(f"Error running es.exe: {e}")
            return []