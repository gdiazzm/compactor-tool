import streamlit as st
import datetime

# Page styling for a clean mobile look
st.set_page_config(page_title="Compactor Wheel Pro", layout="centered")

st.title("🚜 Wheel Inspection Pro")
st.write(f"**Date:** {datetime.date.today().strftime('%B %d, %y')}")

# 1. MACHINE HEADER (Now includes Brand and Tip Specs)
with st.expander("📋 Machine Information", expanded=True):
    cust = st.text_input("Customer Name")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        base_model = st.radio("Base Model", ["826", "836"], horizontal=True)
    with col_m2:
        series_letter = st.text_input("Series Letter (C, G, H, K)", value="K").upper()
    
    full_model = f"{base_model}{series_letter}"
    sn = st.text_input("Serial Number")
    
    # NEW FIELDS: Brand and Tip Specs
    brand = st.text_input("Wheel Brand (e.g., Cat, Caron, Al-jon)")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        tip_type = st.text_input("Tip Type (e.g., Plus, Paddle, Diamond)")
    with col_t2:
        tip_count = st.number_input("Tip Count Per Wheel", min_value=0, value=40)

    st.info(f"Inspecting: **{full_model}** | **{brand}** Wheels | **{tip_count} {tip_type}** Tips")

# 2. THE 4-WHEEL INSPECTION
wheels = ["Front Left", "Front Right", "Rear Left", "Rear Right"]

for wheel in wheels:
    st.markdown(f"### 📍 {wheel}")
    with st.container():
        # Measurements
        col1, col2 = st.columns(2)
        with col1:
            rim = st.number_input(f"Rim Thickness (mm)", min_value=0.0, value=25.0, key=f"rim_{wheel}")
            cone = st.number_input(f"Cone Thickness (mm)", min_value=0.0, value=15.0, key=f"cone_{wheel}")
        with col2:
            tip_h = st.number_input(f"Measured Tip Height (mm)", value=190.0, key=f"tip_{wheel}")
            wear_bars = st.selectbox("Wear Bars", ["Good", "Worn", "Replace/Add"], key=f"bars_{wheel}")

        # Dimensions
        d1, d2 = st.columns(2)
        with d1:
            dia = st.text_input("Wrapped Diameter (mm)", key=f"dia_{wheel}")
        with d2:
            width = st.text_input("Wrapped Width (mm)", key=f"width_{wheel}")

        # Visual/Structural Checks
        st.write("**Integrity Checks:**")
        c1, c2, c3 = st.columns(3)
        with c1:
            weld_fail = st.toggle("Weld Worn?", key=f"weld_{wheel}")
        with c2:
            hub_fail = st.toggle("Hub Damage?", key=f"hub_{wheel}")
        with c3:
            struct_fail = st.toggle("Deformed?", key=f"struct_{wheel}")

        # Safety Logic & Visual Feedback
        wear_pct = max(0, min(100, (25 - rim) / (25 - 16)))
        st.write(f"Rim Wear Progress:")
        st.progress(wear_pct)

        if rim <= 16:
            st.error(f"❌ **CRITICAL:** Rim is {rim}mm. DO NOT WELD NEW TIPS.")
        elif rim <= 18:
            st.warning(f"⚠️ **WARNING:** Rim is approaching scrap limit.")
            
        if cone <= 9:
            st.error(f"❌ **CRITICAL:** Cone is {cone}mm. REINFORCE OR REPLACE.")
            
        if weld_fail or hub_fail or struct_fail:
            st.error("🚨 **FAIL:** Structural issues detected. Core reuse denied.")
        
        st.camera_input(f"Take Photo of {wheel}", key=f"cam_{wheel}")
        st.divider()

# 3. FINAL SUMMARY
st.subheader("📝 Final Recommendation")
rec = st.text_area("Enter maintenance plan...")

if st.button("🚀 Generate Summary"):
    st.balloons()
    st.success(f"Inspection Complete for {full_model} SN: {sn}")
