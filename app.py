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
# modes = ["Air Freight", "Road Freight", "Sea Freight", "Bond", "Export"]
modes = {
    "Air Freight": "AA", 
    "Road Freight": "", 
    "Sea Freight": "SA", 
    "Bond": "KB", 
    "Export": "KE",
    "Transit": "SE"
}

# Road Freight routes with specific prefixes
road_freight_routes = {
    "Beitbridge": "KA",
    "Mutare": "KX",
    "Plumtree": "KAA",
    "Chirundu": "KAA"
}

# Sample registered clients (Load from file if needed)
# registered_clients = ["ABC Logistics", "XYZ Traders", "Global Cargo Ltd"]
registered_clients = {
    "ABC Logistics": "TSLC0001",
    "XYZ Traders": "TSLC0002",
    "Global Cargo Ltd": "TSLC0003"
}

# Function to get next file reference
def get_next_file_reference(mode, route=None):
    today = datetime.today()
    month_year = today.strftime("%m/%Y")
    
    # Determine prefix
    # prefix = road_freight_routes.get(route, mode[:2].upper())
    prefix = road_freight_routes.get(route, modes.get(mode))

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
st.title("File Management System")

# Select shipment mode
# mode = st.selectbox("Select Mode", modes)
mode = st.selectbox("Select Mode", list(modes.keys()))
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

customer = st.selectbox("Select Customer", registered_clients.keys()) if customer_option == "Select from Registered Clients" else st.text_input("Enter Customer Name")

# # NHS Charge Sheet Data Entry
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

# NHS Charge Sheet Data Entry
st.subheader("Enter Charges for Selected File Reference")

charge_fields = [
    "Disbursement Fees", "Professional Handlers", "Agency", "Documentation Fee", "Storage (DHL)", 
    "Border Agent Handling Fee", "Handling", "Airway Bill Fee", "Release Fee (DHL)", "GMS Charges", 
    "ZIMRA Submission Fee", "ZIMRA Duty", "ZIMRA VAT", "Physical Inspection", "Special Attendance", 
    "Presumptive Tax", "RIB Entry", "Warehouse Entry", "Consumption Entry", "Export Permits", 
    "Phytosanitary Certificate", "CSA/SADC Certificate of Origin", "Port Health and EMA Inspection Fee", 
    "AMA Certificate", "Courier (FedEx/DHL)", "Cargo Carriers", "Professional Handlers", 
    "PE Charges at Port of Entry", "Other"
]

charge_data = {}
for i, field in enumerate(charge_fields):
    charge_data[field] = st.number_input(f"{field} (USD)", min_value=0.0, format="%.2f", key=f"charge_{i}")


# Function to generate charge sheet with non-zero values only
def generate_charge_sheet(reference, customer, charge_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 8, f"Charge Out Sheet - {reference}", ln=True, align="C")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 5, f"Customer: {customer}", ln=True)
    pdf.cell(100, 5, f"Customer ID: {registered_clients.get(customer)}", ln=True)
    pdf.cell(100, 5, f"Date: {datetime.today().strftime('%d-%m-%Y')}", ln=True)
    
    pdf.ln(4)

    # Table Headers
    pdf.set_font("Arial", "B", 10)
    pdf.cell(120, 6, "NHS Service", border=1)
    pdf.cell(60, 6, "Charge (USD)", border=1, ln=True)

    pdf.set_font("Arial", "", 10)
    
    total_amount = 0
    for field, amount in charge_data.items():
        if amount > 0:  # Only include non-zero charges
            pdf.cell(120, 6, field, border=1)
            pdf.cell(60, 6, f"${amount:.2f}", border=1, ln=True)
            total_amount += amount

    pdf.ln(4)

    # Total Amount
    pdf.set_font("Arial", "B", 10)
    pdf.cell(120, 6, "TOTAL", border=1)
    pdf.cell(60, 6, f"${total_amount:.2f}", border=1, ln=True)

    pdf.ln(6)  

    # Approval Section
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 5, "Compiled by: Operations", ln=True)
    pdf.cell(100, 5, "Approver 1: ___________________", ln=True)
    pdf.cell(100, 5, "Approver 2: ___________________", ln=True)

    # Save PDF
    charge_sheet_path = f"charge_sheets/Charge_Sheet_{reference.replace('/', '')}.pdf"
    pdf.output(charge_sheet_path)
    
    return charge_sheet_path


# Function to generate Sales Estimate Invoice PDF
def generate_sales_estimate(reference, customer, charge_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 8, "IFS SALES ESTIMATE INVOICE", ln=True, align="C")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 5, f"Customer: {customer}", ln=True)
    pdf.cell(100, 5, f"Customer ID: {registered_clients.get(customer)}", ln=True)
    pdf.cell(100, 5, f"Invoice Ref: {reference}", ln=True)
    pdf.cell(100, 5, f"Date: {datetime.today().strftime('%d-%m-%Y')}", ln=True)

    pdf.ln(4)

    # Table Headers
    pdf.set_font("Arial", "B", 10)
    pdf.cell(120, 6, "Service Description", border=1)
    pdf.cell(60, 6, "Amount (USD)", border=1, ln=True)

    pdf.set_font("Arial", "", 10)

    subtotal = 0
    for field, amount in charge_data.items():
        if amount > 0:
            pdf.cell(120, 6, field, border=1)
            pdf.cell(60, 6, f"${amount:.2f}", border=1, ln=True)
            subtotal += amount

    pdf.ln(4)

    # VAT Calculation
    vat = subtotal * 0.15  # Assuming 15% VAT rate
    total = subtotal + vat

    pdf.set_font("Arial", "B", 10)
    pdf.cell(120, 6, "TOTAL EXCL. VAT", border=1)
    pdf.cell(60, 6, f"${subtotal:.2f}", border=1, ln=True)

    pdf.cell(120, 6, "VAT @ 15%", border=1)
    pdf.cell(60, 6, f"${vat:.2f}", border=1, ln=True)

    pdf.cell(120, 6, "TOTAL", border=1)
    pdf.cell(60, 6, f"${total:.2f}", border=1, ln=True)

    pdf.ln(10)
    
    # Payment Terms & Notes (Based on Template)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, "This Sales Estimate is valid for 30 days. Payment should be made in full before service is rendered.", border=0)

    # Save PDF
    sales_estimate_path = f"invoices/Sales_Estimate_{reference.replace('/', '')}.pdf"
    pdf.output(sales_estimate_path)
    
    return sales_estimate_path



# Generate Charge Sheet Button
if st.button("Generate Charge Sheet"):
    if selected_ref and customer:
        charge_sheet_path = generate_charge_sheet(selected_ref, customer, charge_data)
        st.success(f"Charge Sheet Generated: {charge_sheet_path}")
        with open(charge_sheet_path, "rb") as f:
            st.download_button("Download Charge Sheet", f, file_name=f"Charge_Sheet_{selected_ref}.pdf", mime="application/pdf")
    else:
        st.error("Select a file reference and customer.")

# Generate Sales Estimate Button
if st.button("Generate Sales Estimate Invoice"):
    if selected_ref and customer:
        sales_estimate_path = generate_sales_estimate(selected_ref, customer, charge_data)
        st.success(f"Sales Estimate Generated: {sales_estimate_path}")
        with open(sales_estimate_path, "rb") as f:
            st.download_button("Download Sales Estimate", f, file_name=f"Sales_Estimate_{selected_ref}.pdf", mime="application/pdf")
    else:
        st.error("Select a file reference and customer.")


# 🚀 Final Enhancements
# ✅ Full NHS Charge Sheet Format
# ✅ Approver Signatures Section
# ✅ Electronic Approval (TBD in Next Version)

