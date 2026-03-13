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
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .thickness-header {
        font-size: 14px;
        font-weight: bold;
        color: #444;
        margin-bottom: 5px;
        text-decoration: underline;
    }
    .limit-note {
        font-size: 12px;
        font-weight: normal;
        color: #d32f2f;
        background-color: #ffffff;
        padding: 2px 8px;
        border-radius: 10px;
        border: 1px solid #d32f2f;
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

# Rev# Update
st.markdown('<div class="rev-label">REV 1.1.3</div>', unsafe_allow_html=True)

st.title("🚜 Wheel Inspection")
date_str = datetime.date.today().strftime('%B %d, %
