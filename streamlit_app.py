import streamlit as st
import datetime
from fpdf import FPDF

# Page styling
st.set_page_config(page_title="Wheel Inspection", layout="centered")

# Custom CSS for the CAT/Al-jon Component History look
st.markdown("""
    <style>
    .tips-row {
        background-color: #f0f2f6;
        padding: 12px;
        border-left: 10px solid #808080;
        border-radius: 5px 5px 0px 0px;
        margin-bottom: 0px;
        font-weight: bold;
    }
    .wrapper-row {
        background-color: #fffde7;
        padding: 12px;
        border-left: 10px solid #fbc02d;
        border-radius: 0px 0px 5px 5px;
        margin-bottom: 25px;
        font-weight: bold;
    }
    .status-ok {
        color: #2e7d32;
        background-color: #e8f5e9;
        padding: 5px 10px;
        border-radius: 5px;
        border: 1px solid #2e7d32;
        font-weight: bold;
    }
    .status-fail {
        color: #c62828;
        background-color: #ffebee;
        padding: 5px 10px;
        border-radius: 5px;
        border: 1px solid #c62828;
        font-weight: bold;
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

# 2. THE 4-WHEEL INSPECTION
wheels = ["Front Left", "Front Right", "Rear Left", "Rear Right"]
report_data = []

for wheel in wheels:
    st.subheader(f"📍 {wheel} Wheel")
    
    # TIPS SECTION (Gray)
    st.markdown(f'<div class="tips-row">{wheel} Wheel, Tips</div>', unsafe_allow_html=True)
    with st.container():
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            tip_h = st.number_input(f"Tip Height (mm)", value=190.0, key=f"tip_{wheel}")
        with col_t2:
            wear_bars = st.selectbox("Wear Bars Pattern", ["Normal Wear", "Worn (Add midpoint bars)", "Replace"], key=f"bars_{wheel}")

    # WRAPPER SECTION (Yellow)
    st.markdown(f'<div class="wrapper-row">{wheel} Wheel, Wrapper Measurements (12 Points)</div>', unsafe_allow_html=True)
    with st.container():
        st.write("Enter rim thickness at 12 locations (mm):")
        # COMPACT GRID FOR MEASUREMENTS
        m_cols = st.columns(6)
        rim_measurements = []
        for i in range(12):
            with m_cols[i % 6]:
                val = st.number_input(f"Pt {i+1}", value=25.0, step=0.5, key=f"m_{wheel}_{i}", label_visibility="collapsed")
                rim_measurements.append(val)
        
        min_rim = min(rim_measurements)
        
        st.divider()
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            cone = st.number_input(f"Cone Thickness (mm)", value=15.0, key=f"cone_{wheel}", help="Scrap limit is 9mm")
            weld_edge = st.toggle("Edge worn into weld?", key=f"weld_{wheel}")
        with col_w2:
            hub_damage = st.toggle("Hub/Inner rim damage?", key=f"hub_{wheel}")
            struct_damage = st.toggle("Extensive deformation?", key=f"struct_{wheel}")
            st.camera_input(f"Upload Photo", key=f"cam_{wheel}")

    # CRITERIA LOGIC
    reasons = []
    if min_rim <= 16: reasons.append(f"Min rim thickness ({min_rim}mm) ≤ 16mm")
    if cone <= 9: reasons.append("Cone thickness ≤ 9mm")
    if weld_edge: reasons.append("Edge worn into weld")
    if hub_damage: reasons.append("Hub/Inner rim damage")
    if struct_damage: reasons.append("Structural deformation")

    if reasons:
        st.markdown(f'**Result:** <span class="status-fail">❌ FAIL / IMMEDIATE ATTENTION</span>', unsafe_allow_html=True)
        for r in reasons: st.warning(f"⚠️ {r}")
        final_status = "Immediate Attention"
    else:
        st.markdown(f'**Result:** <span class="status-ok">✅ OK / NORMAL WEAR</span>', unsafe_allow_html=True)
        final_status = "Normal Wear"

    report_data.append({
        "name": wheel, "rim_avg": sum(rim_measurements)/12, "rim_min": min_rim,
        "cone": cone, "tip": tip_h, "status": final_status, "bars": wear_bars, "notes": ", ".join(reasons)
    })
    st.divider()

# 3. FINAL SUMMARY & PDF
st.subheader("📝 Final Recommendation")
rec = st.text_area("Enter maintenance plan...")

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    def clean_text(text): return str(text).encode('latin-1', 'ignore').decode('latin-1')
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, txt="Component History Report", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 5, txt=clean_text(f"Customer: {cust} (Acc: {cust_acc}) | Date: {date_str}"), ln=True, align='C')
    pdf.cell(190, 5, txt=clean_text(f"Machine: {full_model} (SN: {sn}) | Hours: {hours}"), ln=True, align='C')
    pdf.ln(5)

    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(45, 8, "Component", 1, 0, 'C', True)
    pdf.cell(35, 8, "Condition", 1, 0, 'C', True)
    pdf.cell(30, 8, "Min/Avg Measure", 1, 0, 'C', True)
    pdf.cell(80, 8, "Alerts/Notes", 1, 1, 'C', True)

    for data in report_data:
        pdf.set_font("Arial", '', 8)
        # Tips
        pdf.cell(45, 8, clean_text(f"{data['name']} Tips"), 1)
        pdf.cell(35, 8, clean_text(data['bars']), 1, 0, 'C')
        pdf.cell(30, 8, f"{data['tip']} mm", 1, 0, 'C')
        pdf.cell(80, 8, clean_text(f"Type: {tip_type}"), 1, 1)
        # Wrapper
        pdf.set_fill_color(255, 250, 205)
        pdf.cell(45, 8, clean_text(f"{data['name']} Wrapper"), 1, 0, 'L', True)
        pdf.cell(35, 8, clean_text(data['status']), 1, 0, 'C', True)
        pdf.cell(30, 8, f"{data['rim_min']} / {data['rim_avg']:.1f}", 1, 0, 'C', True)
        pdf.cell(80, 8, clean_text(f"Cone: {data['cone']}mm | {data['notes']}"), 1, 1, 'L', True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, txt="Recommendation:", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.multi_cell(0, 5, txt=clean_text(rec))
    return pdf.output(dest='S').encode('latin-1', 'ignore')

if st.button("🚀 Generate PDF Summary"):
    pdf_bytes = create_pdf()
    st.download_button(label="📥 Download History PDF", data=pdf_bytes, file_name=f"History_{sn}.pdf", mime="application/pdf")
