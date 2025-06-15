import os
import time
import pandas as pd
from nptdms import TdmsFile
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Config ---
TDMS_DIR = os.path.join(os.path.dirname(__file__), 'tdms_files')
CHECK_INTERVAL = 30  # seconds
CHANNEL_NAME = "accelerationgroup"
SPREADSHEET_NAME = "TDMS Dashboard Data"
PROCESSED_LOG = "processed_files.log"

# --- Setup Google Sheets API ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open(SPREADSHEET_NAME)

# --- Helper Functions ---

def read_tdms(file_path):
    tdms_file = TdmsFile.read(file_path)
    group = tdms_file.groups()[0]
    channel = tdms_file[group][CHANNEL_NAME]
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    df = pd.DataFrame({f"z-axis-{timestamp}": channel[:]})
    return df

def update_sheet(freq_name, df):
    try:
        worksheet = spreadsheet.worksheet(freq_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=freq_name, rows="1000", cols="50")
        worksheet.update('A1', [[df.columns[0]]])
        worksheet.update('A2', df.values.tolist())
    else:
        existing_data = worksheet.get_all_values()
        col_index = len(existing_data[0]) + 1 if existing_data else 1
        worksheet.update_cell(1, col_index, df.columns[0])
        for row_num, val in enumerate(df.values.tolist(), start=2):
            worksheet.update_cell(row_num, col_index, val[0])

def load_processed_log():
    if not os.path.exists(PROCESSED_LOG):
        return {}
    with open(PROCESSED_LOG, 'r') as f:
        return dict(line.strip().split(',') for line in f.readlines())

def save_processed_log(log_dict):
    with open(PROCESSED_LOG, 'w') as f:
        for file, mtime in log_dict.items():
            f.write(f"{file},{mtime}\n")

# --- Main Loop ---

def monitor():
    print("Starting TDMS to Google Sheets monitor...")
    processed = load_processed_log()

    while True:
        current_files = {f: str(os.path.getmtime(os.path.join(TDMS_DIR, f)))
                         for f in os.listdir(TDMS_DIR) if f.endswith('.tdms')}
        
        for filename, mtime in current_files.items():
            if filename not in processed or processed[filename] != mtime:
                print(f"[+] Processing: {filename}")
                try:
                    df = read_tdms(os.path.join(TDMS_DIR, filename))
                    freq_name = os.path.splitext(filename)[0]
                    update_sheet(freq_name, df)
                    processed[filename] = mtime
                    save_processed_log(processed)
                except Exception as e:
                    print(f"[!] Error with file {filename}: {e}")
        
        time.sleep(CHECK_INTERVAL)

# --- Run ---
if __name__ == "__main__":
    monitor()
