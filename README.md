# 🧬 Hepatitis B HCC Risk Predictor (LLV Population)

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://hcc-risk-predictor-laaavtlojk9bfhctqywxgm.streamlit.app/) [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

本專案是一款基於臨床實證醫學研究開發的**肝細胞癌 (HCC) 累積發生風險評估工具**。專為**慢性B型肝炎低病毒血症 (Low-Level Viremia, LLV)** 患者（定義為 HBV DNA 介於 20 至 2000 IU/mL 之間）所設計。

本網頁工具將複雜的多變量 Cox 比例風險模型與 Nomogram 積分邏輯轉化為直觀的互動式介面，協助臨床醫師與研究人員評估患者在 3 年、5 年及 10 年內的 HCC 累積發生風險。

---

## 📖 原始研究與文獻來源

本工具之核心數學模型與臨床參數權重完全基於以下已發表之同儕審查（Peer-reviewed）學術論文：

* **研究題目**：*Risk Factors and Nomogram Model for Hepatocellular Carcinoma Development in Chronic Hepatitis B Patients with Low-Level Viremia*
* **主要作者**：Chen, Y.C. et al.
* **發表期刊**：*International Journal of Medical Sciences*, 21(9): 1661 (2024).
* **論文全文連結**：[International Journal of Medical Sciences (v21p1661)](https://www.medsci.org/v21p1661.htm)

---

## 🌟 核心功能特點

* **精確的累積發生率計算**：不同於傳統的存活率（Survival Rate）邏輯，本工具嚴謹地將公式翻轉為符合臨床直覺的**累積發生率 ($1 - S(t)$)**，曲線從 0% 隨追蹤年數動態爬升。
* **群體排名參考 (Risk Percentile)**：尊重原始研究未設定特定風險分層切點（Cut-off point）的客觀數據，改以「低分位」、「中位水準」與「高分位」呈現患者在研究背景族群中的相對風險排名。
* **智慧顏色預警系統**：當計算積分達到研究高風險分位區間時，介面數字將動態切換為紅色，提供即時的視覺警示。
* **臨床數據輸入提示**：各項臨床指標（如 AST 正常值上限、血小板低下定義等）均附帶滑鼠懸停提示問號（Tooltips），確保數據輸入的標準化。
* **安全性密碼防護**：內建 Session-state 密碼驗證機制，防止未授權對象任意存取學術模擬數據。

---

## 🛠️ 評估之臨床指標 (Predictors)

系統依據以下五大臨床獨立危險因子進行 Nomogram 積分加總：
1.  **性別 (Gender)**
2.  **年齡 (Age)** 
3.  **肝硬化 (Cirrhosis)** 
4.  **血小板計數 (Platelet count)**
5.  **AST 數值 (GOT)**

---

## 🚀 個人的電腦或本地安裝 (Local Installation)

若您想在個人的電腦或本地端伺服器運行此 App，請按照以下步驟操作：

### 1. 複製儲存庫
```bash
git clone [https://github.com/subechen-wq/hcc_risk_predictor.git](https://github.com/您的帳號/hcc_risk_predictor.git)
cd hcc_risk_predictor

2. 建立並啟動虛擬環境 (建議)
python -bin venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

3. 安裝必要套件
pip install -r requirements.txt
(註：requirements.txt 需包含 streamlit, plotly, numpy, watchdog)

4. 啟動 Streamlit 服務
streamlit run app.py

啟動後，瀏覽器將自動開啟 http://localhost:8501。預設存取密碼為 hcc2026。

📌 學術與免責聲明 (Disclaimer)
學術研究專用：本工具僅供學術交流與合作研究參考，嚴禁直接用於臨床診斷、醫療決策或取代專科醫師之實際臨床判斷。

無分層聲明：本研究原始文獻僅提供 Cox regression analysis預測模型以計算發生機率，未定義絕對的臨床高低風險分層。百分位區間僅為研究群體之相對比較。

隱私保護：本網頁應用程式為純前端/快取運算，不會收集、儲存或上傳任何患者的個人識別資訊 (PII)。

法律責任：開發團隊對於依據本工具模擬結果所做出之任何臨床醫療決策，概不承擔任何法律與醫療責任。

