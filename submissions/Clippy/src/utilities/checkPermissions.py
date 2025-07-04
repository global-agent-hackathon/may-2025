import platform
import os
import subprocess


class CheckPermission:
    @staticmethod
    def checkDiskPermission():
        system = platform.system()
        def hasFullAccess() -> bool:

            if system == "Darwin":
                try:
                    protected_folder = os.path.expanduser("~/Library/Mail")
                    if os.path.exists(protected_folder):
                        _ = os.listdir(protected_folder)
                    return True
                except PermissionError:
                    return False
                except Exception:
                    return False
            else:
                return False
        if not hasFullAccess() and system == "Darwin":
            subprocess.run(
                ["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"])
