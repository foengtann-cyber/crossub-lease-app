import streamlit as st
from docx import Document
import io

st.set_page_config(page_title="Crossub Assistant", layout="centered")

st.title("📑 Crossub Lease Preparer")

# --- NAVIGATION ---
st.info("Step 1: Open the Portal and find your tenant data.")
st.link_button("🌐 Open Crossub Portal", "https://agent.crossub.com.au/Leasing/Admin/List")

st.divider()

# --- INPUT FORM ---
st.subheader("Step 2: Enter Contract Details")
work_type = st.radio("Task", ["New Leasing", "Lease Renewal"])

t_name = st.text_input("Tenant Name", placeholder="e.g. Angela Williams")
addr = st.text_input("Address", placeholder="e.g. 69 Wills Road")
rent = st.number_input("Weekly Rent ($)", min_value=0.0, step=10.0)

if work_type == "New Leasing" and rent > 0:
    st.write(f"✅ **Calculated Bond:** ${rent * 4:,.2f}")

start_date = st.date_input("Lease Start Date")

st.divider()

# --- DOCUMENT GENERATION ---
st.subheader("Step 3: Generate Agreement")
template_file = st.file_uploader("Upload Word Template (.docx)", type="docx")

if st.button("🚀 Create Completed Lease"):
    if template_file:
        doc = Document(template_file)
        
        # This scans the Word doc for your tags and replaces them
        for p in doc.paragraphs:
            if "{{TENANT}}" in p.text: p.text = p.text.replace("{{TENANT}}", t_name)
            if "{{ADDRESS}}" in p.text: p.text = p.text.replace("{{ADDRESS}}", addr)
            if "{{RENT}}" in p.text: p.text = p.text.replace("{{RENT}}", f"${rent:,.2f}")
            if "{{DATE}}" in p.text: p.text = p.text.replace("{{DATE}}", start_date.strftime("%d/%m/%Y"))
        
        # Buffer for the download
        out_io = io.BytesIO()
        doc.save(out_io)
        out_io.seek(0)
        st.download_button("⬇️ Download Now", data=out_io, file_name=f"Lease_{t_name}.docx")
    else:
        st.error("Please upload your Template.docx first!")
