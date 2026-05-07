import streamlit as st
import pandas as pd
from docx import Document
import io

st.set_page_config(page_title="Crossub Auto-Fill Tool", layout="wide")

st.title("⚡ Crossub Smart Lease Tool")

# --- STEP 1: UPLOAD DATA FROM CROSSUB ---
st.sidebar.header("1. Sync System Data")
uploaded_csv = st.sidebar.file_uploader("Upload CSV/Excel from Crossub", type=["csv", "xlsx"])

# Variables to hold auto-filled data
auto_addr = ""
auto_rent = 0.0
auto_tenant = ""

if uploaded_csv:
    # Read the file exported from your system
    df = pd.read_csv(uploaded_csv) if uploaded_csv.name.endswith('.csv') else pd.read_excel(uploaded_csv)
    
    st.sidebar.success("System Data Linked!")
    # Let you pick the property from the system list
    selected_prop = st.sidebar.selectbox("Choose Property", df.iloc[:, 0].tolist())
    
    # Auto-find the data in the table
    row = df[df.iloc[:, 0] == selected_prop].iloc[0]
    auto_addr = selected_prop
    # Adjust 'Rent' and 'Tenant' below to match your Excel column names
    auto_rent = float(row.get('Rent', 0.0)) 
    auto_tenant = row.get('Tenant', "")

# --- STEP 2: THE FORM (Auto-filled) ---
st.subheader("2. Confirm Details")
col1, col2 = st.columns(2)

with col1:
    addr = st.text_input("Property Address", value=auto_addr)
    rent = st.number_input("Weekly Rent ($)", value=auto_rent)
    l_name = st.text_input("Landlord Name") # If this is in your CSV, we can auto-fill it too

with col2:
    tenants = st.text_area("Tenant(s)", value=auto_tenant)
    start_date = st.date_input("Lease Start Date")
    term = st.text_input("Term", value="52 weeks")

# --- STEP 3: GENERATE ---
st.divider()
template = st.file_uploader("Upload Word Template (.docx)", type="docx")

if st.button("🚀 Generate Agreement"):
    if template and addr:
        doc = Document(template)
        # Replacing tags like {{ADDRESS}}, {{RENT}}, {{TENANTS}}, {{LANDLORD_NAME}}
        replacements = {
            "{{ADDRESS}}": addr,
            "{{TENANTS}}": tenants,
            "{{LANDLORD_NAME}}": l_name,
            "{{RENT}}": f"${rent:,.2f}",
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
        st.download_button("⬇️ Download Completed Agreement", data=bio, file_name=f"Lease_{addr[:10]}.docx")
