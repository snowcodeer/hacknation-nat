# AeroCraft - AI-Powered Aerospace CAD Web Application

A full-stack web application for generating, modifying, and exporting 3D CAD models of aerospace components using AI.
- Demo video: https://youtu.be/xMromFDNgXw

## Tech Stack

### Frontend
- **SvelteKit** - Full-stack Svelte framework with routing and SSR
- **Threlte** - Declarative Three.js integration for Svelte
- **Three.js** - 3D rendering engine (WebGL)
- **TypeScript** - Type-safe development

### Backend
- **Python 3.11+** - Backend runtime
- **FastAPI** - High-performance async API framework
- **OpenAI API** - GPT-4 for parameter extraction, DALL-E for image processing
- **Trimesh** - 3D mesh processing and STL export
- **pythonOCC** - OpenCascade wrapper for STEP/IGES export

## Project Structure

```
hacknation-nat/
├── frontend/                 # SvelteKit application
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/  # Svelte components
│   │   │   │   ├── 3d/      # Threlte 3D components
│   │   │   │   ├── ui/      # UI components
│   │   │   │   └── editor/  # Parametric editor components
│   │   │   ├── stores/      # Svelte stores for state
│   │   │   ├── services/    # API clients
│   │   │   └── types/       # TypeScript types
│   │   ├── routes/          # SvelteKit routes
│   │   └── app.html
│   ├── static/
│   ├── package.json
│   └── svelte.config.js
│
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/             # API routes
│   │   │   ├── generation.py
│   │   │   ├── export.py
│   │   │   └── images.py
│   │   ├── services/
│   │   │   ├── ai_service.py      # OpenAI integration
│   │   │   ├── geometry_service.py # 3D geometry generation
│   │   │   └── export_service.py   # CAD export
│   │   ├── models/          # Pydantic models
│   │   ├── core/            # Config and utilities
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── README.md
└── .gitignore
```

## Features

### MVP (Phase 1)
- ✅ Text-to-3D generation (natural language → parametric models)
- ✅ Image reference viewer (upload and display reference images)
- ✅ Parametric controls (real-time dimension editing)
- ✅ CAD export (STL, STEP, IGES formats)

### Future Enhancements
- Image-to-3D reconstruction
- Version control and revision history
- Collaborative editing
- Cloud storage integration
- Advanced aerodynamic analysis
- Multi-part assemblies

## Quick Start

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.11+
- OpenAI API key

### Setup

1. **Clone and navigate to project**
```bash
cd hacknation-nat
```

2. **Set up backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
```

3. **Set up frontend**
```bash
cd ../frontend
npm install
```

4. **Run development servers**

Terminal 1 (Backend):
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

5. **Open browser**
Navigate to `http://localhost:5173`

## API Endpoints

### Generation
- `POST /api/generate/from-text` - Generate 3D model from text description
- `POST /api/generate/update-parameters` - Update model with new parameters

### Export
- `POST /api/export/stl` - Export model as STL
- `POST /api/export/step` - Export model as STEP
- `POST /api/export/iges` - Export model as IGES

### Images
- `POST /api/images/upload` - Upload reference image
- `GET /api/images/{id}` - Retrieve reference image

## Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run check        # Type checking
```

### Backend Development
```bash
cd backend
uvicorn app.main:app --reload  # Start with hot reload
pytest                         # Run tests
```

## Architecture

### Text-to-3D Pipeline
1. User enters text description (e.g., "delta wing with 45° sweep, 2m span")
2. FastAPI sends to OpenAI GPT-4 with aerospace engineering prompt
3. GPT-4 extracts structured parameters (wing type, dimensions, angles)
4. Geometry service generates 3D mesh using parametric templates
5. Frontend receives mesh data and renders with Threlte
6. User can adjust parameters in real-time

### Data Flow
```
User Input (Text/Image)
    ↓
Frontend (SvelteKit)
    ↓
API (FastAPI)
    ↓
AI Service (OpenAI) → Parameters
    ↓
Geometry Service → 3D Mesh
    ↓
Export Service → CAD Files
    ↓
Frontend (Threlte) → 3D Viewer
```

## License

MIT
