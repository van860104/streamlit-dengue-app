
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
from google.oauth2 import service_account
import matplotlib.font_manager as fm
import os

# 設定字型路徑（Render 上會自動從 fonts 資料夾載入）
font_path = "fonts/NotoSansTC-VariableFont_wght.ttf"
fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Noto Sans TC'

# 強制使用 Render 上的 Secret 金鑰認證 BigQuery
SERVICE_ACCOUNT_FILE = "/etc/secrets/renderBigqueryKey.json"
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
client = bigquery.Client(credentials=credentials, project="dengue-health-vanessav2")

# ✅ 修正：取得 URL 參數（使用正確函式）
query_params = st.experimental_get_query_params()
location = query_params.get("location", [None])[0]
month = query_params.get("month", [None])[0]
year = query_params.get("year", [None])[0]

# 顯示目前參數（Debug）
st.markdown(f"**🔍 目前參數：** 地區 = `{location}`，年份 = `{year}`，月份 = `{month}`")

# 驗證參數有效性
if not location or not month or not year:
    st.error("請提供完整參數，例如 https://streamlit-dengue-app.onrender.com?location=台南市&year=2024&month=5")
    st.stop()

# 查詢資料（已更新為英文欄位名的新資料表）
sql = """
    SELECT onset_date, COUNT(*) as case_count
    FROM `dengue-health-vanessav2.health_data.dengue_cases_sreamlit`
    WHERE residence_city LIKE CONCAT(@location, '%')
      AND EXTRACT(MONTH FROM onset_date) = @month
      AND EXTRACT(YEAR FROM onset_date) = @year
    GROUP BY onset_date
    ORDER BY onset_date
"""

st.code(sql, language="sql")  # 顯示實際查詢 SQL（Debug）

job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("location", "STRING", location),
        bigquery.ScalarQueryParameter("month", "INT64", int(month)),
        bigquery.ScalarQueryParameter("year", "INT64", int(year)),
    ]
)

try:
    df = client.query(sql, job_config=job_config).to_dataframe()
except Exception as e:
    st.error(f"查詢資料失敗：{e}")
    st.stop()

if df.empty:
    st.warning("查無資料，請確認地區、年份與月份是否正確。")
    st.stop()

# 顯示標題
st.title(f"{location} 地區 {year} 年 {month} 月登革熱病例趨勢圖")

# 繪製圖表
df['onset_date'] = pd.to_datetime(df['onset_date'])
fig, ax = plt.subplots()
ax.plot(df['onset_date'], df['case_count'], marker='o')
ax.set_xlabel("發病日")
ax.set_ylabel("病例數")
ax.set_title(f"{location} 登革熱趨勢")
plt.xticks(rotation=45)

st.pyplot(fig)
