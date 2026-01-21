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

def get_dashboard_data():
    """
    Helper function to load and process data.
    Used by both the main dashboard view (HTML) and the live API (JSON).
    """
    # 1. Determine Year & File Path
    selected_year = request.args.get('year', str(datetime.now().year))
    year_path = os.path.join(RECORD_DIR, selected_year)
    
    if not os.path.exists(year_path):
        os.makedirs(year_path)
    
    # Get available Excel files
    available_files = [f for f in os.listdir(year_path) if f.endswith('.xlsx') and not f.startswith('Report_')]
    available_files.sort() 

    selected_file = request.args.get('month_file')

    # Default File Logic: Use current month if available, else latest
    if not selected_file or selected_file not in available_files:
        current_month_filename = f"log_{datetime.now().strftime('%Y%m')}.xlsx"
        if current_month_filename in available_files:
            selected_file = current_month_filename
        elif available_files:
            selected_file = available_files[-1]

    # 2. Initialize Stats Structure
    data = {
        'total_visitors': 0, 'student_count': 0, 'guest_count': 0,
        'top_dept': "N/A", 'peak_hour': "N/A", 'busiest_day': "N/A",
        'avg_daily': 0, 'data_rows': [], 'recent_logs': [],
        'dept_labels': [], 'dept_counts': [], 
        'time_labels': [], 'time_counts': [],
        'dept_breakdown': {}
    }

    # 3. Process Data if File Exists
    if selected_file:
        try:
            file_path = os.path.join(year_path, selected_file)
            df = load_excel_data(file_path)

            if not df.empty:
                # Ensure Date_Logged exists
                if 'Date_Logged' not in df.columns:
                    df['Date_Logged'] = datetime.now().strftime("%Y-%m-%d")

                # --- FILTERS ---
                filter_day = request.args.get('filter_day')
                filter_hour = request.args.get('filter_hour')

                if filter_day:
                    df = df[df['Date_Logged'].astype(str).str.endswith(f"-{filter_day}")]
                if filter_hour:
                    df = df[df['Time_In'].astype(str).str.startswith(filter_hour)]

                # --- CALCULATIONS ---
                data['data_rows'] = df.to_dict('records')
                data['total_visitors'] = len(df)
                data['student_count'] = len(df[df['Type'] == 'Student'])
                data['guest_count'] = len(df[df['Type'] == 'Guest'])
                
                # Top Program & Charts
                dept_stats = df[df['Type'] == 'Student']['Program'].value_counts()
                data['dept_labels'] = dept_stats.index.tolist()
                data['dept_counts'] = dept_stats.values.tolist()
                data['dept_breakdown'] = dept_stats.to_dict()
                if not dept_stats.empty: 
                    data['top_dept'] = dept_stats.idxmax()

                # Peak Hour & Charts
                df['Hour'] = df['Time_In'].astype(str).str.slice(0, 2)
                time_stats = df['Hour'].value_counts().sort_index()
                data['time_labels'] = time_stats.index.tolist()
                data['time_counts'] = time_stats.values.tolist()
                if not time_stats.empty: 
                    data['peak_hour'] = f"{time_stats.idxmax()}:00"

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

                # Average Daily
                unique_days = df['Date_Logged'].nunique()
                if unique_days > 0: 
                    data['avg_daily'] = int(data['total_visitors'] / unique_days)

                # Recent Logs
                data['recent_logs'] = df.tail(5).iloc[::-1].to_dict('records')

        except Exception as e:
            print(f"Error processing dashboard data: {e}")

    return data, available_files, selected_file, selected_year


@dashboard_bp.route('/dashboard')
def dashboard_view():
    """
    Renders the main dashboard HTML page.
    """
    if not session.get('is_admin'): 
        return redirect(url_for('auth.admin_login'))
    
    # Get all data using the helper
    data, available_files, selected_file, selected_year = get_dashboard_data()

    return render_template('dashboard.html', 
        files=available_files, 
        current_file=selected_file,
        selected_year=selected_year,
        
        # Unpack the data dictionary into variables
        **data,
        
        # JSON dumps for Chart.js
        dept_labels_json=json.dumps(data['dept_labels']), 
        dept_counts_json=json.dumps(data['dept_counts']),
        time_labels_json=json.dumps(data['time_labels']), 
        time_counts_json=json.dumps(data['time_counts']),
        
        # Pass filters back to template
        filter_day=request.args.get('filter_day'), 
        filter_hour=request.args.get('filter_hour')
    )


@dashboard_bp.route('/api/updates')
def dashboard_api():
    """
    API Endpoint for Live Polling (AJAX).
    Returns data as JSON instead of HTML.
    """
    if not session.get('is_admin'): 
        return jsonify({'error': 'Unauthorized'}), 401
    
    data, _, _, _ = get_dashboard_data()
    
    # Restructure specifically for the Javascript frontend
    return jsonify({
        'total_visitors': data['total_visitors'],
        'student_count': data['student_count'],
        'guest_count': data['guest_count'],
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
        }
    })


@dashboard_bp.route('/download_report')
def download_report():
    if not session.get('is_admin'): 
        return redirect(url_for('auth.admin_login'))
    
    filename = request.args.get('file')
    
    # Auto-detect year from filename if parameter is missing
    # Try to get year from URL, otherwise extract it from the filename (e.g., log_202512.xlsx -> 2025)
    selected_year = request.args.get('year')
    
    if not selected_year and filename and filename.startswith("log_") and len(filename) >= 8:
        try:
            # Extract "2025" from "log_202512.xlsx"
            selected_year = filename[4:8]
        except:
            selected_year = str(datetime.now().year)
            
    # Fallback to current year if all else fails
    if not selected_year:
        selected_year = str(datetime.now().year)
    
    source_path = os.path.join(RECORD_DIR, selected_year, filename)
    output_path = os.path.join(RECORD_DIR, selected_year, f"Report_{filename}")
    
    try:
        if not os.path.exists(source_path):
            return f"Error: File '{filename}' not found in {selected_year} folder. (Path: {source_path})"

        df = load_excel_data(source_path)
        
        # Create Excel Writer
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
        
        # 1. Summary Sheet
        summary_data = pd.DataFrame({
            'Metric': ['Total Logins', 'Students', 'Guests'],
            'Count': [len(df), len(df[df['Type'] == 'Student']), len(df[df['Type'] == 'Guest'])]
        })
        summary_data.to_excel(writer, sheet_name='Summary', index=False, startrow=0)
        
        # Add Department Breakdown to Summary Sheet
        dept_counts = df[df['Type'] == 'Student']['Program'].value_counts().reset_index()
        dept_counts.columns = ['Program', 'Count']
        dept_counts.to_excel(writer, sheet_name='Summary', index=False, startrow=5)
        
        # 2. Detailed Logs Sheet
        df.to_excel(writer, sheet_name='Detailed Logs', index=False)
        
        # 3. Add Charts (XlsxWriter)
        workbook = writer.book
        worksheet = writer.sheets['Summary']
        chart = workbook.add_chart({'type': 'pie'})
        
        # Configure Chart Data Ranges
        max_row = len(dept_counts) + 6
        chart.add_series({
            'name': 'Program Distribution',
            'categories': ['Summary', 6, 0, max_row, 0], # Column A (Program Names)
            'values':     ['Summary', 6, 1, max_row, 1], # Column B (Counts)
            'data_labels': {'value': True}
        })
        
        worksheet.insert_chart('E2', chart)
        
        writer.close()
        return send_file(output_path, as_attachment=True)
        
    except Exception as e:
        return f"Error generating report: {e}"