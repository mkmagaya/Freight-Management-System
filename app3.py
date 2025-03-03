import streamlit as st
import os
from datetime import datetime

# Options for modes
modes = ["Air Freight", "Road Freight", "Sea Freight", "Bond", "Export"]

# Road Freight routes (only available for Road Freight)
road_freight_routes = ["Beitbridge", "Mutare", "Plumtree", "Chirundu"]

# Folder to store uploads
UPLOAD_FOLDER = "uploads"

# Function to generate file reference based on mode and route
def generate_file_reference(mode, route=None):
    # Get today's date for file reference generation
    date_today = datetime.today().strftime('%d/%m/%y')
    
    # Build the file reference
    if mode == "Road Freight" and route:
        file_reference = f"{route}_{date_today.replace('/', '')}"
    else:
        file_reference = f"{mode}_{date_today.replace('/', '')}"
    
    return file_reference

# Collect input from the user
mode = st.selectbox("Select Mode", modes)

# Conditionally show routes based on selected mode
route = None
if mode == "Road Freight":
    route = st.selectbox("Select Route", road_freight_routes)

# Display selected mode and route
st.write(f"Selected Mode: {mode}")
if route:
    st.write(f"Selected Route: {route}")

# Process file upload if required
uploaded_file = st.file_uploader("Upload a file", type=["pdf", "jpg", "png"])

if uploaded_file:
    # Generate the file reference
    file_reference = generate_file_reference(mode, route)
    filename = f"{file_reference}_{uploaded_file.name}"
    
    # Create the directory if it does not exist
    file_path = os.path.join(UPLOAD_FOLDER, file_reference)
    os.makedirs(file_path, exist_ok=True)  # This will create the directory if it doesn't exist
    
    # Save the uploaded file
    save_path = os.path.join(file_path, filename)
    try:
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"File saved: {save_path}")
    except Exception as e:
        st.error(f"Error saving file: {e}")
