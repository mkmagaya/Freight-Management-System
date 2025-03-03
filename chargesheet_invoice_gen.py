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

# Load running numbers from file
def load_running_numbers():
    data_file = os.path.join(DATA_DIR, "running_numbers.json")
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    return {}

# Save running numbers to file
def save_running_numbers(running_numbers):
    data_file = os.path.join(DATA_DIR, "running_numbers.json")
    with open(data_file, "w") as file:
        json.dump(running_numbers, file)

# Function to get and update running number
def get_next_file_reference(mode, route=None):
    today = datetime.today()
    month_year = today.strftime("%m/%Y")

    # Determine prefix
    if mode == "Road Freight" and route in road_freight_routes:
        prefix = road_freight_routes[route]
    else:
        prefix = mode[:2].upper()

    running_numbers = load_running_numbers()
    key = f"{prefix}/{month_year}"

    # Reset counter if a new month starts
    if key not in running_numbers:
        running_numbers[key] = 1
    else:
        running_numbers[key] += 1

    new_number = str(running_numbers[key]).zfill(3)  # Ensure 3-digit format (001, 002, ...)

    save_running_numbers(running_numbers)
    return f"{prefix}{new_number}/{month_year}"

# Streamlit UI
st.title("Freight Management System")

# Select shipment mode
mode = st.selectbox("Select Mode", modes)

# If Road Freight, allow selecting route
route = None
if mode == "Road Freight":
    route = st.selectbox("Select Route", list(road_freight_routes.keys()))

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

if customer_option == "Select from Registered Clients":
    customer = st.selectbox("Select Customer", registered_clients)
else:
    customer = st.text_input("Enter Customer Name")

# File Upload Section
uploaded_file = st.file_uploader("Upload Document", type=["pdf", "jpg", "png"])

if uploaded_file and selected_ref != "No references yet":
    if st.button("Upload"):
        file_path = os.path.join(UPLOAD_FOLDER, selected_ref.replace("/", ""))
        os.makedirs(file_path, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{uploaded_file.name.split('.')[0]}_{timestamp}.{uploaded_file.name.split('.')[-1]}"
        save_path = os.path.join(file_path, filename)

        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success(f"File uploaded successfully: {save_path}")

# 📌 Charge Input Section
st.subheader("Enter Charges for Selected File Reference")
charge_fields = ["VAT", "Customs", "Freight", "Penalties", "Other Charges"]
charge_data = {}

for field in charge_fields:
    charge_data[field] = st.number_input(f"{field} (USD)", min_value=0.0, format="%.2f")

# Generate Sales Estimate Invoice
def generate_invoice(reference, customer, charge_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Sales Estimate Invoice - {reference}", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Customer: {customer}", ln=True)

    total_amount = 0
    for field, amount in charge_data.items():
        pdf.cell(100, 10, f"{field}: ${amount:.2f}", ln=True)
        total_amount += amount

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(100, 10, f"Total: ${total_amount:.2f}", ln=True)

    invoice_path = os.path.join(INVOICES_FOLDER, f"Invoice_{reference.replace('/', '')}.pdf")
    pdf.output(invoice_path)
    return invoice_path

if st.button("Generate Sales Estimate Invoice"):
    if selected_ref and customer:
        invoice_path = generate_invoice(selected_ref, customer, charge_data)
        st.success(f"Invoice Generated: {invoice_path}")
        with open(invoice_path, "rb") as f:
            st.download_button("Download Invoice", f, file_name=f"Invoice_{selected_ref}.pdf", mime="application/pdf")
    else:
        st.error("Select a file reference and customer.")

# NHS Charge Sheet Section
st.subheader("Enter NHS Charges for Comparison")
nhs_charge_data = {}

for field in charge_fields:
    nhs_charge_data[field] = st.number_input(f"NHS {field} (USD)", min_value=0.0, format="%.2f")

# Compare NHS Charges and Identify Variances
st.subheader("Variance Analysis")
discrepancies = {}
for field in charge_fields:
    variance = nhs_charge_data[field] - charge_data[field]
    if variance != 0:
        discrepancies[field] = variance

if discrepancies:
    st.warning("Discrepancies found!")
    for field, variance in discrepancies.items():
        st.write(f"**{field}:** Variance of ${variance:.2f}")

# Generate NHS Charge Sheet
if st.button("Generate NHS Charge Sheet"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"NHS Charge Sheet - {selected_ref}", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Customer: {customer}", ln=True)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, "NHS Service", border=1)
    pdf.cell(100, 10, "Charge (USD)", border=1, ln=True)

    for field, amount in nhs_charge_data.items():
        pdf.cell(100, 10, field, border=1)
        pdf.cell(100, 10, f"${amount:.2f}", border=1, ln=True)

    charge_sheet_path = os.path.join(CHARGE_SHEETS_FOLDER, f"NHS_Charge_Sheet_{selected_ref.replace('/', '')}.pdf")
    pdf.output(charge_sheet_path)
    st.success("NHS Charge Sheet Generated")
