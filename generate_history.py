import pandas as pd
import random
import os
from datetime import datetime, timedelta, time
from utils import RECORD_DIR

# --- CONFIGURATION ---
START_DATE = datetime(2025, 8, 1)   # Start of Term 1
END_DATE = datetime(2025, 12, 7)    # Day before Term 2 starts
DAILY_VISITORS = 120                # Average people per day
MASTER_FILE = "Master_List.xlsx"

# Probability Settings
PROB_MULTIPLE_VISIT = 0.15  # 15% of people visit more than once
PROB_FORGOT_LOGOUT = 0.05   # 5% forget to tap out

def load_master_list():
    if not os.path.exists(MASTER_FILE):
        print("❌ Error: Master_List.xlsx not found. Please run create_master.py first.")
        exit()
    return pd.read_excel(MASTER_FILE, dtype=str)

def generate_random_time(start_hour=7, end_hour=20):
    """Generates a random time between library hours."""
    hour = random.randint(start_hour, end_hour)
    minute = random.randint(0, 59)
    return time(hour, minute)

def add_minutes(t, minutes):
    """Adds minutes to a time object."""
    full_datetime = datetime(2000, 1, 1, t.hour, t.minute) + timedelta(minutes=minutes)
    return full_datetime.time()

def main():
    print(f"⏳ Generating History from {START_DATE.date()} to {END_DATE.date()}...")
    
    master_df = load_master_list()
    if master_df.empty:
        print("❌ Master List is empty.")
        return

    current_date = START_DATE
    all_logs = []

    # --- LOOP THROUGH EACH DAY ---
    while current_date <= END_DATE:
        # Skip Sundays (Library Closed)
        if current_date.weekday() == 6:
            current_date += timedelta(days=1)
            continue

        date_str = current_date.strftime("%Y-%m-%d")
        
        # 1. Pick today's visitors
        num_today = random.randint(DAILY_VISITORS - 20, DAILY_VISITORS + 40)
        daily_visitors = master_df.sample(n=min(num_today, len(master_df)))

        for _, person in daily_visitors.iterrows():
            
            # DECISION: How many times do they visit?
            visits = 1
            if random.random() < PROB_MULTIPLE_VISIT:
                visits = random.randint(2, 3)

            # Generate each visit
            current_time_in = generate_random_time(7, 16) # Start between 7am and 4pm
            
            for v in range(visits):
                # Duration: 30 mins to 3 hours
                duration = random.randint(30, 180)
                
                # Calculate Time Out
                # If they visit multiple times, ensure gaps between visits
                if v > 0:
                    # Add gap of 1-2 hours from previous checkout
                    current_time_in = add_minutes(current_time_in, duration + random.randint(60, 120))
                    if current_time_in.hour >= 20: break # Too late, stop visiting
                
                time_out_obj = add_minutes(current_time_in, duration)
                
                # Format Strings
                t_in_str = current_time_in.strftime("%H:%M")
                t_out_str = time_out_obj.strftime("%H:%M")
                notes = ""

                # DECISION: Did they forget to logout?
                # Only simulate this on their LAST visit of the day
                if v == visits - 1 and random.random() < PROB_FORGOT_LOGOUT:
                    # Simulate the system auto-closing it at 9 PM
                    t_out_str = "21:00"
                    notes = "Auto-Closed (Forgot Logout)"

                log_entry = {
                    'Type': person['Role'],
                    'Last_Name': person['Last_Name'],
                    'First_Name': person['First_Name'],
                    'ID_Number': person['ID_Number'],
                    'Program': person['Department'],
                    'Date_Logged': date_str,
                    'Time_In': t_in_str,
                    'Time_Out': t_out_str,
                    'Notes': notes
                }
                all_logs.append(log_entry)

        print(f"   Generated {len(daily_visitors)} visitors for {date_str}")
        current_date += timedelta(days=1)

    # --- SAVE TO MONTHLY FILES ---
    print("💾 Saving to Excel files...")
    
    df_all = pd.DataFrame(all_logs)
    
    # Group by Month (YYYYMM)
    df_all['Month_Key'] = df_all['Date_Logged'].apply(lambda x: x[:4] + x[5:7])
    
    for month_key, group in df_all.groupby('Month_Key'):
        year = month_key[:4]
        
        # Ensure folder exists
        year_dir = os.path.join(RECORD_DIR, year)
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)
            
        filename = f"log_{month_key}.xlsx"
        path = os.path.join(year_dir, filename)
        
        # Save
        group = group.drop(columns=['Month_Key']) # Clean up
        group.to_excel(path, index=False)
        print(f"   -> Created {filename} ({len(group)} records)")

    print("✅ History Generation Complete!")

if __name__ == "__main__":
    main()