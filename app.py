import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from datetime import datetime

st.set_page_config(
    page_title="Finansal Asistan",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def supabase_baglanti():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SECRET_KEY"]
    return create_client(url, key)

supabase = supabase_baglanti()

if "sayfa" not in st.session_state:
    st.session_state.sayfa = "anasayfa"
if "user" not in st.session_state:
    st.session_state.user = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
* { font-family: 'Nunito', sans-serif !important; }
.stApp { background-color: #F2F5FA; }
.main .block-container { max-width: 460px !important; padding: 0 0.75rem 110px 0.75rem !important; margin: 0 auto; }
h1 { font-size: 1.5rem !important; color: #1A1F36 !important; font-weight: 900 !important; margin-bottom: 0 !important; }
h2 { font-size: 1.15rem !important; color: #1A1F36 !important; font-weight: 800 !important; }
h3 { font-size: 0.95rem !important; color: #1A1F36 !important; font-weight: 700 !important; }
.header-card { background: linear-gradient(135deg, #1A73E8 0%, #0D47A1 100%); border-radius: 24px; padding: 24px 20px 28px 20px; margin-bottom: 16px; color: white; position: relative; overflow: hidden; }
.header-card::before { content: ''; position: absolute; top: -40px; right: -40px; width: 160px; height: 160px; background: rgba(255,255,255,0.07); border-radius: 50%; }
.header-card::after { content: ''; position: absolute; bottom: -60px; left: -20px; width: 200px; height: 200px; background: rgba(255,255,255,0.05); border-radius: 50%; }
.header-title { font-size: 13px; font-weight: 700; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.header-amount { font-size: 2.6rem; font-weight: 900; line-height: 1.1; margin-bottom: 20px; }
.header-row { display: flex; gap: 12px; }
.header-pill { flex: 1; background: rgba(255,255,255,0.15); border-radius: 14px; padding: 10px 12px; }
.header-pill-label { font-size: 11px; font-weight: 700; opacity: 0.75; text-transform: uppercase; letter-spacing: 0.5px; }
.header-pill-value { font-size: 1.1rem; font-weight: 900; margin-top: 2px; }
.pill-green { color: #69F0AE; }
.pill-red { color: #FF6B6B; }
.section-title { font-size: 13px; font-weight: 800; color: #8A92A6; margin: 18px 0 10px 2px; text-transform: uppercase; letter-spacing: 0.8px; }
.cat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }
.cat-card { border-radius: 18px; padding: 16px 14px; color: white; position: relative; overflow: hidden; }
.cat-card::after { content: ''; position: absolute; bottom: -20px; right: -20px; width: 80px; height: 80px; background: rgba(255,255,255,0.12); border-radius: 50%; }
.cat-icon { font-size: 1.6rem; margin-bottom: 8px; }
.cat-label { font-size: 11px; font-weight: 700; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px; }
.cat-amount { font-size: 1.2rem; font-weight: 900; margin-top: 2px; }
.txn-card { background: white; border-radius: 16px; padding: 12px 14px; margin-bottom: 8px; display: flex; align-items: center; gap: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.txn-icon { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0; }
.txn-info { flex: 1; }
.txn-name { font-size: 13px; font-weight: 700; color: #1A1F36; }
.txn-date { font-size: 11px; color: #8A92A6; margin-top: 1px; }
.txn-amount { font-size: 14px; font-weight: 800; color: #EE0979; }
div[data-testid="metric-container"] { background: white !important; border-radius: 16px !important; padding: 14px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important; border: none !important; }
div[data-testid="metric-container"] label { font-size: 10px !important; color: #8A92A6 !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 1.2rem !important; color: #1A1F36 !important; font-weight: 900 !important; }
.stButton > button { border-radius: 14px !important; font-weight: 800 !important; font-size: 14px !important; min-height: 50px !important; background: #1A73E8 !important; color: white !important; border: none !important; box-shadow: 0 4px 15px rgba(26,115,232,0.3) !important; transition: all 0.2s !important; }
.stButton > button:hover { background: #1557B0 !important; transform: translateY(-1px) !important; }
input, .stTextInput input, .stNumberInput input { font-size: 15px !important; border-radius: 12px !important; border: 2px solid #E8ECF4 !important; background: #ffffff !important; color: #1A1F36 !important; font-weight: 600 !important; }
.stSelectbox > div > div { border-radius: 12px !important; border: 2px solid #E8ECF4 !important; background: white !important; font-weight: 600 !important; }
div[data-testid="stForm"] { background: white !important; border-radius: 20px !important; padding: 20px !important; box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important; border: none !important; }
.stTabs [data-baseweb="tab-list"] { background: #E8ECF4 !important; border-radius: 14px !important; padding: 4px !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { border-radius: 10px !important; font-size: 12px !important; font-weight: 800 !important; color: #8A92A6 !important; background: transparent !important; padding: 8px 12px !important; }
.stTabs [aria-selected="true"] { background: white !important; color: #1A73E8 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important; }
section[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
div[data-testid="stBottom"] { background: white !important; border-top: 1px solid #E8ECF4 !important; box-shadow: 0 -4px 20px rgba(0,0,0,0.08) !important; padding: 6px 0 10px 0 !important; }
div[data-testid="stBottom"] .stButton > button { background: transparent !important; color: #8A92A6 !important; font-size: 9px !important; font-weight: 800 !important; min-height: 56px !important; border-radius: 0 !important; padding: 2px 4px !important; line-height: 1.4 !important; box-shadow: none !important; text-transform: uppercase !important; }
div[data-testid="stBottom"] .stButton > button:hover { background: #F2F5FA !important; color: #1A73E8 !important; transform: none !important; }
.stDataFrame { border-radius: 14px !important; overflow: hidden !important; }
.stAlert { border-radius: 14px !important; font-size: 13px !important; font-weight: 600 !important; }
hr { border-color: #E8ECF4 !important; margin: 16px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── SABİTLER ─────────────────────────────────────────────────────
VARSAYILAN_KATEGORILER = [
    "Eğitim","Akaryakıt","Fatura","Market","Giyim",
    "Yemek","Araç Bakım-Vergi","İlaç","Kredi Kartı Geçmiş Borç"
]

VARSAYILAN_KİŞİLER = ["Genel"]

KAT_GRADYANLAR = [
    "linear-gradient(135deg,#4776E6,#8E54E9)",
    "linear-gradient(135deg,#11998E,#38EF7D)",
    "linear-gradient(135deg,#F7971E,#FFD200)",
    "linear-gradient(135deg,#FF6B6B,#EE0979)",
    "linear-gradient(135deg,#F953C6,#B91D73)",
    "linear-gradient(135deg,#FF8008,#FFC837)",
    "linear-gradient(135deg,#2C3E50,#4CA1AF)",
    "linear-gradient(135deg,#1D976C,#93F9B9)",
    "linear-gradient(135deg,#C94B4B,#4B134F)",
    "linear-gradient(135deg,#667eea,#764ba2)",
    "linear-gradient(135deg,#f093fb,#f5576c)",
    "linear-gradient(135deg,#4facfe,#00f2fe)",
]

KAT_İKONLAR = ["📚","⛽","💡","🛒","👗","🍽️","🚗","💊","💳","💰","🎯","🏠","✈️","🎮","💻","👶","🐾","🎵"]

KİŞİ_RENKLER = ["#1A73E8","#E91E8C","#FF6B35","#11998E","#8E54E9","#F7971E","#C94B4B","#4776E6"]

CHART = dict(
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font_color='#1A1F36', margin=dict(l=0, r=0, t=36, b=0),
    legend=dict(bgcolor='rgba(255,255,255,0.9)', bordercolor='#E8ECF4', borderwidth=1),
)

# ─── SUPABASE TABLO KURULUMU ──────────────────────────────────────
def tablolari_kur():
    # Bu fonksiyon ilk girişte Supabase'de profil tablosunu kontrol eder
    pass

# ─── VERİ FONKSİYONLARI ──────────────────────────────────────────
@st.cache_data
def kisiler_yukle(user_id):
    try:
        res = supabase.table("kisiler").select("*").eq("user_id", user_id).execute()
        kisiler = [r["ad"] for r in res.data] if res.data else []
        if not kisiler:
            return VARSAYILAN_KİŞİLER
        return kisiler
    except:
        return VARSAYILAN_KİŞİLER

@st.cache_data
def kategoriler_yukle(user_id):
    try:
        res = supabase.table("kategoriler").select("*").eq("user_id", user_id).order("ad").execute()
        if res.data:
            return res.data  # [{"ad":..., "ikon":..., "renk_index":...}]
        return []
    except:
        return []

@st.cache_data
def veri_yukle(user_id):
    try:
        g  = supabase.table("gelirler").select("*").eq("user_id", user_id).execute()
        gi = supabase.table("giderler").select("*").eq("user_id", user_id).execute()
        return g.data or [], gi.data or []
    except:
        return [], []

def df_hazirla(gelirler, giderler):
    ay = {1:"Oca",2:"Şub",3:"Mar",4:"Nis",5:"May",6:"Haz",
          7:"Tem",8:"Ağu",9:"Eyl",10:"Eki",11:"Kas",12:"Ara"}
    df_g  = pd.DataFrame(gelirler)
    df_gi = pd.DataFrame(giderler)
    if not df_gi.empty:
        df_gi['tarih_dt'] = pd.to_datetime(df_gi['tarih'], format='%d.%m.%Y', errors='coerce')
        df_gi['Yıl']    = df_gi['tarih_dt'].dt.year.fillna(datetime.now().year).astype(int)
        df_gi['Ay_No']  = df_gi['tarih_dt'].dt.month.fillna(datetime.now().month).astype(int)
        df_gi['Ay']     = df_gi['Ay_No'].map(ay)
        df_gi['Ay-Yıl'] = df_gi['Ay'] + " " + df_gi['Yıl'].astype(str)
    return df_g, df_gi

def kat_renk_ikon(kategoriler):
    """Kategori listesinden renk/ikon sözlüğü oluştur"""
    sonuc = {}
    for i, kat in enumerate(kategoriler):
        ad = kat["ad"]
        ikon = kat.get("ikon", "💰")
        renk_idx = kat.get("renk_index", i % len(KAT_GRADYANLAR))
        sonuc[ad] = {"bg": KAT_GRADYANLAR[renk_idx % len(KAT_GRADYANLAR)], "icon": ikon}
    return sonuc

# ═══════════════════════════════════════════════════════
# GİRİŞ / KAYIT SAYFASI
# ═══════════════════════════════════════════════════════
if st.session_state.user is None:
    st.markdown("""
    <div style='text-align:center; padding: 30px 0 10px 0;'>
        <div style='font-size:3rem'>🏦</div>
        <div style='font-size:1.6rem; font-weight:900; color:#1A1F36'>Finansal Asistan</div>
        <div style='font-size:14px; color:#8A92A6; font-weight:600; margin-top:4px'>Aile bütçenizi kolayca takip edin</div>
    </div>
    """, unsafe_allow_html=True)

    tab_giris, tab_kayit = st.tabs(["🔑 Giriş Yap", "✨ Kayıt Ol"])

    with tab_giris:
        with st.form("giris_form"):
            email = st.text_input("📧 E-posta")
            sifre = st.text_input("🔒 Şifre", type="password")
            if st.form_submit_button("Giriş Yap", use_container_width=True):
                if email and sifre:
                    try:
                        # Supabase'e giriş isteği atıyoruz
                        res = supabase.auth.sign_in_with_password({"email": email, "password": sifre})
                        
                        # Başarılı olursa session'a kaydedip sayfayı yeniliyoruz
                        st.session_state.user = res.user
                        st.session_state.access_token = res.session.access_token
                        st.success("✅ Giriş başarılı, yönlendiriliyorsunuz...")
                        st.rerun()
                        
                    except Exception as e:
                        # ARTIK SUPABASE'İN BİZE GÖNDERDİĞİ GERÇEK HATAYI GÖRECEĞİZ
                        st.error(f"❌ Giriş Hatası: {str(e)}")
                else:
                    st.error("⚠️ Lütfen e-posta ve şifrenizi girin.")

    with tab_kayit:
        with st.form("kayit_form"):
            yeni_email  = st.text_input("📧 E-posta")
            yeni_sifre  = st.text_input("🔒 Şifre", type="password")
            yeni_sifre2 = st.text_input("🔒 Şifre Tekrar", type="password")
            if st.form_submit_button("Kayıt Ol", use_container_width=True):
                if yeni_email and yeni_sifre and yeni_sifre2:
                    if yeni_sifre != yeni_sifre2:
                        st.error("❌ Şifreler eşleşmiyor!")
                    elif len(yeni_sifre) < 6:
                        st.error("❌ Şifre en az 6 karakter olmalı!")
                    else:
                        try:
                            res = supabase.auth.sign_up({"email": yeni_email, "password": yeni_sifre})
                            
                            if res.session:
                                st.session_state.user = res.user
                                st.session_state.access_token = res.session.access_token
                                st.success("✅ Kayıt başarılı! Hesabınıza yönlendiriliyorsunuz...")
                                st.rerun()
                            else:
                                st.success("✅ Kayıt başarılı! Lütfen Giriş Yap sekmesinden sisteme girin.")
                        except Exception as e:
                            st.error(f"❌ Kayıt başarısız: {str(e)}")
                else:
                    st.error("⚠️ Lütfen tüm alanları doldurun.")
    st.stop()

# ─── KULLANICI GİRİŞ YAPMIŞ ──────────────────────────────────────
user_id    = st.session_state.user.id
kisiler    = kisiler_yukle(user_id)
kategoriler = kategoriler_yukle(user_id)
kat_sozluk = kat_renk_ikon(kategoriler)
kat_adlari = [k["ad"] for k in kategoriler] if kategoriler else VARSAYILAN_KATEGORILER

gelirler, giderler = veri_yukle(user_id)
df_gelir, df_gider = df_hazirla(gelirler, giderler)

toplam_gelir = df_gelir['tutar'].sum() if not df_gelir.empty else 0
toplam_gider = df_gider['tutar'].sum() if not df_gider.empty else 0
net_durum    = toplam_gelir - toplam_gider
sayfa        = st.session_state.sayfa

# ═══════════════════════════════════════════════════════
# SAYFALAR
# ═══════════════════════════════════════════════════════

if sayfa == "anasayfa":
    col_title, col_cikis = st.columns([4, 1])
    with col_title:
        st.markdown(f"<div style='font-size:12px;color:#8A92A6;font-weight:700;padding-top:12px'>👤 {st.session_state.user.email}</div>", unsafe_allow_html=True)
    with col_cikis:
        if st.button("Çıkış", key="cikis"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.session_state.access_token = None
            st.cache_data.clear() # Çıkış yaparken önbelleği temizlemek iyi bir pratiktir
            st.rerun()

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

    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕  Gider Ekle", use_container_width=True):
            st.session_state.sayfa = "ekle"; st.rerun()
    with c2:
        if st.button("📈  Analizi Gör", use_container_width=True):
            st.session_state.sayfa = "analiz"; st.rerun()

    if not df_gider.empty:
        st.markdown('<div class="section-title">📂 Kategoriler</div>', unsafe_allow_html=True)
        kat_ozet = df_gider.groupby('kategori')['tutar'].sum().to_dict()
        cards_html = '<div class="cat-grid">'
        for kat, bilgi in kat_sozluk.items():
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

        st.markdown('<div class="section-title">🕐 Son İşlemler</div>', unsafe_allow_html=True)
        son = df_gider.sort_values('tarih_dt', ascending=False).head(5)
        txn_html = ''
        for _, row in son.iterrows():
            kat = row.get('kategori', 'Genel')
            bilgi = kat_sozluk.get(kat, {"bg": "linear-gradient(135deg,#667eea,#764ba2)", "icon": "💸"})
            kisi = row.get('kisi', '')
            kisi_idx = kisiler.index(kisi) if kisi in kisiler else 0
            kisi_renk = KİŞİ_RENKLER[kisi_idx % len(KİŞİ_RENKLER)]
            txn_html += f"""
            <div class="txn-card">
                <div class="txn-icon" style="background:{bilgi['bg']}">{bilgi['icon']}</div>
                <div class="txn-info">
                    <div class="txn-name">{kat}</div>
                    <div class="txn-date">{row.get('tarih','')} · <span style="color:{kisi_renk};font-weight:800">{kisi}</span></div>
                </div>
                <div class="txn-amount">-₺{row['tutar']:,.0f}</div>
            </div>"""
        st.markdown(txn_html, unsafe_allow_html=True)
    else:
        st.info("Henüz harcama kaydı yok. ➕ Gider Ekle butonuyla başlayabilirsin!")

elif sayfa == "ozet":
    st.markdown("## 📊 Finansal Özet")
    net_gradient = "linear-gradient(135deg,#1D976C,#93F9B9)" if net_durum >= 0 else "linear-gradient(135deg,#C94B4B,#FF6B6B)"
    st.markdown(f"""
    <div class="header-card" style="background:{net_gradient}">
        <div class="header-title">Net Bakiye</div>
        <div class="header-amount">₺{net_durum:,.0f}</div>
        <div class="header-row">
            <div class="header-pill">
                <div class="header-pill-label">📈 Gelir</div>
                <div class="header-pill-value" style="color:#fff">₺{toplam_gelir:,.0f}</div>
            </div>
            <div class="header-pill">
                <div class="header-pill-label">📉 Gider</div>
                <div class="header-pill-value" style="color:#fff">₺{toplam_gider:,.0f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not df_gider.empty:
        if toplam_gelir > 0:
            harcama_oran = min(toplam_gider / toplam_gelir * 100, 100)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=harcama_oran,
                title={'text': "Bütçe Kullanımı %", 'font': {'size': 13, 'color': '#1A1F36', 'family': 'Nunito'}},
                delta={'reference': 80, 'increasing': {'color': "#EE0979"}, 'decreasing': {'color': "#1D976C"}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#8A92A6'},
                    'bar': {'color': "#1A73E8", 'thickness': 0.25},
                    'bgcolor': "white", 'borderwidth': 0,
                    'steps': [
                        {'range': [0, 60],   'color': '#E8F5E9'},
                        {'range': [60, 80],  'color': '#FFF8E1'},
                        {'range': [80, 100], 'color': '#FFEBEE'},
                    ],
                    'threshold': {'line': {'color': "#EE0979", 'width': 3}, 'thickness': 0.75, 'value': 80}
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=220, margin=dict(l=20, r=20, t=40, b=10), font={'family': 'Nunito'}
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        kat_ozet = df_gider.groupby('kategori')['tutar'].sum().nlargest(5).reset_index()
        bar_renkler = ["#FF6B6B","#F7971E","#1A73E8","#11998E","#8E54E9"]
        fig = px.bar(kat_ozet, x='tutar', y='kategori', orientation='h',
                     title="Top 5 Harcama Kategorisi", labels={'tutar':'₺','kategori':''})
        fig.update_traces(marker_color=bar_renkler[:len(kat_ozet)], marker_line_width=0,
                          text=[f"₺{v:,.0f}" for v in kat_ozet['tutar']],
                          textposition='outside', textfont=dict(size=11, color='#1A1F36'))
        fig.update_layout(**CHART, height=270, font=dict(family='Nunito'),
                          title_font=dict(size=13, color='#1A1F36'))
        fig.update_xaxes(gridcolor='#E8ECF4', tickfont=dict(color='#8A92A6'))
        fig.update_yaxes(gridcolor='rgba(0,0,0,0)', tickfont=dict(color='#1A1F36'))
        st.plotly_chart(fig, use_container_width=True)

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
        if not kat_adlari:
            st.warning("⚠️ Önce ⚙️ Ayarlar sayfasından kategori ekleyin.")
        elif not kisiler:
            st.warning("⚠️ Önce ⚙️ Ayarlar sayfasından kişi ekleyin.")
        else:
            with st.form("gider_form", clear_on_submit=True):
                tutar    = st.number_input("💵 Tutar (₺)", min_value=0.0, step=50.0)
                kisi     = st.selectbox("👤 Kişi", kisiler)
                kategori = st.selectbox("📂 Kategori", kat_adlari)
                aciklama = st.text_input("📝 Açıklama (isteğe bağlı)")
                tarih    = st.date_input("📅 Tarih")
                if st.form_submit_button("💾  Kaydet", use_container_width=True):
                    if tutar > 0:
                        try:
                            supabase.table("giderler").insert({
                                "user_id": user_id, "tutar": tutar, "kisi": kisi,
                                "kategori": kategori,
                                "aciklama": aciklama or "Belirtilmedi",
                                "tarih": tarih.strftime("%d.%m.%Y")
                            }).execute()
                            
                            st.cache_data.clear() # Veri önbelleğini temizle
                            
                            st.success("✅ Gider kaydedildi!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Hata: {str(e)}")
                    else:
                        st.error("⚠️ Geçerli bir tutar giriniz.")
    else:
        with st.form("gelir_form", clear_on_submit=True):
            tutar    = st.number_input("💵 Tutar (₺)", min_value=0.0, step=100.0)
            aciklama = st.text_input("📝 Açıklama (Maaş, Prim vb.)")
            tarih    = st.date_input("📅 Tarih")
            if st.form_submit_button("💾  Kaydet", use_container_width=True):
                if tutar > 0:
                    try:
                        supabase.table("gelirler").insert({
                            "user_id": user_id, "tutar": tutar,
                            "aciklama": aciklama or "Belirtilmedi",
                            "tarih": tarih.strftime("%d.%m.%Y")
                        }).execute()
                        
                        st.cache_data.clear() # Veri önbelleğini temizle
                        
                        st.success("✅ Gelir kaydedildi!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Hata: {str(e)}")
                else:
                    st.error("⚠️ Geçerli bir tutar giriniz.")

elif sayfa == "analiz":
    st.markdown("## 📈 Analiz")
    if df_gider.empty:
        st.warning("Analiz için önce gider verisi giriniz.")
    else:
        tab1, tab2, tab3 = st.tabs(["📅 Aylık", "📂 Kategori", "👤 Kişi"])

        with tab1:
            aylik = df_gider.groupby(['Yıl','Ay_No','Ay-Yıl'])['tutar'].sum().reset_index()
            aylik = aylik.sort_values(['Yıl','Ay_No'])
            fig = px.bar(aylik, x='Ay-Yıl', y='tutar',
                         title="Aylık Harcama", labels={'tutar':'₺','Ay-Yıl':''})
            fig.update_traces(marker_color='#1A73E8', marker_line_width=0,
                              text=[f"₺{v:,.0f}" for v in aylik['tutar']],
                              textposition='outside', textfont=dict(size=10, color='#1A1F36'))
            fig.update_layout(**CHART, height=320, xaxis_tickangle=-45, font=dict(family='Nunito'))
            fig.update_xaxes(gridcolor='#E8ECF4')
            fig.update_yaxes(gridcolor='#E8ECF4')
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            kat = df_gider.groupby('kategori')['tutar'].sum().reset_index()
            pie_renkler = ["#FF6B6B","#F7971E","#FFD200","#1A73E8","#11998E","#8E54E9","#F953C6","#4776E6","#C94B4B"]
            fig2 = px.pie(kat, values='tutar', names='kategori',
                          title="Kategori Dağılımı", hole=0.45,
                          color_discrete_sequence=pie_renkler)
            fig2.update_traces(textfont=dict(size=11), pull=[0.03]*len(kat))
            fig2.update_layout(**CHART, height=340, font=dict(family='Nunito'))
            st.plotly_chart(fig2, use_container_width=True)

            if 'kisi' in df_gider.columns:
                fig3 = px.sunburst(df_gider, path=['kategori','kisi'], values='tutar',
                                   title="Kategori & Kişi Detayı",
                                   color_discrete_sequence=pie_renkler)
                fig3.update_layout(**CHART, height=340, font=dict(family='Nunito'))
                st.plotly_chart(fig3, use_container_width=True)

        with tab3:
            if 'kisi' in df_gider.columns:
                kisi_df = df_gider.groupby('kisi')['tutar'].sum().reset_index()
                kisi_renk_map = {k: KİŞİ_RENKLER[i % len(KİŞİ_RENKLER)] for i, k in enumerate(kisiler)}
                fig4 = px.bar(kisi_df.sort_values('tutar'), x='tutar', y='kisi',
                              orientation='h', title="Kişi Bazlı Harcama",
                              labels={'tutar':'₺','kisi':''},
                              color='kisi', color_discrete_map=kisi_renk_map)
                fig4.update_traces(marker_line_width=0,
                                   text=[f"₺{v:,.0f}" for v in kisi_df.sort_values('tutar')['tutar']],
                                   textposition='outside', textfont=dict(size=11, color='#1A1F36'))
                fig4.update_layout(**CHART, height=300, showlegend=False, font=dict(family='Nunito'))
                fig4.update_xaxes(gridcolor='#E8ECF4')
                st.plotly_chart(fig4, use_container_width=True)

                kisi_ay = df_gider.groupby(['Ay-Yıl','kisi','Yıl','Ay_No'])['tutar'].sum().reset_index()
                kisi_ay = kisi_ay.sort_values(['Yıl','Ay_No'])
                fig5 = px.line(kisi_ay, x='Ay-Yıl', y='tutar', color='kisi',
                               markers=True, title="Aylık Kişi Trendi",
                               labels={'tutar':'₺','Ay-Yıl':''},
                               color_discrete_map=kisi_renk_map)
                fig5.update_traces(line_width=2.5, marker_size=7)
                fig5.update_layout(**CHART, height=320, xaxis_tickangle=-45, font=dict(family='Nunito'))
                fig5.update_xaxes(gridcolor='#E8ECF4')
                fig5.update_yaxes(gridcolor='#E8ECF4')
                st.plotly_chart(fig5, use_container_width=True)

elif sayfa == "ayarlar":
    st.markdown("## ⚙️ Ayarlar")
    tab1, tab2, tab3 = st.tabs(["👥 Kişiler", "📂 Kategoriler", "🗃️ Veriler"])

    # ── KİŞİLER ──
    with tab1:
        st.markdown("### Kişi Ekle")
        with st.form("kisi_ekle_form", clear_on_submit=True):
            yeni_kisi = st.text_input("👤 Kişi Adı")
            if st.form_submit_button("➕ Ekle", use_container_width=True):
                if yeni_kisi.strip():
                    if yeni_kisi.strip() in kisiler:
                        st.error("❌ Bu kişi zaten var!")
                    else:
                        try:
                            supabase.table("kisiler").insert({
                                "user_id": user_id, "ad": yeni_kisi.strip()
                            }).execute()
                            
                            st.cache_data.clear() # Veri önbelleğini temizle
                            
                            st.success(f"✅ '{yeni_kisi}' eklendi!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Hata: {str(e)}")
                else:
                    st.error("⚠️ Kişi adı boş olamaz.")

        st.markdown("### Mevcut Kişiler")
        if kisiler and kisiler != VARSAYILAN_KİŞİLER:
            for kisi in kisiler:
                c1, c2 = st.columns([4, 1])
                with c1:
                    idx = kisiler.index(kisi) % len(KİŞİ_RENKLER)
                    st.markdown(f"<div style='padding:10px;background:white;border-radius:10px;margin-bottom:6px;font-weight:700;color:{KİŞİ_RENKLER[idx]}'>👤 {kisi}</div>", unsafe_allow_html=True)
                with c2:
                    if st.button("🗑️", key=f"kisi_sil_{kisi}"):
                        try:
                            supabase.table("kisiler").delete().eq("user_id", user_id).eq("ad", kisi).execute()
                            st.cache_data.clear() # Veri önbelleğini temizle
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {str(e)}")
        else:
            st.info("Henüz kişi eklenmedi.")

    # ── KATEGORİLER ──
    with tab2:
        st.markdown("### Kategori Ekle")
        with st.form("kat_ekle_form", clear_on_submit=True):
            yeni_kat  = st.text_input("📂 Kategori Adı")
            ikon_sec  = st.selectbox("İkon Seç", KAT_İKONLAR)
            renk_sec  = st.selectbox("Renk Seç", 
                options=list(range(len(KAT_GRADYANLAR))),
                format_func=lambda i: f"Renk {i+1}")
            if st.form_submit_button("➕ Ekle", use_container_width=True):
                if yeni_kat.strip():
                    if yeni_kat.strip() in kat_adlari:
                        st.error("❌ Bu kategori zaten var!")
                    else:
                        try:
                            supabase.table("kategoriler").insert({
                                "user_id": user_id,
                                "ad": yeni_kat.strip(),
                                "ikon": ikon_sec,
                                "renk_index": renk_sec
                            }).execute()
                            
                            st.cache_data.clear() # Veri önbelleğini temizle
                            
                            st.success(f"✅ '{yeni_kat}' kategorisi eklendi!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Hata: {str(e)}")
                else:
                    st.error("⚠️ Kategori adı boş olamaz.")

        st.markdown("### Mevcut Kategoriler")
        if kategoriler:
            for kat in kategoriler:
                c1, c2 = st.columns([4, 1])
                with c1:
                    bg = KAT_GRADYANLAR[kat.get("renk_index", 0) % len(KAT_GRADYANLAR)]
                    st.markdown(f"<div style='padding:10px;background:{bg};border-radius:10px;margin-bottom:6px;font-weight:700;color:white'>{kat['ikon']} {kat['ad']}</div>", unsafe_allow_html=True)
                with c2:
                    if st.button("🗑️", key=f"kat_sil_{kat['ad']}"):
                        try:
                            supabase.table("kategoriler").delete().eq("user_id", user_id).eq("ad", kat["ad"]).execute()
                            st.cache_data.clear() # Veri önbelleğini temizle
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {str(e)}")
        else:
            st.info("Henüz kategori eklenmedi.")

    # ── VERİLER ──
    with tab3:
        st.markdown("### 📉 Gider Kayıtları")
        if not df_gider.empty:
            gider_saf = df_gider[['id','tarih','kisi','kategori','aciklama','tutar']].copy()
            edited_g = st.data_editor(gider_saf, num_rows="dynamic",
                                      use_container_width=True, key="ed_gider", disabled=["id"])
            if st.button("💾  Giderleri Kaydet", type="primary", use_container_width=True):
                try:
                    supabase.table("giderler").delete().eq("user_id", user_id).execute()
                    for _, row in edited_g.iterrows():
                        supabase.table("giderler").insert({
                            "user_id": user_id, "tutar": row['tutar'], "kisi": row['kisi'],
                            "kategori": row['kategori'], "aciklama": row['aciklama'], "tarih": row['tarih']
                        }).execute()
                        
                    st.cache_data.clear() # Veri önbelleğini temizle
                    
                    st.success("✅ Güncellendi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")
        else:
            st.info("Kayıt yok.")

        st.markdown("---")
        st.markdown("### 📈 Gelir Kayıtları")
        if not df_gelir.empty:
            gelir_saf = df_gelir[['id','tarih','aciklama','tutar']].copy()
            edited_gelir = st.data_editor(gelir_saf, num_rows="dynamic",
                                          use_container_width=True, key="ed_gelir", disabled=["id"])
            if st.button("💾  Gelirleri Kaydet", type="primary", use_container_width=True):
                try:
                    supabase.table("gelirler").delete().eq("user_id", user_id).execute()
                    for _, row in edited_gelir.iterrows():
                        supabase.table("gelirler").insert({
                            "user_id": user_id, "tutar": row['tutar'],
                            "aciklama": row['aciklama'], "tarih": row['tarih']
                        }).execute()
                        
                    st.cache_data.clear() # Veri önbelleğini temizle
                    
                    st.success("✅ Güncellendi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")
        else:
            st.info("Kayıt yok.")

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
        ("ayarlar",  "⚙️", "Ayarlar"),
    ]
    for col, (key, icon, label) in zip(nav_cols, nav_items):
        with col:
            btn_label = f"**{icon}**\n{label}" if aktif == key else f"{icon}\n{label}"
            if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
                st.session_state.sayfa = key
                st.rerun()

