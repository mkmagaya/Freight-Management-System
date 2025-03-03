import streamlit as st
import os
import json
from datetime import datetime
from fpdf import FPDF

# Directories
DATA_DIR = "data"
UPLOAD_FOLDER = "uploads"
CHARGE_SHEETS_FOLDER = "charge_sheets"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHARGE_SHEETS_FOLDER, exist_ok=True)

# Modes for selection
modes = ["Air Freight", "Road Freight", "Sea Freight", "Bond", "Export"]

# Road Freight routes with specific prefixes
road_freight_routes = {
    "Beitbridge": "KY",
    "Mutare": "KAA",
    "Plumtree": "KEX",
    "Chirundu": "SY"
}

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
    """
    Generates the next available file reference, resetting the count each month.
    """
    today = datetime.today()
    month_year = today.strftime("%m/%Y")  # Example: "03/2025"

    # Determine prefix
    if mode == "Road Freight" and route in road_freight_routes:
        prefix = road_freight_routes[route]
    else:
        prefix = mode[:2].upper()  # Default to first 2 letters

    # Load running numbers
    running_numbers = load_running_numbers()

    # Reset counter if a new month starts
    key = f"{prefix}/{month_year}"
    if key not in running_numbers:
        running_numbers[key] = 1
    else:
        running_numbers[key] += 1

    new_number = str(running_numbers[key]).zfill(3)  # Ensure 3-digit format (001, 002, ...)

    # Save updated running numbers
    save_running_numbers(running_numbers)

    return f"{prefix}{new_number}/{month_year}"

# Streamlit UI
st.title("File Reference & Document Management")

# Select shipment mode
mode = st.selectbox("Select Mode", modes)

# If Road Freight, allow selecting route
route = None
if mode == "Road Freight":
    route = st.selectbox("Select Route", list(road_freight_routes.keys()))

# Generate file reference
if st.button("Generate File Reference"):
    file_ref = get_next_file_reference(mode, route)
    st.session_state.setdefault("file_refs", []).append(file_ref)  # Store in session
    st.success(f"Generated File Reference: {file_ref}")

# Dropdown for selecting generated file references
file_refs = st.session_state.get("file_refs", [])
selected_ref = st.selectbox("Select File Reference", file_refs if file_refs else ["No references yet"], index=0)

# File Upload Section
uploaded_file = st.file_uploader("Upload Document", type=["pdf", "jpg", "png"])

if uploaded_file and selected_ref and selected_ref != "No references yet":
    if st.button("Upload"):
        # Ensure directory exists
        file_path = os.path.join(UPLOAD_FOLDER, selected_ref.replace("/", ""))
        os.makedirs(file_path, exist_ok=True)

        # Save file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{uploaded_file.name.split('.')[0]}_{timestamp}.{uploaded_file.name.split('.')[-1]}"  # ✅ Modified filename
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

# Function to generate charge sheet PDF
def generate_charge_sheet(reference, charge_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Charge Sheet - {reference}", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 12)

    total_amount = 0
    for field, amount in charge_data.items():
        pdf.cell(100, 10, f"{field}: ${amount:.2f}", ln=True)
        total_amount += amount

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(100, 10, f"Total: ${total_amount:.2f}", ln=True)

    # Save the PDF
    charge_sheet_path = os.path.join(CHARGE_SHEETS_FOLDER, f"Charge_Sheet_{reference.replace('/', '')}.pdf")
    pdf.output(charge_sheet_path)
    return charge_sheet_path

# Generate Charge Sheet Button
if st.button("Generate Charge Sheet"):
    if selected_ref and selected_ref != "No references yet":
        charge_sheet_path = generate_charge_sheet(selected_ref, charge_data)
        st.success(f"Charge Sheet Generated: {charge_sheet_path}")
        with open(charge_sheet_path, "rb") as f:
            st.download_button("Download Charge Sheet", f, file_name=f"Charge_Sheet_{selected_ref}.pdf", mime="application/pdf")
    else:
        st.error("Please select a valid file reference before generating a charge sheet.")
