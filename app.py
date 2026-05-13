import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go

# 設定一個簡單的密碼
def check_password():
    """如果密碼正確則傳回 True，否則顯示輸入框。"""
    def password_entered():
        if st.session_state["password"] == "hcc2026": 
            st.session_state["password_correct"] = True
            del st.session_state["password"]  
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("請輸入研究授權密碼", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("密碼錯誤，請重新輸入", type="password", on_change=password_entered, key="password")
        st.error("😕 密碼不正確")
        return False
    else:
        return True

if not check_password():
    st.stop()  

# 1. 頁面配置
st.set_page_config(
    page_title="HCC Risk Explorer", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 法律聲明與研究資訊 ---
st.error("⚠️ **學術研究專用聲明**：本工具僅供合作醫師及研究人員作為學術參考，**嚴禁**直接用於臨床診斷或醫療決策。使用前請務必核對原始研究論文。")

with st.expander("📖 原始研究與模型來源"):
    st.write("""
    **研究題目**：Risk Factors and Nomogram Model for Hepatocellular Carcinoma Development in Chronic Hepatitis B Patients with Low-Level Viremia
    **作者**：Chen, Y.C. et al.
    **發表期刊**：International Journal of Medical Sciences 21.9 (2024): 1661
    **連結**：[點此查看論文原文](https://www.medsci.org/v21p1661.htm)
    """)

# CSS 樣式
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🧬 慢性B型肝炎低病毒血症患者發生肝細胞癌(HCC)風險評分系統")
st.caption("本工具根據慢性B型肝炎低病毒血症患者(HBV DNA 20-2000 IU/mL)研究建立。")

# --- 側邊欄輸入 ---
with st.sidebar:
    st.header("📍 患者臨床指標")
    gender = st.radio("性別 (Gender)", options=["男 (Male)", "女 (Female)"], horizontal=True)
    age = st.slider("年齡 (Age)", 20, 90, 55, help="針對 20 歲以上成年患者開發。")
    cirrhosis = st.segmented_control("肝硬化 (Cirrhosis)", options=["無 (No)", "有 (Yes)"], default="無 (No)", help="指影像學或切片確診之肝硬化。")
    platelet = st.selectbox("血小板計數 (Platelet)", options=["正常 (150~400)", "異常 (<150 or >400)"], help="單位為 10^3/μL。")
    ast = st.selectbox("AST 數值 (GOT)", options=["正常 (5~34)", "異常 (Abnormal)"], help="通常以 >34 U/L 為異常上限。")

# --- 核心計算邏輯 ---
age_factor = (31.95164 * 3.57680) / 80
age_points = round(age_factor * (age - 20))
gender_points = 20 if "男" in gender else 0
cirrhosis_points = 22 if "有" in cirrhosis else 0
platelet_points = 23 if "異常" in platelet else 0
ast_points = 13 if "異常" in ast else 0

total_points = age_points + gender_points + cirrhosis_points + platelet_points + ast_points

# --- 風險排名與顏色邏輯 (修正區) ---
if total_points >= 135:
    rank_text = "高分位區間 (Top Percentile)"
    rank_desc = "該患者風險值高於研究群體中大多數對象。"
    risk_advice = "建議加強追蹤頻率，並密切監控影像學變化。"
    display_color = "#e74c3c"  # 紅色
    risk_color = "#e74c3c"
elif total_points >= 100:
    rank_text = "中分位區間 (Median Range)"
    rank_desc = "該患者風險值接近研究群體之平均水準。"
    risk_advice = "維持定期臨床評估與常規追蹤。"
    display_color = "#fd7e14"  # 橘色
    risk_color = "#fd7e14"
else:
    rank_text = "低分位區間 (Low Percentile)"
    rank_desc = "該患者風險值低於研究群體之平均水準。"
    risk_advice = "建議依照標準指引進行常規追蹤。"
    display_color = "#1f77b4"  # 藍色
    risk_color = "#1f77b4"

# --- 計算曲線函數 ---
def get_curve(score):
    lp = 0.03166 * (score - 72.641166)
    exponent = math.exp(lp)
    times = [0, 3, 5, 10]
    base_survival = [1.0, 0.9741862491, 0.963424793, 0.9205781806]
    pts_incidence = [(1 - (s ** exponent)) for s in base_survival]
    full_t = np.linspace(0, 10, 100)
    full_s_survival = np.interp(full_t, times, [s ** exponent for s in base_survival])
    full_i_incidence = 1 - full_s_survival 
    return full_t, full_i_incidence, pts_incidence

full_t, full_i, key_risks = get_curve(total_points)

# --- 視覺呈現區 ---
col_score, col_chart = st.columns([1, 2], gap="large")

with col_score:
    # 1. 群體排名卡片
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 5px solid {display_color};">
            <h3 style="margin-top:0; color: #333;">📊 群體排名參考</h3>
            <p style="font-size: 1.1rem; color: #666; margin-bottom: 5px;">總積分：<strong>{total_points} 分</strong></p>
            <h2 style="color: {display_color}; margin: 10px 0;">{rank_text}</h2>
            <p style="font-size: 0.95rem; color: #555; line-height: 1.5;">{rank_desc}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # 間隔
    st.metric("總風險評分 (Total Points)", f"{total_points} Pts")
    st.info(f"💡 **臨床建議**\n\n{risk_advice}")

with col_chart:
    st.subheader("📈 肝細胞癌 (HCC) 累積發生風險率")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=full_t, y=full_i, fill='tozeroy', mode='lines',
        line=dict(color=risk_color, width=4),
        name='Cumulative Incidence'
    ))
    
    fig.add_trace(go.Scatter(
        x=[3, 5, 10], y=[key_risks[1], key_risks[2], key_risks[3]],
        mode='markers+text',
        text=[f"{key_risks[1]:.1%}", f"{key_risks[2]:.1%}", f"{key_risks[3]:.1%}"],
        textposition="top left",
        textfont=dict(size=14, color='black'),
        marker=dict(color='black', size=8)
    ))
    
    fig.update_layout(
        yaxis=dict(title="累積發生率 (%)", tickformat=".1%", range=[0, max(full_i)*1.5 if max(full_i)>0 else 0.1]),
        xaxis=dict(title="評估後追蹤年數 (Years)", dtick=1),
        margin=dict(l=40, r=40, t=20, b=40)
    )
    st.plotly_chart(fig, width='stretch')

    st.write("**預估 HCC 累積發生率：**")
    m_col1, m_col2, m_col3 = st.columns(3)
    
    def big_metric(label, value, color):
        return f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #eee; text-align: center;">
            <p style="margin:0; font-size: 1rem; color: #666;">{label}</p>
            <p style="margin:0; font-size: 2.2rem; font-weight: 800; color: {color};">{value:.1%}</p>
        </div>
        """

    with m_col1:
        st.markdown(big_metric("3年累積發生率", key_risks[1], display_color), unsafe_allow_html=True)
    with m_col2:
        st.markdown(big_metric("5年累積發生率", key_risks[2], display_color), unsafe_allow_html=True)
    with m_col3:
        st.markdown(big_metric("10年累積發生率", key_risks[3], display_color), unsafe_allow_html=True)

# --- 頁尾與聲明 ---
with st.expander("🔬 查看模型詳細參數與說明"):
    st.write("本研究基於多變量 Cox 比例風險模型。")
    st.latex(r"S(t | x) = S_0(t)^{\exp(\sum \beta_i x_i)}")
    st.write(f"當前患者線性預測因子 (Linear Predictor): `{0.03166 * (total_points - 72.641166):.4f}`")

st.warning("⚠️ 聲明：本工具基於學術公式模擬，臨床決策請諮詢醫師。")    

# 使用水平線分隔主程式與免責聲明
st.divider()
st.caption("""
**📌 學術與臨床說明：**
1. **百分位意義**：百分位係指該患者分數在原始研究群體中的相對位置，非臨床診斷切點。
2. **無分層聲明**：本研究原始文獻僅提供 Cox 回歸預測模型，並未定義特定的風險分層標準。
3. **臨床應用**：本工具提供之機率僅供臨床參考，實際診療請務必結合超音波、AFP 及患者病史由專科醫師決定。
""")

# 建立免責聲明區域
st.markdown("""
<small>

**Disclaimer / 免責聲明**

* **Academic Purpose Only:** This tool is designed exclusively for academic research and clinical reference. It is not intended for direct medical diagnosis or treatment. The developer assumes no liability for clinical decisions.
* **專業用途：** 本工具僅限於學術研究與臨床參考，不應作為醫療診斷或治療的唯一依據。
* **Professional Judgment:** All predictions should be interpreted by qualified healthcare professionals in conjunction with the patient's full clinical profile and other diagnostic findings.
* **專業判斷：** 所有預測結果均應由具備資格的醫療專業人員，結合病患完整臨床資料及其他診斷結果進行綜合評估。
* **Data Privacy:** No personal identifiable information (PII) is collected or stored by this application.
* **數據隱私：** 本應用程式不會收集或儲存任何個人識別資訊。
* **Liability:** The developer shall not be held liable for any clinical decisions made based on the results of this tool.
* **法律責任：** 開發者對於依據本工具結果所做出的任何臨床決策概不負責。

</small>
""", unsafe_allow_html=True)
