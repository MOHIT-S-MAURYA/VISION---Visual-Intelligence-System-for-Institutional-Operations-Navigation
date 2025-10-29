#!/bin/bash

echo "🚀 Starting Face Recognition Attendance System..."

# Activate virtual environment
source venv/bin/activate

# Start Django backend
echo "📦 Starting Django backend on port 8000..."
cd backend
python manage.py runserver &
DJANGO_PID=$!
cd ..

# Wait a moment for Django to start
sleep 2

echo "✅ Backend services started!"
echo "📍 Django API: http://localhost:8000"
echo ""
echo "ℹ️  To start AI service, run: cd ai_service && python main.py"
echo "ℹ️  To start Frontend, run: cd frontend && npm start"
echo ""
echo "⏹️  Press Ctrl+C to stop all services"

# Wait for user interrupt
wait $DJANGO_PID
