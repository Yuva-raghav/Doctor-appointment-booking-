import gspread
from google.oauth2.service_account import Credentials

# ---------------- CONFIG ----------------
SPREADSHEET_ID = "1WeAySjhKMjq97tefVxLIZd3NJRTmacFVhfaSBTyXA7Q"
SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# --------------------------------------

# In-memory user sessions
sessions = {}

def connect_sheet():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)

def get_sheets():
    sheet = connect_sheet()
    doctors = sheet.worksheet("doctors availability")
    customers = sheet.worksheet("customer details")
    return doctors, customers

def get_available_doctors():
    doctors_sheet, _ = get_sheets()
    records = doctors_sheet.get_all_records()

    available = []
    for idx, row in enumerate(records, start=2):
        try:
            slots = int(row["available_slots"])
        except:
            continue

        if slots > 0:
            row["row_index"] = idx
            available.append(row)

    return available

def deduct_slot(row_index, current_slots):
    doctors_sheet, _ = get_sheets()
    doctors_sheet.update_cell(row_index, 3, current_slots - 1)

def save_customer(name, phone, department, doctor):
    _, customers_sheet = get_sheets()
    customers_sheet.append_row([
        name,
        phone,
        department,
        doctor,
        "Confirmed"
    ])
