import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
from google.oauth2 import service\_account
import matplotlib.font\_manager as fm
import urllib.parse
import os

# 設定字型路徑（Render 上會自動從 fonts 資料夾載入）

font\_path = "fonts/NotoSansTC-VariableFont\_wght.ttf"
fm.fontManager.addfont(font\_path)
plt.rcParams\['font.family'] = 'Noto Sans TC'

# BigQuery 客戶端初始化（Render 環境建議設 GOOGLE\_APPLICATION\_CREDENTIALS）

SERVICE\_ACCOUNT\_FILE = "/etc/secrets/renderBigqueryKey.json"
if os.getenv("GOOGLE\_APPLICATION\_CREDENTIALS"):
client = bigquery.Client()
else:
credentials = service\_account.Credentials.from\_service\_account\_file(SERVICE\_ACCOUNT\_FILE)
client = bigquery.Client(credentials=credentials)

# 取得 URL 參數

query\_params = st.experimental\_get\_query\_params()
location = query\_params.get("location", \[None])\[0]
month = query\_params.get("month", \[None])\[0]

# 驗證參數有效性

if not location or not month:
st.error("請提供完整參數（地區與月份），例如 ?location=台南\&month=5")
st.stop()

# 查詢資料

sql = f'''
SELECT 發病日, COUNT(\*) as 病例數
FROM `dengue-health-vanessav2.health_data.dengue_cases`
WHERE 居住縣市 LIKE '%{location}%'
AND EXTRACT(MONTH FROM 發病日) = {month}
GROUP BY 發病日
ORDER BY 發病日
'''

@st.cache\_data
def load\_data():
df = client.query(sql).to\_dataframe()
return df

# 載入資料

try:
df = load\_data()
except Exception as e:
st.error(f"查詢資料失敗：{e}")
st.stop()

if df.empty:
st.warning("查無資料，請確認地區與月份是否正確。")
st.stop()

# 顯示標題

st.title(f"{location} 地區 {month} 月登革熱病例趨勢圖")

# 日期轉換與繪圖

df\['發病日'] = pd.to\_datetime(df\['發病日'])
fig, ax = plt.subplots()
ax.plot(df\['發病日'], df\['病例數'], marker='o')
ax.set\_xlabel("發病日")
ax.set\_ylabel("病例數")
ax.set\_title(f"{location} 登革熱趨勢")
plt.xticks(rotation=45)

st.pyplot(fig)
