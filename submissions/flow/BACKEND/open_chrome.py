import os
import platform
import subprocess
import time
import json
import urllib.request

def is_chrome_running_with_debugging():
    """Check if Chrome is already running with debugging enabled"""
    try:
        response = urllib.request.urlopen('http://localhost:9222/json/version')
        data = json.loads(response.read())
        return True
    except:
        return False

def open_chrome_with_debugging():
    """
    Opens Chrome with remote debugging enabled on port 9222.
    """
    system = platform.system().lower()
    
    # Check if Chrome is already running with debugging
    if is_chrome_running_with_debugging():
        print("Chrome is already running with debugging enabled on port 9222")
        return True
    
    # Define Chrome paths for different operating systems
    chrome_paths = {
        'windows': [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\Application\chrome.exe"
        ],
        'darwin': [  # macOS
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ],
        'linux': [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable"
        ]
    }
    
    # Find Chrome executable
    chrome_path = None
    for path in chrome_paths.get(system, []):
        if os.path.exists(path):
            chrome_path = path
            break
    
    if not chrome_path:
        print("Chrome not found in common locations. Please specify the path to Chrome manually.")
        return False
    
    # Close any existing Chrome instances with debugging port
    try:
        if system == 'windows':
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True)
        else:
            subprocess.run(['pkill', 'chrome'], capture_output=True)
    except:
        pass
    
    # Wait a moment for Chrome to close
    time.sleep(1)
    
    # Open Chrome with remote debugging
    try:
        cmd = [
            chrome_path,
            '--remote-debugging-port=9222',
            '--user-data-dir=' + os.path.join(os.path.expanduser('~'), 'chrome-debug-profile'),
            '--no-first-run',
            '--no-default-browser-check'
        ]
        subprocess.Popen(cmd)
        
        # Wait for Chrome to start and enable debugging
        max_attempts = 10
        for _ in range(max_attempts):
            if is_chrome_running_with_debugging():
                print("Chrome opened with remote debugging enabled on port 9222")
                print("You can now run capture_screenshot.py")
                return True
            time.sleep(1)
        
        print("Chrome started but debugging port not available")
        return False
        
    except Exception as e:
        print(f"Error opening Chrome: {e}")
        return False

if __name__ == "__main__":
    open_chrome_with_debugging() 