import os
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORD_DIR = os.path.join(BASE_DIR, 'Record')

# Ensure main record directory exists on import
if not os.path.exists(RECORD_DIR):
    os.makedirs(RECORD_DIR)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_current_excel_path():
    """
    Determines the path for the current month's Excel file.
    Creates the folder and file with headers if they don't exist.
    """
    now = datetime.now()
    year_folder = os.path.join(RECORD_DIR, str(now.year))
    filename = f"log_{now.strftime('%Y%m')}.xlsx"
    full_path = os.path.join(year_folder, filename)

    # Create Year Folder if missing
    if not os.path.exists(year_folder):
        os.makedirs(year_folder)

    # Create File with Headers if missing
    if not os.path.exists(full_path):
        df = pd.DataFrame(columns=[
            'Type', 'Last_Name', 'First_Name', 
            'ID_Number', 'Program', 'Time_In', 'Date_Logged'
        ])
        df.to_excel(full_path, index=False)
    
    return full_path

def load_excel_data(file_path):
    """
    Safely loads Excel data, ensuring ID_Number is treated as a string.
    """
    try:
        # dtype={'ID_Number': str} forces the ID column to be text
        df = pd.read_excel(file_path, dtype={'ID_Number': str})
        
        # Clean up 'nan' string if it appears
        if 'ID_Number' in df.columns:
            df['ID_Number'] = df['ID_Number'].fillna('N/A').astype(str).replace('nan', 'N/A')
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        return pd.DataFrame()