# Development Guide

## Project Structure Explained

### Frontend (`/frontend`)

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── 3d/
│   │   │   │   ├── Viewer3D.svelte      # Main 3D canvas wrapper
│   │   │   │   ├── Scene.svelte          # 3D scene with camera, lights, grid
│   │   │   │   └── AeroModel.svelte      # Renders the 3D wing mesh
│   │   │   ├── ui/
│   │   │   │   ├── TextPrompt.svelte     # Text-to-3D input component
│   │   │   │   ├── ImageReference.svelte # Image upload component
│   │   │   │   └── ExportPanel.svelte    # Export buttons (STL/STEP/IGES)
│   │   │   └── editor/
│   │   │       └── ParametricControls.svelte # Sliders for wing parameters
│   │   ├── stores/
│   │   │   └── modelStore.ts             # Svelte stores for state management
│   │   ├── services/
│   │   │   └── apiService.ts             # API client for backend
│   │   └── types/
│   │       └── model.ts                  # TypeScript type definitions
│   ├── routes/
│   │   ├── +layout.svelte                # Root layout (imports CSS)
│   │   └── +page.svelte                  # Main page (workspace layout)
│   └── app.css                           # Global styles
└── package.json
```

### Backend (`/backend`)

```
backend/
├── app/
│   ├── api/
│   │   ├── generation.py    # POST /api/generate/from-text, /update-parameters
│   │   ├── export.py        # POST /api/export/{stl|step|iges}
│   │   └── images.py        # POST /api/images/upload, GET /api/images/{id}
│   ├── services/
│   │   ├── ai_service.py       # OpenAI integration for parameter extraction
│   │   ├── geometry_service.py # 3D mesh generation from parameters
│   │   └── export_service.py   # CAD file export (STL, STEP, IGES)
│   ├── models/
│   │   └── schemas.py          # Pydantic models for validation
│   ├── core/
│   │   └── config.py           # Settings and environment variables
│   └── main.py                 # FastAPI app initialization
└── requirements.txt
```

## Key Technologies

### Frontend Stack
- **SvelteKit**: Full-stack Svelte framework with routing
- **Threlte**: Declarative Three.js wrapper for Svelte
- **Three.js**: WebGL-based 3D rendering
- **TypeScript**: Type safety

### Backend Stack
- **FastAPI**: Modern async Python web framework
- **OpenAI API**: GPT-4 for parameter extraction
- **Trimesh**: 3D mesh processing and manipulation
- **NumPy**: Numerical computations for geometry

## API Endpoints

### Generation
- **POST /api/generate/from-text**
  - Body: `{ "prompt": "delta wing with 45° sweep" }`
  - Returns: `Model3D` with geometry and parameters

- **POST /api/generate/update-parameters**
  - Body: `{ "parameters": { ... } }`
  - Returns: Updated `Model3D`

### Export
- **POST /api/export/stl**
  - Body: `{ "model_id": "...", "options": {...} }`
  - Returns: Binary STL file

- **POST /api/export/step** (Not yet implemented)
- **POST /api/export/iges** (Not yet implemented)

### Images
- **POST /api/images/upload**
  - Body: FormData with image file
  - Returns: `{ "success": true, "url": "/api/images/..." }`

- **GET /api/images/{filename}**
  - Returns: Image file

## Data Flow

### Text-to-3D Generation

1. **User inputs text** → `TextPrompt.svelte`
2. **Frontend calls API** → `apiService.generateFromText()`
3. **Backend receives request** → `/api/generate/from-text`
4. **AI extracts parameters** → `ai_service.extract_parameters_from_text()`
   - Sends prompt to OpenAI GPT-4
   - Receives structured JSON with wing parameters
5. **Generate 3D mesh** → `geometry_service.create_model_from_parameters()`
   - Creates vertices and faces based on parameters
   - Returns `Model3D` with geometry data
6. **Return to frontend** → JSON response
7. **Update store** → `modelStore.setModel()`
8. **Render in 3D** → `AeroModel.svelte` creates Three.js mesh

### Parameter Updates

1. **User adjusts slider** → `ParametricControls.svelte`
2. **Store updates** → `updateParameter(key, value)`
3. **User clicks "Update Model"** → Calls API
4. **Backend regenerates mesh** → Same as step 5 above
5. **Frontend re-renders** → 3D view updates

## State Management (Svelte Stores)

```typescript
// Current 3D model
currentModel: Writable<Model3D | null>

// Editable parameters
parameters: Writable<AeroParameters>

// UI state
isGenerating: Writable<boolean>
generationError: Writable<string | null>

// Reference image
referenceImage: Writable<string | null>
```

## Adding New Wing Types

To add a new wing type (e.g., "biplane"):

1. **Update types** (`frontend/src/lib/types/model.ts`):
```typescript
wingType: 'delta' | 'swept' | 'straight' | 'tapered' | 'biplane'
```

2. **Update backend schema** (`backend/app/models/schemas.py`):
```python
wing_type: Literal['delta', 'swept', 'straight', 'tapered', 'biplane']
```

3. **Add geometry generation** (`backend/app/services/geometry_service.py`):
```python
def _create_biplane_wing(self, params: AeroParameters) -> trimesh.Trimesh:
    # Your geometry logic here
    pass
```

4. **Update UI dropdown** (`frontend/src/lib/components/editor/ParametricControls.svelte`):
```html
<option value="biplane">Biplane</option>
```

## Testing

### Backend Testing
```bash
cd backend
pytest  # (after creating tests/)
```

### Frontend Testing
```bash
cd frontend
npm run test  # (after setting up Vitest)
```

### Manual Testing
1. Start both servers
2. Open http://localhost:5173
3. Try examples from QUICKSTART.md
4. Check browser console for errors
5. Verify API responses in Network tab

## Common Development Tasks

### Adding a New Parameter

1. Add to `AeroParameters` type (frontend and backend)
2. Add to AI prompt in `ai_service.py`
3. Add UI control in `ParametricControls.svelte`
4. Update geometry generation to use the parameter

### Improving 3D Geometry

Edit `backend/app/services/geometry_service.py`:
- Increase `num_chord` and `num_span` for smoother surfaces
- Modify airfoil shape calculations
- Add more complex geometry (fuselage, stabilizers)

### Styling Changes

- Global styles: `frontend/src/app.css`
- Component styles: `<style>` block in `.svelte` files
- CSS variables: Defined in `:root` in `app.css`

## Performance Optimization

### Frontend
- Threlte handles Three.js optimization automatically
- Keep geometry vertex count reasonable (< 10,000 vertices)
- Use `OrbitControls` damping for smooth interaction

### Backend
- Current implementation uses in-memory storage
- For production: Add PostgreSQL/MongoDB for model persistence
- Consider caching AI responses to reduce OpenAI costs

## Future Enhancements

### High Priority
- [ ] Add database for model persistence
- [ ] Implement user authentication
- [ ] Add pythonOCC for STEP/IGES export
- [ ] Improve geometry generation (better airfoils, fuselages)

### Medium Priority
- [ ] Image-to-3D using vision models
- [ ] Multiple components (fuselage, tail, engines)
- [ ] Assembly mode
- [ ] Cloud storage integration (S3, Azure)

### Nice to Have
- [ ] Collaboration features
- [ ] Version control for models
- [ ] Aerodynamic analysis integration
- [ ] 3D printing orientation suggestions

## Deployment

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy build/ directory
```

### Backend (Docker)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### OpenAI API Errors
- Check API key in `.env`
- Verify account has credits
- Check rate limits

### Geometry Issues
- Verify parameter ranges
- Check for NaN values in calculations
- Use mesh.fix_normals() for rendering issues

### CORS Errors
- Ensure backend CORS settings include frontend URL
- Check proxy configuration in `vite.config.ts`

## Resources

- [SvelteKit Docs](https://kit.svelte.dev/docs)
- [Threlte Docs](https://threlte.xyz/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Trimesh Docs](https://trimsh.org/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
