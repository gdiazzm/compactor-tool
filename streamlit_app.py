import streamlit as st
import datetime
from fpdf import FPDF

# Page styling
st.set_page_config(page_title="Wheel Inspection", layout="centered")

# Custom CSS for the Rev# and CAT/Al-jon styling
st.markdown("""
    <style>
    .rev-label {
        position: absolute;
        top: -50px;
        right: 0px;
        font-size: 10px;
        color: #9e9e9e;
        font-family: monospace;
    }
    .tips-row {
        background-color: #f0f2f6;
        padding: 12px;
        border-left: 10px solid #808080;
        border-radius: 5px 5px 0px 0px;
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
        padding: 4px 8px;
        border-radius: 4px;
        border: 1px solid #2e7d32;
        font-weight: bold;
    }
    .status-fail {
        color: #c62828;
        background-color: #ffebee;
        padding: 4px 8px;
        border-radius: 4px;
        border: 1px solid #c62828;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Rev# in top right
st.markdown('<div class="rev-label">REV 1.0.9</div>', unsafe_allow_html=True)

st.title("🚜 Wheel Inspection")
date_str = datetime.date.today().strftime('%B %d, %y')

# 1. CLEANED MACHINE HEADER
with st.expander("📋 Machine Information", expanded=True):
    # Customer Info Row
    c1, c2 = st.columns([2, 1])
    cust = c1.text_input("Customer Name")
    cust_acc = c2.text_input("Account #")
    
    # Machine Specs Row
    m1, m2, m3 = st.columns([1, 1, 1])
    base_model = m1.selectbox("Model", ["826", "836"])
    series_letter = m2.text_input("Series", value="K").upper()
    sn = m3.text_input("Serial Number")
    
    # Usage and Branding Row
    h1, h2, h3 = st.columns(3)
    hours = h1.number_input("Hours", min_value=0, step=100)
    brand = h2.text_input("Wheel Brand")
    tip_type = h3.text_input("Tip Type")

    # Dimensions Row
    d1, d2, d3 = st.columns(3)
    dia = d1.text_input("Wrapper Dia (in)")
    width = d2.text_input("Wrapper Width (in)")
    tip_count = d3.number_input("Tips/Wheel", min_value=0, value=40)

    full_model = f"{base_model}{series_letter}"

# 2. THE 4-WHEEL INSPECTION (PICTURES REMOVED)
wheels = ["Front Left", "Front Right", "Rear Left", "Rear Right"]
report_data = []

for wheel in wheels:
    st.subheader(f"📍 {wheel} Wheel")
    
    # TIPS SECTION
    st.markdown(f'<div class="tips-row">{wheel} Wheel, Tips</div>', unsafe_allow_html=True)
    with st.container():
        col_t1, col_t2 = st.columns(2)
        tip_h = col_t1.number_input(f"Tip Height (mm)", value=190.0, key=f"tip_{wheel}")
        wear_bars = col_t2.selectbox("Wear Bars Pattern", ["Normal Wear", "Worn (Add midpoint bars)", "Replace"], key=f"bars_{wheel}")

    # WRAPPER SECTION (12 Points Grid)
    st.markdown(f'<div class="wrapper-row">{wheel} Wheel, Wrapper Measurements (12 Points)</div>', unsafe_allow_html=True)
    with st.container():
        m_cols = st.columns(6)
        rim_measurements = []
        for i in range(12):
            with m_cols[i % 6]:
                val = st.number_input(f"Pt{i+1}", value=25.0, step=0.5, key=f"m_{wheel}_{i}", label_visibility="collapsed")
                rim_measurements.append(val)
        
        min_rim = min(rim_measurements)
        
        col_w1, col_w2, col_w3 = st.columns(3)
        cone = col_w1.number_input(f"Cone (mm)", value=15.0, key=f"cone_{wheel}")
        weld_edge = col_w2.toggle("Edge in weld?", key=f"weld_{wheel}")
        hub_damage = col_w3.toggle("Hub/Rim damage?", key=f"hub_{wheel}")
        struct_damage = st.toggle("Extensive deformation / Broken welds?", key=f"struct_{wheel}")

    # CRITERIA LOGIC
    reasons = []
    if min_rim <= 16: reasons.append(f"Min rim ({min_rim}mm) ≤ 16mm")
    if cone <= 9: reasons.append("Cone ≤ 9mm")
    if weld_edge: reasons.append("Edge worn into weld")
    if hub_damage: reasons.append("Hub/Inner rim damage")
    if struct_damage: reasons.append("Structural deformation")

    if reasons:
        st.markdown(f'**Result:** <span class="status-fail">❌ FAIL</span>', unsafe_allow_html=True)
        for r in reasons: st.warning(f"⚠️ {r}")
        final_status = "Immediate Attention"
    else:
        st.markdown(f'**Result:** <span class="status-ok">✅ OK</span>', unsafe_allow_html=True)
        final_status = "Normal Wear"

    report_data.append({
        "name": wheel, "rim_avg": sum(rim_measurements)/12, "rim_min": min_rim,
        "cone": cone, "tip": tip_h, "status": final_status, "bars": wear_bars, "notes": ", ".join(reasons)
    })
    st.divider()

# 3. FINAL SUMMARY & PDF
st.subheader("📝 Final Recommendation")
rec = st.text_area("Maintenance plan notes...")

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    def clean_text(text): return str(text).encode('latin-1', 'ignore').decode('latin-1')
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, txt="Component History Report", ln=True, align='C')
    pdf.set_font("Arial", '', 8)
    pdf.cell(190, 5, txt=f"REV 1.0.9", ln=True, align='R')
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 5, txt=clean_text(f"Customer: {cust} (Acc: {cust_acc}) | Date: {date_str}"), ln=True, align='C')
    pdf.cell(190, 5, txt=clean_text(f"Machine: {full_model} (SN: {sn}) | Hours: {hours}"), ln=True, align='C')
    pdf.ln(5)

    pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 8)
    pdf.cell(45, 8, "Component", 1, 0, 'C', True)
    pdf.cell(35, 8, "Condition", 1, 0, 'C', True)
    pdf.cell(30, 8, "Min/Avg Measure", 1, 0, 'C', True)
    pdf.cell(80, 8, "Alerts/Notes", 1, 1, 'C', True)

    for data in report_data:
        pdf.set_font("Arial", '', 8)
        pdf.cell(45, 8, clean_text(f"{data['name']} Tips"), 1)
        pdf.cell(35, 8, clean_text(data['bars']), 1, 0, 'C')
        pdf.cell(30, 8, f"{data['tip']} mm", 1, 0, 'C')
        pdf.cell(80, 8, clean_text(f"Type: {tip_type}"), 1, 1)
        pdf.set_fill_color(255, 250, 205)
        pdf.cell(45, 8, clean_text(f"{data['name']} Wrapper"), 1, 0, 'L', True)
        pdf.cell(35, 8, clean_text(data['status']), 1, 0, 'C', True)
        pdf.cell(30, 8, f"{data['rim_min']} / {data['rim_avg']:.1f}", 1, 0, 'C', True)
        pdf.cell(80, 8, clean_text(f"Cone: {data['cone']}mm | {data['notes']}"), 1, 1, 'L', True)

    pdf.ln(5); pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, txt="Recommendation:", ln=True)
    pdf.set_font("Arial", size=9); pdf.multi_cell(0, 5, txt=clean_text(rec))
    return pdf.output(dest='S').encode('latin-1', 'ignore')

if st.button("🚀 Generate PDF Summary"):
    pdf_bytes = create_pdf()
    st.download_button(label="📥 Download History PDF", data=pdf_bytes, file_name=f"History_{sn}_Rev109.pdf", mime="application/pdf")
