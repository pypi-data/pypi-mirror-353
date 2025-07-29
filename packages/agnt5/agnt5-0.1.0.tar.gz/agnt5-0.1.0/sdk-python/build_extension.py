#!/usr/bin/env python3
"""
Build script for the AGNT5 Python SDK with Rust extension.

This script builds the PyO3 extension using Maturin and installs
it in development mode for testing.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and print output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result

def main():
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    print("Building AGNT5 Python SDK with Rust core...")
    
    # Check if maturin is installed
    try:
        run_command(["maturin", "--version"])
    except FileNotFoundError:
        print("Maturin not found. Installing...")
        run_command([sys.executable, "-m", "pip", "install", "maturin[patchelf]"])
    
    # Build and install in development mode
    print("\nBuilding and installing in development mode...")
    run_command(["maturin", "develop", "--release"], cwd=script_dir)
    
    print("\nBuild completed successfully!")
    print("You can now import agnt5 in Python:")
    print("  import agnt5")
    print("  worker = agnt5.get_worker('my-service')")
    
    # Test the installation
    print("\nTesting installation...")
    try:
        result = run_command([sys.executable, "-c", "import agnt5; print('✓ agnt5 imported successfully')"])
        result = run_command([sys.executable, "-c", "import agnt5; print(f'Rust core available: {agnt5._rust_core_available}')"])
        
        if result.returncode == 0:
            print("✓ Installation test passed!")
        else:
            print("✗ Installation test failed!")
            return 1
            
    except Exception as e:
        print(f"✗ Installation test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())