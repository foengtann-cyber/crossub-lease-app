import streamlit as st
from docx import Document
import io

st.set_page_config(page_title="Crossub Workspace", layout="wide")

# --- APP LAYOUT ---
# We split the screen: Left side is the website, Right side is your tool
col_web, col_tool = st.columns([2, 1]) 

with col_web:
    st.subheader("Company System")
    # This embeds your company portal directly into the app
    st.components.v1.iframe("https://agent.crossub.com.au/Leasing/Admin/List", height=800, scrolling=True)

with col_tool:
    st.subheader("Quick Amendment Tool")
    
    # You look at the left side and type the info here
    mode = st.selectbox("Task:", ["New Leasing", "Lease Renewal"])
    t_name = st.text_input("Tenant Name")
    addr = st.text_input("Property Address")
    rent = st.number_input("Weekly Rent", step=10.0)
    
    # Auto-calc bond like your Granville sample (4 weeks) [cite: 942, 963]
    bond = rent * 4
    if mode == "New Leasing":
        st.write(f"**Bond to collect:** ${bond:,.2f}")
    
    # Date selection [cite: 931, 932]
    start_date = st.date_input("Start Date")
    
    st.divider()
    
    uploaded_file = st.file_uploader("Upload Template", type="docx")
    
    if st.button("Generate Contract"):
        if uploaded_file:
            # Logic to swap the tags {{TENANT}}, {{ADDRESS}}, {{RENT}}
            st.success("Contract Prepared!")
            # (Download button code goes here)
