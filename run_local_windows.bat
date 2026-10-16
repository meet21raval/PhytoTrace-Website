@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3.12 -m venv .venv 2>nul
    if not exist ".venv\Scripts\python.exe" py -3.11 -m venv .venv 2>nul
    if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv 2>nul
  ) else (
    where python >nul 2>nul
    if errorlevel 1 (
      echo Python was not found. Install Python 3.12 64-bit and retry.
      pause
      exit /b 1
    )
    python -m venv .venv
  )
)
if not exist ".venv\Scripts\python.exe" (
  echo Could not create a virtual environment. Install Python 3.12 64-bit and retry.
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Check your internet connection and Python version.
  pause
  exit /b 1
)
streamlit run app.py
pause
