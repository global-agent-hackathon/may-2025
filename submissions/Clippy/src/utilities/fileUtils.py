import os
import platform


class FileUtils:
    @staticmethod
    def getExtension(path: str) -> str:
        _, ext = os.path.splitext(path)
        return ext

    @staticmethod
    def getFilename(path: str) -> str:
        return os.path.basename(path)

    @staticmethod
    def isExecutable(path: str) -> bool:
        if platform.system() == "Darwin":
            if FileUtils.getExtension(path) == ".app":
                return True
            else:
                return False
        elif platform.system() == "Windows":
            if FileUtils.getExtension(path) == ".exe":
                return True
            else:
                return False
        else:
            raise Exception(
                f"The app is not configure for {platform.system()}")
