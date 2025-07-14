#!/usr/bin/env python3
"""
Final launcher for AI Image Editor with truly persistent server.
"""

import subprocess
import sys
import time
import argparse
import signal
import os
import requests
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import torch
        import diffusers
        import streamlit
        import fastapi
        import requests
        print("✅ All dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def check_model():
    """Check if the FLUX model is available."""
    model_path = os.getenv("MODEL_PATH", "./models/black-forest-labs/FLUX.1-Kontext-dev")
    if Path(model_path).exists():
        print(f"✅ FLUX model found at {model_path}")
        return True
    else:
        print(f"❌ FLUX model not found at {model_path}")
        print("Set MODEL_PATH environment variable")
        return False


def check_server_health(server_url="http://localhost:8888"):
    """Check if the persistent server is running."""
    try:
        response = requests.get(f"{server_url}/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get("ready", False)
        return False
    except:
        return False


def wait_for_server(server_url="http://localhost:8888", timeout=30000):
    """Wait for server to be ready."""
    print("⏳ Waiting for server to load model...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if check_server_health(server_url):
            print("✅ Server is ready!")
            return True
        
        print(".", end="", flush=True)
        time.sleep(2)
    
    print(f"\n❌ Server not ready after {timeout} seconds")
    return False


def start_server():
    """Start the persistent server."""
    print("🚀 Starting persistent server...")
    try:
        subprocess.run([sys.executable, "server.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")


def start_webui():
    """Start the WebUI."""
    print("🌐 Starting Web UI...")
    
    # Check if server is running
    if not check_server_health():
        print("❌ Server not running! Start server first: python server.py")
        return
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "webui.py",
            "--server.address", "0.0.0.0",
            "--server.port", "30700"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Web UI stopped")


def start_both():
    """Start both server and WebUI with proper coordination."""
    print("🎨 AI Image Editor - Persistent Architecture")
    print("=" * 50)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_model():
        sys.exit(1)
    
    print("\n📋 Starting persistent server + WebUI:")
    print("1. Server: Loads model once and stays running")
    print("2. WebUI: Connects via HTTP (no new processes)")
    print("\nPress Ctrl+C to stop everything")
    print("=" * 50)
    
    server_process = None
    webui_process = None
    
    try:
        # Start server
        print("\n🚀 Step 1: Starting persistent server...")
        server_process = subprocess.Popen(
            [sys.executable, "server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Wait for server to be ready
        if not wait_for_server():
            print("❌ Server failed to start properly")
            return
        
        # Start WebUI
        print("\n🌐 Step 2: Starting WebUI...")
        webui_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "webui.py",
            "--server.address", "0.0.0.0",
            "--server.port", "30700"
        ])
        
        print(f"✅ WebUI started at: http://localhost:30700")
        print("\n🎯 System ready!")
        print("- Server: http://localhost:8888 (model loaded)")
        print("- WebUI: http://localhost:30700 (user interface)")
        print("- Each image edit will be FAST (no model reloading)")
        print("\nPress Ctrl+C to stop everything")
        
        # Monitor processes
        while True:
            if server_process.poll() is not None:
                print("❌ Server stopped unexpectedly")
                break
            if webui_process.poll() is not None:
                print("❌ WebUI stopped unexpectedly") 
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
    finally:
        # Cleanup
        if webui_process:
            webui_process.terminate()
            try:
                webui_process.wait(timeout=5)
            except:
                webui_process.kill()
        
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except:
                server_process.kill()
        
        print("✅ All services stopped")


def main():
    """Main launcher entry point."""
    parser = argparse.ArgumentParser(description="AI Image Editor Final Launcher")
    parser.add_argument("command", nargs="?", choices=["server", "webui", "both", "check", "status"], 
                       default="both", help="What to start")
    
    args = parser.parse_args()
    
    if args.command == "check":
        print("🔍 Checking system...")
        deps_ok = check_dependencies()
        model_ok = check_model()
        
        if deps_ok and model_ok:
            print("\n✅ Everything looks good!")
        else:
            print("\n❌ Please fix the issues above")
            sys.exit(1)
    
    elif args.command == "status":
        print("🔍 Checking server status...")
        if check_server_health():
            print("✅ Server is running and ready")
        else:
            print("❌ Server not running or not ready")
    
    elif args.command == "server":
        if not check_dependencies():
            sys.exit(1)
        start_server()
    
    elif args.command == "webui":
        if not check_dependencies():
            sys.exit(1)
        start_webui()
    
    elif args.command == "both":
        start_both()
    
    else:
        print("Usage:")
        print("  python launcher.py server    # Start persistent server")
        print("  python launcher.py webui     # Start WebUI (server must be running)")
        print("  python launcher.py both      # Start both (default)")
        print("  python launcher.py check     # Check dependencies")
        print("  python launcher.py status    # Check server status")


if __name__ == "__main__":
    main()