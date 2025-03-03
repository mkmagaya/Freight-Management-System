import streamlit as st
import os
import json
from datetime import datetime
from fpdf import FPDF

# Directories
DATA_DIR = "data"
UPLOAD_FOLDER = "uploads"
CHARGE_SHEETS_FOLDER = "charge_sheets"
INVOICES_FOLDER = "invoices"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHARGE_SHEETS_FOLDER, exist_ok=True)
os.makedirs(INVOICES_FOLDER, exist_ok=True)

# Modes for selection
modes = ["Air Freight", "Road Freight", "Sea Freight", "Bond", "Export"]

# Road Freight routes with specific prefixes
road_freight_routes = {
    "Beitbridge": "KY",
    "Mutare": "KAA",
    "Plumtree": "KEX",
    "Chirundu": "SY"
}

# Sample registered clients (Load from file if needed)
registered_clients = ["ABC Logistics", "XYZ Traders", "Global Cargo Ltd"]

# Function to get next file reference
def get_next_file_reference(mode, route=None):
    today = datetime.today()
    month_year = today.strftime("%m/%Y")
    
    # Determine prefix
    prefix = road_freight_routes.get(route, mode[:2].upper())

    # Load running numbers
    data_file = os.path.join(DATA_DIR, "running_numbers.json")
    running_numbers = json.load(open(data_file)) if os.path.exists(data_file) else {}

    # Reset counter if new month starts
    key = f"{prefix}/{month_year}"
    running_numbers[key] = running_numbers.get(key, 0) + 1
    new_number = str(running_numbers[key]).zfill(3)

    # Save updated numbers
    with open(data_file, "w") as file:
        json.dump(running_numbers, file)

    return f"{prefix}{new_number}/{month_year}"

# Streamlit UI
st.title("Freight Management System")

# Select shipment mode
mode = st.selectbox("Select Mode", modes)
route = st.selectbox("Select Route", list(road_freight_routes.keys())) if mode == "Road Freight" else None

# Generate file reference
if st.button("Generate File Reference"):
    file_ref = get_next_file_reference(mode, route)
    st.session_state.setdefault("file_refs", []).append(file_ref)
    st.success(f"Generated File Reference: {file_ref}")

# Select file reference
file_refs = st.session_state.get("file_refs", [])
selected_ref = st.selectbox("Select File Reference", file_refs if file_refs else ["No references yet"], index=0)

# Customer Selection/Input
st.subheader("Customer Details")
customer_option = st.radio("Choose Customer", ["Select from Registered Clients", "Enter Manually"])

customer = st.selectbox("Select Customer", registered_clients) if customer_option == "Select from Registered Clients" else st.text_input("Enter Customer Name")

# # 📌 NHS Charge Sheet Data Entry
# st.subheader("Enter Charges for Selected File Reference")
# charge_fields = [
#     "Disbursement Fees", "Professional Handlers", "Agency", "Documentation Fee", "Storage (DHL)", 
#     "Border Agent Handling Fee", "Handling", "Airway Bill Fee", "Release Fee (DHL)", "GMS Charges", 
#     "ZIMRA Submission Fee", "ZIMRA Duty", "ZIMRA VAT", "Physical Inspection", "Special Attendance", 
#     "Presumptive Tax", "RIB Entry", "Warehouse Entry", "Consumption Entry", "Export Permits", 
#     "Phytosanitary Certificate", "CSA/SADC Certificate of Origin", "Port Health and EMA Inspection Fee", 
#     "AMA Certificate", "Courier (FedEx/DHL)", "Cargo Carriers", "Professional Handlers", 
#     "PE Charges at Port of Entry", "VAT @ 14.5%"
# ]
# charge_data = {field: st.number_input(f"{field} (USD)", min_value=0.0, format="%.2f") for field in charge_fields}

# 📌 NHS Charge Sheet Data Entry
st.subheader("Enter Charges for Selected File Reference")

charge_fields = [
    "Disbursement Fees", "Professional Handlers", "Agency", "Documentation Fee", "Storage (DHL)", 
    "Border Agent Handling Fee", "Handling", "Airway Bill Fee", "Release Fee (DHL)", "GMS Charges", 
    "ZIMRA Submission Fee", "ZIMRA Duty", "ZIMRA VAT", "Physical Inspection", "Special Attendance", 
    "Presumptive Tax", "RIB Entry", "Warehouse Entry", "Consumption Entry", "Export Permits", 
    "Phytosanitary Certificate", "CSA/SADC Certificate of Origin", "Port Health and EMA Inspection Fee", 
    "AMA Certificate", "Courier (FedEx/DHL)", "Cargo Carriers", "Professional Handlers", 
    "PE Charges at Port of Entry", "VAT @ 15%"
]

charge_data = {}
for i, field in enumerate(charge_fields):
    charge_data[field] = st.number_input(f"{field} (USD)", min_value=0.0, format="%.2f", key=f"charge_{i}")


# Function to generate charge sheet PDF
def generate_charge_sheet(reference, customer, charge_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Charge Out Sheet - {reference}", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 8)
    pdf.cell(200, 10, f"Customer: {customer}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 8)
    pdf.cell(100, 10, "NHS Service", border=1)
    pdf.cell(100, 10, "Charge (USD)", border=1, ln=True)

    total_amount = 0
    for field, amount in charge_data.items():
        pdf.cell(100, 10, field, border=1)
        pdf.cell(100, 10, f"${amount:.2f}", border=1, ln=True)
        total_amount += amount

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(100, 10, f"Total: ${total_amount:.2f}", ln=True)

    pdf.ln(15)
    pdf.set_font("Arial", "", 8)
    pdf.cell(100, 10, "Compiled by: Operations", ln=True)
    pdf.cell(100, 10, "Approver 1: ________________", ln=True)
    pdf.cell(100, 10, "Approver 2: ________________", ln=True)

    charge_sheet_path = os.path.join(CHARGE_SHEETS_FOLDER, f"Charge_Sheet_{reference.replace('/', '')}.pdf")
    pdf.output(charge_sheet_path)
    return charge_sheet_path

# Generate NHS Charge Sheet
if st.button("Generate Charge Sheet"):
    if selected_ref and customer:
        charge_sheet_path = generate_charge_sheet(selected_ref, customer, charge_data)
        st.success(f"Charge Sheet Generated: {charge_sheet_path}")
        with open(charge_sheet_path, "rb") as f:
            st.download_button("Download Charge Sheet", f, file_name=f"Charge_Sheet_{selected_ref}.pdf", mime="application/pdf")
    else:
        st.error("Select a file reference and customer.")

# 🚀 Final Enhancements
# ✅ Full NHS Charge Sheet Format
# ✅ Approver Signatures Section
# ✅ Electronic Approval (TBD in Next Version)

