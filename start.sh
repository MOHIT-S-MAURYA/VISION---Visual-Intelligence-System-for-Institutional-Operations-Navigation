#!/bin/bash

echo "🚀 Starting Face Recognition Attendance System..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $DJANGO_PID $AI_PID $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Start Django backend
echo "📦 Starting Django backend on port 8000..."
cd backend
python manage.py runserver 2>&1 | sed 's/^/[BACKEND] /' &
DJANGO_PID=$!
cd ..

# Wait a moment for Django to start
sleep 2

# Start AI Service
echo "🤖 Starting AI Service (FastAPI) on port 8001..."
cd ai_service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload 2>&1 | sed 's/^/[AI-SERVICE] /' &
AI_PID=$!
cd ..

# Wait a moment for AI service to start
sleep 2

# Start Frontend
echo "⚛️  Starting React Frontend on port 3000..."
cd frontend
npm run dev 2>&1 | sed 's/^/[FRONTEND] /' &
FRONTEND_PID=$!
cd ..

# Wait for all services to initialize
sleep 3

echo ""
echo "✅ All services started successfully!"
echo ""
echo "📍 Access URLs:"
echo "   🌐 Frontend:    http://localhost:3000"
echo "   🔗 Backend API: http://localhost:8000"
echo "   🤖 AI Service:  http://localhost:8001"
echo "   📚 API Docs:    http://localhost:8001/docs"
echo ""
echo "📊 Service Status:"
echo "   Backend PID:  $DJANGO_PID"
echo "   AI Service:   $AI_PID"
echo "   Frontend:     $FRONTEND_PID"
echo ""
echo "⏹️  Press Ctrl+C to stop all services"
echo ""

# Wait for all processes
wait $DJANGO_PID $AI_PID $FRONTEND_PID
