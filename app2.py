import streamlit as st
import os
from file_reference import generate_file_reference, save_file_reference

# # Streamlit UI
# st.title("📂 Clearing & Forwarding - File Reference Generator")

# # File Reference Form
# mode = st.selectbox("Select Mode:", ["Air Freight", "Road Freight", "Sea Freight", "Bond", "Export"])
# route = st.text_input("Enter Route:")

# # # File Upload Section
# # uploaded_file = st.file_uploader("Upload Initial Document", type=["pdf", "docx", "png", "jpg"])

# # if st.button("Generate File Reference"):
# #     if mode and route:
# #         file_reference = generate_file_reference(mode, route)
# #         document_path = None

# #         # Save uploaded file
# #         if uploaded_file:
# #             save_path = f"uploads/{file_reference}_{uploaded_file.name}"
# #             os.makedirs("uploads", exist_ok=True)
# #             with open(save_path, "wb") as f:
# #                 f.write(uploaded_file.read())
# #             document_path = save_path

# #         # Save file reference in DB
# #         save_file_reference(mode, route, file_reference, document_path)
# #         st.success(f"Generated File Reference: **{file_reference}**")
# #         if document_path:
# #             st.info(f"Document saved at: {document_path}")
# #     else:
# #         st.error("Please enter all details.")

# # Ensure the uploads directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# if uploaded_file:
#     # Generate a structured file name
#     file_reference = generate_file_reference(mode, route)
#     filename = f"{file_reference}_{uploaded_file.name}"
#     save_path = os.path.join(UPLOAD_FOLDER, filename)

#     # Write file to disk
#     try:
#         with open(save_path, "wb") as f:
#             f.write(uploaded_file.read())
#         st.success(f"File saved: {save_path}")

#         # Save file reference in DB
#         save_file_reference(mode, route, file_reference, save_path)

#     except Exception as e:
#         st.error(f"Error saving file: {e}")
import streamlit as st

# Options for modes
modes = ["Air Freight", "Road Freight", "Sea Freight", "Bond", "Export"]

# Road Freight routes (only available for Road Freight)
road_freight_routes = ["Beitbridge", "Mutare", "Plumtree", "Chirundu"]

# Collect input from the user
mode = st.selectbox("Select Mode", modes)

# Conditionally show routes based on selected mode
if mode == "Road Freight":
    route = st.selectbox("Select Route", road_freight_routes)
else:
    route = None  # No route for other modes

# Display selected mode and route
st.write(f"Selected Mode: {mode}")
if route:
    st.write(f"Selected Route: {route}")

# Process file upload if required
uploaded_file = st.file_uploader("Upload a file", type=["pdf", "jpg", "png"])
if uploaded_file:
    # Generate the file reference and save the file (code from previous step)
    file_reference = generate_file_reference(mode, route)
    filename = f"{file_reference}_{uploaded_file.name}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    try:
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"File saved: {save_path}")
    except Exception as e:
        st.error(f"Error saving file: {e}")
