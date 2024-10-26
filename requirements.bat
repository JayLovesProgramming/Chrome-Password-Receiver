@echo off

echo Installing packages required to run this Python script
echo These are official packages meaning they are safe to use from my knowledge

pip install -r requirements.txt

echo IF "Requirement already satisfied" THEN YOU ALREADY HAVE THEM INSTALLED SO JUST CONTINUE

set /p DUMMY=Enter to continue...

