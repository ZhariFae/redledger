import os
import pandas as pd
from datetime import datetime
from flask import Blueprint, request, jsonify
from utils import get_current_excel_path, load_excel_data, RECORD_DIR

# Create Blueprint
api_bp = Blueprint('api', __name__)

MASTER_FILE = "Master_List.xlsx"

def get_master_list():
    """Loads the student/employee database."""
    if not os.path.exists(MASTER_FILE):
        return pd.DataFrame() # Return empty if missing
    # Force ID_Number to be string to prevent "2023..." becoming a number
    return pd.read_excel(MASTER_FILE, dtype={'ID_Number': str, 'RFID_UID': str})

@api_bp.route('/rfid_tap', methods=['POST'])
def rfid_tap():
    """
    Receives RFID UID -> Processes Attendance -> Returns User Info
    Expected JSON: { "uid": "A1B2C3D4" }
    """
    data = request.json
    uid = data.get('uid')

    if not uid:
        return jsonify({'status': 'error', 'message': 'No UID provided'}), 400

    # 1. LOOKUP USER IN MASTER LIST
    master_df = get_master_list()
    user_row = master_df[master_df['RFID_UID'] == uid]

    if user_row.empty:
        return jsonify({'status': 'error', 'message': 'Card not registered.'}), 404

    # Extract User Details
    user = user_row.iloc[0]
    id_number = str(user['ID_Number'])
    full_name = f"{user['First_Name']} {user['Last_Name']}"
    role = user['Role']
    program = user['Department']

    # 2. LOAD TODAY'S LOG FILE
    log_path = get_current_excel_path()
    log_df = load_excel_data(log_path)

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    # 3. CHECK LAST STATUS
    # We filter the log to find this specific user's history
    user_logs = log_df[log_df['ID_Number'] == id_number]
    
    action = "IN" # Default assumption
    message = f"Welcome, {user['First_Name']}!"

    if not user_logs.empty:
        # Get the very last entry for this user
        last_index = user_logs.index[-1]
        last_entry = log_df.loc[last_index]
        
        # Check if the last session is "Open" (Time_Out is empty/NaN)
        is_open = pd.isna(last_entry['Time_Out']) or str(last_entry['Time_Out']).strip() == '' or str(last_entry['Time_Out']) == 'nan'

        if is_open:
            # We found an open session. Now check the DATE.
            last_date = str(last_entry['Date_Logged'])
            
            if last_date == current_date:
                # SCENARIO: SAME DAY -> TAP OUT
                log_df.at[last_index, 'Time_Out'] = current_time
                action = "OUT"
                message = f"Goodbye, {user['First_Name']}!"
            else:
                # SCENARIO: FORGOTTEN LOGOUT (Different Day)
                # 1. Auto-close the old record (Set to 9:00 PM)
                log_df.at[last_index, 'Time_Out'] = "21:00"
                log_df.at[last_index, 'Notes'] = "Auto-Closed (Forgot Logout)"
                
                # 2. Create a NEW "IN" record for today (proceeds to logic below)
                action = "IN"
                message = f"Welcome Back, {user['First_Name']}! (Previous session auto-closed)"
                
                # Create new row
                new_row = {
                    'Type': role,
                    'Last_Name': user['Last_Name'],
                    'First_Name': user['First_Name'],
                    'ID_Number': id_number,
                    'Program': program,
                    'Date_Logged': current_date,
                    'Time_In': current_time,
                    'Time_Out': None # Open session
                }
                log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

        else:
            # Last session was closed. Start a NEW one.
            new_row = {
                'Type': role,
                'Last_Name': user['Last_Name'],
                'First_Name': user['First_Name'],
                'ID_Number': id_number,
                'Program': program,
                'Date_Logged': current_date,
                'Time_In': current_time,
                'Time_Out': None
            }
            log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

    else:
        # First time ever logging in this month
        new_row = {
            'Type': role,
            'Last_Name': user['Last_Name'],
            'First_Name': user['First_Name'],
            'ID_Number': id_number,
            'Program': program,
            'Date_Logged': current_date,
            'Time_In': current_time,
            'Time_Out': None
        }
        log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

    # 4. SAVE CHANGES
    log_df.to_excel(log_path, index=False)

    return jsonify({
        'status': 'success',
        'action': action,
        'name': full_name,
        'time': current_time,
        'message': message
    })