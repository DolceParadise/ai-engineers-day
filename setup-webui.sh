#!/bin/bash
# Quick setup script to get the web UI running

echo "╔════════════════════════════════════════════════════════╗"
echo "║     KhetSetu Web UI - Quick Start Setup             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Install backend dependencies
echo "📦 Installing Flask dependencies..."
pip install flask flask-cors

# Step 2: Display setup instructions
echo ""
echo "✅ Setup complete! Now run the backend:"
echo ""
echo "   python backend_api.py"
echo ""
echo "This will start the server on http://localhost:5000"
echo ""
echo "📂 Files created:"
echo "   - backend_api.py       (Flask API server with /ask endpoint)"
echo "   - index.html           (Web UI structure)"
echo "   - styles.css           (Web UI styling)"
echo "   - app.js               (Web UI logic)"
echo ""
echo "🚀 To use the Web UI:"
echo "   1. Start backend:  python backend_api.py"
echo "   2. Open browser:   file://$(pwd)/index.html"
echo "   3. Test query:     'What crops should I plant?'"
echo ""
echo "📝 Notes:"
echo "   - The backend currently returns mock data"
echo "   - See FRONTEND_INTEGRATION_GUIDE.md for integration with real main.py"
echo "   - Update app.js API_ENDPOINT if using different port"
echo ""
