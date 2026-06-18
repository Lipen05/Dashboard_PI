import streamlit as st
import pandas as pd
import plotly.express as px
import warnings
import os

warnings.filterwarnings('ignore')

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA & STYLING (CSS)
# ==========================================
st.set_page_config(
    page_title="Dashboard Kekerasan Perempuan",
    page_icon="📊",
    layout="wide"
)

# CSS Kustom untuk Sidebar, Tombol, dan Kartu KPI
st.markdown("""
<style>
/* SIDEBAR */
[data-testid="stSidebar"]{
    background-color:#14245C;
}

section[data-testid="stSidebar"]{
    padding-top:25px;
}

/* label filter */
[data-testid="stSidebar"] label{
    color:white !important;
    font-weight:600;
}

/* heading sidebar */
.sidebar-title{
    color:white;
}

.sidebar-subtitle{
    color:white;
    line-height:1.4;
}

/* tombol */
.stButton button{
    background:white;
    color:#14245C !important;
    border-radius:8px;
    font-weight:bold;
    width: 100%;
}

/* KPI CARD */
.metric-card{
    background:#F8F9FA;
    border-radius:12px;
    padding:20px;
    text-align:center;
    box-shadow:0px 2px 8px rgba(0,0,0,0.08);
    min-height:120px;
}

.metric-title{
    color:#666;
    font-size:15px;
}

.metric-value{
    color:#14245C;
    font-size:26px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PROSES MEMUAT & MEMBERSIHKAN DATASET
# ==========================================
try:
    # Membaca menggunakan pemisah koma ',' sesuai dengan format file hasil_clustering.csv Anda
    df = pd.read_csv("hasil_clustering.csv", sep=",")
except FileNotFoundError:
    st.error("Berkas data 'hasil_clustering.csv' tidak ditemukan di direktori kerja.")
    st.stop()

# Menghapus spasi gaib pada nama kolom jika ada
df.columns = df.columns.str.strip()

# Mengubah "Wilayah" menjadi "Kabupaten/Kota" sesuai isi file csv
df = df.dropna(subset=["Provinsi", "Tahun", "Kabupaten/Kota"], how="all")

# Menentukan kolom dimensi jenis kekerasan yang tersedia di berkas Anda
jenis_kekerasan = ["Fisik", "Psikis", "Seksual", "Eksploitasi", "TPPO", "Penelantaran"]

# Membuat kalkulasi Total Kasus secara dinamis dari jumlahan baris jenis kekerasan
df["Total_Kasus"] = df[jenis_kekerasan].sum(axis=1)

# ==========================================
# 3. SIDEBAR NAVIGATION & FILTER DATA
# ==========================================
with st.sidebar:
    col_logo, col_text = st.columns([1,2])
    
    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=60)
        else:
            st.markdown("<h1 style='color: white; margin: 0;'>📊</h1>", unsafe_allow_html=True)

    with col_text:
        st.markdown("""
        <div class="sidebar-title">
            <h4 style="margin-bottom:0; font-weight:bold;">DASHBOARD</h4>
        </div>
        <div class="sidebar-subtitle">
            KEKERASAN PEREMPUAN<br>DEWASA DI INDONESIA
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## FILTER DATA")

    tahun_pilihan = st.selectbox(
        "Pilih Tahun",
        options=["Semua"] + sorted(df["Tahun"].dropna().unique().astype(int).tolist())
    )

    provinsi_pilihan = st.selectbox(
        "Pilih Provinsi",
        options=["Semua"] + sorted(df["Provinsi"].dropna().unique().tolist())
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reset Filter"):
        st.rerun()

# Menjalankan Logika Filter
df_filter = df.copy()

if tahun_pilihan != "Semua":
    df_filter = df_filter[df_filter["Tahun"] == tahun_pilihan]

if provinsi_pilihan != "Semua":
    df_filter = df_filter[df_filter["Provinsi"] == provinsi_pilihan]

# ==========================================
# 4. HEADER UTAMA DASHBOARD
# ==========================================
st.title("Dashboard Kasus Kekerasan Terhadap Perempuan Dewasa di Pulau Jawa")
st.subheader("Analisis Pemantauan Deskriptif, Tingkat Kerentanan, dan Klasterisasi")
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. RINGKASAN METRIK (KPI CARDS)
# ==========================================
total_kasus = int(df_filter["Total_Kasus"].sum())

if len(df_filter) > 0:
    provinsi_dominan = df_filter.groupby("Provinsi")["Total_Kasus"].sum().idxmax()
    total_per_jenis = df_filter[jenis_kekerasan].sum()
    kekerasan_dominan = total_per_jenis.idxmax()
    
    # Mencari cluster mana yang memiliki sebaran total kasus terbanyak
    cluster_dominan = df_filter.groupby("Cluster_Label")["Total_Kasus"].sum().idxmax()
else:
    provinsi_dominan = "-"
    kekerasan_dominan = "-"
    cluster_dominan = "-"

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Dampak Kasus</div>
        <div class="metric-value">{total_kasus:,}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Provinsi Kasus Tertinggi</div>
        <div class="metric-value" style="font-size:18px; padding-top:5px;">{provinsi_dominan}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Jenis Kekerasan Dominan</div>
        <div class="metric-value" style="font-size:18px; padding-top:5px;">{kekerasan_dominan}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Klaster Mayoritas Dominan</div>
        <div class="metric-value" style="font-size:16px; padding-top:7px; color: #E53935;">{cluster_dominan}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. ROW BARIS 1: GAMBAR 1 (TREEMAP) & GAMBAR 2 (TREN LINE)
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🗺️ Gambar 1: Pandangan Hierarki Wilayah (TreeMap)")
    fig_tree = px.treemap(
        df_filter, 
        path=["Provinsi", "Kabupaten/Kota"], 
        values="Total_Kasus", 
        color="Total_Kasus",
        color_continuous_scale="Reds",
        template="plotly_dark"
    )
    fig_tree.update_layout(height=420, margin=dict(t=10, b=10, r=10, l=10))
    st.plotly_chart(fig_tree, width="stretch")
    
    # --- REKAPAN DATA CSV UNTUK GAMBAR 1 ---
    st.markdown("#### 📋 Rekapan Data: Proporsi Sebaran Kasus Per Provinsi")
    if len(df_filter) > 0:
        summary_prov = df_filter.groupby("Provinsi")["Total_Kasus"].sum().reset_index()
        summary_prov["Persentase (%)"] = ((summary_prov["Total_Kasus"] / summary_prov["Total_Kasus"].sum()) * 100).round(2)
        summary_prov = summary_prov.sort_values(by="Total_Kasus", ascending=False).reset_index(drop=True)
        st.dataframe(summary_prov, width="stretch", height=150)
        
        # Tombol download CSV Gambar 1
        csv_g1 = summary_prov.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Unduh Data Provinsi (.csv)", data=csv_g1, file_name="Rekap_Kasus_Per_Provinsi.csv", mime="text/csv", key="download_g1")
    else:
        st.info("Tidak ada data untuk kombinasi filter saat ini.")

with col2:
    st.subheader("📈 Gambar 2: Analisis Tren Kasus Berdasarkan Tahun")
    df_filter["Tahun_Str"] = df_filter["Tahun"].astype(int).astype(str)
    trend_data = df_filter.groupby("Tahun_Str")["Total_Kasus"].sum().reset_index().sort_values("Tahun_Str")
    
    fig_trend = px.line(
        trend_data, 
        x="Tahun_Str", 
        y="Total_Kasus", 
        labels={"Tahun_Str": "Tahun", "Total_Kasus": "Jumlah Kasus"},
        template="gridon", 
        markers=True
    )
    fig_trend.update_layout(height=420)
    fig_trend.update_traces(line=dict(color="#14245C", width=3))
    st.plotly_chart(fig_trend, width="stretch")
    
    # --- REKAPAN DATA CSV UNTUK GAMBAR 2 ---
    st.markdown("#### 📋 Rekapan Data: Historis Tren Kasus Tahunan")
    if len(trend_data) > 0:
        trend_table = trend_data.rename(columns={"Tahun_Str": "Tahun", "Total_Kasus": "Total_Kasus_Korban"}).reset_index(drop=True)
        st.dataframe(trend_table, width="stretch", height=150)
        
        # Tombol download CSV Gambar 2
        csv_g2 = trend_table.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Unduh Data Tren Tahunan (.csv)", data=csv_g2, file_name="Rekap_Tren_Tahunan.csv", mime="text/csv", key="download_g2")
    else:
        st.info("Tidak ada data tren historis.")

st.divider()

# ==========================================
# 7. ROW BARIS 2: GAMBAR 3 (BAR CHART) & GAMBAR 4 (SCATTER PLOT KLASTER)
# ==========================================
col3, col4 = st.columns([1, 1])

with col3:
    st.subheader("📊 Gambar 3: Perbandingan Sebaran Jenis Kekerasan")
    kekerasan_provinsi = df_filter.groupby("Provinsi")[jenis_kekerasan].sum().reset_index()
    kekerasan_long = kekerasan_provinsi.melt(
        id_vars="Provinsi", 
        value_vars=jenis_kekerasan, 
        var_name="Jenis Kekerasan", 
        value_name="Jumlah"
    )
    
    fig_bar = px.bar(
        kekerasan_long, 
        x="Provinsi", 
        y="Jumlah", 
        color="Jenis Kekerasan", 
        barmode="stack",
        template="gridon",
        color_discrete_sequence=["#1565C0", "#64B5F6", "#E53935", "#EF9A9A", "#9C27B0", "#81C784"]
    )
    fig_bar.update_layout(height=420, xaxis_title="Provinsi", yaxis_title="Jumlah Korban")
    st.plotly_chart(fig_bar, width="stretch", height=420)
    
    # --- REKAPAN DATA CSV UNTUK GAMBAR 3 ---
    st.markdown("#### 📋 Rekapan Data: Matriks Kasus Fisik Berdasarkan Kabupaten/Kota")
    if len(df_filter) > 0:
        pivot_wilayah_tahun = pd.pivot_table(
            data=df_filter, 
            values="Fisik", 
            index=["Kabupaten/Kota"], 
            columns="Tahun", 
            aggfunc='sum', 
            fill_value=0
        )
        st.write(pivot_wilayah_tahun.style.background_gradient(cmap="Reds"))
        
        # Tombol download CSV Gambar 3
        csv_g3 = pivot_wilayah_tahun.to_csv().encode('utf-8')
        st.download_button(label="📥 Unduh Matriks Wilayah Lintas Tahun (.csv)", data=csv_g3, file_name="Rekap_Matriks_Wilayah_Tahun.csv", mime="text/csv", key="download_g3")
    else:
        st.info("Data matriks kosong.")

with col4:
    st.subheader("🎯 Gambar 4: Hasil Klasterisasi Kerentanan (Scatter Plot)")
    fig_scatter = px.scatter(
        df_filter, 
        x="Fisik", 
        y="Psikis", 
        size="Total_Kasus", 
        color="Cluster_Label", 
        hover_name="Kabupaten/Kota",
        template="gridon",
        color_discrete_map={
            "Kerentanan Tinggi": "#E53935",
            "Kerentanan Sedang": "#FB8C00",
            "Kerentanan Relatif Rendah": "#2E7D32"
        }
    )
    fig_scatter.update_layout(
        height=420,
        xaxis=dict(title=dict(text="Jumlah Kasus Fisik", font=dict(size=12))),
        yaxis=dict(title=dict(text="Jumlah Kasus Psikis", font=dict(size=12)))
    )
    st.plotly_chart(fig_scatter, width="stretch")
    
    # --- REKAPAN DATA CSV UNTUK GAMBAR 4 ---
    st.markdown("#### 📋 Rekapan Data: Total Kasus Berdasarkan Hasil Klaster (Cluster)")
    if len(df_filter) > 0:
        summary_cluster = df_filter.groupby("Cluster_Label")["Total_Kasus"].sum().reset_index()
        summary_cluster = summary_cluster.rename(columns={"Cluster_Label": "ID Klaster / Label", "Total_Kasus": "Total Dampak Kasus"})
        summary_cluster = summary_cluster.sort_values(by="Total Dampak Kasus", ascending=False).reset_index(drop=True)
        st.dataframe(summary_cluster, width="stretch", height=150)
        
        # Tombol download CSV Gambar 4
        csv_g4 = summary_cluster.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Unduh Data Klaster (.csv)", data=csv_g4, file_name="Rekap_Hasil_Klasterisasi.csv", mime="text/csv", key="download_g4")
    else:
        st.info("Data klaster tidak ditemukan.")

st.divider()

# ==========================================
# 8. EXPANDER DETAIL RINGKASAN DATA & MATRIKS PIVOT
# ==========================================
st.subheader("📋 Detail Ringkasan Data & Sampel Matriks")

with st.expander("Lihat Sampel Tabel Kontribusi & Matriks Pivot Lintas Tahun"):
    kolom_sampel = ["Tahun", "Provinsi", "Kabupaten/Kota", "Fisik", "Psikis", "Seksual", "Cluster_Label"]
    st.markdown("**Sampel Data Terfilter:**")
    st.dataframe(df_filter[kolom_sampel].head(10), width="stretch")
    
    st.markdown("<br>**Matriks Pivot Jumlah Kasus Fisik Berdasarkan Kabupaten/Kota Lintas Tahun:**", unsafe_allow_html=True)
    if len(df_filter) > 0:
        pivot_wilayah_tahun_full = pd.pivot_table(
            data=df_filter, 
            values="Fisik", 
            index=["Kabupaten/Kota"], 
            columns="Tahun", 
            aggfunc='sum', 
            fill_value=0
        )
        st.write(pivot_wilayah_tahun_full.style.background_gradient(cmap="Reds"))

with st.expander("Lihat Seluruh Data Mentah Hasil Klasterisasi"):
    st.dataframe(df_filter, width="stretch", height=300)

# Penyediaan unduhan file data aktif utama (Gabungan Keseluruhan)
csv_data = df_filter.to_csv(index=False).encode('utf-8')
st.download_button(
    label='📥 Unduh Seluruh Dataset Hasil Klasterisasi Aktif (.csv)', 
    data=csv_data, 
    file_name="Dataset_Kekerasan_Perempuan_Terklaster.csv", 
    mime="text/csv",
    key="download_full_main"
)

# ==========================================
# 9. FOOTER KREDIT DOKUMENTASI
# ==========================================
st.markdown("---")
st.caption("""
Sumber Data: Hasil Pemrosesan Algoritma Klasterisasi K-Means berbasis Data SIMFONI PPA.  

*Dashboard Analitik Monitoring Kasus Kekerasan Tingkat Perempuan Dewasa di Pulau Jawa.*

Periode : 2022-2024.
""")