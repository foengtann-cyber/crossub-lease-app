import streamlit as st
from docx import Document
import io

st.set_page_config(page_title="Crossub Leasing Helper", layout="centered")

st.title("📜 Lease Amendment Tool")
st.info("Fill this in based on the Crossub screen you just completed.")

# --- FORM SECTION ---
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        addr = st.text_input("Property Address", placeholder="e.g. U1102, 66 Berry St")
        rent = st.number_input("Rent Amount ($)", min_value=0.0, step=50.0)
        freq = st.selectbox("Frequency", ["per Week", "per Month"])
        
    with col2:
        tenants = st.text_area("Tenant Names", placeholder="Enter one per line")
        start_date = st.date_input("Lease Start Date")
        term = st.text_input("Lease Term", value="52 weeks")

# Special Amendments Section
st.subheader("📝 Special Amendments")
special_clause = st.text_area("Add any special conditions here (e.g. Pet clauses, Rent increases)")

st.divider()

# --- GENERATION SECTION ---
st.subheader("Step 3: Generate Document")
template = st.file_uploader("Upload your Lease Template (.docx)", type="docx")

if st.button("🚀 Create Amended Agreement"):
    if template and addr:
        doc = Document(template)
        
        # Mapping our inputs to the "Tags" in your Word doc
        replacements = {
            "{{ADDRESS}}": addr,
            "{{TENANTS}}": tenants,
            "{{RENT}}": f"${rent:,.2f} {freq}",
            "{{START_DATE}}": start_date.strftime("%d/%m/%Y"),
            "{{TERM}}": term,
            "{{SPECIAL}}": special_clause
        }
        
        # Replace the tags in every paragraph
        for p in doc.paragraphs:
            for tag, val in replacements.items():
                if tag in p.text:
                    p.text = p.text.replace(tag, val)
        
        # Save and provide download
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        st.success("Done! Your amended agreement is ready.")
        st.download_button("⬇️ Download Now", data=bio, file_name=f"Lease_Amended_{addr[:10]}.docx")
    else:
        st.error("Please provide the Address and the Template file.")
