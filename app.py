import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime

# ─── SAYFA AYARLARI ───────────────────────────────────────────────
st.set_page_config(
    page_title="Finansal Asistan",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── NAVİGASYON STATE ─────────────────────────────────────────────
if "sayfa" not in st.session_state:
    st.session_state.sayfa = "anasayfa"

sayfa = st.session_state.sayfa

# ─── CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

* { font-family: 'Nunito', sans-serif !important; }

.stApp { background-color: #F2F5FA; }

.main .block-container {
    max-width: 460px !important;
    padding: 0 0.75rem 110px 0.75rem !important;
    margin: 0 auto;
}

h1 { font-size: 1.5rem !important; color: #1A1F36 !important; font-weight: 900 !important; margin-bottom: 0 !important; }
h2 { font-size: 1.15rem !important; color: #1A1F36 !important; font-weight: 800 !important; }
h3 { font-size: 0.95rem !important; color: #1A1F36 !important; font-weight: 700 !important; }

/* ── HEADER KARTI ── */
.header-card {
    background: linear-gradient(135deg, #1A73E8 0%, #0D47A1 100%);
    border-radius: 24px;
    padding: 24px 20px 28px 20px;
    margin-bottom: 16px;
    color: white;
    position: relative;
    overflow: hidden;
}
.header-card::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    background: rgba(255,255,255,0.07);
    border-radius: 50%;
}
.header-card::after {
    content: '';
    position: absolute;
    bottom: -60px; left: -20px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.header-title {
    font-size: 13px;
    font-weight: 700;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.header-amount {
    font-size: 2.6rem;
    font-weight: 900;
    line-height: 1.1;
    margin-bottom: 20px;
}
.header-row {
    display: flex;
    gap: 12px;
}
.header-pill {
    flex: 1;
    background: rgba(255,255,255,0.15);
    border-radius: 14px;
    padding: 10px 12px;
    backdrop-filter: blur(10px);
}
.header-pill-label {
    font-size: 11px;
    font-weight: 700;
    opacity: 0.75;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.header-pill-value {
    font-size: 1.1rem;
    font-weight: 900;
    margin-top: 2px;
}
.pill-green { color: #69F0AE; }
.pill-red   { color: #FF6B6B; }

/* ── RENKLİ KATEGORİ KARTLARI ── */
.section-title {
    font-size: 14px;
    font-weight: 800;
    color: #1A1F36;
    margin: 18px 0 10px 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.cat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 16px;
}
.cat-card {
    border-radius: 18px;
    padding: 16px 14px;
    color: white;
    position: relative;
    overflow: hidden;
    cursor: pointer;
}
.cat-card::after {
    content: '';
    position: absolute;
    bottom: -20px; right: -20px;
    width: 80px; height: 80px;
    background: rgba(255,255,255,0.12);
    border-radius: 50%;
}
.cat-icon { font-size: 1.6rem; margin-bottom: 8px; }
.cat-label { font-size: 11px; font-weight: 700; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px; }
.cat-amount { font-size: 1.25rem; font-weight: 900; margin-top: 2px; }

/* ── SON İŞLEMLER ── */
.txn-card {
    background: white;
    border-radius: 16px;
    padding: 12px 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.txn-icon {
    width: 42px; height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.txn-info { flex: 1; }
.txn-name { font-size: 13px; font-weight: 700; color: #1A1F36; }
.txn-date { font-size: 11px; color: #8A92A6; margin-top: 1px; }
.txn-amount { font-size: 14px; font-weight: 800; }

/* ── METRİK KARTLARI ── */
div[data-testid="metric-container"] {
    background: white !important;
    border-radius: 16px !important;
    padding: 14px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    border: none !important;
}
div[data-testid="metric-container"] label {
    font-size: 10px !important;
    color: #8A92A6 !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-size: 1.2rem !important;
    color: #1A1F36 !important;
    font-weight: 900 !important;
}

/* ── BUTONLAR ── */
.stButton > button {
    border-radius: 14px !important;
    font-weight: 800 !important;
    font-size: 14px !important;
    min-height: 50px !important;
    background: #1A73E8 !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(26,115,232,0.3) !important;
    transition: all 0.2s !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    background: #1557B0 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(26,115,232,0.4) !important;
}

/* ── FORM ELEMENTLERİ ── */
input, .stTextInput input, .stNumberInput input, textarea {
    font-size: 15px !important;
    border-radius: 12px !important;
    border: 2px solid #E8ECF4 !important;
    background: #ffffff !important;
    color: #1A1F36 !important;
    font-weight: 600 !important;
}
input:focus, .stTextInput input:focus {
    border-color: #1A73E8 !important;
    box-shadow: 0 0 0 3px rgba(26,115,232,0.1) !important;
}

.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 2px solid #E8ECF4 !important;
    background: white !important;
    font-weight: 600 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #E8ECF4 !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-size: 12px !important;
    font-weight: 800 !important;
    color: #8A92A6 !important;
    background: transparent !important;
    padding: 8px 12px !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #1A73E8 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

/* ── ALT NAV ── */
section[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"]   { display: none !important; }

div[data-testid="stBottom"] {
    background: white !important;
    border-top: 1px solid #E8ECF4 !important;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.08) !important;
    padding: 6px 0 10px 0 !important;
}
div[data-testid="stBottom"] .stButton > button {
    background: transparent !important;
    color: #8A92A6 !important;
    font-size: 9px !important;
    font-weight: 800 !important;
    min-height: 56px !important;
    border-radius: 0 !important;
    padding: 2px 4px !important;
    line-height: 1.4 !important;
    box-shadow: none !important;
    letter-spacing: 0.3px !important;
    text-transform: uppercase !important;
}
div[data-testid="stBottom"] .stButton > button:hover {
    background: #F2F5FA !important;
    color: #1A73E8 !important;
    transform: none !important;
}

.stDataFrame { border-radius: 14px !important; overflow: hidden !important; }
.stAlert { border-radius: 14px !important; font-size: 13px !important; font-weight: 600 !important; }

/* Form arka planı */
div[data-testid="stForm"] {
    background: white !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    border: none !important;
}

div[data-testid="stRadio"] label {
    font-weight: 700 !important;
    font-size: 14px !important;
}

hr { border-color: #E8ECF4 !important; margin: 16px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── VERİ YÖNETİMİ ────────────────────────────────────────────────
DATA_FILE = "butce_veritabaniniz.json"

KATEGORI_RENK = {
    "Market":               {"bg": "linear-gradient(135deg,#FF6B6B,#EE0979)", "icon": "🛒"},
    "Fatura":               {"bg": "linear-gradient(135deg,#F7971E,#FFD200)", "icon": "💡"},
    "Akaryakıt":            {"bg": "linear-gradient(135deg,#11998E,#38EF7D)", "icon": "⛽"},
    "Eğitim":               {"bg": "linear-gradient(135deg,#4776E6,#8E54E9)", "icon": "📚"},
    "Giyim":                {"bg": "linear-gradient(135deg,#F953C6,#B91D73)", "icon": "👗"},
    "Yemek":                {"bg": "linear-gradient(135deg,#FF8008,#FFC837)", "icon": "🍽️"},
    "Araç Bakım-Vergi":     {"bg": "linear-gradient(135deg,#2C3E50,#4CA1AF)", "icon": "🚗"},
    "İlaç":                 {"bg": "linear-gradient(135deg,#1D976C,#93F9B9)", "icon": "💊"},
    "Kredi Kartı Geçmiş Borç": {"bg": "linear-gradient(135deg,#C94B4B,#4B134F)", "icon": "💳"},
}

KİŞİ_RENK = {
    "Burak":   "#1A73E8",
    "Kerime":  "#E91E8C",
    "Ece":     "#FF6B35",
    "Berkay":  "#11998E",
    "Genel":   "#8E54E9",
}

@st.cache_data(ttl=300)
def veri_yukle():
    if not os.path.exists(DATA_FILE):
        return {"gelirler": [], "giderler": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def veri_kaydet(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    st.cache_data.clear()

def df_hazirla(data):
    ay = {1:"Oca",2:"Şub",3:"Mar",4:"Nis",5:"May",6:"Haz",
          7:"Tem",8:"Ağu",9:"Eyl",10:"Eki",11:"Kas",12:"Ara"}
    df_g  = pd.DataFrame(data.get("gelirler", []))
    df_gi = pd.DataFrame(data.get("giderler", []))
    if not df_gi.empty:
        df_gi['tarih_dt'] = pd.to_datetime(df_gi['tarih'], format='%d.%m.%Y', errors='coerce')
        df_gi['Yıl']    = df_gi['tarih_dt'].dt.year.fillna(datetime.now().year).astype(int)
        df_gi['Ay_No']  = df_gi['tarih_dt'].dt.month.fillna(datetime.now().month).astype(int)
        df_gi['Ay']     = df_gi['Ay_No'].map(ay)
        df_gi['Ay-Yıl'] = df_gi['Ay'] + " " + df_gi['Yıl'].astype(str)
    return df_g, df_gi

app_data = veri_yukle()
df_gelir, df_gider = df_hazirla(app_data)

toplam_gelir = df_gelir['tutar'].sum() if not df_gelir.empty else 0
toplam_gider = df_gider['tutar'].sum() if not df_gider.empty else 0
net_durum    = toplam_gelir - toplam_gider

CHART = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#1A1F36',
    margin=dict(l=0, r=0, t=36, b=0),
    legend=dict(bgcolor='rgba(255,255,255,0.9)', bordercolor='#E8ECF4', borderwidth=1),
)

# ═══════════════════════════════════════════════════════
# SAYFALAR
# ═══════════════════════════════════════════════════════

if sayfa == "anasayfa":
    # Header kartı
    net_renk = "#69F0AE" if net_durum >= 0 else "#FF6B6B"
    st.markdown(f"""
    <div class="header-card">
        <div class="header-title">💰 Toplam Bakiye</div>
        <div class="header-amount">₺{net_durum:,.0f}</div>
        <div class="header-row">
            <div class="header-pill">
                <div class="header-pill-label">📈 Gelir</div>
                <div class="header-pill-value pill-green">₺{toplam_gelir:,.0f}</div>
            </div>
            <div class="header-pill">
                <div class="header-pill-label">📉 Gider</div>
                <div class="header-pill-value pill-red">₺{toplam_gider:,.0f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hızlı işlem butonları
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕  Gider Ekle", use_container_width=True):
            st.session_state.sayfa = "ekle"; st.rerun()
    with c2:
        if st.button("📈  Analizi Gör", use_container_width=True):
            st.session_state.sayfa = "analiz"; st.rerun()

    # Kategorilere göre harcama kartları
    if not df_gider.empty:
        st.markdown('<div class="section-title">📂 Kategoriler</div>', unsafe_allow_html=True)
        kat_ozet = df_gider.groupby('kategori')['tutar'].sum().to_dict()

        cards_html = '<div class="cat-grid">'
        for kat, bilgi in KATEGORI_RENK.items():
            tutar = kat_ozet.get(kat, 0)
            if tutar > 0:
                cards_html += f"""
                <div class="cat-card" style="background:{bilgi['bg']}">
                    <div class="cat-icon">{bilgi['icon']}</div>
                    <div class="cat-label">{kat}</div>
                    <div class="cat-amount">₺{tutar:,.0f}</div>
                </div>"""
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

        # Son işlemler
        st.markdown('<div class="section-title">🕐 Son İşlemler</div>', unsafe_allow_html=True)
        son = df_gider.sort_values('tarih_dt', ascending=False).head(5)
        txn_html = ''
        for _, row in son.iterrows():
            kat = row.get('kategori', 'Genel')
            bilgi = KATEGORI_RENK.get(kat, {"bg": "linear-gradient(135deg,#667eea,#764ba2)", "icon": "💸"})
            kisi = row.get('kisi', '')
            kisi_renk = KİŞİ_RENK.get(kisi, '#8A92A6')
            txn_html += f"""
            <div class="txn-card">
                <div class="txn-icon" style="background:{bilgi['bg']}">{bilgi['icon']}</div>
                <div class="txn-info">
                    <div class="txn-name">{kat}</div>
                    <div class="txn-date">{row.get('tarih','')} · <span style="color:{kisi_renk};font-weight:800">{kisi}</span></div>
                </div>
                <div class="txn-amount" style="color:#EE0979">-₺{row['tutar']:,.0f}</div>
            </div>"""
        st.markdown(txn_html, unsafe_allow_html=True)
    else:
        st.info("Henüz harcama kaydı yok. ➕ Gider Ekle butonuyla başlayabilirsin!")

elif sayfa == "ozet":
    st.markdown("## 📊 Finansal Özet")

    # Bakiye kartı
    net_renk = "#1D976C" if net_durum >= 0 else "#C94B4B"
    st.markdown(f"""
    <div class="header-card" style="background:linear-gradient(135deg,{net_renk},{net_renk}99)">
        <div class="header-title">Net Bakiye</div>
        <div class="header-amount">₺{net_durum:,.0f}</div>
        <div class="header-row">
            <div class="header-pill">
                <div class="header-pill-label">📈 Gelir</div>
                <div class="header-pill-value" style="color:#69F0AE">₺{toplam_gelir:,.0f}</div>
            </div>
            <div class="header-pill">
                <div class="header-pill-label">📉 Gider</div>
                <div class="header-pill-value" style="color:#FF6B6B">₺{toplam_gider:,.0f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not df_gider.empty:
        # Gelir/Gider karşılaştırma gauge
        if toplam_gelir > 0:
            harcama_oran = min(toplam_gider / toplam_gelir * 100, 100)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=harcama_oran,
                title={'text': "Bütçe Kullanımı %", 'font': {'size': 14, 'color': '#1A1F36', 'family': 'Nunito'}},
                delta={'reference': 80, 'increasing': {'color': "#EE0979"}, 'decreasing': {'color': "#1D976C"}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#8A92A6'},
                    'bar': {'color': "#1A73E8", 'thickness': 0.25},
                    'bgcolor': "white",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 60],  'color': '#E8F5E9'},
                        {'range': [60, 80], 'color': '#FFF8E1'},
                        {'range': [80, 100],'color': '#FFEBEE'},
                    ],
                    'threshold': {'line': {'color': "#EE0979", 'width': 3}, 'thickness': 0.75, 'value': 80}
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=220,
                margin=dict(l=20, r=20, t=40, b=10),
                font={'family': 'Nunito'}
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        # Top 5 kategori
        kat_ozet = df_gider.groupby('kategori')['tutar'].sum().nlargest(5).reset_index()
        renkler = [KATEGORI_RENK.get(k, {}).get("bg", "linear-gradient(135deg,#667eea,#764ba2)") for k in kat_ozet['kategori']]
        bar_renkler = ["#FF6B6B","#F7971E","#1A73E8","#11998E","#8E54E9"]

        fig = px.bar(kat_ozet, x='tutar', y='kategori', orientation='h',
                     title="Top 5 Harcama Kategorisi",
                     labels={'tutar': '₺', 'kategori': ''})
        fig.update_traces(marker_color=bar_renkler[:len(kat_ozet)], marker_line_width=0,
                          text=[f"₺{v:,.0f}" for v in kat_ozet['tutar']],
                          textposition='outside', textfont=dict(size=11, color='#1A1F36', family='Nunito'))
        fig.update_layout(**CHART, height=270,
                          font=dict(family='Nunito'),
                          title_font=dict(size=13, color='#1A1F36', family='Nunito'))
        fig.update_xaxes(gridcolor='#E8ECF4', tickfont=dict(color='#8A92A6', family='Nunito'))
        fig.update_yaxes(gridcolor='rgba(0,0,0,0)', tickfont=dict(color='#1A1F36', family='Nunito'))
        st.plotly_chart(fig, use_container_width=True)

        # Son 5 harcama tablosu
        st.markdown('<div class="section-title">Son 5 Harcama</div>', unsafe_allow_html=True)
        son = df_gider[['tarih','kisi','kategori','tutar']].sort_values('tarih', ascending=False).head(5)
        st.dataframe(son, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz harcama kaydı yok.")

elif sayfa == "ekle":
    st.markdown("## ➕ Yeni İşlem")
    tur = st.radio("İşlem türü", ["💸 Gider", "💰 Gelir"], horizontal=True)
    st.markdown("---")

    if tur == "💸 Gider":
        with st.form("gider_form", clear_on_submit=True):
            tutar    = st.number_input("💵 Tutar (₺)", min_value=0.0, step=50.0)
            kisi     = st.selectbox("👤 Kişi", ["Burak","Kerime","Ece","Berkay","Genel"])
            kategori = st.selectbox("📂 Kategori", list(KATEGORI_RENK.keys()))
            aciklama = st.text_input("📝 Açıklama (isteğe bağlı)")
            tarih    = st.date_input("📅 Tarih")
            if st.form_submit_button("💾  Kaydet", use_container_width=True):
                if tutar > 0:
                    app_data["giderler"].append({
                        "tutar": tutar, "kisi": kisi, "kategori": kategori,
                        "aciklama": aciklama or "Belirtilmedi",
                        "tarih": tarih.strftime("%d.%m.%Y")
                    })
                    veri_kaydet(app_data)
                    st.success("✅ Gider başarıyla kaydedildi!")
                    st.balloons()
                else:
                    st.error("⚠️ Lütfen geçerli bir tutar giriniz.")
    else:
        with st.form("gelir_form", clear_on_submit=True):
            tutar    = st.number_input("💵 Tutar (₺)", min_value=0.0, step=100.0)
            aciklama = st.text_input("📝 Açıklama (Maaş, Prim vb.)")
            tarih    = st.date_input("📅 Tarih")
            if st.form_submit_button("💾  Kaydet", use_container_width=True):
                if tutar > 0:
                    app_data["gelirler"].append({
                        "tutar": tutar,
                        "aciklama": aciklama or "Belirtilmedi",
                        "tarih": tarih.strftime("%d.%m.%Y")
                    })
                    veri_kaydet(app_data)
                    st.success("✅ Gelir başarıyla kaydedildi!")
                    st.balloons()
                else:
                    st.error("⚠️ Lütfen geçerli bir tutar giriniz.")

elif sayfa == "analiz":
    st.markdown("## 📈 Analiz")

    if df_gider.empty:
        st.warning("⚠️ Analiz için önce gider verisi giriniz.")
    else:
        tab1, tab2, tab3 = st.tabs(["📅 Aylık", "📂 Kategori", "👤 Kişi"])

        with tab1:
            aylik = df_gider.groupby(['Yıl','Ay_No','Ay-Yıl'])['tutar'].sum().reset_index()
            aylik = aylik.sort_values(['Yıl','Ay_No'])
            renkler_aylik = ["#1A73E8","#4285F4","#669DF6","#A8C7FA"] * 12
            fig = px.bar(aylik, x='Ay-Yıl', y='tutar',
                         title="Aylık Harcama", labels={'tutar':'₺','Ay-Yıl':''})
            fig.update_traces(marker_color='#1A73E8', marker_line_width=0,
                              text=[f"₺{v:,.0f}" for v in aylik['tutar']],
                              textposition='outside', textfont=dict(size=10, color='#1A1F36', family='Nunito'))
            fig.update_layout(**CHART, height=320, xaxis_tickangle=-45,
                              font=dict(family='Nunito'),
                              title_font=dict(size=13, color='#1A1F36', family='Nunito'))
            fig.update_xaxes(gridcolor='#E8ECF4')
            fig.update_yaxes(gridcolor='#E8ECF4')
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            kat = df_gider.groupby('kategori')['tutar'].sum().reset_index()
            pie_renkler = ["#FF6B6B","#F7971E","#FFD200","#1A73E8","#11998E","#8E54E9","#F953C6","#4776E6","#C94B4B"]
            fig2 = px.pie(kat, values='tutar', names='kategori',
                          title="Kategori Dağılımı", hole=0.45,
                          color_discrete_sequence=pie_renkler)
            fig2.update_traces(textfont=dict(size=11, family='Nunito'),
                               pull=[0.03]*len(kat))
            fig2.update_layout(**CHART, height=340,
                               font=dict(family='Nunito'),
                               title_font=dict(size=13, color='#1A1F36', family='Nunito'))
            st.plotly_chart(fig2, use_container_width=True)

            fig3 = px.sunburst(df_gider, path=['kategori','kisi'], values='tutar',
                               title="Kategori & Kişi Detayı",
                               color_discrete_sequence=pie_renkler)
            fig3.update_layout(**CHART, height=340,
                               font=dict(family='Nunito'),
                               title_font=dict(size=13, color='#1A1F36', family='Nunito'))
            st.plotly_chart(fig3, use_container_width=True)

        with tab3:
            kisi_renkler = [KİŞİ_RENK.get(k, '#8A92A6') for k in df_gider.groupby('kisi')['tutar'].sum().sort_values().index]
            kisi = df_gider.groupby('kisi')['tutar'].sum().reset_index()
            fig4 = px.bar(kisi.sort_values('tutar'), x='tutar', y='kisi',
                          orientation='h', title="Kişi Bazlı Harcama",
                          labels={'tutar':'₺','kisi':''},
                          color='kisi',
                          color_discrete_map=KİŞİ_RENK)
            fig4.update_traces(marker_line_width=0,
                               text=[f"₺{v:,.0f}" for v in kisi.sort_values('tutar')['tutar']],
                               textposition='outside', textfont=dict(size=11, color='#1A1F36', family='Nunito'))
            fig4.update_layout(**CHART, height=300, showlegend=False,
                               font=dict(family='Nunito'),
                               title_font=dict(size=13, color='#1A1F36', family='Nunito'))
            fig4.update_xaxes(gridcolor='#E8ECF4')
            st.plotly_chart(fig4, use_container_width=True)

            kisi_ay = df_gider.groupby(['Ay-Yıl','kisi','Yıl','Ay_No'])['tutar'].sum().reset_index()
            kisi_ay = kisi_ay.sort_values(['Yıl','Ay_No'])
            fig5 = px.line(kisi_ay, x='Ay-Yıl', y='tutar', color='kisi',
                           markers=True, title="Aylık Kişi Trendi",
                           labels={'tutar':'₺','Ay-Yıl':''},
                           color_discrete_map=KİŞİ_RENK)
            fig5.update_traces(line_width=2.5, marker_size=7)
            fig5.update_layout(**CHART, height=320, xaxis_tickangle=-45,
                               font=dict(family='Nunito'),
                               title_font=dict(size=13, color='#1A1F36', family='Nunito'))
            fig5.update_xaxes(gridcolor='#E8ECF4')
            fig5.update_yaxes(gridcolor='#E8ECF4')
            st.plotly_chart(fig5, use_container_width=True)

elif sayfa == "duzenle":
    st.markdown("## ⚙️ Veri Yönetimi")
    st.info("💡 Hücreye tıklayıp düzenleyin, satır seçip Delete tuşuyla silin.")

    st.markdown("### 📉 Gider Kayıtları")
    if not df_gider.empty:
        gider_saf = df_gider[['tarih','kisi','kategori','aciklama','tutar']]
        edited_g = st.data_editor(gider_saf, num_rows="dynamic",
                                  use_container_width=True, key="ed_gider")
        if st.button("💾  Giderleri Kaydet", type="primary", use_container_width=True):
            app_data["giderler"] = edited_g.to_dict('records')
            veri_kaydet(app_data)
            st.success("✅ Güncellendi!")
            st.rerun()
    else:
        st.write("Kayıt yok.")

    st.markdown("---")
    st.markdown("### 📈 Gelir Kayıtları")
    if not df_gelir.empty:
        edited_gelir = st.data_editor(df_gelir, num_rows="dynamic",
                                      use_container_width=True, key="ed_gelir")
        if st.button("💾  Gelirleri Kaydet", type="primary", use_container_width=True):
            app_data["gelirler"] = edited_gelir.to_dict('records')
            veri_kaydet(app_data)
            st.success("✅ Güncellendi!")
            st.rerun()
    else:
        st.write("Kayıt yok.")

# ═══════════════════════════════════════════════════════
# ALT NAVİGASYON
# ═══════════════════════════════════════════════════════
aktif = st.session_state.sayfa

try:
    bottom = st.bottom()
except AttributeError:
    bottom = st.container()

with bottom:
    nav_cols = st.columns(5)
    nav_items = [
        ("anasayfa", "🏠", "Ana"),
        ("ozet",     "📊", "Özet"),
        ("ekle",     "➕", "Ekle"),
        ("analiz",   "📈", "Analiz"),
        ("duzenle",  "⚙️", "Düzenle"),
    ]
    for col, (key, icon, label) in zip(nav_cols, nav_items):
        with col:
            btn_label = f"**{icon}**\n{label}" if aktif == key else f"{icon}\n{label}"
            if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
                st.session_state.sayfa = key
                st.rerun()
