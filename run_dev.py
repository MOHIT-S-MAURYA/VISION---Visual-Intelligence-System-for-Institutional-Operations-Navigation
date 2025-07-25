#!/usr/bin/env python3
"""
VISION - Visual Intelligence System for Institutional Operations & Navigation
Development Server Runner
"""
import uvicorn
import os
from pathlib import Path

def main():
    """Start VISION development server"""
    
    # Ensure upload directories exist
    directories = [
        "uploads/students",
        "uploads/classes", 
        "static",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("🔍 Starting VISION - Visual Intelligence System")
    print("=" * 60)
    print("📖 System: Visual Intelligence System for Institutional Operations & Navigation")
    print("🔗 Dashboard: http://localhost:8000/")
    print("👤 Register Student: http://localhost:8000/register-student")
    print("📷 Mark Attendance: http://localhost:8000/mark-attendance")
    print("📊 Reports: http://localhost:8000/attendance-reports")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("💚 Health Check: http://localhost:8000/health")
    print("=" * 60)
    print("🚀 Starting server on http://localhost:8000")
    print("📝 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 VISION server stopped")
    except Exception as e:
        print(f"\n❌ Error starting VISION: {e}")

if __name__ == "__main__":
    main()
