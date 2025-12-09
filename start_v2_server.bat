@echo off
echo Iniciando PineServer con Gamification V2 Activado...
set USE_GAMIFICATION_V2=true
set PYTHONPATH=%PYTHONPATH%;%CD%
python -m uvicorn pineServer.main:app --host 0.0.0.0 --port 8000 --reload
