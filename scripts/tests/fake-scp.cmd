@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fake-scp.ps1" %*
exit /b %ERRORLEVEL%
