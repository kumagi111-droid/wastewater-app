import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. Page Configuration
st.set_page_config(page_title="WIS - Wastewater Intelligence System", page_icon="💧", layout="wide")

# Database Setup
DB_FILE = "wastewater_history.csv"

def save_to_csv(data_dict):
    df = pd.DataFrame([data_dict])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(DB_FILE, mode='a', index=False, header=False, encoding='utf-8-sig')

# 2. Header Section
st.title("💧 Wastewater Intelligence System (WIS)")
st.markdown(f"**Expert Analysis by:** Mr. WUTTIKRON TIWAWAL | **Date:** {datetime.now().strftime('%d/%m/%Y')}")
st.divider()

# 3. SIDEBAR
with st.sidebar:
    st.header("🏗️ Plant Specifications")
    design_q = st.number_input("น้ำเสียที่ออกแบบ (m3/day)", value=98)
    tank_v = st.number_input("ขนาดบ่อเติมอากาศ (m3)", value=60)
    st.divider()
    
    st.header("🎮 Control Center")
    run_diagnosis = st.button("🚀 Run Diagnosis (วิเคราะห์ผล)", use_container_width=True, type="primary")
    
    st.divider()
    if st.button("🗑️ Clear History (ล้างประวัติ)", use_container_width=True):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.rerun()

# 4. MAIN TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Daily Input (ลงข้อมูล)", 
    "🔍 Diagnosis (ผลวิเคราะห์)", 
    "⚙️ Machine (คำแนะนำ)", 
    "📜 History (ประวัติ)"
])

# --- TAB 1: บันทึกข้อมูล ---
with tab1:
    col1, col2 = st.columns(2)
    
    # ฝั่งซ้าย: เน้นเรื่องการหาค่าจุลินทรีย์ (MLSS)
    with col1:
        st.subheader("🔬 Microbial Status (MLSS)")
        method = st.radio("เลือกวิธีหาค่า MLSS:", ["Quick SV30 (แบบเร็ว)", "Lab Weight (ชั่งน้ำหนัก)", "Manual (กรอกเอง)"])
        
        if method == "Quick SV30 (แบบเร็ว)":
            sv30_val = st.number_input("ค่า SV30 ที่วัดได้ (mL/L)", value=900, key="sv30_q")
            calc_mlss = (sv30_val * 1000) / 120
        elif method == "Lab Weight (ชั่งน้ำหนัก)":
            w = st.number_input("น้ำหนักตะกอนแห้ง (g)", value=0.1500, format="%.4f")
            v = st.number_input("ปริมาตรน้ำตัวอย่าง (mL)", value=50)
            sv30_val = st.number_input("ค่า SV30 ที่วัดได้ (mL/L)", value=900, key="sv30_l")
            calc_mlss = (w * 1000000) / v if v > 0 else 0
        else:
            calc_mlss = st.number_input("ระบุค่า MLSS เอง (mg/L)", value=3000)
            sv30_val = st.number_input("ค่า SV30 ที่วัดได้ (mL/L)", value=900, key="sv30_m")
        
        st.divider()
        st.metric("Estimated MLSS Result", f"{calc_mlss:,.0f} mg/L")

    # ฝั่งขวา: รวมกลุ่ม Parameter (Flow, DO, Cl2 และ pH ทั้งหมด)
    with col2:
        st.subheader("📊 Field & Operational Parameters")
        q_act = st.number_input("ปริมาณน้ำเข้าจริง (m3/day)", value=98)
        do_act = st.number_input("ค่า DO ในบ่อ (mg/L)", value=2.0, step=0.1)
        cl_out = st.number_input("Chlorine น้ำออก (mg/L)", value=0.5, step=0.1)
        bod_est = st.number_input("BOD ประมาณการ (mg/L)", value=250)
        
        st.divider()
        st.subheader("🌡️ pH Monitoring (pH 3 จุด)")
        ph_in = st.number_input("pH น้ำเข้า (Inlet)", value=7.0, step=0.1)
        ph_aer = st.number_input("pH บ่อเติมอากาศ (Aeration)", value=7.2, step=0.1)
        ph_out = st.number_input("pH น้ำออก (Effluent)", value=7.0, step=0.1)

# --- TAB 2: ผลวิเคราะห์ ---
with tab2:
    if run_diagnosis:
        # การคำนวณทางวิศวกรรม
        fm = (q_act * bod_est) / (calc_mlss * tank_v) if calc_mlss > 0 else 0
        svi = (sv30_val * 1000) / calc_mlss if calc_mlss > 0 else 0
        hrt = (tank_v / q_act) * 24 if q_act > 0 else 0
        
        # แสดงผล Metrics หลัก
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("F/M Ratio", f"{fm:.2f}")
        m2.metric("SVI Index", f"{svi:.0f}")
        m3.metric("DO Level", f"{do_act}")
        m4.metric("Cl2 Residual", f"{cl_out}")

        st.divider()
        st.subheader("🔍 Professional Diagnosis & Risk Assessment")
        
        # วิเคราะห์ตะกอน
        if sv30_val > 600:
            st.error(f"🔴 **วิกฤตตะกอน (SV30 = {sv30_val}):** ตะกอนแน่นเกินไป ระบบแยกชั้นน้ำไม่ได้")
        
        # วิเคราะห์ pH
        if ph_aer < 6.5:
            st.error(f"🔴 **pH บ่อเติมอากาศต่ำ ({ph_aer}):** สภาวะเป็นกรด จุลินทรีย์ทำงานได้แย่ลง")
        elif 6.5 <= ph_aer <= 8.5:
            st.success("🟢 **pH ปกติ:** สภาวะในบ่อเหมาะสมดีมาก")

        # วิเคราะห์ Chlorine
        if cl_out < 0.2:
            st.warning(f"⚠️ **คลอรีนต่ำ ({cl_out}):** ระวังการฆ่าเชื้อไม่สมบูรณ์")
        else:
            st.success("🟢 **การฆ่าเชื้อปกติ:** อยู่ในเกณฑ์มาตรฐาน")

        # บันทึกข้อมูล
        log_data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Flow": q_act, "SV30": sv30_val, "MLSS": calc_mlss, "DO": do_act,
            "pH_In": ph_in, "pH_Aer": ph_aer, "pH_Out": ph_out, 
            "Cl2": cl_out, "FM": round(fm, 2), "SVI": round(svi, 0)
        }
        save_to_csv(log_data)
        st.toast("บันทึกข้อมูลและวิเคราะห์เสร็จสมบูรณ์!")
    else:
        st.info("👈 กรุณากดปุ่ม 'Run Diagnosis' เพื่อเริ่มประมวลผล")

# --- TAB 3: คำแนะนำ ---
with tab3:
    st.subheader("⚙️ Operational Strategy")
    if sv30_val > 500:
        st.error("💡 **Action:** เร่งสูบตะกอนทิ้ง (WAS) หรือเดินเครื่องรีดตะกอน")
    if ph_aer < 6.5:
        st.warning("💡 **Action:** ตรวจสอบระบบเติมด่าง (Alkali Dosing)")

# --- TAB 4: ประวัติ ---
with tab4:
    if os.path.exists(DB_FILE):
        hist_df = pd.read_csv(DB_FILE)
        st.dataframe(hist_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
        st.download_button("📥 Download CSV Report", data=hist_df.to_csv(index=False).encode('utf-8-sig'), file_name="Report.csv")

# 5. Footer
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>WASTEWATER INTELLIGENCE SYSTEM (WIS) by Mr. WUTTIKRON</p>", unsafe_allow_html=True)