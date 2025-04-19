@echo off
SET PROJECT_DIR=%~dp0
cd /d %PROJECT_DIR%

echo.
echo === Virtuelle Umgebung prüfen ...
if not exist venv (
    echo Erstelle virtuelle Umgebung ...
    python -m venv venv
)

echo.
echo === Aktiviere Umgebung ...
call venv\Scripts\activate

echo.
echo === Installiere Pakete ...
pip install -r requirements.txt

echo.
echo === Starte Migration ...
python manage.py migrate

echo.
echo === Erstelle Superuser ...
python manage.py createsuperuser

echo.
echo === Starte lokalen Server ...
python manage.py runserver

echo.
echo === Server wurde beendet oder ein Fehler ist aufgetreten.
pause