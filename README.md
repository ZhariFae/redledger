# Campus Visitor Logging System

A lightweight, Flask-based web application designed to digitize visitor tracking for campus or facility access. This system replaces physical logbooks with a digital interface, offering real-time data visualization, automated Excel logging, and administrative reporting capabilities.

## 📋 Features

-   **User Portal:** simple, fast entry form for Students and Guests.
    
    -   _Students:_ Validates 10-digit Student IDs automatically.
        
    -   _Guests:_ Captures agency/department details.
        
-   **Automated Database:** entries are automatically saved to monthly Excel files (e.g., `log_202601.xlsx`) to ensure data persistence and easy archiving.
    
-   **Admin Dashboard:**
    
    -   Secure login authentication.
        
    -   Real-time statistics (Total Visitors, Peak Hours, Busiest Days).
        
    -   Dynamic charts for Department/Program distribution.
        
    -   Historical data filtering by Year, Month, Day, and Hour.
        
-   **Reporting:** one-click generation of formatted Excel reports, including summary statistics and pie charts.
    

## 🛠️ Technology Stack

-   **Backend:** Python (Flask)
    
-   **Data Manipulation:** Pandas
    
-   **Storage:** Local Excel Files (`.xlsx`)
    
-   **Reporting Engine:** XlsxWriter, OpenPyXL
    
-   **Configuration:** Python-Dotenv
    

## ⚙️ Installation & Setup

### 1. Prerequisites

Ensure you have **Python 3.8+** installed on your system.

### 2. Clone or Download

Extract the project files to your local directory.

### 3. Install Dependencies

Open your terminal (Command Prompt) in the project folder and run:

Bash

```
pip install -r requirements.txt

```

### 4. Configuration (Environment Variables)

For security, this project uses environment variables to store credentials. You must create a file named `.env` in the root directory.

1.  Create a file named `.env`
    
2.  Add the following configurations:
    

Ini, TOML

```
FLASK_SECRET_KEY=YourSecureRandomStringHere
ADMIN_USERNAME=Admin123
ADMIN_PASSWORD=MapuaUniv123

```

> **Note:** The `.env` file is excluded from version control via `.gitignore` to protect sensitive information.

## 🚀 Usage

### Starting the Application

Run the following command in your terminal:

Bash

```
python app.py

```

You should see output indicating the server is running (usually `Running on http://127.0.0.1:5000`).

### Accessing the System

Open your web browser and navigate to:

1.  **Public Logbook:** `http://127.0.0.1:5000/`
    
    -   Used by students and guests to sign in.
        
2.  **Admin Dashboard:** `http://127.0.0.1:5000/admin_login`
    
    -   Use the credentials defined in your `.env` file to log in.
        

## 📂 Project Structure

    TheRedLedger/
    │
    ├── Record/                 # Auto-generated Excel database storage
    │   ├── 2025/               # Yearly archives
    │   └── 2026/
    │
    ├── routes/                 # Modular Application Logic (Blueprints)
    │   ├── __init__.py         # Package initialization
    │   ├── auth.py             # Admin authentication routes
    │   ├── dashboard.py        # Analytics and reporting routes
    │   └── main.py             # Public kiosk and form submission routes
    │
    ├── static/                 # Static Assets
    │   └── css/
    │       ├── admin.css       # Admin login styling
    │       ├── dashboard.css   # Dashboard layout and theming
    │       └── login.css       # Main kiosk interface styling
    │
    ├── templates/              # HTML Interface Files
    │   ├── admin_login.html    # Admin login page
    │   ├── dashboard.html      # Analytics dashboard
    │   └── index.html          # Main student/guest kiosk
    │
    ├── .env                    # Configuration secrets (Excluded from Git)
    ├── .gitignore              # Git exclusion rules
    ├── app.py                  # Main application entry point
    ├── dummy_data.py           # Utility for generating test records
    ├── README.md               # Project documentation
    ├── requirements.txt        # Python dependency list
    └── utils.py                # Shared helper functions & Excel logic

## 🛡️ Security Note

This application is designed for **local deployment**. If deploying to a public server, ensure `DEBUG=True` is turned off in `app.py` and that the `.env` file is not accessible publicly.

## 📄 License

This project is created for educational purposes within Mapúa University.