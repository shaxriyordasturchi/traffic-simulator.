import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="VoIP Monitoring", layout="wide")

st.title("📞 IP-Telefoniya Monitoring Tizimi")

# Ma’lumotlar bazasi
def get_connection():
    return sqlite3.connect("database.db", check_same_thread=False)

conn = get_connection()

# IP manzillar statistikasi
def get_ip_stats():
    df = pd.read_sql_query("""
        SELECT ip_manzil, COUNT(*) as miqdor
        FROM voip_qongiroqlar
        GROUP BY ip_manzil
        ORDER BY miqdor DESC
    """, conn)
    return df

# Ovoz sifati statistikasi
def get_audio_stats():
    df = pd.read_sql_query("""
        SELECT ovoz_sifati, COUNT(*) as soni
        FROM voip_qongiroqlar
        GROUP BY ovoz_sifati
        ORDER BY ovoz_sifati
    """, conn)
    return df

# Umumiy statistikalar
def get_overall_stats():
    total_calls = pd.read_sql_query("SELECT COUNT(*) as soni FROM voip_qongiroqlar", conn)["soni"][0]
    total_users = pd.read_sql_query("SELECT COUNT(DISTINCT user_id) as user_soni FROM voip_qongiroqlar", conn)["user_soni"][0]
    return total_calls, total_users


# Interfeys
col1, col2 = st.columns(2)

with col1:
    st.subheader("📶 Eng ko‘p ishlatilgan IP-manzillar")
    ip_df = get_ip_stats()
    st.dataframe(ip_df)
    fig_ip = px.bar(ip_df, x='ip_manzil', y='miqdor', title="IP Manzillar bo‘yicha qo‘ng‘iroqlar soni", color='ip_manzil')
    st.plotly_chart(fig_ip, use_container_width=True)

with col2:
    st.subheader("🎧 Ovoz sifati statistikasi")
    audio_df = get_audio_stats()
    st.dataframe(audio_df)
    fig_audio = px.pie(audio_df, names='ovoz_sifati', values='soni', title="Ovoz sifati bo‘yicha taqsimot")
    st.plotly_chart(fig_audio, use_container_width=True)

st.divider()
st.subheader("📈 Umumiy statistikalar")

total_calls, total_users = get_overall_stats()
st.metric("Jami qo‘ng‘iroqlar", total_calls)
st.metric("Foydalanuvchilar soni", total_users)

conn.close()
