@echo off
echo Running TDMS to CSV Monitor...
cd monitor
python monitor.py

echo Starting Web Dashboard...
cd ../dashboard
python app.py

pause