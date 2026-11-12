@echo off
title GitLaTeX IDE - Group 9 Smart Grid FDI Anomaly Engine
echo ==============================================================================
echo   GitLaTeX IDE - Local Web-based LaTeX Studio with Git
echo ==============================================================================
echo.
echo Ensuring repository junction exists in %USERPROFILE%\Desktop\latex_repos...
if not exist "%USERPROFILE%\Desktop\latex_repos" mkdir "%USERPROFILE%\Desktop\latex_repos"
if not exist "%USERPROFILE%\Desktop\latex_repos\group_project" (
    mklink /J "%USERPROFILE%\Desktop\latex_repos\group_project" "%~dp0."
)

echo.
echo Starting GitLaTeX Server on http://127.0.0.1:5000 ...
echo.
echo Press CTRL+C in this terminal window to stop the server.
echo ==============================================================================
echo.
python -m gitlatex --repos "%USERPROFILE%\Desktop\latex_repos" --port 5000
pause
