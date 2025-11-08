@echo off
echo Starting AeroCraft Frontend...
echo.

cd frontend

if not exist node_modules (
    echo Installing dependencies...
    npm install
)

echo.
echo Starting SvelteKit development server...
echo Frontend will be available at: http://localhost:5173
echo.

npm run dev
