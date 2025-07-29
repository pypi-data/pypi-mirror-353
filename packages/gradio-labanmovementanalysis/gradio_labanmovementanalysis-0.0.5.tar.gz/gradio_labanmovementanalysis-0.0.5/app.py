#!/usr/bin/env python3
"""
Laban Movement Analysis - Complete Suite
Hugging Face Spaces Deployment

Created by: Csaba Bolyós (BladeSzaSza)
Contact: bladeszasza@gmail.com
GitHub: https://github.com/bladeszasza
LinkedIn: https://www.linkedin.com/in/csaba-bolyós-00a11767/
Hugging Face: https://huggingface.co/BladeSzaSza

Heavy Beta Version - Under Active Development
"""

import sys
from pathlib import Path
import traceback

# Import version info
try:
    from version import __version__, __author__
    print(f"🎭 Laban Movement Analysis v{__version__} by {__author__}")
except ImportError:
    __version__ = "not-found"
    print("🎭 Laban Movement Analysis")

# Add demo directory to path
sys.path.insert(0, str(Path(__file__).parent / "demo"))

try:
    # Import from demo.app to avoid circular import
    from demo.app import create_demo
    
    if __name__ == "__main__":
        print("🚀 Starting Laban Movement Analysis...")
        demo = create_demo()
        
        # Configure for Hugging Face Spaces
        # Try a simpler launch first for debugging
        demo.launch(server_name='0.0.0.0', server_port=7860, mcp_server=True)
        
        
except Exception as e:
    print(f"❌ Error launching demo: {e}")
    print("Full traceback below:")
    print(traceback.format_exc())
    print("Check the logs above for more details.") 