import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 假資料（之後換成 BigQuery 查詢或 CSV 讀入）
data = {
    '月份': ['1月', '2月', '3月', '4月', '5月'],
    '病例數': [5, 20, 35, 80, 120]
}
df = pd.DataFrame(data)

# 頁面標題
st.title("登革熱趨勢圖表")

# 折線圖
fig, ax = plt.subplots()
ax.plot(df['月份'], df['病例數'], marker='o')
ax.set_xlabel("月份")
ax.set_ylabel("病例數")
ax.set_title("2025 年登革熱病例趨勢")
st.pyplot(fig)
