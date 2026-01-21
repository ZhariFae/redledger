import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
import pandas as pd
from utils import get_current_excel_path, load_excel_data

# Create the Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Ensure file exists on load
    get_current_excel_path()
    return render_template('index.html')

@main_bp.route('/submit', methods=['POST'])
def submit():
    # 1. Extract Form Data
    user_type = request.form.get('user_type')
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    
    id_number = ""
    dept_or_agency = ""

    # 2. Validate based on User Type
    if user_type == 'Student':
        id_number = request.form.get('id_number')
        dept_or_agency = request.form.get('program')
        
        if not id_number or len(id_number) != 10 or not id_number.isdigit():
            return jsonify({'status': 'error', 'message': 'Student Number must be exactly 10 digits.'}), 400
        if not dept_or_agency:
            return jsonify({'status': 'error', 'message': 'Please select a Program.'}), 400
    else:
        id_number = "N/A"
        dept_or_agency = request.form.get('agency')
        if not dept_or_agency:
            return jsonify({'status': 'error', 'message': 'Please enter your Agency or School.'}), 400

    # 3. Save to Excel
    file_path = get_current_excel_path()
    df = load_excel_data(file_path)

    new_data = {
        'Type': user_type,
        'Last_Name': last_name, 
        'First_Name': first_name,
        'ID_Number': str(id_number),
        'Program': dept_or_agency,
        'Time_In': datetime.now().strftime("%H:%M"), 
        'Date_Logged': datetime.now().strftime("%Y-%m-%d")
    }
    
    try:
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel(file_path, index=False)
        return jsonify({
            'status': 'success', 
            'message': f'Welcome, {first_name}!',
            'detail': f'Logged at {datetime.now().strftime("%I:%M %p")}'
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'System Error: {str(e)}'}), 500