@echo off
REM Test V2 with auto-initialization

echo.
echo ===============================================
echo  Gamification V2 - Test with Auto-Init
echo ===============================================
echo.

REM Kill any existing uvicorn processes
echo Stopping any running servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ===============================================
echo  Starting PineServer with V2 Auto-Init...
echo ===============================================
echo.

REM Start server in background
cd pineServer
start /B python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

echo Waiting 8 seconds for server to initialize...
timeout /t 8 /nobreak >nul

cd ..

echo.
echo ===============================================
echo  Running V2 Tests...
echo ===============================================
echo.

REM Run tests
python -m pytest pineServer/tests -v

echo.
echo ===============================================
echo  Done! Check results above.
echo ===============================================
echo.

pause
