
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
from google.oauth2 import service_account
import matplotlib.font_manager as fm
import os

# 設定字型路徑
font_path = "fonts/NotoSansTC-VariableFont_wght.ttf"
fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Noto Sans TC'

# 使用服務金鑰進行 BigQuery 認證
SERVICE_ACCOUNT_FILE = "/etc/secrets/renderBigqueryKey.json"
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
client = bigquery.Client(credentials=credentials, project="dengue-health-vanessav2")

# 取得 URL 參數（使用新版 API）
query_params = st.query_params
location = query_params.get("location", [None])[0]
month = query_params.get("month", [None])[0]

# 驗證參數
if not location or not month:
    st.error("請提供完整參數（地區與月份），例如 ?location=台南&month=5")
    st.stop()

# SQL 查詢（使用參數化）
sql = '''
    SELECT 發病日, COUNT(*) as 病例數
    FROM `dengue-health-vanessav2.health_data.dengue_cases`
    WHERE 居住縣市 LIKE @location
      AND EXTRACT(MONTH FROM 發病日) = @month
    GROUP BY 發病日
    ORDER BY 發病日
'''

job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("location", "STRING", f"%{location}%"),
        bigquery.ScalarQueryParameter("month", "INT64", int(month))
    ]
)

# 查詢與例外處理
try:
    df = client.query(sql, job_config=job_config).to_dataframe()
except Exception as e:
    st.error(f"查詢資料失敗：{e}")
    st.stop()

if df.empty:
    st.warning("查無資料，請確認地區與月份是否正確。")
    st.stop()

# 顯示圖表
st.title(f"{location} 地區 {month} 月登革熱病例趨勢圖")
df['發病日'] = pd.to_datetime(df['發病日'])

fig, ax = plt.subplots()
ax.plot(df['發病日'], df['病例數'], marker='o')
ax.set_xlabel("發病日")
ax.set_ylabel("病例數")
ax.set_title(f"{location} 登革熱趨勢")
plt.xticks(rotation=45)
st.pyplot(fig)
