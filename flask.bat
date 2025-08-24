@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ====== CONFIG ======
set "ROOT=D:\OWC25"
set "VENV_ACT=%ROOT%\venv\Scripts\activate.bat"
set "PY=%ROOT%\venv\Scripts\python.exe"
set "DB_DIR=%ROOT%\instance"
set "BACKUP_DIR=%ROOT%\backups\db"
set "REPORTS=%ROOT%\reports"
set "RUNLOG_DIR=%ROOT%\runlogs"
set "PORTS=5000 5001 5050 8000"
set "FLASK_HOST=127.0.0.1"
set "FLASK_PORT=5000"
set "MSG=%~1"
if "%MSG%"=="" set "MSG=auto: tests passed - commit"
REM Optional: set to 1 if you want commits even when there are no changes
set "ALLOW_EMPTY_COMMITS=0"

REM ====== LOG SETUP ======
if not exist "%RUNLOG_DIR%" mkdir "%RUNLOG_DIR%" >nul 2>&1
for /f %%t in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyyMMdd-HHmmss\")"') do set "STAMP=%%t"
set "LOG=%RUNLOG_DIR%\owc_run_%STAMP%.log"

call :log "[0/7] Prep..."
cd /d "%ROOT%" || (call :log "[FAIL] Project folder not found: %ROOT%" & goto FAIL)

REM ====== 1) KILL FLASK ======
call :kill_flask

REM ====== 2) START VENV ======
call :log "[2/7] Activate venv..."
if not exist "%VENV_ACT%" (call :log "[FAIL] venv not found: %VENV_ACT%" & goto FAIL)
call "%VENV_ACT%" || (call :log "[FAIL] Could not activate venv." & goto FAIL)
if not exist "%PY%" (call :log "[FAIL] Python not found in venv: %PY%" & goto FAIL)
"%PY%" -V >>"%LOG%" 2>&1 || (call :log "[FAIL] venv Python not runnable." & goto FAIL)

REM ====== 3) BACKUP DB ======
call :backup_db || goto FAIL

REM ====== 4) RUN PYTEST ======
call :pytest_gate || goto FAIL

REM ====== 5) COMMIT TO GIT ======
call :git_commit || goto FAIL

REM ====== 6) SUCCESS BANNER ======
call :log "[6/7] Commit done. Preparing to start Flask..."

REM ====== 7) START FLASK (blocks until Ctrl+C) ======
call :start_flask

REM When Flask exits normally:
call :log "[7/7] Flask exited."
echo Wrote log: "%LOG%"
call :hold
endlocal & exit /b 0

:FAIL
echo.
echo =======================
echo   PROCESS FAILED
echo =======================
echo See log: "%LOG%"
call :hold
endlocal & exit /b 1


:: ---------- helpers ----------
:log
echo %~1
>>"%LOG%" echo %~1
goto :eof

:kill_flask
call :log "[1/7] Kill Flask..."

REM 1) Kill anything LISTENING on the known ports
for %%P in (%PORTS%) do (
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr /r /c:":%%P .*LISTENING"') do (
    call :log "  - kill by port: PID %%A on %%P"
    taskkill /PID %%A /F >nul 2>&1
  )
)

REM 2) PowerShell sweep by command-line patterns and listening owners (cross-port)
REM    matches: "flask run" OR "-m flask run" OR "werkzeug.serving"
powershell -NoProfile -Command ^
  "$ErrorActionPreference='SilentlyContinue';" ^
  "$ports = '%PORTS%'.Split(' ',[System.StringSplitOptions]::RemoveEmptyEntries) | ForEach-Object {[int]$_};" ^
  "$pidsByPort = @(); foreach($p in $ports){ try { $pidsByPort += (Get-NetTCPConnection -State Listen -LocalPort $p | Select-Object -ExpandProperty OwningProcess) } catch {} }" ^
  "$regex = 'flask(\.exe)?\s+run|-m\s+flask\s+run|werkzeug\.serving';" ^
  "$procs = Get-CimInstance Win32_Process | Where-Object { ($_.Name -match '^(python(w)?|py)\.exe$' -or $_.Name -match '^flask\.exe$') -and ($_.CommandLine -match $regex) };" ^
  "$pids = @(); if($procs){ $pids += ($procs | Select-Object -ExpandProperty ProcessId) };" ^
  "$pids += $pidsByPort;" ^
  "$pids = $pids | Sort-Object -Unique;" ^
  "foreach($pid in $pids){ try { Stop-Process -Id $pid -Force; Write-Output ('  - PS killed PID ' + $pid) } catch {} }" >>"%LOG%" 2>&1

call :log "  - PS sweep done."
goto :eof

:backup_db
call :log "[3/7] Backup DB..."
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%" >nul 2>&1
for /f %%t in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyyMMdd-HHmmss\")"') do set "TS=%%t"
set "DEST=%BACKUP_DIR%\app_%TS%.db"
set "DB_PATH="
if exist "%DB_DIR%\app.db" set "DB_PATH=%DB_DIR%\app.db"
if not defined DB_PATH for %%F in ("%DB_DIR%\*.db") do set "DB_PATH=%%~fF"
if defined DB_PATH (
  copy /Y "%DB_PATH%" "%DEST%" >nul
  if errorlevel 1 (call :log "[FAIL] DB backup failed: %DB_PATH%" & exit /b 1)
  call :log "  - backup OK: %DEST%"
) else (
  call :log "  - WARNING: no .db found in %DB_DIR% (skipping)"
)
exit /b 0

:pytest_gate
call :log "[4/7] Pytest gate..."
if not exist "%REPORTS%" mkdir "%REPORTS%" >nul 2>&1
set "PYTHONPATH=%ROOT%;%PYTHONPATH%"
"%PY%" -m pytest -q --maxfail=1 --junitxml="%REPORTS%\pytest.xml" >>"%LOG%" 2>&1
if errorlevel 1 (call :log "[FAIL] Tests failed. See reports\pytest.xml" & exit /b 1)
call :log "  - tests OK"
exit /b 0

:git_commit
call :log "[5/7] Git commit..."

REM --- Resolve git exe, with proper quoting ---
set "GITEXE=git"
where git >nul 2>&1
if errorlevel 1 (
  if exist "C:\Program Files\Git\bin\git.exe" (
    set "GITEXE=\"C:\Program Files\Git\bin\git.exe\""
  ) else (
    call :log "[FAIL] Git not found (PATH or default install)."
    exit /b 1
  )
)

REM --- Ensure we're inside a git work tree ---
for /f "usebackq delims=" %%S in (`%GITEXE% rev-parse --is-inside-work-tree 2^>nul`) do set "INWT=%%S"
if /I not "%INWT%"=="true" (
  call :log "[FAIL] Not inside a Git work tree at %CD%."
  exit /b 1
)

REM --- Status snapshot BEFORE staging ---
set "GIT_STATUS_FILE=%RUNLOG_DIR%\git_status_%STAMP%.txt"
%GITEXE% status --porcelain=v1 > "%GIT_STATUS_FILE%" 2>&1
type "%GIT_STATUS_FILE%" >>"%LOG%"

REM --- Stage everything (incl. deletes) ---
%GITEXE% add -A >>"%LOG%" 2>&1

REM --- Snapshot of what is STAGED now ---
set "GIT_CACHED_FILE=%RUNLOG_DIR%\git_cached_%STAMP%.txt"
%GITEXE% diff --cached --name-status > "%GIT_CACHED_FILE%" 2>&1
type "%GIT_CACHED_FILE%" >>"%LOG%"

REM --- If nothing is staged, optionally do an empty commit or skip ---
for %%Z in ("%GIT_CACHED_FILE%") do set "CACHED_SIZE=%%~zZ"
if "%CACHED_SIZE%"=="0" (
  if "%ALLOW_EMPTY_COMMITS%"=="1" (
    %GITEXE% commit --allow-empty -m "%MSG%" >>"%LOG%" 2>&1
    if errorlevel 1 (call :log "[FAIL] empty commit failed." & exit /b 1) else (call :log "  - empty commit OK: %MSG%")
  ) else (
    call :log "  - nothing to commit (index clean after add)."
  )
  exit /b 0
)

REM --- Commit with message ---
%GITEXE% commit -m "%MSG%" >>"%LOG%" 2>&1
if errorlevel 1 (
  call :log "[FAIL] git commit failed. See log for details."
  exit /b 1
) else (
  for /f "usebackq delims=" %%H in (`%GITEXE% rev-parse --short HEAD 2^>nul`) do set "LASTCOMMIT=%%H"
  if defined LASTCOMMIT (call :log "  - commit OK: %MSG% (#%LASTCOMMIT%)") else (call :log "  - commit OK: %MSG%")
)
exit /b 0

:start_flask
call :log "[7/7] Starting Flask (Ctrl+C to stop)..."
set "FLASK_APP=app.py"
set "FLASK_ENV=development"
set "FLASK_RUN_HOST=%FLASK_HOST%"
set "FLASK_RUN_PORT=%FLASK_PORT%"
call :log "  - http://%FLASK_HOST%:%FLASK_PORT%"
"%PY%" -m flask run
exit /b 0

:hold
echo.
echo ===== Press Ctrl+C to stop Flask, or any key to close this window =====
pause >nul
exit /b 0
