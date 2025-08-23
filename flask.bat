@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ====== CONFIG ======
set "ROOT=D:\OWC25"
set "VENV_ACT=%ROOT%\venv\Scripts\activate.bat"
set "PY=%ROOT%\venv\Scripts\python.exe"
set "DB_DIR=%ROOT%\instance"
set "BACKUP_DIR=%ROOT%\backups\db"
set "PORTS=5000 5001 5050 8000"
set "MSG=%~1"
if "%MSG%"=="" set "MSG=auto: tests passed — commit"

echo [0/6] Prep...
cd /d "%ROOT%" || (echo [FAIL] Project folder not found: %ROOT% & goto FAIL)

REM ====== 1) KILL FLASK ======
echo [1/6] Kill Flask (ports + 'flask run')...
for %%P in (%PORTS%) do (
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr /r /c:":%%P .*LISTENING"') do (
    echo   - kill PID %%A on port %%P
    taskkill /PID %%A /F >nul 2>&1
  )
)
for /f "skip=1 tokens=2 delims== " %%P in ('wmic process where "CommandLine like '%%%flask%%%run%%%' and Name='python.exe'" get ProcessId /value 2^>nul') do (
  if not "%%~P"=="" (
    echo   - kill 'flask run' PID %%P
    taskkill /PID %%P /F >nul 2>&1
  )
)

REM ====== 2) START VENV ======
echo [2/6] Activate venv...
if not exist "%VENV_ACT%" (echo [FAIL] venv not found: %VENV_ACT% & goto FAIL)
call "%VENV_ACT%" || (echo [FAIL] Could not activate venv. & goto FAIL)
if not exist "%PY%" (echo [FAIL] Python not found in venv: %PY% & goto FAIL)
"%PY%" -V || (echo [FAIL] venv Python not runnable. & goto FAIL)

REM ====== 3) BACKUP DB ======
echo [3/6] Backup DB...
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%" >nul 2>&1
for /f "tokens=2 delims==." %%A in ('wmic os get localdatetime /value') do set TS=%%A
set "STAMP=%TS:~0,8%-%TS:~8,6%"

set "DB_PATH="
if exist "%DB_DIR%\app.db" set "DB_PATH=%DB_DIR%\app.db"
if not defined DB_PATH (
  for %%F in ("%DB_DIR%\*.db") do (
    set "DB_PATH=%%~fF"
    goto :DB_PICKED
  )
)
:DB_PICKED
if defined DB_PATH (
  copy /Y "%DB_PATH%" "%BACKUP_DIR%\app_%STAMP%.db" >nul
  if errorlevel 1 (echo [FAIL] DB backup failed: "%DB_PATH%" & goto FAIL)
  echo   - backup OK: %BACKUP_DIR%\app_%STAMP%.db
) else (
  echo   - WARNING: no .db found in %DB_DIR% (skipping)
)

REM ====== 4) RUN PYTEST ======
echo [4/6] Pytest gate...
if not exist "%ROOT%\reports" mkdir "%ROOT%\reports" >nul 2>&1
set "PYTHONPATH=%ROOT%;%PYTHONPATH%"
"%PY%" -m pytest -q --maxfail=1 --junitxml="%ROOT%\reports\pytest.xml"
if errorlevel 1 (echo [FAIL] Tests failed. See reports\pytest.xml & goto FAIL)
echo   - tests OK

REM ====== 5) COMMIT TO GIT ======
echo [5/6] Git commit...
REM Ensure git is available
where git >nul 2>&1
if errorlevel 1 (
  if exist "C:\Program Files\Git\bin\git.exe" (
    set "GIT=C:\Program Files\Git\bin\git.exe"
  ) else (
    echo [FAIL] Git not found in PATH. Install Git or add to PATH.
    goto FAIL
  )
) else (
  set "GIT=git"
)

"%GIT%" status -s
"%GIT%" add -A
"%GIT%" diff --cached --stat

"%GIT%" commit -m "%MSG%"
if errorlevel 1 (
  echo   - nothing to commit (clean). Continuing.
  call :CLEARERR
) else (
  echo   - commit OK: %MSG%
)

echo [6/6] Done. Success.
echo/
echo SUCCESS. Press any key to close...
pause >nul
endlocal
exit /b 0

:FAIL
echo/
echo =======================
echo   PROCESS FAILED
echo =======================
echo (See the last [FAIL] line above for the reason.)
echo Press any key to close...
pause >nul
endlocal
exit /b 1

:CLEARERR
exit /b 0
