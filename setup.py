#!/usr/bin/env python3
"""
Setup script for AI-Based Classroom Attendance System
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def setup_project():
    """Setup the project environment"""
    print("🚀 Setting up AI-Based Classroom Attendance System")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Create directories
    directories = [
        "uploads/students",
        "uploads/classes", 
        "static",
        "alembic/versions"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Copy environment file
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            run_command("cp .env.example .env", "Creating environment file")
            print("⚠️  Please edit .env file with your configuration")
        else:
            print("⚠️  .env.example not found, skipping environment setup")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies")
        return False
    
    # Initialize database
    if not run_command("alembic revision --autogenerate -m 'Initial migration'", "Creating initial migration"):
        print("⚠️  Migration creation failed, continuing...")
    
    if not run_command("alembic upgrade head", "Setting up database"):
        print("⚠️  Database setup failed, continuing...")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📖 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run: python run_dev.py")
    print("3. Open: http://localhost:8000/docs")
    print("\n📚 For more information, see README.md")
    
    return True

if __name__ == "__main__":
    success = setup_project()
    sys.exit(0 if success else 1)
