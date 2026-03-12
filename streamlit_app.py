import streamlit as st
import datetime
from fpdf import FPDF

# Page styling
st.set_page_config(page_title="Wheel Inspection", layout="centered")

st.title("🚜 Wheel Inspection")
date_str = datetime.date.today().strftime('%B %d, %y')
st.write(f"**Date:** {date_str}")

# 1. MACHINE HEADER
with st.expander("📋 Machine Information", expanded=True):
    cust = st.text_input("Customer Name")
    # NEW: Customer Account Number
    cust_acc = st.text_input("Customer Account Number")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        base_model = st.radio("Base Model", ["826", "836"], horizontal=True)
    with col_m2: 
        series_letter = st.text_input("Series Letter", value="K").upper()
    
    full_model = f"{base_model}{series_letter}"
    
    col_h1, col_h2 = st.columns(2)
    with col_h1: 
        sn = st.text_input("Serial Number")
    with col_h2: 
        hours = st.number_input("Machine Hours", min_value=0, value=0, step=50)
    
    brand = st.text_input("Wheel Brand")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        dia = st.text_input("Wrapper Diameter (Inches)")
        tip_type = st.text_input("Tip Type")
    with col_s2:
        width = st.text_input("Wrapper Width (Inches)")
        tip_count = st.number_input("Tip Count Per Wheel", min_value=0, value=40)

    st.info(f"Inspecting: **{full_model}** | **{dia}\" x {width}\"** | **{tip_count} {tip_type}** Tips")

# 2. THE 4-WHEEL INSPECTION
wheels = ["Front Left", "Front Right", "Rear Left", "Rear Right"]
report_data = []

for wheel in wheels:
    st.markdown(f"### 📍 {wheel}")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            rim = st.number_input(f"Rim Thickness (mm)", value=25.0, key=f"rim_{wheel}")
            cone = st.number_input(f"Cone Thickness (mm)", value=15.0, key=f"cone_{wheel}")
        with col2:
            tip_h = st.number_input(f"Measured Tip Height (mm)", value=190.0, key=f"tip_{wheel}")
            wear_bars = st.selectbox("Wear Bars", ["Good", "Worn", "Replace/Add"], key=f"bars_{wheel}")

        st.write("**Integrity Checks:**")
        c1, c2, c3 = st.columns(3)
        with c1: w_fail = st.toggle("Weld Worn?", key=f"weld_{wheel}")
        with c2: h_fail = st.toggle("Hub Damage?", key=f"hub_{wheel}")
        with c3: s_fail = st.toggle("Deformed?", key=f"struct_{wheel}")

        status = "PASS"
        if rim <= 16 or cone <= 9 or w_fail or h_fail or s_fail:
            status = "FAIL/ATTENTION"
            st.error(f"🚨 {status}")
        else: 
            st.success("✅ OK")
        
        report_data.append({"name": wheel, "rim": rim, "cone": cone, "tip": tip_h, "status": status})
        st.camera_input(f"Take Photo of {wheel}", key=f"cam_{wheel}")
        st.divider()

# 3. FINAL SUMMARY & PDF
st.subheader("📝 Final Recommendation")
rec = st.text_area("Enter maintenance plan...")

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    def clean_text(text): return str(text).encode('latin-1', 'ignore').decode('latin-1')

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="WHEEL INSPECTION REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=11)
    pdf.ln(10)
    pdf.cell(200, 8, txt=clean_text(f"Customer: {cust} (Acc #: {cust_acc}) | Date: {date_str}"), ln=True)
    pdf.cell(200, 8, txt=clean_text(f"Machine: {full_model} | SN: {sn} | Hours: {hours}"), ln=True)
    pdf.cell(200, 8, txt=clean_text(f"Wheel Specs: {brand} | {dia}\" x {width}\" | {tip_count} {tip_type} Tips"), ln=True)
    pdf.ln(5)
    pdf.cell(200, 0, txt="", border="T", ln=True)
    pdf.ln(5)

    for data in report_data:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=clean_text(f"WHEEL: {data['name']} - {data['status']}"), ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 8, txt=clean_text(f"  Rim: {data['rim']}mm | Cone: {data['cone']}mm | Tip Height: {data['tip']}mm"), ln=True)
        pdf.ln(2)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Recommendation:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, txt=clean_text(rec))
    return pdf.output(dest='S').encode('latin-1', 'ignore')

if st.button("🚀 Prepare PDF Report"):
    pdf_bytes = create_pdf()
    st.download_button(
        label="📥 Download PDF Summary",
        data=pdf_bytes,
        file_name=f"Inspection_{sn}_{datetime.date.today()}.pdf",
        mime="application/pdf"
    )
