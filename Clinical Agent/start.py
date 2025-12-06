"""
Quick Start Script - Launches the Clinical Q&A System
"""

import subprocess
import sys
import os

def main():
    print("=" * 70)
    print("AI-Powered Clinical Q&A and Drug Interaction Validation System")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT: This is a DEMO for educational purposes only!")
    print("    NOT for real medical use.")
    print()
    print("Starting Streamlit application...")
    print("The app will open in your default browser.")
    print()
    print("Press Ctrl+C to stop the server.")
    print("=" * 70)
    print()
    
    # Run streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        print("Thank you for using the Clinical Q&A System!")

if __name__ == "__main__":
    main()
