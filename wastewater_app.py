import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. Page Configuration (ใช้ค่ามาตรฐานเพื่อให้ระบบเลือกสีที่เหมาะสมที่สุด)
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
st.markdown(f"**Developed by:** Mr. WUTTIKRON TIWAWAL | **Date:** {datetime.now().strftime('%d/%m/%Y')}")
st.divider()

# 3. SIDEBAR (เมนูด้านซ้าย)
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

# 4. MAIN CONTENT TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Daily Input (ลงข้อมูล)", 
    "🔍 Diagnosis (ผลวิเคราะห์)", 
    "⚙️ Machine (คำแนะนำ)", 
    "📜 History (ประวัติ)"
])

# --- TAB 1: บันทึกข้อมูล ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔬 Microbial Status (MLSS)")
        method = st.radio("วิธีหาค่า MLSS:", ["Quick SV30 (แบบเร็ว)", "Lab Weight (ชั่งน้ำหนัก)", "Manual (กรอกเอง)"])
        
        if method == "Quick SV30 (แบบเร็ว)":
            sv30_in = st.number_input("ค่า SV30 ที่วัดได้ (mL/L)", value=900)
            calc_mlss = (sv30_in * 1000) / 120
        elif method == "Lab Weight (ชั่งน้ำหนัก)":
            w = st.number_input("น้ำหนักตะกอนแห้ง (g)", value=0.15, format="%.4f")
            v = st.number_input("ปริมาตรน้ำตัวอย่าง (mL)", value=50)
            calc_mlss = (w * 1000000) / v if v > 0 else 0
        else:
            calc_mlss = st.number_input("ระบุค่า MLSS (mg/L)", value=3000)
        
        st.metric("Estimated MLSS", f"{calc_mlss:,.0f} mg/L")

    with col2:
        st.subheader("📊 Field Parameters")
        q_act = st.number_input("ปริมาณน้ำเข้าจริง (m3/day)", value=98)
        bod_in = st.number_input("ค่า BOD ขาเข้าประมาณการ (mg/L)", value=250)
        do_act = st.number_input("ค่า DO ในบ่อเติมอากาศ (mg/L)", value=2.0, step=0.1)
        sv30_act = st.number_input("ค่า SV30 หน้างาน (mL/L)", value=900)

# --- TAB 2: ผลวิเคราะห์ ---
with tab2:
    if run_diagnosis:
        # การคำนวณทางวิศวกรรม
        fm = (q_act * bod_in) / (calc_mlss * tank_v)
        svi = (sv30_act * 1000) / calc_mlss
        hrt = (tank_v / q_act) * 24 if q_act > 0 else 0
        
        # แสดงผลในรูปแบบ Card
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("F/M Ratio", f"{fm:.2f}")
        m2.metric("SVI Index", f"{svi:.0f}")
        m3.metric("DO Level", f"{do_act}")
        m4.metric("HRT (Hours)", f"{hrt:.1f}")

        st.divider()
        st.subheader("🚨 Risk Analysis & Diagnosis")
        
        if sv30_act > 600:
            st.error(f"🔴 **วิกฤต (SV30 = {sv30_act}):** ตะกอนแน่นเกินไป บ่อตกตะกอนจะแยกชั้นน้ำไม่ได้")
            st.info("💡 **วิธีแก้:** ต้องรีบสูบตะกอนส่วนเกินทิ้ง (WAS) เพื่อลดระดับตะกอนลง")

        if hrt < 18:
            st.warning(f"⚠️ **แจ้งเตือน (HRT = {hrt:.1f} ชม.):** น้ำไหลผ่านเร็วเกินไป จุลินทรีย์อาจบำบัดไม่สมบูรณ์")

        if do_act < 1.0:
            st.error("🔴 **วิกฤต (DO ต่ำ):** ออกซิเจนไม่พอ จุลินทรีย์จะตายและน้ำจะเริ่มเหม็น")

        if 0.1 <= fm <= 0.6 and sv30_act < 500:
            st.success("🟢 **ระบบสมดุล:** สภาวะการบำบัดน้ำเสียอยู่ในเกณฑ์ปกติ")

        # บันทึกข้อมูล
        log_data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Flow": q_act, "MLSS": calc_mlss, "SV30": sv30_act, 
            "DO": do_act, "FM": round(fm, 2), "SVI": round(svi, 0)
        }
        save_to_csv(log_data)
        st.toast("บันทึกข้อมูลสำเร็จ!")
    else:
        st.info("👈 กรุณากดปุ่ม 'Run Diagnosis' ที่เมนูซ้ายมือเพื่อดูผลการประมวลผล")

# --- TAB 3: เครื่องจักร ---
with tab3:
    st.subheader("🛠️ Machine Strategy")
    if sv30_act > 500:
        st.info("✅ **ข้อเสนอแนะ:** ควรเดินเครื่องรีดตะกอน (Screw Press) หรือเพิ่มความถี่ในการสูบตะกอนทิ้งทันที")

# --- TAB 4: ประวัติ ---
with tab4:
    st.subheader("📜 Operation History")
    if os.path.exists(DB_FILE):
        hist_df = pd.read_csv(DB_FILE)
        st.dataframe(hist_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
        
        csv_data = hist_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 ดาวน์โหลดรายงาน (Excel/CSV)", data=csv_data, file_name="WW_Report.csv", mime="text/csv")
    else:
        st.info("ยังไม่มีข้อมูลในประวัติ")

# 5. Footer (แบบเรียบง่าย)
st.divider()
st.center = st.markdown("<p style='text-align: center; color: gray;'>WASTEWATER INTELLIGENCE SYSTEM (WIS) | Sustainable Water Management</p>", unsafe_allow_html=True)