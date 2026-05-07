import streamlit as st
import easyocr
from PIL import Image
import numpy as np
from docx import Document
import io
import re

st.set_page_config(page_title="Crossub OCR Tool", layout="centered")
st.title("📸 Screenshot to Lease Tool")
st.info("Upload a screenshot of the Crossub Property Details page.")

# --- STEP 1: UPLOAD & READ SCREENSHOT ---
uploaded_img = st.file_uploader("Upload Crossub Screenshot", type=["png", "jpg", "jpeg"])

extracted_data = {"Address": "", "Landlord": "", "Tenant": "", "Rent": 0.0}

if uploaded_img:
    with st.spinner("Reading screenshot..."):
        reader = easyocr.Reader(['en'])
        image = Image.open(uploaded_img)
        result = reader.readtext(np.array(image), detail=0)
        full_text = " ".join(result)

        # Basic logic to find data in the text (Customized for your system)
        # These regex patterns look for numbers near words like 'Rent'
        rent_match = re.search(r'Rent\s*\$?\s*(\d+)', full_text, re.IGNORECASE)
        if rent_match:
            extracted_data["Rent"] = float(rent_match.group(1))

        # Search for address patterns (e.g., Berry St, Wills Road)
        addr_match = re.search(r'(\d+\s+[\w\s]+(?:Road|Street|St|Rd|Ave))', full_text, re.IGNORECASE)
        if addr_match:
            extracted_data["Address"] = addr_match.group(1)

        st.success("Data Extracted! Please verify below.")

# --- STEP 2: VERIFY & AMEND ---
st.subheader("Confirm Details")
addr = st.text_input("Property Address", value=extracted_data["Address"])
l_name = st.text_input("Landlord Name") # Can be pulled if 'Landlord' is clear in image
t_name = st.text_area("Tenant Name(s)", value=extracted_data["Tenant"])
rent = st.number_input("Weekly Rent ($)", value=extracted_data["Rent"])
start_date = st.date_input("Lease Start Date")

st.divider()

# --- STEP 3: GENERATE ---
template = st.file_uploader("Upload Word Template (.docx)", type="docx")

if st.button("🚀 Generate Agreement"):
    if template and addr:
        doc = Document(template)
        replacements = {
            "{{ADDRESS}}": addr,
            "{{TENANT}}": t_name,
            "{{LANDLORD}}": l_name,
            "{{RENT}}": f"${rent:,.2f}",
            "{{DATE}}": start_date.strftime("%d/%m/%Y")
        }
        
        for p in doc.paragraphs:
            for tag, val in replacements.items():
                if tag in p.text:
                    p.text = p.text.replace(tag, val)
        
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        st.download_button("⬇️ Download Completed Agreement", data=bio, file_name=f"Lease_{addr[:10]}.docx")
