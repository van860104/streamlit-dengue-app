import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
import matplotlib.font_manager as fm
import urllib.parse

# 設定字型路徑（Render 上會自動從 fonts 資料夾載入）

font_path = "fonts/NotoSansTC-VariableFont_wght.ttf"
fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Noto Sans TC'

# BigQuery 客戶端初始化（Render 環境需設定 GOOGLE_APPLICATION_CREDENTIALS）

client = bigquery.Client()

# 取得 URL 參數

query_params = st.experimental_get_query_params()
location = query_params.get("location", [None])[0]
month = query_params.get("month", [None])[0]

# 驗證參數有效性

if not location or not month:
st.error("請提供完整參數（地區與月份），例如 ?location=台南&month=5")
st.stop()

# 查詢資料

sql = f'''
SELECT 發病日, COUNT(*) as 病例數
FROM `dengue-health-vanessav2.health_data.dengue_cases`
WHERE 居住縣市 LIKE '%{location}%'
AND EXTRACT(MONTH FROM 發病日) = {month}
GROUP BY 發病日
ORDER BY 發病日
'''

@st.cache_data
def load_data():
df = client.query(sql).to_dataframe()
return df

# 載入資料

try:
df = load_data()
except Exception as e:
st.error(f"查詢資料失敗：{e}")
st.stop()

if df.empty:
st.warning("查無資料，請確認地區與月份是否正確。")
st.stop()

# 顯示標題

st.title(f"{location} 地區 {month} 月登革熱病例趨勢圖")

# 日期轉換與繪圖

df['發病日'] = pd.to_datetime(df['發病日'])
fig, ax = plt.subplots()
ax.plot(df['發病日'], df['病例數'], marker='o')
ax.set_xlabel("發病日")
ax.set_ylabel("病例數")
ax.set_title(f"{location} 登革熱趨勢")
plt.xticks(rotation=45)

st.pyplot(fig)
