import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go

import streamlit as st

# 設定一個簡單的密碼
def check_password():
    """如果密碼正確則傳回 True，否則顯示輸入框。"""
    def password_entered():
        if st.session_state["password"] == "hcc2026": # 你可以修改你的密碼
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 不要儲存密碼
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 顯示輸入框
        st.text_input("請輸入研究授權密碼", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # 密碼錯誤
        st.text_input("密碼錯誤，請重新輸入", type="password", on_change=password_entered, key="password")
        st.error("😕 密碼不正確")
        return False
    else:
        return True

if not check_password():
    st.stop()  # 密碼不正確就停止執行後續程式碼

# --- 後續才是你原本的網頁內容 (st.title, st.sidebar 等) ---

# 1. 頁面配置：讓介面寬一點，看起來不擁擠
st.set_page_config(
    page_title="HCC Risk Explorer", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. 頁面配置後立即加入法律聲明 ---
st.error("⚠️ **學術研究專用聲明**：本工具僅供合作醫師及研究人員作為學術參考，**嚴禁**直接用於臨床診斷或醫療決策。使用前請務必核對原始研究論文。")

with st.expander("📖 原始研究與模型來源"):
    st.write("""
    **研究題目**：Risk Factors and Nomogram Model for Hepatocellular Carcinoma Development in Chronic Hepatitis B Patients with Low-Level Viremia
    **作者**：Chen, Y.C. et al.
    **發表期刊**：nternational Journal of Medical Sciences 21.9 (2024): 1661
    **連結**：[點此查看論文原文](https://www.medsci.org/v21p1661.htm)
    """)

# 使用自定義 CSS 調整樣式
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        background: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 標題區 ---
st.title("🧬 慢性B型肝炎低病毒血症患者發生肝細胞癌(HCC)風險評分系統")
st.caption("本工具根據慢性B型肝炎低病毒血症患者(HBV DNA 檢測結果在 20 至 2000 IU/mL之間)研究建立，提供精確的風險評分與動態生存曲線預測。")

# --- 側邊欄：重新設計外觀 ---
with st.sidebar:
    st.header("📍 患者臨床指標")
    st.info("請輸入以下參數以獲取即時評估報告")
    
    gender = st.radio("性別 (Gender)", options=["男 (Male)", "女 (Female)"], horizontal=True)
    age = st.slider("年齡 (Age)", 20, 90, 55)
    
    st.divider() # 加入分隔線
    
    cirrhosis = st.segmented_control("肝硬化 (Cirrhosis)", options=["無 (No)", "有 (Yes)"], default="無 (No)")
    platelet = st.selectbox("血小板計數 (Platelet)", options=["正常 (150~400)", "異常 (<150 or >400)"])
    ast = st.selectbox("AST 數值", options=["正常 (5~34)", "異常 (Abnormal)"])

# --- 核心計算邏輯 ---
age_factor = (31.95164 * 3.57680) / 80
age_points = round(age_factor * (age - 20))
gender_points = 20 if "男" in gender else 0
cirrhosis_points = 22 if "有" in cirrhosis else 0
platelet_points = 23 if "異常" in platelet else 0
ast_points = 13 if "異常" in ast else 0

total_points = age_points + gender_points + cirrhosis_points + platelet_points + ast_points

# 風險分層判定 (切點建議：80, 130 可依研究自行調整)
if total_points < 90:
    risk_status = "低風險 (Low)"
    risk_color = "#28a745" # 綠色
    risk_advice = "建議每年定期超音波與 AFP 追蹤。"
elif 90 <= total_points < 135:
    risk_status = "中風險 (Intermediate)"
    risk_color = "#fd7e14" # 橘色
    risk_advice = "建議每 6 個月追蹤，並密切監測 HBV DNA 濃度。"
else:
    risk_status = "高風險 (High)"
    risk_color = "#dc3545" # 紅色
    risk_advice = "強烈建議每 3 個月密切追蹤，並諮詢專科醫師考慮預防性治療。"

# --- 計算生存曲線 ---
def get_curve(score):
    lp = 0.03166 * (score - 72.641166)
    exponent = math.exp(lp)
    times = [0, 3, 5, 10]
    base = [1.0, 0.9741862491, 0.963424793, 0.9205781806]
    pts = [s ** exponent for s in base]
    full_t = np.linspace(0, 10, 100)
    full_s = np.interp(full_t, times, pts)
    return full_t, full_s, pts

full_t, full_s, key_probs = get_curve(total_points)

# --- 視覺結果呈現區 ---
col_score, col_chart = st.columns([1, 2], gap="large")

with col_score:
    st.subheader("📋 評估摘要")
    
    # 1. 風險指示卡 (保留顏色分級)
    st.markdown(f"""
        <div style="background-color:{risk_color}; padding:20px; border-radius:10px; color:white; margin-bottom:20px">
            <h4 style="margin:0">當前風險分層</h4>
            <h2 style="margin:0">{risk_status}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. 顯示評分
    st.metric("總風險評分 (Total Points)", f"{total_points} Pts")
    
    # 3. 臨床建議 
    st.info(f"💡 **臨床建議**\n\n{risk_advice}")

with col_chart:
    st.subheader("📈 生存概率演變曲線")

    # 使用 HTML/CSS 建立一個可橫向滑動的包裝層
    st.markdown('<div style="overflow-x: auto; white-space: nowrap;">', unsafe_allow_html=True)

    fig = go.Figure()
    # 填充區域
    fig.add_trace(go.Scatter(
        x=full_t, y=full_s, fill='tozeroy', mode='lines',
        line=dict(color=risk_color, width=4),
        name='HCC-free Probability'
    ))

    # 關鍵切點標記
    fig.add_trace(go.Scatter(
        x=[3, 5, 10], 
        y=[key_probs[1], key_probs[2], key_probs[3]],
        mode='markers+text',
        text=[f"{key_probs[1]:.1%}", f"{key_probs[2]:.1%}", f"{key_probs[3]:.1%}"],
        textposition="top center",  # 改為正上方，減少右側被切掉的機率
        textfont=dict(size=20),     # 即使字體很大
        marker=dict(color='black', size=10, symbol='diamond')
    ))

    fig.update_layout(
        # 增加右側(r)和上方(t)的邊距，留空間給大字體
        margin=dict(l=50, r=80, b=50, t=50), 
        template="plotly_white",
        yaxis=dict(
            range=[0, 1.1], # 稍微拉高 y 軸上限至 1.1，避免 top 的文字被切掉
            tickformat=".0%",
            tickfont=dict(size=14)
        ),
        xaxis=dict(
            range=[0, 11],  # 稍微拉長 x 軸上限至 11，避免 10年的文字被切掉
            title=dict(text="Years Following Evaluation", font=dict(size=16)),
            tickfont=dict(size=14),
            dtick=1
        ),
        height=500,
        showlegend=False
    )

    # 在這裡設定一個固定的寬度（例如 800px），確保字體變大時圖表不會縮小
    st.plotly_chart(fig, use_container_width=False, width=800)
    # --- 新增：在圖表下方橫向顯示存活率 ---
    st.write("**預估 HCC-free 存活率：**")
    st.markdown('</div>', unsafe_allow_html=True)

    # 建立三欄來橫向擺放
    m_col1, m_col2, m_col3 = st.columns(3)
    
    def big_metric(label, value):
        return f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #eee; text-align: center;">
            <p style="margin:0; font-size: 1rem; color: #666;">{label}</p>
            <p style="margin:0; font-size: 2.2rem; font-weight: 800; color: #1f77b4;">{value:.1%}</p>
        </div>
        """

    with m_col1:
        st.markdown(big_metric("3年 HCC-free", key_probs[1]), unsafe_allow_html=True)
    with m_col2:
        st.markdown(big_metric("5年 HCC-free", key_probs[2]), unsafe_allow_html=True)
    with m_col3:
        st.markdown(big_metric("10年 HCC-free", key_probs[3]), unsafe_allow_html=True)


# --- 頁尾說明 ---
with st.expander("🔬 查看模型詳細參數與說明"):
    st.write("本研究基於多變量 Cox 比例風險模型。")
    st.latex(r"S(t | x) = S_0(t)^{\exp(\sum \beta_i x_i)}")
    st.write(f"當前患者線性預測因子 (Linear Predictor): `{0.03166 * (total_points - 72.641166):.4f}`")

st.warning("⚠️ 聲明：本工具基於學術公式模擬，臨床決策請諮詢醫師。")    

# 使用水平線分隔主程式與免責聲明
st.divider()

# 建立免責聲明區域
st.markdown("""
<small>

**Disclaimer / 免責聲明**

* **Academic Purpose Only:** This tool is designed exclusively for academic research and clinical reference. It is not intended for direct medical diagnosis or treatment.
* **專業用途：** 本工具僅限於學術研究與臨床參考，不應作為醫療診斷或治療的唯一依據。
* **Professional Judgment:** All predictions should be interpreted by qualified healthcare professionals in conjunction with the patient's full clinical profile and other diagnostic findings.
* **專業判斷：** 所有預測結果均應由具備資格的醫療專業人員，結合病患完整臨床資料及其他診斷結果進行綜合評估。
* **Data Privacy:** No personal identifiable information (PII) is collected or stored by this application.
* **數據隱私：** 本應用程式不會收集或儲存任何個人識別資訊。
* **Liability:** The developer shall not be held liable for any clinical decisions made based on the results of this tool.
* **法律責任：** 開發者對於依據本工具結果所做出的任何臨床決策概不負責。

</small>
""", unsafe_allow_html=True)