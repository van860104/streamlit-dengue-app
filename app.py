import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 設定中文字型避免亂碼
font_path = os.path.join("fonts", "NotoSansTC-VariableFont_wght.ttf")
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams["font.family"] = "Noto Sans TC"

# 假設已有本地 CSV 資料
DATA_PATH = os.path.join("..", "data", "monthly_cases.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df

df = load_data()

# Streamlit 視覺化介面
st.title("登革熱趨勢圖表")

# 側邊欄選擇區域與月份
cities = sorted(df["縣市"].dropna().unique())
months = sorted(df["月份"].dropna().unique())

selected_city = st.sidebar.selectbox("選擇縣市", cities)
selected_month = st.sidebar.selectbox("選擇月份", months)

# 過濾資料
filtered_df = df[(df["縣市"] == selected_city) & (df["月份"] == selected_month)]

if not filtered_df.empty:
    fig, ax = plt.subplots()
    ax.plot(filtered_df["日期"], filtered_df["確定病例數"], marker="o")
    ax.set_title(f"{selected_month} 月 {selected_city} 登革熱趨勢")
    ax.set_xlabel("日期")
    ax.set_ylabel("確定病例數")
    st.pyplot(fig)
else:
    st.warning("查無資料，請重新選擇。")