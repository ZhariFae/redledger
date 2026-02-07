import os
from flask import Blueprint, render_template, request, redirect, url_for, session
from dotenv import load_dotenv

# Create the Blueprint
auth_bp = Blueprint('auth', __name__)

# Load Environment Variables
load_dotenv()
ADMIN_USER = os.getenv('ADMIN_USERNAME')
ADMIN_PASS = os.getenv('ADMIN_PASSWORD')

# MAIN LOGIN ROUTE
@auth_bp.route('/', methods=['GET', 'POST'])
def admin_login():
    # If user is already logged in, send them straight to dashboard
    if session.get('is_admin'):
        return redirect(url_for('dashboard.dashboard_view'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['is_admin'] = True
            return redirect(url_for('dashboard.dashboard_view'))
        else:
            error = "Invalid Credentials."
            
    return render_template('admin_login.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.pop('is_admin', None)
    # UPDATED: Redirects back to the admin login page
    return redirect(url_for('auth.admin_login'))