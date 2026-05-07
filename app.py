import streamlit as st
from docx import Document
import io

st.set_page_config(page_title="Crossub Leasing Helper", layout="centered")

st.title("📜 Lease Amendment Tool")
st.info("Copy the details from your Crossub screen into the boxes below.")

# --- FORM SECTION ---
st.subheader("1. Property & Rent")
col1, col2 = st.columns(2)
with col1:
    addr = st.text_input("Property Address", placeholder="e.g. U1102, 66 Berry St")
    rent = st.number_input("Rent Amount ($)", min_value=0.0, step=10.0)
with col2:
    freq = st.selectbox("Frequency", ["per Week", "per Month"])
    start_date = st.date_input("Lease Start Date")

st.divider()

# --- LANDLORD SECTION ---
st.subheader("2. Landlord Information")
l_name = st.text_input("Landlord Full Name")
l_contact = st.text_input("Landlord Phone/Email")

# --- TENANT SECTION ---
st.subheader("3. Tenant Information")
tenants = st.text_area("Tenant Names (one per line)")
term = st.text_input("Lease Term", value="52 weeks")

st.divider()

# --- GENERATION SECTION ---
st.subheader("4. Generate Document")
template = st.file_uploader("Upload Word Template (.docx)", type="docx")

if st.button("🚀 Create Completed Lease"):
    if template and addr:
        doc = Document(template)
        
        # Updated replacements including Landlord data
        replacements = {
            "{{ADDRESS}}": addr,
            "{{TENANTS}}": tenants,
            "{{LANDLORD_NAME}}": l_name,
            "{{LANDLORD_CONTACT}}": l_contact,
            "{{RENT}}": f"${rent:,.2f} {freq}",
            "{{START_DATE}}": start_date.strftime("%d/%m/%Y"),
            "{{TERM}}": term
        }
        
        for p in doc.paragraphs:
            for tag, val in replacements.items():
                if tag in p.text:
                    p.text = p.text.replace(tag, val)
        
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        st.success("Done! Your agreement is ready.")
        st.download_button("⬇️ Download Now", data=bio, file_name=f"Lease_{addr[:10]}.docx")
    else:
        st.error("Please provide the Address and the Template file.")
