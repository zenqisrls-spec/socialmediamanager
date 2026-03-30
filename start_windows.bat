@echo off
setlocal

cd /d "%~dp0"

echo [1/6] Verifico ambiente virtuale...
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 goto :error
)

echo [2/6] Attivo ambiente virtuale...
call ".venv\Scripts\activate.bat"
if errorlevel 1 goto :error

echo [3/6] Aggiorno strumenti pip...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :error

echo [4/6] Aggiorno pydantic compatibile...
pip install --index-url https://pypi.org/simple --upgrade "pydantic>=2.12.4,<3"
if errorlevel 1 goto :error

echo [5/6] Installo dipendenze progetto...
pip install --index-url https://pypi.org/simple -r requirements.txt
if errorlevel 1 goto :error

echo [6/6] Preparo .env se mancante...
if not exist ".env" copy /Y ".env.example" ".env" >nul

echo.
echo Avvio server FastAPI su http://127.0.0.1:8000
echo Documentazione: http://127.0.0.1:8000/docs
echo.
python -m uvicorn app.main:app --reload
goto :eof

:error
echo.
echo ERRORE durante l'esecuzione dello script.
echo Controlla i messaggi sopra e riprova.
pause
exit /b 1

