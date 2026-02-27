import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. Page Configuration
st.set_page_config(page_title="WIS Professional", page_icon="💧", layout="wide")

# --- CUSTOM CSS: MINIMAL & THAI FONT ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    .stApp { background-color: #f8f9fa; }
    
    /* Full Width & Centered Tabs */
    div[data-baseweb="tab-list"] {
        display: flex; justify-content: center; gap: 5px; background-color: #e9ecef; padding: 8px; border-radius: 15px; width: 100%;
    }
    div[data-baseweb="tab"] {
        flex: 1; text-align: center; background-color: #ffffff; border-radius: 10px; padding: 12px 0px; border: 1px solid #dee2e6;
    }
    div[data-baseweb="tab"][aria-selected="true"] { background-color: #007bff !important; }
    div[data-baseweb="tab"] p { font-size: 16px !important; font-weight: bold !important; margin: 0px; color: #495057; }
    div[data-baseweb="tab"][aria-selected="true"] p { color: white !important; }

    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff; border-left: 5px solid #007bff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Footer Style */
    .footer-text {
        text-align: center;
        color: #6c757d;
        font-size: 14px;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.write("##")
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center;'><h1>💧</h1><h2 style='color: #007bff;'>WIS SYSTEM ACCESS</h2><p>ระบบจัดการสารสนเทศน้ำเสียอัจฉริยะ</p></div>", unsafe_allow_html=True)
        pwd = st.text_input("กรุณาใส่รหัสผ่าน (Enter Password)", type="password")
        if st.button("UNLOCK SYSTEM / เข้าสู่ระบบ", use_container_width=True):
            if pwd == "TUM1234":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("รหัสผ่านไม่ถูกต้อง (Incorrect Password)")
    st.stop()

# --- DATABASE SETUP ---
DB_FILE = "wastewater_history.csv"
def save_data(data_dict):
    df = pd.DataFrame([data_dict])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(DB_FILE, mode='a', index=False, header=False, encoding='utf-8-sig')

# --- MAIN APP ---
st.title("📊 Wastewater Intelligence System (WIS)")
st.info(f"👨‍🔬 **ผู้เชี่ยวชาญ (Analyzed by):** Mr. WUTTIKRON TIWAWAL | 📅 **วันที่ (Date):** {datetime.now().strftime('%d/%m/%Y')}")

with st.sidebar:
    st.markdown("### 🏗️ ข้อมูลเทคนิค (Plant Specs)")
    design_q = st.number_input("ปริมาณน้ำออกแบบ (Design Flow) [m3/d]", value=98.0)
    tank_v = st.number_input("ปริมาตรถังเติมอากาศ (Tank Volume) [m3]", value=60.0)
    st.divider()
    run_diagnosis = st.button("🚀 ประมวลผล (Run Diagnosis)", use_container_width=True, type="primary")

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 บันทึกข้อมูล (Input)", 
    "🔍 การวินิจฉัย (Diagnosis)", 
    "⚙️ คำแนะนำ (Strategy)", 
    "📊 ประวัติ (History)"
])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔬 สถานะจุลินทรีย์ (Microbial Status)")
        sv30_val = st.number_input("ค่า SV30 (mL/L)", value=900)
        calc_mlss = (sv30_val * 1000) / 120
        st.metric("ค่า MLSS (ประมาณการ)", f"{calc_mlss:,.0f} mg/L")
    with c2:
        st.subheader("📊 ข้อมูลหน้างาน (Field Data)")
        q_act = st.number_input("ปริมาณน้ำจริง (Actual Flow) [m3/d]", value=98.0)
        do_act = st.number_input("ค่าออกซิเจนละลาย (DO) [mg/L]", value=2.0)
        cl_out = st.number_input("คลอรีนอิสระ (Cl2 Residual) [mg/L]", value=0.5)
        st.divider()
        st.subheader("🌡️ ระดับความเป็นกรด-ด่าง (pH Level)")
        p1, p2, p3 = st.columns(3)
        ph_in = p1.number_input("น้ำเข้า (Inlet)", value=7.0)
        ph_aer = p2.number_input("บ่อเติมอากาศ (Aeration)", value=7.2)
        ph_out = p3.number_input("น้ำทิ้ง (Effluent)", value=7.0)

with tab2:
    if run_diagnosis:
        fm = (q_act * 250) / (calc_mlss * tank_v) if calc_mlss > 0 else 0
        svi = (sv30_val * 1000) / calc_mlss if calc_mlss > 0 else 0
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("F/M Ratio", f"{fm:.2f}")
        m2.metric("SVI Index", f"{svi:.0f}")
        m3.metric("สถานะ DO", f"{do_act} mg/L")
        m4.metric("คลอรีน Cl2", f"{cl_out} mg/L")
        
        save_data({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Flow": q_act, "SV30": sv30_val, "MLSS": calc_mlss, "DO": do_act, "pH_Aer": ph_aer, "Cl2": cl_out
        })
        st.success("✅ บันทึกข้อมูลและวิเคราะห์เสร็จสมบูรณ์ (Data Logged Successfully)")

with tab4:
    st.subheader("📊 ประวัติข้อมูล (Historical Data)")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)

# --- FOOTER: DEVELOPER INFO ---
st.markdown("""
    <div class="footer-text">
        <p><b>WIS Professional v2.6</b> | Intelligent Wastewater Solution</p>
        <p><i>Developed by Mr. WUTTIKRON TIWAWAL</i><br>
        Full Stack AI & Engineering Systems Developer<br>
        Specializing in Activated Sludge Process Optimization and Digital Transformation</p>
        <p style="font-size: 11px;">© 2026 All Rights Reserved | Authorized Personnel Only</p>
    </div>
""", unsafe_allow_html=True)