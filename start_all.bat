@echo off
echo [NamoNexus Sovereign System] Awakening All Modules...

cd /d "%~dp0"
echo Running from: %cd%

echo [NamoNexus] Stopping existing services...
docker compose down

echo [NamoNexus] Building and starting all services...
docker compose up --build -d

echo [System] All NamoNexus services are running in Docker. Use 'docker compose logs -f' to view logs.
pause
