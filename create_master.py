import pandas as pd
import random
from faker import Faker

# CONFIGURATION
fake = Faker('en_PH')
NUM_PEOPLE = 2000
FILENAME = "Master_List.xlsx"

DEPARTMENTS = [
    "SOIT", "ETYSBM", "SMDA", "DLA", 
    "School of Health Sciences",  
    "Senior High School"
]

def generate_rfid_uid():
    """Generates a random 8-character hex code (e.g., A3B2C1D4)"""
    return "".join([random.choice("0123456789ABCDEF") for _ in range(8)])

print(f"Generating {NUM_PEOPLE} mock users (Students & Employees)...")

data = []
for _ in range(NUM_PEOPLE):
    # 90% Student, 10% Employee
    is_student = random.random() < 0.9
    
    if is_student:
        # Student Number: Year + 6 Digits
        batch = random.choice(["2022", "2023", "2024", "2025"])
        seq = random.randint(100000, 999999) 
        id_number = f"{batch}{seq}"
        role = "Student"
    else:
        # Employee ID: E-XXXX
        id_number = f"E-{random.randint(1000, 9999)}"
        role = "Employee"

    row = {
        "RFID_UID": generate_rfid_uid(), 
        "ID_Number": id_number,
        "Last_Name": fake.last_name(),
        "First_Name": fake.first_name(),
        "Department": random.choice(DEPARTMENTS),
        "Role": role
    }
    data.append(row)

# Save to Excel
df = pd.DataFrame(data)
df.to_excel(FILENAME, index=False)

print(f"✅ DONE! Created '{FILENAME}' with {len(df)} records.")