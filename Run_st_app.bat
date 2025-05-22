@echo off

:: Print current directory
echo Current directory: "%cd%"

:: Change to the batch file's directory
cd /d "%~dp0"
echo New directory: "%cd%"
setlocal enabledelayedexpansion
:: Set the path to the assets folder where db_details.json will be stored
set "folder=Assets"

:: Ensure the assets folder exists
if not exist "%folder%" (
    mkdir "%folder%"
)

:: Check if db_details.json already exists
if exist "%folder%\db_details.json" (
    echo The db_details.json file already exists.
    echo Skipping file creation. If you want to change database details, delete the file in assets.
    echo onward to run streamlit app ...
) 
if not exist "%folder%\db_details.json" (
    :: If db_details.json doesn't exist, create the file and prompt for input
    echo Creating db_details.json...
    
    :: Prompt for inputs
    set /p arg1= Enter host: 
    set /p arg2= Enter user with admin access or at least access which lets you perform all operations on db and its tables: 
    set /p arg3= Enter password for user: 
    :: Create JSON structure and store in assets\db_details.json
    echo { >> "%folder%\db_details.json"
    echo   "host": "!arg1!", >> "%folder%\db_details.json"
    echo   "user": "!arg2!", >> "%folder%\db_details.json"
    echo   "password": "!arg3!" >> "%folder%\db_details.json"
    echo } >> "%folder%\db_details.json"

    echo db_details.json file has been created successfully in the assets folder.
    echo onward to run streamlit app
)
endlocal
REM Run the Streamlit app
D:
cd "D:\my work\project\consistancy_migrating_from_prototype\consistancy_ver_2"
call .venv\Scripts\activate.bat
python -m streamlit run navigation.py

REM Pause the command window after execution
pause
