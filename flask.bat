@echo off
echo === Killing existing Flask processes ===
taskkill /F /IM python.exe /T >nul 2>&1

echo === Navigating to project folder ===
cd /d D:\OWC25

echo === Activating virtual environment ===
call venv\Scripts\activate.bat

echo === Committing and pushing to Git ===
git add .
git commit -m "✅ Fix: navbar"
git push origin main

echo === Restarting Flask server ===
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
