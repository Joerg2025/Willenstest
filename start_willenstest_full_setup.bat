@echo off
SET PROJECT_DIR=%~dp0
cd /d %PROJECT_DIR%

echo.
echo === Prüfe virtuelle Umgebung ...
if not exist venv (
    echo Erstelle virtuelle Umgebung ...
    python -m venv venv
)

echo.
echo === Aktiviere virtuelle Umgebung ...
call venv\Scripts\activate

echo.
echo === Installiere Django & Abhängigkeiten ...
pip install --upgrade pip
pip install django gunicorn whitenoise

echo.
echo === Starte Datenbankmigration ...
python manage.py migrate

echo.
echo === Starte Server ...
python manage.py runserver

echo.
echo === Server wurde beendet oder ein Fehler ist aufgetreten.
pause