# The Red Ledger 📕
### RFID Library Attendance System - Mapúa University

**The Red Ledger** is a Flask-based web application designed to track, manage, and visualize library attendance for Mapúa University. It interfaces with RFID scanners to log student and employee entry/exit times and provides a powerful admin dashboard for analytics.

---

## 🚀 Key Features

### 1. **Smart RFID Logging**
- **Tap IN / Tap OUT:** Automatically detects if a user is entering or leaving based on their last status.
- **"Forgotten Logout" Fix:** If a student forgets to tap out and returns the next day, the system automatically:
    - Closes the previous day's session at **21:00 (9:00 PM)**.
    - Marks the record as "Auto-Closed".
    - Starts a fresh "IN" session for the current visit.

### 2. **Admin Dashboard**
- **Live Analytics:** View real-time Total Visitors, Peak Hours, and Busiest Days.
- **Interactive Charts:**
    - **Traffic Volume:** Hourly breakdown with gradient bar charts.
    - **Department Share:** Doughnut chart showing which programs use the library most.
    - **Visitor Composition:** Student vs. Employee ratio.
- **Dual View Modes:**
    - **Monthly View:** Deep dive into specific months with granular **Day** and **Hour** filters.
    - **Quarterly View:** aggregated data based on Mapúa's academic terms (Quarter 1 - Quarter 4).

### 3. **Reporting & Tools**
- **Excel Export:** Download comprehensive reports for any selected date range or month.
- **Print Mode:** A clean, ink-friendly layout for printing detailed logs directly from the browser.
- **Advanced Filtering:** Drill down data by specific days or hours using the advanced filter modal.

---

## 🛠️ Installation & Setup

### **1. Prerequisites**
Ensure you have Python installed. Then, install the required dependencies:

```bash
pip install -r requirements.txt

```

_(If `requirements.txt` is missing, you need: `flask`, `pandas`, `openpyxl`, `xlsxwriter`, `faker`)_

### **2. Generate Dummy Data (First Run)**

Before running the app, you need a database of users and some historical logs to visualize.

**Step A: Create the Master List** Generates `Master_List.xlsx` with 500 fake students and employees.

Bash

```
python create_master.py

```

**Step B: Generate Historical Logs** Simulates library traffic from Term 1 (Aug 2025) to present, including realistic "forgotten logout" scenarios.

Bash

```
python generate_history.py

```

----------

## 🖥️ How to Run

### **1. Start the Server**

Run the Flask application:

Bash

```
python app.py

```

_Access the dashboard at:_ `http://127.0.0.1:5000/`

**Login Credentials:**

-   **Username:** `Admin123`
    
-   **Password:** `MapuaUniv123`
    

### **2. Simulate RFID Taps (Testing)**

Since you may not have the physical scanner connected, use this script to simulate a card tap:

Bash

```
python test_tap.py

```

-   **First Run:** Logs the user **IN**.
    
-   **Second Run:** Logs the user **OUT**.
    
-   **Next Day:** Auto-closes the previous session and logs **IN**.
    

----------

## 📂 Project Structure

```
RedLedger/
│
├── app.py                 # Main Flask Application
├── create_master.py       # Script: Generates Master_List.xlsx
├── generate_history.py    # Script: Generates past attendance logs
├── test_tap.py            # Script: Simulates RFID hardware taps
├── utils.py               # Helper functions (Excel handling)
├── requirements.txt       # Python dependencies
│
├── Record/                # Database Folder (Auto-generated)
│   ├── 2025/              # Logs organized by Year
│   └── 2026/
│
├── routes/                # Blueprint Routes
│   ├── api.py             # RFID Tap Logic & JSON API
│   ├── auth.py            # Login/Logout Logic
│   └── dashboard.py       # Dashboard Analytics & Reporting
│
├── static/
│   └── css/
│       ├── admin.css      # Login Page Styles
│       └── dashboard.css  # Main Dashboard Theme
│
└── templates/
    ├── admin_login.html   # Login Page
    └── dashboard.html     # Main Admin Interface

```

----------

## 🎨 Credits

**Developed for:** Mapúa University

**Theme:** "Cardinal Admin" (Custom CSS)

**Tech Stack:** Python, Flask, Pandas, Chart.js, Tom Select, DataTables.