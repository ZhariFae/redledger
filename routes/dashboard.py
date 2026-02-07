import os
import sys 

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import json
import pandas as pd
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, jsonify
from utils import RECORD_DIR, load_excel_data 

# Create the Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# --- ADDED: MAPÚA QUARTER CONFIGURATION ---
MAPUA_TERMS = {
    "T1_2025": {"label": "1st Quarter (Aug-Nov 2025)", "start": "2025-08-01", "end": "2025-11-20"},
    "T2_2025": {"label": "2nd Quarter (Dec 2025-Mar 2026)", "start": "2025-12-08", "end": "2026-03-01"},
    "T3_2026": {"label": "3rd Quarter (Mar-Jun 2026)", "start": "2026-03-09", "end": "2026-05-30"},
    "T4_2026": {"label": "4th Quarter (Jun-Aug 2026)", "start": "2026-06-08", "end": "2026-08-30"},
}

def merge_excel_files(start_date_str, end_date_str):
    """Merges multiple Excel files based on a date range."""
    merged_df = pd.DataFrame()
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        years_to_check = range(start_date.year, end_date.year + 1)
        
        for year in years_to_check:
            year_path = os.path.join(RECORD_DIR, str(year))
            if not os.path.exists(year_path): continue
            for filename in os.listdir(year_path):
                if filename.startswith("log_") and filename.endswith(".xlsx"):
                    try:
                        file_ym = filename[4:10]
                        # Create dummy date (1st of month) to check if month is in range
                        file_date = datetime(int(file_ym[:4]), int(file_ym[4:6]), 1)
                        
                        # Rough check: Is the file's month relevant?
                        if (file_date.year > start_date.year or (file_date.year == start_date.year and file_date.month >= start_date.month)) and \
                           (file_date.year < end_date.year or (file_date.year == end_date.year and file_date.month <= end_date.month)):
                            
                            df = load_excel_data(os.path.join(year_path, filename))
                            # Ensure Date_Logged exists for filtering
                            if 'Date_Logged' not in df.columns:
                                df['Date_Logged'] = datetime.now().strftime("%Y-%m-%d")
                            merged_df = pd.concat([merged_df, df], ignore_index=True)
                    except: continue

        # Precise Date Filtering
        if not merged_df.empty and 'Date_Logged' in merged_df.columns:
            merged_df['Date_Obj'] = pd.to_datetime(merged_df['Date_Logged'])
            mask = (merged_df['Date_Obj'] >= start_date) & (merged_df['Date_Obj'] <= end_date)
            merged_df = merged_df.loc[mask].drop(columns=['Date_Obj'])
            
    except Exception as e: print(f"Merge Error: {e}")
    return merged_df

def get_dashboard_data():
    """
    Helper function to load and process data.
    """
    # 1. Determine View Mode (Default to Monthly)
    view_mode = request.args.get('view_mode', 'monthly')
    
    selected_file = None
    start_date = None
    end_date = None
    df = pd.DataFrame()
    label = ""
    
    # Capture Filters
    filter_day = request.args.get('filter_day')
    filter_hour = request.args.get('filter_hour')
    term_key = request.args.get('term_key') # Captured here for both modes

    # --- LOGIC FOR MONTHLY VIEW ---
    if view_mode == 'monthly':
        selected_year = request.args.get('year', str(datetime.now().year))
        year_path = os.path.join(RECORD_DIR, selected_year)
        
        if not os.path.exists(year_path): os.makedirs(year_path)

        available_files = [f for f in os.listdir(year_path) if f.endswith('.xlsx') and not f.startswith('Report_')]
        available_files.sort(reverse=True) 
        
        selected_file = request.args.get('month_file')
        if not selected_file or selected_file not in available_files:
            if available_files: selected_file = available_files[0]
            
        if selected_file:
            df = load_excel_data(os.path.join(year_path, selected_file))
            label = f"Monthly: {selected_file}"
            
        extra_context = {
            'files': available_files, 
            'selected_year': selected_year, 
            'current_file': selected_file
        }

    # --- LOGIC FOR QUARTERLY VIEW ---
    else:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # If no custom dates, check if a Term is selected
        if not start_date or not end_date:
            if term_key and term_key in MAPUA_TERMS:
                start_date = MAPUA_TERMS[term_key]['start']
                end_date = MAPUA_TERMS[term_key]['end']
            else:
                # Default fallback: Current Month
                now = datetime.now()
                start_date = now.strftime("%Y-%m-01")
                end_date = now.strftime("%Y-%m-%d")
        
        df = merge_excel_files(start_date, end_date)
        label = f"Range: {start_date} to {end_date}"
        extra_context = {'start_date': start_date, 'end_date': end_date}

    # 3. Initialize Stats Structure
    data = {
        'total_visitors': 0, 'student_count': 0, 'guest_count': 0,
        'emp_count': 0,
        'top_dept': "N/A", 'peak_hour': "N/A", 'busiest_day': "N/A",
        'avg_daily': 0, 'data_rows': [], 'recent_logs': [],
        'dept_labels': [], 'dept_counts': [], 
        'time_labels': [], 'time_counts': [],
        'dept_breakdown': {},
        'report_label': label,
        'view_mode': view_mode,
        'filter_day': filter_day,
        'filter_hour': filter_hour,
        'selected_term': term_key
    }
    data.update(extra_context)

    # 4. Process Data Frame
    if not df.empty:
        # Ensure standard columns exist
        if 'Date_Logged' not in df.columns:
            df['Date_Logged'] = datetime.now().strftime("%Y-%m-%d")
        if 'Time_In' not in df.columns:
            df['Time_In'] = "00:00"

        # --- APPLY ADVANCED FILTERS ---
        if filter_day:
            df = df[df['Date_Logged'].astype(str).str.endswith(f"-{filter_day}")]
        if filter_hour:
            df = df[df['Time_In'].astype(str).str.startswith(filter_hour)]

        # --- CALCULATIONS ---
        data['data_rows'] = df.to_dict('records')
        data['total_visitors'] = len(df)
        data['student_count'] = len(df[df['Type'] == 'Student'])
        data['emp_count'] = len(df[(df['Type'] == 'Guest') | (df['Type'] == 'Employee')])
        data['guest_count'] = data['emp_count'] 
        
        # Department Stats
        dept_stats = df[df['Type'] == 'Student']['Program'].value_counts()
        data['dept_labels'] = dept_stats.index.tolist()
        data['dept_counts'] = dept_stats.values.tolist()
        data['dept_breakdown'] = dept_stats.to_dict()
        if not dept_stats.empty: data['top_dept'] = dept_stats.idxmax()

        # Peak Hour
        df['Hour'] = df['Time_In'].astype(str).str.slice(0, 2)
        time_stats = df['Hour'].value_counts().sort_index()
        data['time_labels'] = time_stats.index.tolist()
        data['time_counts'] = time_stats.values.tolist()
        if not time_stats.empty: data['peak_hour'] = f"{time_stats.idxmax()}:00"

        # Busiest Day
        day_stats = df['Date_Logged'].value_counts()
        if not day_stats.empty:
            b_day = day_stats.idxmax()
            b_count = day_stats.max()
            try:
                date_obj = datetime.strptime(str(b_day), '%Y-%m-%d')
                data['busiest_day'] = f"{date_obj.strftime('%b %d')} ({b_count})"
            except:
                data['busiest_day'] = f"{b_day} ({b_count})"

        # Averages & Recent
        unique_days = df['Date_Logged'].nunique()
        if unique_days > 0: data['avg_daily'] = int(data['total_visitors'] / unique_days)
        data['recent_logs'] = df.tail(8).iloc[::-1].to_dict('records')

    return data

@dashboard_bp.route('/dashboard')
def dashboard_view():
    if not session.get('is_admin'): return redirect(url_for('auth.admin_login'))
    
    data = get_dashboard_data()

    return render_template('dashboard.html', 
        terms=MAPUA_TERMS,  # <--- THIS WAS THE MISSING PIECE
        **data,
        dept_labels_json=json.dumps(data['dept_labels']), 
        dept_counts_json=json.dumps(data['dept_counts']),
        time_labels_json=json.dumps(data['time_labels']), 
        time_counts_json=json.dumps(data['time_counts'])
    )

@dashboard_bp.route('/api/updates')
def dashboard_api():
    if not session.get('is_admin'): return jsonify({'error': 'Unauthorized'}), 401
    data = get_dashboard_data()
    return jsonify({
        'total_visitors': data['total_visitors'],
        'student_count': data['student_count'],
        'guest_count': data['emp_count'],
        'top_dept': data['top_dept'],
        'peak_hour': data['peak_hour'],
        'busiest_day': data['busiest_day'],
        'avg_daily': data['avg_daily'],
        'recent_logs': data['recent_logs'],
        'charts': {
            'dept_labels': data['dept_labels'],
            'dept_counts': data['dept_counts'],
            'time_labels': data['time_labels'],
            'time_counts': data['time_counts']
        },
        'dept_breakdown': data['dept_breakdown']
    })

@dashboard_bp.route('/download_report')
def download_report():
    if not session.get('is_admin'): return redirect(url_for('auth.admin_login'))
    
    view_mode = request.args.get('view_mode', 'monthly')
    
    # Re-use logic (simplified for download)
    if view_mode == 'monthly':
        year = request.args.get('year')
        file = request.args.get('month_file')
        path = os.path.join(RECORD_DIR, year, file)
        # Check if file exists
        if not os.path.exists(path): return "File not found."
        df = load_excel_data(path)
        filename = f"Report_{file}"
    else:
        start = request.args.get('start_date')
        end = request.args.get('end_date')
        df = merge_excel_files(start, end)
        filename = f"Report_Quarterly_{start}_to_{end}.xlsx"

    # Apply filters
    f_day = request.args.get('filter_day')
    f_hour = request.args.get('filter_hour')
    
    if not df.empty:
        if 'Date_Logged' not in df.columns: df['Date_Logged'] = datetime.now().strftime("%Y-%m-%d")
        if 'Time_In' not in df.columns: df['Time_In'] = "00:00"
        
        if f_day: df = df[df['Date_Logged'].astype(str).str.endswith(f"-{f_day}")]
        if f_hour: df = df[df['Time_In'].astype(str).str.startswith(f_hour)]
    
    if df.empty: return "No data found to export."
    
    output_path = os.path.join(RECORD_DIR, filename)
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    
    # Summary Sheet
    pd.DataFrame({
        'Metric': ['Total Visits', 'Students', 'Employees', 'Peak Hour', 'Top Dept'],
        'Value': [len(df), len(df[df['Type']=='Student']), len(df[(df['Type']=='Guest')|(df['Type']=='Employee')]), 
                  df['Time_In'].str.slice(0,2).value_counts().idxmax() + ":00" if not df.empty else "N/A",
                  df['Program'].value_counts().idxmax() if not df.empty else "N/A"]
    }).to_excel(writer, sheet_name='Summary', index=False)
    
    # Data Sheet
    df.to_excel(writer, sheet_name='Detailed Logs', index=False)
    writer.close()
    
    return send_file(output_path, as_attachment=True)