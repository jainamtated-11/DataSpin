@echo off
echo Running TDMS to Google Sheets Monitor...
cd monitor
start "" python monitor.py
cd ..

echo Starting Web Dashboard...
cd dashboard
python app.py

pause
