import streamlit as st
import datetime
from fpdf import FPDF

# Page styling for a "CAT/Al-jon Component History" look
st.set_page_config(page_title="Wheel Inspection", layout="centered")

# Custom CSS to mimic the screenshot styling
st.markdown("""
    <style>
    .tips-row {
        background-color: #f0f2f6;
        padding: 10px;
        border-left: 10px solid #808080;
        border-radius: 5px;
        margin-bottom: 2px;
    }
    .wrapper-row {
        background-color: #fffde7;
        padding: 10px;
        border-left: 10px solid #fbc02d;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚜 Wheel Inspection")
date_str = datetime.date.today().strftime('%B %d, %y')

# 1. MACHINE HEADER
with st.expander("📋 Machine Information", expanded=True):
    cust = st.text_input("Customer Name")
    cust_acc = st.text_input("Customer Account Number")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        base_model = st.radio("Base Model", ["826", "836"], horizontal=True)
    with col_m2: 
        series_letter = st.text_input("Series Letter", value="K").upper()
    
    full_model = f"{base_model}{series_letter}"
    
    col_h1, col_h2 = st.columns(2)
    with col_h1: sn = st.text_input("Serial Number")
    with col_h2: hours = st.number_input("Machine Hours", min_value=0, value=0)
    
    brand = st.text_input("Wheel Brand")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        dia = st.text_input("Wrapper Diameter (Inches)")
        tip_type = st.text_input("Tip Type")
    with col_s2:
        width = st.text_input("Wrapper Width (Inches)")
        tip_count = st.number_input("Tip Count Per Wheel", min_value=0, value=40)

# 2. THE 4-WHEEL INSPECTION (Visual Style Update)
wheels = ["Front Left", "Front Right", "Rear Left", "Rear Right"]
report_data = []

for wheel in wheels:
    st.subheader(f"📍 {wheel} Wheel")
    
    # TIPS SECTION (Gray Look)
    st.markdown(f'<div class="tips-row"><strong>{wheel} Wheel, Tips</strong></div>', unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            tip_h = st.number_input(f"Tip Height (mm)", value=190.0, key=f"tip_{wheel}")
        with col2:
            wear_bars = st.selectbox("Wear Bars", ["Normal Wear", "Worn", "Replace"], key=f"bars_{wheel}")

    # WRAPPER SECTION (Yellow Look)
    st.markdown(f'<div class="wrapper-row"><strong>{wheel} Wheel, Wrapper</strong></div>', unsafe_allow_html=True)
    with st.container():
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            rim = st.number_input(f"Rim Thickness (mm)", value=25.0, key=f"rim_{wheel}")
            cone = st.number_input(f"Cone Thickness (mm)", value=15.0, key=f"cone_{wheel}")
        with col_w2:
            status = st.selectbox("Condition", ["Normal Wear", "Monitoring", "Immediate Attention"], key=f"stat_{wheel}")
            st.camera_input(f"Photo", key=f"cam_{wheel}")

    report_data.append({
        "name": wheel, "rim": rim, "cone": cone, "tip": tip_h, 
        "status": status, "bars": wear_bars
    })

# 3. FINAL SUMMARY & PDF
st.subheader("📝 Final Recommendation")
rec = st.text_area("Enter maintenance plan...")

# [PDF Function remains the same as the previous "Component History" version]
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    def clean_text(text): return str(text).encode('latin-1', 'ignore').decode('latin-1')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, txt="Component History", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 8); pdf.set_text_color(150, 150, 150)
    pdf.cell(35, 10, "Part Description", 0, 0, 'C'); pdf.cell(30, 10, "Condition", 0, 0, 'C')
    pdf.cell(30, 10, "Measurement (mm)", 0, 0, 'C'); pdf.cell(20, 10, "Install Date", 0, 0, 'C')
    pdf.cell(75, 10, "Notes", 0, 1, 'C'); pdf.set_text_color(0, 0, 0); pdf.cell(190, 0, "", border="T", ln=1)
    for data in report_data:
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", 'B', 9)
        pdf.cell(190, 8, txt=clean_text(f"{data['name']} Wheel, Tips"), ln=True)
        pdf.set_font("Arial", '', 9); pdf.cell(5, 10, "", fill=True); pdf.cell(30, 10, clean_text(tip_type), 0, 0, 'C', True)
        pdf.cell(30, 10, "Normal Wear", 0, 0, 'C', True); pdf.cell(30, 10, str(data['tip']), 0, 0, 'C', True)
        pdf.cell(20, 10, date_str, 0, 0, 'C', True); pdf.cell(75, 10, "--", 0, 1, 'C', True)
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 8, txt=clean_text(f"{data['name']} Wheel, Wrapper"), ln=True)
        pdf.set_fill_color(255, 250, 205); pdf.cell(5, 12, "", fill=True); pdf.set_font("Arial", '', 9)
        pdf.cell(30, 12, "Wrapper Plate", 0, 0, 'C'); pdf.cell(30, 12, clean_text(data['status']), 0, 0, 'C')
        pdf.cell(30, 12, str(data['rim']), 0, 0, 'C'); pdf.cell(20, 12, date_str, 0, 0, 'C')
        pdf.set_font("Arial", 'I', 8); pdf.cell(75, 12, clean_text(f"Tip height: {data['tip']}mm"), 0, 1, 'L'); pdf.ln(2)
    pdf.ln(10); pdf.set_font("Arial", 'B', 10); pdf.cell(190, 8, txt="General Recommendation:", ln=True)
    pdf.set_font("Arial", size=9); pdf.multi_cell(0, 5, txt=clean_text(rec))
    return pdf.output(dest='S').encode('latin-1', 'ignore')

if st.button("🚀 Generate PDF Summary"):
    pdf_bytes = create_pdf()
    st.download_button(label="📥 Download History PDF", data=pdf_bytes, file_name=f"History_{sn}.pdf", mime="application/pdf")
