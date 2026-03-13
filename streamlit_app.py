import streamlit as st
import datetime
from fpdf import FPDF

# Page styling
st.set_page_config(page_title="Wheel Inspection", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .rev-label { position: absolute; top: -50px; right: 0px; font-size: 10px; color: #9e9e9e; font-family: monospace; }
    .tips-row { background-color: #f0f2f6; padding: 12px; border-left: 10px solid #808080; border-radius: 5px 5px 0px 0px; font-weight: bold; }
    .wrapper-row { background-color: #fffde7; padding: 12px; border-left: 10px solid #fbc02d; border-radius: 0px 0px 5px 5px; margin-bottom: 25px; font-weight: bold; }
    .thickness-container { display: flex; align-items: center; gap: 15px; margin-bottom: 10px; }
    .thickness-label { font-size: 14px; font-weight: 400; color: rgb(49, 51, 63); font-family: "Source Sans Pro", sans-serif; }
    .limit-note { font-size: 12px; font-weight: normal; color: #d32f2f; background-color: #ffffff; padding: 2px 8px; border-radius: 10px; border: 1px solid #d32f2f; }
    .status-ok { color: #2e7d32; background-color: #e8f5e9; padding: 4px 8px; border-radius: 4px; border: 1px solid #2e7d32; font-weight: bold; }
    .status-fail { color: #c62828; background-color: #ffebee; padding: 4px 8px; border-radius: 4px; border: 1px solid #c62828; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="rev-label">REV 1.1.8</div>', unsafe_allow_html=True)

st.title("🚜 Wheel Inspection")
date_str = datetime.date.today().strftime('%B %d, %y')

# 1. MACHINE HEADER
with st.expander("📋 Machine Information", expanded=True):
    c1, c2 = st.columns([2, 1])
    cust = c1.text_input("Customer Name")
    cust_acc = c2.text_input("Account #")
    
    m1, m2, m3 = st.columns([1, 1, 1])
    base_model = m1.selectbox("Model", ["826", "836"])
    series_letter = m2.text_input("Series", value="K").upper()
    sn = m3.text_input("Serial Number")
    
    h1, h2, h3 = st.columns(3)
    hours = h1.number_input("Hours", min_value=0, step=100)
    brand = h2.text_input("Wheel Brand")
    inspector = h3.text_input("Inspector Name") # NEW FIELD

    d1, d2, d3, d4 = st.columns(4)
    tip_type = d1.selectbox("Tip Type", ["Plus", "Paddle", "Combo", "Diamond"])
    dia = d2.text_input("Wrapper Dia (in)")
    width = d3.text_input("Wrapper Width (in)")
    tip_count = d4.number_input("Tips/Wheel", min_value=0, value=40)

    full_model = f"{base_model}{series_letter}"

scrap_limit = 20 if tip_type == "Diamond" else 16

# 2. THE 4-WHEEL INSPECTION
wheels = ["Front Left", "Front Right", "Rear Left", "Rear Right"]
report_data = []

for wheel in wheels:
    st.subheader(f"📍 {wheel} Wheel")
    st.markdown(f'<div class="tips-row">{wheel} Wheel, Tips</div>', unsafe_allow_html=True)
    with st.container():
        col_t1, col_t2 = st.columns(2)
        tip_h = col_t1.number_input(f"Tip Height (mm)", value=190.0, key=f"tip_{wheel}")
        wear_bars = col_t2.selectbox("Wear Bars Pattern", ["Normal Wear", "Worn (Add midpoint bars)", "Replace"], key=f"bars_{wheel}")

    st.markdown(f'<div class="wrapper-row">{wheel} Wheel, Wrapper Info</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="thickness-container"><span class="thickness-label">Wrapper Thickness (mm)</span><span class="limit-note">Scrap Limit: {scrap_limit}mm</span></div>', unsafe_allow_html=True)
        rim_measurements = []
        m_cols = st.columns(6)
        for i in range(12):
            with m_cols[i % 6]:
                val = st.number_input(f"pt{i+1}", value=25.0, step=0.5, key=f"m_{wheel}_{i}", label_visibility="collapsed")
                rim_measurements.append(val)
        
        min_rim = min(rim_measurements)
        st.divider()
        col_left, col_right = st.columns([1.5, 1])
        with col_left:
            cone = st.number_input(f"Cone Thickness (mm)", value=15.0, key=f"cone_{wheel}")
        with col_right:
            weld_edge = st.toggle("Edge in weld?", key=f"weld_{wheel}")
            hub_damage = st.toggle("Hub/Rim damage?", key=f"hub_{wheel}")
            struct_damage = st.toggle("Extensive deformation?", key=f"struct_{wheel}")

    # CRITERIA LOGIC
    reasons = []
    if min_rim <= scrap_limit: reasons.append(f"Min rim ({min_rim}mm) <= {scrap_limit}mm")
    if cone <= 9: reasons.append("Cone <= 9mm")
    if weld_edge: reasons.append("Edge in weld")
    if hub_damage: reasons.append("Hub damage")
    if struct_damage: reasons.append("Structural deformation")

    wheel_result = "FAIL" if reasons else "PASS"
    status_class = "status-fail" if reasons else "status-ok"
    st.markdown(f'**Result:** <span class="{status_class}">{wheel_result}</span>', unsafe_allow_html=True)
    if reasons:
        for r in reasons: st.warning(f"⚠️ {r}")

    report_data.append({"name": wheel, "rim_pts": rim_measurements, "rim_min": min_rim, "cone": cone, "tip": tip_h, "result": wheel_result, "bars": wear_bars, "notes": ", ".join(reasons)})
    st.divider()

# 3. PDF GENERATION
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    def clean_text(text): return str(text).encode('latin-1', 'ignore').decode('latin-1')
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt="Wheel Inspection Report", ln=True, align='C')
    pdf.set_font("Arial", '', 7)
    pdf.cell(190, 5, txt=f"REV 1.1.8", ln=True, align='R')
    pdf.ln(5)

    # HEADER (3x3 grid)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, txt=" INSPECTION INFORMATION", ln=True, fill=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(63, 7, txt=clean_text(f"Customer: {cust}"), border='LRB')
    pdf.cell(63, 7, txt=clean_text(f"Account #: {cust_acc}"), border='RB')
    pdf.cell(64, 7, txt=clean_text(f"Inspector: {inspector}"), border='RB', ln=True)
    
    pdf.cell(63, 7, txt=clean_text(f"Model: {full_model}"), border='LRB')
    pdf.cell(63, 7, txt=clean_text(f"Serial #: {sn}"), border='RB')
    pdf.cell(64, 7, txt=clean_text(f"Hours: {hours}"), border='RB', ln=True)

    pdf.cell(47.5, 7, txt=clean_text(f"Tip Type: {tip_type}"), border='LRB')
    pdf.cell(47.5, 7, txt=clean_text(f"Tip Count: {tip_count}"), border='RB')
    pdf.cell(47.5, 7, txt=clean_text(f"Diameter: {dia} in"), border='RB')
    pdf.cell(47.5, 7, txt=clean_text(f"Width: {width} in"), border='RB', ln=True)
    pdf.ln(10)

    for data in report_data:
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(140, 9, txt=clean_text(f" LOCATION: {data['name'].upper()}"), border='LBT', fill=True)
        
        # Result marking
        if data['result'] == "PASS":
            pdf.set_text_color(0, 128, 0)
        else:
            pdf.set_text_color(200, 0, 0)
        pdf.cell(50, 9, txt=f"RESULT: {data['result']}", border='RBT', ln=True, fill=True, align='C')
        pdf.set_text_color(0, 0, 0)

        # Tables...
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(40, 7, "Component", 1); pdf.cell(40, 7, "Condition", 1); pdf.cell(35, 7, "Measure", 1); pdf.cell(75, 7, "Notes", 1, ln=True)
        pdf.set_font("Arial", '', 9)
        pdf.cell(40, 7, "Tips", 1); pdf.cell(40, 7, clean_text(data['bars']), 1); pdf.cell(35, 7, f"{data['tip']}mm", 1); pdf.cell(75, 7, "--", 1, ln=True)
        pdf.cell(40, 7, "Wrapper Plate", 1); pdf.cell(40, 7, "--", 1); pdf.cell(35, 7, f"Min: {data['rim_min']}mm", 1); pdf.cell(75, 7, clean_text(f"Cone: {data['cone']}mm | {data['notes']}"), 1, ln=True)

        pdf.set_font("Arial", 'I', 8)
        pdf.cell(190, 6, "12-Point Wrapper Thickness Detail:", ln=True)
        pdf.set_font("Arial", '', 8)
        for row in range(2):
            for i in range(6):
                idx = i + (row * 6)
                pdf.cell(31.6, 6, f"Pt{idx+1}: {data['rim_pts'][idx]}", 1, 0, 'C')
            pdf.ln()
        pdf.ln(5)

    return pdf.output(dest='S').encode('latin-1', 'ignore')

if st.button("🚀 Generate PDF Summary"):
    pdf_bytes = create_pdf()
    st.download_button(label="📥 Download History PDF", data=pdf_bytes, file_name=f"History_{sn}_Rev118.pdf", mime="application/pdf")
