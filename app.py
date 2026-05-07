import streamlit as st
import easyocr
from PIL import Image
import numpy as np
from docx import Document
import io
import re

st.set_page_config(page_title="Crossub OCR Tool", layout="centered")
st.title("📸 Screenshot to Lease Tool")

uploaded_img = st.file_uploader("Upload Crossub Screenshot", type=["png", "jpg", "jpeg"])

# Initial state
extracted_data = {"Address": "", "Landlord": "", "Tenants": "", "Rent": 0.0}

if uploaded_img:
    with st.spinner("Analyzing screenshot..."):
        reader = easyocr.Reader(['en'])
        image = Image.open(uploaded_img)
        # We get the 'detail' so we know exactly where the words are
        result = reader.readtext(np.array(image), detail=1) 
        
        # We turn all the found words into one long string to search
        full_text_list = [res[1] for res in result]
        full_text = " ".join(full_text_list)

        # --- IMPROVED SEARCH RULES ---
        
        # 1. Search for Address (looking for keywords like St, Road, NSW, etc.)
        # This rule ignores words like 'Property Type'
        addr_patterns = [
            r'(\d+\s+[\w\s]+(?:Road|Street|St|Rd|Ave|Way|Circuit|Cct|Pl|Place))',
            r'(\d+/\d+\s+[\w\s]+(?:Road|Street|St|Rd|Ave))'
        ]
        for pat in addr_patterns:
            match = re.search(pat, full_text, re.IGNORECASE)
            if match:
                extracted_data["Address"] = match.group(1).strip()
                break

        # 2. Search for Landlord Name (Looking for text right after 'Landlord's Name')
        for i, text in enumerate(full_text_list):
            if "Landlord's Name" in text or "Landlord Name" in text:
                if i + 1 < len(full_text_list):
                    extracted_data["Landlord"] = full_text_list[i+1]

        # 3. Search for Tenant Names (Looking for 'Main Applicant' or 'Tenant 1')
        tenant_found = []
        for i, text in enumerate(full_text_list):
            if any(key in text for key in ["Main Applicant", "Tenant Name", "Tenant 1"]):
                if i + 1 < len(full_text_list):
                    tenant_found.append(full_text_list[i+1])
        extracted_data["Tenants"] = "\n".join(tenant_found)

        # 4. Search for Rent (Looking for $ sign or digits before 'Weekly')
        rent_match = re.search(r'(\d+)\s*(?:Weekly|per Week|\$)', full_text, re.IGNORECASE)
        if rent_match:
            extracted_data["Rent"] = float(rent_match.group(1))

        st.success("Analysis Complete!")

# --- THE VERIFICATION FORM ---
st.subheader("Confirm Details")
final_addr = st.text_input("Property Address", value=extracted_data["Address"])
final_landlord = st.text_input("Landlord Name", value=extracted_data["Landlord"])
final_tenants = st.text_area("Tenant Name(s)", value=extracted_data["Tenants"])
final_rent = st.number_input("Weekly Rent ($)", value=extracted_data["Rent"])

st.divider()

# --- WORD GENERATOR ---
template = st.file_uploader("Upload Word Template (.docx)", type="docx")

if st.button("🚀 Generate Agreement"):
    if template and final_addr:
        doc = Document(template)
        # Update your Word doc tags to match these:
        replacements = {
            "{{ADDRESS}}": final_addr,
            "{{TENANT}}": final_tenants,
            "{{LANDLORD}}": final_landlord,
            "{{RENT}}": f"${final_rent:,.2f}",
            "{{DATE}}": st.date_input("Lease Start").strftime("%d/%m/%Y")
        }
        
        for p in doc.paragraphs:
            for tag, val in replacements.items():
                if tag in p.text:
                    p.text = p.text.replace(tag, val)
        
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        st.download_button("⬇️ Download Completed Agreement", data=bio, file_name=f"Lease_{final_addr[:10]}.docx")
