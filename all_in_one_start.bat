@echo off
echo [NamoNexus Sovereign System] Awakening All Modules...

:: Change directory to the script's location to ensure all paths are correct
cd /d "%~dp0"
echo Running from: %cd%

:: Stop any existing containers to ensure a clean start
echo [NamoNexus] Stopping existing services...
docker compose down

:: Build and start all services in the background
echo [NamoNexus] Building and starting all services...
docker compose up --build -d

echo [System] All NamoNexus services are running in Docker. Use 'docker compose logs -f' to view logs.
pause
