
import os
import sys


def get_asset_path(relative_path: str) -> str:
    """
    Get the absolute path to an asset, whether the app is running
    from source or as a PyInstaller bundled app (.app/.exe).
    """
    if getattr(sys, 'frozen', False):  # Bundled via PyInstaller
        base_path = sys._MEIPASS  # type: ignore
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
