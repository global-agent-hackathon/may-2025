import platform
import subprocess
import os


class OpenApp:
    @staticmethod
    def open(path: str):
        os_name = platform.system()
        try:
            if os_name == "Darwin":
                subprocess.run(["open", path])
            elif os_name == "Windows":
                os.startfile(path)
            else:
                raise Exception(
                    f"Not implemented for {os} operating system WIP")
        except Exception as e:
            raise Exception(
                f"Not able to run the application {path} for os {os} due to {e}")
