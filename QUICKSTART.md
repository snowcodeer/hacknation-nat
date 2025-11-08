# AeroCraft - Quick Start Guide

Get up and running with AeroCraft in 5 minutes!

## Prerequisites

- **Node.js 18+** and npm
- **Python 3.11+**
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))

## Step 1: Clone and Setup Environment

```bash
# Navigate to project directory
cd hacknation-nat

# Set up environment variables
cd backend
cp .env.example .env
```

**Edit `.env` and add your OpenAI API key:**
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Step 2: Backend Setup (Python + FastAPI)

```bash
# From the backend directory
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be running at: **http://localhost:8000**
- API docs at: **http://localhost:8000/docs**

## Step 3: Frontend Setup (SvelteKit + Threlte)

Open a **new terminal** window:

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend will be running at: **http://localhost:5173**

## Step 4: Try It Out!

1. Open your browser to **http://localhost:5173**
2. You'll see the AeroCraft interface with:
   - Left panel: Text input, parameters, reference images, export
   - Center: 3D viewer (with a placeholder wing)

### Try These Examples:

**Text-to-3D Generation:**
- Type: `"Delta wing with 45° sweep, 2m span"`
- Click "Generate 3D Model"
- Watch as AI extracts parameters and generates the 3D mesh!

**Parametric Controls:**
- After generating a model, adjust the sliders:
  - Span, chord, sweep angle, thickness, dihedral
- Click "Update Model" to see changes in real-time

**Export:**
- Click on any export format (STL, STEP, IGES)
- STL export works out of the box
- STEP/IGES require additional setup (see main README)

## Troubleshooting

### Backend won't start
- **Check Python version:** `python --version` (must be 3.11+)
- **Check OpenAI API key:** Make sure it's set in `.env`
- **Port already in use:** Try a different port with `--port 8001`

### Frontend won't start
- **Check Node version:** `node --version` (must be 18+)
- **Clear cache:** Delete `node_modules` and run `npm install` again
- **Port already in use:** Edit `vite.config.ts` to change port

### CORS errors
- Make sure backend is running on port 8000
- Check `backend/app/core/config.py` CORS settings

### 3D model not rendering
- Open browser console (F12) for errors
- Check that Threlte dependencies installed correctly
- Try refreshing the page

## What's Next?

- Read the full [README.md](README.md) for architecture details
- Explore the [API documentation](http://localhost:8000/docs)
- Customize wing parameters and experiment
- Upload reference images
- Export models to your favorite CAD software

## Need Help?

- Check the [README.md](README.md) for detailed information
- Review the API docs at `/docs` endpoint
- Check console logs for errors

Enjoy building aerospace models with AI!
