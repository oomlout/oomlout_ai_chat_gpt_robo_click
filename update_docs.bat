@echo off
REM RoboClick Documentation Updater - Full Regeneration

echo.
echo =============================================
echo   RoboClick Documentation Updater
echo =============================================
echo.
echo Generating documentation...
echo.

python oomlout_ai_roboclick.py --generate_docs

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  SUCCESS! Documentation Updated
    echo ========================================
    echo.
    echo Files generated:
    echo   ^> action_documentation.html
    echo   ^> configuration\action_documentation.yaml
    echo.
    echo Opening in browser...
    start action_documentation.html
) else (
    echo.
    echo ========================================
    echo  ERROR: Documentation generation failed
    echo ========================================
    echo.
    pause
)
