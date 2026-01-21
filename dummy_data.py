import pandas as pd
import random
import os
from datetime import datetime, timedelta
from faker import Faker

# -- CONFIGURATION --
fake = Faker('tl_PH')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORD_DIR = os.path.join(BASE_DIR, 'Record')
YEAR = "2025"

# -- DATA POOLS --
# Updated Program Selection from your HTML
programs = [
    "CS", "IT", "EMC", "DS", "IS", "NUR", 
    "APSY", "BPSY", "BIO", "MT", "PHAR", 
    "PT", "RT", "SHS", "Other"
]

agencies = ["Visitor", "Alumni", "Parent", "Accreditor"]

def generate_month_data(month_num, filename, target_count):
    data = []
    
    # Determine number of days in the specific month
    if month_num == 11:
        max_days = 30
        month_name = "November"
    else:
        max_days = 31
        month_name = "December"
        
    print(f"Generating {target_count} rows for {month_name} {YEAR}...")
    
    for _ in range(target_count):
        # 1. Random Date Generation
        day = random.randint(1, max_days)
        current_date = datetime(int(YEAR), month_num, day)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # 2. Random Time (07:00 - 18:59)
        hour = random.randint(7, 18)
        minute = random.randint(0, 59)
        time_str = f"{hour:02d}:{minute:02d}"
        
        # 3. Determine Type (90% Student, 10% Guest)
        is_student = random.random() < 0.9
        
        # 4. Generate Filipino Name
        f_name = fake.first_name()
        l_name = fake.last_name()
        
        if is_student:
            row = {
                'Type': 'Student',
                'Last_Name': l_name,
                'First_Name': f_name,
                # Random ID: Year-Random5Digits (e.g., 2025-12345)
                'ID_Number': f"{YEAR}-{random.randint(10000,99999)}", 
                'Program': random.choice(programs),
                'Time_In': time_str,
                'Date_Logged': date_str
            }
        else:
            row = {
                'Type': 'Guest',
                'Last_Name': l_name,
                'First_Name': f_name,
                'ID_Number': 'N/A',
                'Program': random.choice(agencies), # Use Agency list for guests
                'Time_In': time_str,
                'Date_Logged': date_str
            }
        data.append(row)

    # -- SAVE TO EXCEL --
    # Ensure folders exist: Record/2025
    year_folder = os.path.join(RECORD_DIR, YEAR)
    if not os.path.exists(year_folder):
        os.makedirs(year_folder)
        
    full_path = os.path.join(year_folder, filename)
    
    df = pd.DataFrame(data)
    
    # Optional: Sort the data by date and time to make it look realistic
    df = df.sort_values(by=['Date_Logged', 'Time_In'])
    
    df.to_excel(full_path, index=False)
    
    print(f"✅ Success! Generated {target_count} rows in: {full_path}")

if __name__ == "__main__":
    # Generate November 2025
    generate_month_data(11, "log_202511.xlsx", 1000)
    
    # Generate December 2025
    generate_month_data(12, "log_202512.xlsx", 1000)