import streamlit as st
import datetime

# Page styling to make it feel like a mobile app
st.set_page_config(page_title="Compactor Wheel Pro", layout="centered")

st.title("🚜 Wheel Inspection Pro")
st.write(f"**Date:** {datetime.date.today().strftime('%B %d, %y')}")

# 1. MACHINE HEADER
with st.expander("📋 Machine Information", expanded=True):
    cust = st.text_input("Customer Name")
    model = st.selectbox("Model", ["826G", "826H", "826K", "836G", "836H", "836K"])
    sn = st.text_input("Serial Number")

# 2. THE 4-WHEEL INSPECTION GRID
wheels = ["Front Left", "Front Right", "Rear Left", "Rear Right"]
all_wheel_data = {}

for wheel in wheels:
    st.markdown(f"### 📍 {wheel}")
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            rim = st.number_input(f"Rim Thickness (mm)", min_value=0.0, value=25.0, key=f"rim_{wheel}")
            cone = st.number_input(f"Cone Thickness (mm)", min_value=0.0, value=15.0, key=f"cone_{wheel}")
            tip_h = st.number_input(f"Tip Height (mm)", value=190.0, key=f"tip_{wheel}")
        
        with col2:
            dia = st.text_input("Diameter (mm)", key=f"dia_{wheel}")
            width = st.text_input("Width (mm)", key=f"width_{wheel}")
            wear_bars = st.selectbox("Wear Bars", ["Good", "Worn", "Replace/Add"], key=f"bars_{wheel}")

        # Core Integrity Toggles (From your manual image)
        c1, c2 = st.columns(2)
        with c1:
            weld_fail = st.toggle("Worn into cone weld?", key=f"weld_{wheel}")
            hub_fail = st.toggle("Hub/Bolt damage?", key=f"hub_{wheel}")
        with c2:
            struct_fail = st.toggle("Structural deformation?", key=f"struct_{wheel}")

        # AUTOMATIC LOGIC CHECK (The "Red Tape")
        if rim <= 16:
            st.error(f"❌ **CRITICAL:** Rim is {rim}mm. DO NOT WELD NEW TIPS.")
        elif rim <= 18:
            st.warning(f"⚠️ **WARNING:** Rim is approaching scrap limit.")
            
        if cone <= 9:
            st.error(f"❌ **CRITICAL:** Cone is {cone}mm. REINFORCE OR REPLACE.")
            
        if weld_fail or hub_fail or struct_fail:
            st.error("🚨 **FAIL:** Structural issues detected. Core reuse not advised.")
        
        st.divider()

# 3. FINAL SUMMARY
st.subheader("📝 Final Recommendation")
rec = st.text_area("Enter maintenance plan...")

if st.button("🚀 Generate PDF Report"):
    st.balloons()
    st.success("Report Compiled! (Logic for PDF download goes here)")
