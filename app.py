import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analitik Perencanaan Agregat Manufaktur", layout="wide")

st.title("🏭 Aplikasi Analitik Perencanaan Agregat Manufaktur")
st.caption("Berdasarkan Buku Operations Management - Chapter 14: Aggregate Planning")

# Sidebar - Input Parameter
st.sidebar.header("1. Parameter Biaya & Kapasitas")
cost_holding = st.sidebar.number_input("Biaya Simpan Persediaan ($/unit/bulan)", min_value=1.0, value=5.0)
cost_subcontract = st.sidebar.number_input("Biaya Subkontrak ($/unit)", min_value=1.0, value=20.0)
cost_regular = st.sidebar.number_input("Biaya Produksi Reguler ($/unit)", min_value=1.0, value=10.0)
capacity_regular = st.sidebar.number_input("Kapasitas Reguler Maksimal (unit/bulan)", min_value=100, value=1000)

st.sidebar.header("2. Strategi Perencanaan")
strategy = st.sidebar.selectbox("Pilih Strategi Agregat", ["Level Strategy (Kapasitas Tetap)", "Chase Strategy (Subkontrak saat Kurang)"])

# Data Permintaan 6 Bulan
st.subheader("📊 Proyeksi Permintaan Produksi (6 Bulan)")
months = ["Bulan 1", "Bulan 2", "Bulan 3", "Bulan 4", "Bulan 5", "Bulan 6"]
default_demand = [800, 1200, 1500, 900, 1100, 1300]

df_demand = pd.DataFrame({"Bulan": months, "Permintaan (Unit)": default_demand})
st.dataframe(df_demand, use_container_width=True)

# Kalkulasi Strategi Agregat
df_res = df_demand.copy()

if strategy == "Level Strategy (Kapasitas Tetap)":
    # Produksi rata-rata konstan
    avg_prod = int(np.mean(default_demand))
    df_res['Produksi Reguler'] = avg_prod
    df_res['Subkontrak'] = 0
    
    inventory = []
    curr_inv = 0
    for idx, row in df_res.iterrows():
        curr_inv += row['Produksi Reguler'] - row['Permintaan (Unit)']
        inventory.append(max(0, curr_inv))
    df_res['Persediaan Akhir'] = inventory
    df_res['Biaya Simpan'] = df_res['Persediaan Akhir'] * cost_holding
    df_res['Biaya Produksi'] = df_res['Produksi Reguler'] * cost_regular
    df_res['Biaya Subkontrak'] = 0

else:  # Chase Strategy
    df_res['Produksi Reguler'] = df_res['Permintaan (Unit)'].apply(lambda x: min(x, capacity_regular))
    df_res['Subkontrak'] = df_res['Permintaan (Unit)'] - df_res['Produksi Reguler']
    df_res['Persediaan Akhir'] = 0
    df_res['Biaya Simpan'] = 0
    df_res['Biaya Produksi'] = df_res['Produksi Reguler'] * cost_regular
    df_res['Biaya Subkontrak'] = df_res['Subkontrak'] * cost_subcontract

df_res['Total Biaya'] = df_res['Biaya Produksi'] + df_res['Biaya Simpan'] + df_res['Biaya Subkontrak']

# Ringkasan Biaya
total_cost_all = df_res['Total Biaya'].sum()
total_inv_cost = df_res['Biaya Simpan'].sum()
total_sub_cost = df_res['Biaya Subkontrak'].sum()

st.markdown("### 💵 Ringkasan Biaya Perencanaan Agregat")
col1, col2, col3 = st.columns(3)
col1.metric("Total Biaya Keseluruhan", f"${total_cost_all:,.2f}")
col2.metric("Total Biaya Simpan Inventory", f"${total_inv_cost:,.2f}")
col3.metric("Total Biaya Subkontrak", f"${total_sub_cost:,.2f}")

st.markdown("---")
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader(f"📑 Detail Perhitungan ({strategy})")
    st.dataframe(df_res, use_container_width=True)

with col_right:
    st.subheader("📈 Grafik Perbandingan Permintaan vs Produksi")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df_res['Bulan'], df_res['Permintaan (Unit)'], marker='o', label='Permintaan', color='red', linewidth=2)
    ax.bar(df_res['Bulan'], df_res['Produksi Reguler'], alpha=0.6, label='Produksi Reguler', color='blue')
    if strategy != "Level Strategy (Kapasitas Tetap)":
        ax.bar(df_res['Bulan'], df_res['Subkontrak'], bottom=df_res['Produksi Reguler'], alpha=0.6, label='Subkontrak', color='orange')
    ax.set_ylabel("Unit")
    ax.set_title("Profil Produksi dan Permintaan")
    ax.legend()
    st.pyplot(fig)