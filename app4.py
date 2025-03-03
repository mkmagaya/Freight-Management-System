import streamlit as st
import os
from datetime import datetime

# Folder to store uploads
UPLOAD_FOLDER = "uploads"

# Modes for selection
modes = ["Air Freight", "Road Freight", "Sea Freight", "Bond", "Export"]

# Road Freight routes with specific prefixes
road_freight_routes = {
    "Beitbridge": "KY",
    "Mutare": "KAA",
    "Plumtree": "KEX",
    "Chirundu": "SY"
}

# Function to generate file reference based on mode, route, and date
def generate_file_reference(mode, route=None):
    # Get current month and year
    today = datetime.today()
    month_year = today.strftime("%m/%Y")
    
    # Get the running number for the current month
    running_number = get_running_number(month_year)
    
    # Determine the reference prefix based on the route for Road Freight
    if mode == "Road Freight" and route:
        prefix = road_freight_routes.get(route, "KA")  # Default to "KA" if the route is not found
        file_reference = f"{prefix}{running_number}/{month_year.replace('/', '')}"
    else:
        # Default to KA for non-Road Freight modes
        file_reference = f"{mode[:2]}{running_number}/{month_year.replace('/', '')}"
    
    return file_reference

# Function to get and update the running number
def get_running_number(month_year):
    # Ensure the uploads folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Path for the running number store (can be a simple text file)
    running_number_file = f"running_numbers_{month_year.replace('/', '')}.txt"
    
    # Ensure the directory for the running number file exists
    running_number_dir = os.path.dirname(running_number_file)
    if not os.path.exists(running_number_dir) and running_number_dir:
        os.makedirs(running_number_dir)

    # Check if the file for the current month exists
    if os.path.exists(running_number_file):
        with open(running_number_file, "r") as file:
            running_number = int(file.read())
    else:
        running_number = 0
    
    # Increment the running number
    running_number += 1
    
    # Save the updated running number for the next use
    with open(running_number_file, "w") as file:
        file.write(str(running_number).zfill(3))  # Ensure 3 digits (e.g., 001, 002)
    
    return str(running_number).zfill(3)

# Collect input from the user
mode = st.selectbox("Select Mode", modes)

# Conditionally show routes based on selected mode
route = None
if mode == "Road Freight":
    route = st.selectbox("Select Route", road_freight_routes.keys())

# Display selected mode and route
st.write(f"Selected Mode: {mode}")
if route:
    st.write(f"Selected Route: {route}")

# Process file upload if required
uploaded_file = st.file_uploader("Upload a file", type=["pdf", "jpg", "png"])

if uploaded_file:
    # Generate the file reference
    file_reference = generate_file_reference(mode, route)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S.%f")  # Timestamp for uniqueness
    filename = f"{file_reference}_{uploaded_file.name.split('.')[0]}_{timestamp}.{uploaded_file.name.split('.')[-1]}"
    
    # Create the directory if it does not exist
    file_path = os.path.join(UPLOAD_FOLDER, file_reference)  # Corrected path construction
    os.makedirs(file_path, exist_ok=True)  # This will create the directory if it doesn't exist
    
    # Save the uploaded file
    save_path = os.path.join(file_path, filename)
    try:
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"File saved: {save_path}")
    except Exception as e:
        st.error(f"Error saving file: {e}")
