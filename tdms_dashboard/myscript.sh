#!/bin/bash

echo "Running TDMS to CSV Monitor..."
cd monitor || exit
/opt/anaconda3/bin/python monitor.py
cd ..

echo "Starting Web Dashboard..."
cd dashboard || exit
/opt/anaconda3/bin/python app.py
