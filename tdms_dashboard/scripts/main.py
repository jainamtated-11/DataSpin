# scripts/main.py
from process_tdms import process_all_tdms
from upload_to_drive import upload_to_drive

TDMS_FOLDER = "../data"
EXCEL_PATH = "../final_data.xlsx"
DRIVE_NAME = "final_data.xlsx"

# Step 1: Process all TDMS files into Excel
process_all_tdms(TDMS_FOLDER, EXCEL_PATH)

# Step 2: Upload Excel to Google Drive
upload_to_drive(EXCEL_PATH, DRIVE_NAME)
