@echo off
setlocal

REM Usage:
REM   start_all.bat
REM   start_all.bat --no-mcp
REM   start_all.bat --dry-run

set "WITH_MCP=true"
set "DRY_RUN=false"

for %%I in ("%~dpnx0") do set "SCRIPT_DIR=%%~dpI"
set "PS1_PATH=%SCRIPT_DIR%start_all.ps1"

:parse_args
if "%~1"=="" goto parsed
if /I "%~1"=="--no-mcp" (
  set "WITH_MCP=false"
  shift
  goto parse_args
)
if /I "%~1"=="--dry-run" (
  set "DRY_RUN=true"
  shift
  goto parse_args
)
echo [warn] unknown argument: %~1
shift
goto parse_args

:parsed

if not exist "%PS1_PATH%" (
  echo [error] missing PowerShell launcher: "%PS1_PATH%"
  exit /b 1
)

if /I "%WITH_MCP%"=="true" (
  set "PS_ARGS=-WithMcp"
) else (
  set "PS_ARGS="
)

if /I "%DRY_RUN%"=="true" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1_PATH%" %PS_ARGS% -DryRun
  exit /b %ERRORLEVEL%
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1_PATH%" %PS_ARGS%

