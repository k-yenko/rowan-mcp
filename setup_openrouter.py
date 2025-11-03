#!/usr/bin/env python3
"""
Setup script for OpenRouter + Rowan MCP integration.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")

    try:
        # Install using uv if available, otherwise pip
        if subprocess.run(["uv", "--version"], capture_output=True).returncode == 0:
            subprocess.run(["uv", "sync"], check=True)
            print("Dependencies installed using uv")
        else:
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
            print("Dependencies installed using pip")

    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

    return True

def check_environment():
    """Check if environment variables are set."""
    env_file = Path(".env")

    if not env_file.exists():
        print("❌ .env file not found!")
        return False

    required_vars = ["ROWAN_API_KEY", "OPENROUTER_API_KEY"]
    missing_vars = []

    with open(env_file) as f:
        env_content = f.read()

    for var in required_vars:
        if f"{var}=" not in env_content:
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False

    print("✅ Environment variables configured")
    return True

def test_rowan_mcp_server():
    """Test if Rowan MCP server can be started."""
    print("Testing Rowan MCP server...")

    try:
        # Try to import the server to check if dependencies are working
        import rowan_mcp.server
        print("✅ Rowan MCP server can be imported")
        return True
    except ImportError as e:
        print(f"❌ Cannot import Rowan MCP server: {e}")
        return False

def main():
    print("🚀 Setting up OpenRouter + Rowan MCP integration")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Please run this script from the rowan-mcp directory")
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Check environment
    if not check_environment():
        print("\n📝 Please ensure your .env file contains:")
        print("ROWAN_API_KEY=your_rowan_api_key")
        print("OPENROUTER_API_KEY=your_openrouter_api_key")
        print("OPENAI_API_KEY=your_openai_api_key  # Optional fallback")
        sys.exit(1)

    # Test server
    if not test_rowan_mcp_server():
        sys.exit(1)

    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Start your Rowan MCP server:")
    print("   python -m rowan_mcp.server")
    print("")
    print("2. In another terminal, run the OpenRouter client:")
    print("   python openrouter_client.py")
    print("")
    print("3. You can now chat with AI models that have access to your Rowan tools!")
    print("")
    print("💡 Example queries:")
    print("- 'Look up information about caffeine'")
    print("- 'Run a basic calculation on water (H2O)'")
    print("- 'Find conformers for ethanol'")

if __name__ == "__main__":
    main()