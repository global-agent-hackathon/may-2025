"""
Pytest configuration file
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path so we can import core modules
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir)) 