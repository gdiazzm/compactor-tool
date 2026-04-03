import streamlit as st
import datetime
from fpdf import FPDF

# Page styling
st.set_page_config(page_title="Wheel Inspection Tool", layout="centered")

# Custom CSS for UI Professionalism
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

st.markdown('<div class="rev-label">REV 1.2.1</div>', unsafe_allow_html=True)

st.title("🚜 Wheel Inspection")
date_str = datetime.date.today().strftime('%B %d, %y')

# 1. MACHINE HEADER
with st.expander("📋 Machine Information", expanded=True):
    c1, c2 = st.columns([2, 1])
    cust = c1.text_input("Customer Name")
    cust_acc = c2.text_input("Account #")
    
    m1, m2, m3 = st.columns(3)
    base_model = m1.selectbox("Model", ["826", "836"])
    series_letter = m2.text_input("Series", value="K").upper()
    sn = m3.text_input("Serial Number")
    
    h1, h2, h3 = st.columns(3)
    hours = h1.number_input("Hours", min_value=0, step=100)
    brand = h2.text_input("Wheel Brand")
    inspector = h3.text_input("Inspector Name")

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
        st.markdown(f'''<div class="thickness-container"><span class="thickness-label">Wrapper Thickness (mm)</span><span class="limit-note">Scrap Limit: {scrap_limit}mm</span></div>''', unsafe_allow_html=True)
        
        rim_measurements = []
        m_cols = st.columns(6)
        for i in range(6):
            with m_cols[i]:
                val = st.number_input(f"pt{i+1}", value=25.0, step=0.5, key=f"m_{wheel}_{i}", label_visibility="collapsed")
                rim_measurements.append(val)
        
        st.markdown(f'''<div class="thickness-container"><span class="thickness-label">Cone Thickness (mm)</span><span class="limit-note">Scrap Limit: 9mm</span></div>''', unsafe_allow_html=True)
        cone_measurements = []
        c_cols = st.columns(3)
        for i in range(3):
            with c_cols[i]:
                c_val = st.number_input(f"cone_pt{i+1}", value=15.0, step=0.5, key=f"cone_{wheel}_{i}", label_visibility="collapsed")
                cone_measurements.append(c_val)

        min_rim = min(rim_measurements)
        min_cone = min(cone_measurements)
        
        st.divider()
        col_right = st.columns(1)[0]
        with col_right:
            weld_edge = st.toggle("Edge in weld?", key=f"weld_{wheel}")
            hub_damage = st.toggle("Hub/Rim damage?", key=f"hub_{wheel}")
            struct_damage = st.toggle("Extensive deformation?", key=f"struct_{wheel}")

    reasons = []
    if min_rim <= scrap_limit: reasons.append(f"Min rim ({min_rim}mm) <= {scrap_limit}mm")
    if min_cone <= 9: reasons.append(f"Min cone ({min_cone}mm) <= 9mm")
    if weld_edge: reasons.append("Edge in weld")
    if hub_damage: reasons.append("Hub damage")
    if struct_damage: reasons.append("Structural deformation")

    wheel_result = "FAIL" if reasons else "PASS"
    status_class = "status-fail" if reasons else "status-ok"
    st.markdown(f'**Result:** <span class="{status_class}">{wheel_result}</span>', unsafe_allow_html=True)
    if reasons:
        for r in reasons: st.warning(f"⚠️ {r}")

    report_data.append({"name": wheel, "rim_pts": rim_measurements, "rim_min": min_rim, "cone_pts": cone_measurements, "cone_min": min_cone, "tip": tip_h, "result": wheel_result, "bars": wear_bars, "notes": ", ".join(reasons)})
    st.divider()

# 3. FINAL RECOMMENDATION
st.subheader("📝 Final Recommendation")
rec = st.text_area("Maintenance plan notes...")

# 4. PDF GENERATION
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    def clean_text(text): return str(text).encode('latin-1', 'ignore').decode('latin-1')
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt="Wheel Inspection Report", ln=True, align='C')
    pdf.set_font("Arial", '', 7)
    pdf.cell(190, 5, txt=f"REV 1.2.1", ln=True, align='R')
    pdf.ln(5)

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, txt=" INSPECTION & MACHINE DETAILS", ln=True, fill=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(63, 7, txt=clean_text(f"Customer: {cust}"), border='LRB')
    pdf.cell(63, 7, txt=clean_text(f"Account #: {cust_acc}"), border='RB')
    pdf.cell(64, 7, txt=clean_text(f"Date: {date_str}"), border='RB', ln=True)
    pdf.cell(63, 7, txt=clean_text(f"Model: {full_model}"), border='LRB')
    pdf.cell(63, 7, txt=clean_text(f"Serial #: {sn}"), border='RB')
    pdf.cell(64, 7, txt=clean_text(f"Inspector: {inspector}"), border='RB', ln=True)
    pdf.cell(47.5, 7, txt=clean_text(f"Tip: {tip_type} ({tip_count})"), border='LRB')
    pdf.cell(47.5, 7, txt=clean_text(f"Hours: {hours}"), border='RB')
    pdf.cell(47.5, 7, txt=clean_text(f"Dia: {dia} in"), border='RB')
    pdf.cell(47.5, 7, txt=clean_text(f"Width: {width} in"), border='RB', ln=True)
    pdf.ln(8)

    for data in report_data:
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(150, 9, txt=clean_text(f" {data['name'].upper()} WHEEL"), border='LBT', fill=True)
        if data['result'] == "PASS": pdf.set_text_color(0, 100, 0)
        else: pdf.set_text_color(200, 0, 0)
        pdf.cell(40, 9, txt=f"{data['result']}", border='RBT', ln=True, fill=True, align='C')
        pdf.set_text_color(0, 0, 0)

        pdf.set_font("Arial", 'B', 8)
        pdf.cell(40, 6, "Component", 1); pdf.cell(40, 6, "Condition", 1); pdf.cell(30, 6, "Min/Measure", 1); pdf.cell(80, 6, "Alerts/Notes", 1, ln=True)
        pdf.set_font("Arial", '', 8)
        pdf.cell(40, 6, "Tips", 1); pdf.cell(40, 6, clean_text(data['bars']), 1); pdf.cell(30, 6, f"{data['tip']}mm", 1); pdf.cell(80, 6, "--", 1, ln=True)
        pdf.cell(40, 6, "Wrapper", 1); pdf.cell(40, 6, "--", 1); pdf.cell(30, 6, f"{data['rim_min']}mm", 1); pdf.cell(80, 6, clean_text(data['notes']), 1, ln=True)

        pdf.set_font("Arial", 'I', 7)
        pdf.cell(95, 5, "Wrapper Thickness Detail (6 Points):")
        pdf.cell(95, 5, "Cone Thickness Detail (3 Points):", ln=True)
        pdf.set_font("Arial", '', 7)
        
        # Row for details
        for i in range(6):
            pdf.cell(15.8, 5, f"P{i+1}:{data['rim_pts'][i]}", 1, 0, 'C')
        pdf.cell(2, 5, "") # Spacer
        for j in range(3):
            pdf.cell(25.3, 5, f"Cone P{j+1}:{data['cone_pts'][j]}", 1, 0, 'C')
        pdf.ln(8)

    pdf.ln(2)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, txt=" FINAL RECOMMENDATION", ln=True, fill=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(190, 5, txt=clean_text(rec), border=1)
    
    pdf.ln(15)
    pdf.cell(95, 10, "________________________________", align='L')
    pdf.cell(95, 10, "________________________________", ln=1, align='R')
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(95, 5, "Inspector Signature", align='L')
    pdf.cell(95, 5, "Date of Review", align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

if st.button("🚀 Generate PDF Summary"):
    pdf_bytes = create_pdf()
    st.download_button(label="📥 Download Inspection PDF", data=pdf_bytes, file_name=f"Report_{sn}_Rev121.pdf", mime="application/pdf")
