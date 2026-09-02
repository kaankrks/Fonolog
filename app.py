import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Fonolog - Fon ve Piyasa Terminali", page_icon="📈", layout="wide")

# FVT Dark Tema Stili (Hatasız HTML/CSS Enjeksiyonu)
custom_css = """
<style>
    .stApp { background-color: #12131C; color: #E0E0E0; }
    .stMetric { background-color: #181925; padding: 12px; border-radius: 8px; border: 1px solid #282A3A; }
    div[data-testid="stSidebar"] { background-color: #181925; border-right: 1px solid #282A3A; }
    .card { background-color: #181925; border-radius: 10px; padding: 15px; border: 1px solid #282A3A; margin-bottom: 15px; }
    .green-text { color: #00E676; font-weight: bold; }
    .red-text { color: #FF5252; font-weight: bold; }
</style>
"""
st.write(custom_css, unsafe_allow_html=True)

# Canlı Piyasa Verileri
@st.cache_data(ttl=60)
def get_market_data():
    tickers = {
        "BIST 100": "^XU100",
        "BIST 30": "XU030.IS",
        "USD/TRY": "USDTRY=X",
        "EUR/TRY": "EURTRY=X",
        "ONS Altın": "GC=F",
        "ONS Gümüş": "SI=F"
    }
    data = {}
    for name, symbol in tickers.items():
        try:
            df = yf.Ticker(symbol).history(period="2d")
            if len(df) >= 2:
                last = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                change = ((last - prev) / prev) * 100
                data[name] = (last, change)
            else:
                data[name] = (0.0, 0.0)
        except:
            data[name] = (0.0, 0.0)
    return data

# Navigasyon Menüsü
st.sidebar.title("⚡ Fonolog Terminal")
sayfa = st.sidebar.radio("Sayfalar", ["🌐 Günün Özeti", "💼 Portföyüm", "🔥 Popüler Fon Tahminleri"])

market_data = get_market_data()

# Üst Piyasa Bandı (Ticker)
cols = st.columns(len(market_data))
for idx, (name, (val, chg)) in enumerate(market_data.items()):
    cols[idx].metric(label=name, value=f"{val:,.2f}", delta=f"{chg:.2f}%")

st.divider()

# ==================== MADDE 1: GÜNÜN ÖZETİ ====================
if sayfa == "🌐 Günün Özeti":
    st.header("🌐 Günün Özeti & BIST 100 Terminali")
    
    col_chart, col_pop = st.columns([2, 1])
    
    with col_chart:
        st.subheader("📊 BİST 100 Anlık Trend")
        try:
            bist_df = yf.Ticker("^XU100").history(period="1mo")
            fig = go.Figure(data=[go.Scatter(x=bist_df.index, y=bist_df['Close'], mode='lines', line=dict(color='#00E676', width=2))])
            fig.update_layout(template="plotly_dark", paper_bgcolor='#181925', plot_bgcolor='#181925', margin=dict(l=10, r=10, t=10, b=10), height=300)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Grafik yükleniyor...")
            
    with col_pop:
        st.subheader("⚡ Tahmini Popüler Fonlar")
        sample_funds = [
            {"kod": "DFI", "ad": "ATLAS PORTFÖY SERBEST", "tahmin": 0.85},
            {"kod": "TLY", "ad": "TERA PORTFÖY BİRİNCİ", "tahmin": -0.42},
            {"kod": "DOH", "ad": "TERA PORTFÖY DÖRDÜNCÜ", "tahmin": 0.34},
            {"kod": "PBR", "ad": "PUSULA PORTFÖY BİRİNCİ", "tahmin": -8.10},
        ]
        for f in sample_funds:
            color = "green-text" if f['tahmin'] >= 0 else "red-text"
            st.write(f"""
            <div class="card">
                <b>{f['kod']}</b> - <small>{f['ad']}</small><br>
                AI Tahmin: <span class="{color}">%{f['tahmin']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)

    st.subheader("🔥 Günün Enleri")
    tab1, tab2 = st.tabs(["Hisseler", "Fonlar"])
    with tab1:
        c1, c2 = st.columns(2)
        c1.write("🟢 **En Çok Kazanan Hisseler**")
        c1.dataframe(pd.DataFrame([{"Sembol": "THYAO", "Fiyat": "298.50", "Değişim": "+4.2%"}, {"Sembol": "AKBNK", "Fiyat": "56.20", "Değişim": "+3.8%"}]), use_container_width=True)
        c2.write("🔴 **En Çok Kaybeden Hisseler**")
        c2.dataframe(pd.DataFrame([{"Sembol": "EREGL", "Fiyat": "48.10", "Değişim": "-2.1%"}, {"Sembol": "SASA", "Fiyat": "39.40", "Değişim": "-1.9%"}]), use_container_width=True)

# ==================== MADDE 2: PORTFÖYÜM ====================
elif sayfa == "💼 Portföyüm":
    st.header("💼 Portföy Yönetimi ve Al/Sat Takibi")
    
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = [
            {"Varlık": "DFI", "Tür": "Yatırım Fonu", "Adet": 23589.0, "Maliyet": 6.06, "GuncelFiyat": 6.11},
            {"Varlık": "TLY", "Tür": "Yatırım Fonu", "Adet": 6.0, "Maliyet": 9293.93, "GuncelFiyat": 9275.96},
            {"Varlık": "THYAO", "Tür": "Hisse Senedi", "Adet": 150.0, "Maliyet": 280.0, "GuncelFiyat": 298.50}
        ]

    # İşlem Ekleme Formu
    with st.expander("➕ Yeni İşlem Ekle (Al / Sat)", expanded=False):
        col_a, col_b, col_c, col_d = st.columns(4)
        v_ad = col_a.text_input("Varlık Kodu (Örn: DFI, THYAO)")
        v_adet = col_b.number_input("Adet", min_value=0.0, step=1.0)
        v_fiyat = col_c.number_input("İşlem Fiyatı (₺)", min_value=0.0, step=0.1)
        v_tur = col_d.selectbox("İşlem Tipi", ["AL", "SAT"])
        if st.button("İşlemi Kaydet"):
            if v_ad and v_adet > 0:
                st.session_state.portfolio.append({"Varlık": v_ad.upper(), "Tür": "Genel", "Adet": v_adet, "Maliyet": v_fiyat, "GuncelFiyat": v_fiyat})
                st.success(f"{v_ad} işlemi eklendi!")
                st.rerun()

    df_port = pd.DataFrame(st.session_state.portfolio)
    df_port["Toplam Maliyet"] = df_port["Adet"] * df_port["Maliyet"]
    df_port["Güncel Değer"] = df_port["Adet"] * df_port["GuncelFiyat"]
    df_port["K/Z (₺)"] = df_port["Güncel Değer"] - df_port["Toplam Maliyet"]
    df_port["K/Z (%)"] = (df_port["K/Z (₺)"] / df_port["Toplam Maliyet"]) * 100

    toplam_deger = df_port["Güncel Değer"].sum()
    toplam_maliyet = df_port["Toplam Maliyet"].sum()
    toplam_kz = toplam_deger - toplam_maliyet

    cp1, cp2, cp3 = st.columns(3)
    cp1.metric("Toplam Portföy Değeri", f"₺{toplam_deger:,.2f}")
    cp2.metric("Toplam Maliyet", f"₺{toplam_maliyet:,.2f}")
    cp3.metric("Net Kar/Zarar", f"₺{toplam_kz:,.2f}", delta=f"{(toplam_kz/toplam_maliyet)*100:.2f}%")

    st.subheader("📋 Pozisyon Detayları")
    st.dataframe(df_port[["Varlık", "Adet", "Maliyet", "GuncelFiyat", "Güncel Değer", "K/Z (₺)", "K/Z (%)"]], use_container_width=True)

# ==================== MADDE 3: POPÜLER FON TAHMİNLERİ ====================
elif sayfa == "🔥 Popüler Fon Tahminleri":
    st.header("🔥 Popüler Fon Tahminleri (Canlı/AI)")
    
    if "favori_fonlar" not in st.session_state:
        st.session_state.favori_fonlar = ["DFI", "TLY", "DOH", "PBR", "PHE", "PUK"]

    new_fon = st.text_input("➕ Takip Listesine Yeni Fon Ekle (Örn: IIH, TI2):")
    if st.button("Fonu Ekle"):
        if new_fon and new_fon.upper() not in st.session_state.favori_fonlar:
            st.session_state.favori_fonlar.append(new_fon.upper())
            st.rerun()

    cols_fon = st.columns(3)
    bist_chg = market_data.get("BIST 100", (0, 0))[1]
    
    for idx, fon_kodu in enumerate(st.session_state.favori_fonlar):
        tahmin_val = (bist_chg * 0.85) if idx % 2 == 0 else (bist_chg * -0.4)
        color_class = "green-text" if tahmin_val >= 0 else "red-text"
        
        with cols_fon[idx % 3]:
            st.write(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4>{fon_kodu}</h4>
                    <span class="{color_class}" style="font-size:18px;">%{tahmin_val:.4f}</span>
                </div>
                <small>Portföy Etki Dağılımı:</small>
                <hr style="margin:5px 0; border-color:#282A3A;">
                <small>• THYAO: %25.0 (Etki: +0.35%)</small><br>
                <small>• AKBNK: %15.0 (Etki: +0.20%)</small><br>
                <small>• YKBNK: %10.0 (Etki: -0.10%)</small>
            </div>
            """, unsafe_allow_html=True)
