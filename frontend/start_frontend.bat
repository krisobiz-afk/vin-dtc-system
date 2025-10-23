@echo off
REM Start Frontend using 'serve' on port 3000
cd /d %~dp0
echo Starting frontend via serve on port 3000...
serve -s . -l 3000
pause
