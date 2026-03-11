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
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        base_model = st.radio("Base Model", ["826", "836"], horizontal=True)
    with col_m2:
        series_letter = st.text_input("Series Letter", value="K").upper()
    
    full_model = f"{base_model}{series_letter}"
    sn = st.text_input("Serial Number")
    brand = st.text_input("Wheel Brand")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        tip_type = st.text_input("Tip Type")
    with col_t2:
        tip_count = st.number_input("Tip Count Per Wheel", min_value=0, value=40)

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
            tip_h = st.number_input(f"Tip Height (mm)", value=190.0, key=f"tip_{wheel}")
            wear_bars = st.selectbox("Wear Bars", ["Good", "Worn", "Replace/Add"], key=f"bars_{wheel}")

        d1, d2 = st.columns(2)
        with d1:
            dia = st.text_input("Wrapped Diameter (Inches)", key=f"dia_{wheel}")
        with d2:
            width = st.text_input("Wrapped Width (Inches)", key=f"width_{wheel}")

        st.write("**Integrity Checks:**")
        c1, c2, c3 = st.columns(3)
        w_fail = st.toggle("Weld Worn?", key=f"weld_{wheel}")
        h_fail = st.toggle("Hub Damage?", key=f"hub_{wheel}")
        s_fail = st.toggle("Deformed?", key=f"struct_{wheel}")

        # Safety Logic for Report
        status = "PASS"
        if rim <= 16 or cone <= 9 or w_fail or h_fail or s_fail:
            status = "FAIL/ATTENTION REQUIRED"
            st.error(f"🚨 {status}")
        else:
            st.success("✅ Wheel Specs OK")
        
        # Store for PDF
        report_data.append({
            "name": wheel, "rim": rim, "cone": cone, "tip": tip_h, 
            "dia": dia, "width": width, "status": status
        })
        st.divider()

# 3. FINAL SUMMARY & PDF GENERATION
st.subheader("📝 Final Recommendation")
rec = st.text_area("Enter maintenance plan...")

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="WHEEL INSPECTION REPORT", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Customer: {cust} | Date: {date_str}", ln=True)
    pdf.cell(200, 10, txt=f"Machine: {full_model} | SN: {sn}", ln=True)
    pdf.cell(200, 10, txt=f"Wheel Brand: {brand} | Tips: {tip_count} {tip_type}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 0, txt="", border="T", ln=True)
    pdf.ln(5)

    for data in report_data:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"WHEEL: {data['name']} - {data['status']}", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 8, txt=f"  Rim: {data['rim']}mm | Cone: {data['cone']}mm | Tip Height: {data['tip']}mm", ln=True)
        pdf.cell(200, 8, txt=f"  Diameter: {data['dia']}\" | Width: {data['width']}\"", ln=True)
        pdf.ln(2)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Recommendation:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, txt=rec)
    
    return pdf.output(dest='S').encode('latin-1')

if st.button("🚀 Prepare PDF Report"):
    pdf_bytes = create_pdf()
    st.download_button(
        label="📥 Download PDF Summary",
        data=pdf_bytes,
        file_name=f"Inspection_{sn}_{datetime.date.today()}.pdf",
        mime="application/pdf"
    )
