@echo off
rem ------------------------------------------------------------
rem Commit and push the Agent_Solution_BI project to the BI_Solution repository
rem ------------------------------------------------------------

rem Change to the project directory (adjust if needed)
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

rem Initialize git if not already a repository
if not exist ".git" (
    echo Initializing new git repository...
    git init
)

rem Add remote origin pointing to the target repository
git remote remove origin 2>nul
git remote add origin https://github.com/Andrejr82/BI_Solution.git

rem Stage all changes
git add -A

rem Commit with a generic message (edit as needed)
set "COMMIT_MSG=Automated commit: update project files"
git commit -m "%COMMIT_MSG%"

rem Push to the main branch (change to 'master' if that is the default)
git push -u origin main

echo ------------------------------------------------------------
echo Push completed. Verify the remote repository.
pause
