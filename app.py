import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Finansal Asistan",
    page_icon="🏦",
    layout="centered",  # Mobil için "wide" yerine "centered"
    initial_sidebar_state="collapsed"  # Mobilde sidebar kapalı başlasın
)

# --- MOBİL-ÖNCELİKLİ CSS ---
st.markdown("""
<style>
    /* Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Genel arka plan */
    .stApp {
        background-color: #0f1117;
        color: #e8eaf0;
    }

    /* Başlıklar */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Metric kartları */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130 0%, #252a3d 100%);
        border: 1px solid #2e3450;
        border-radius: 16px;
        padding: 16px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] label {
        color: #8892b0 !important;
        font-size: 13px !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #64ffda !important;
        font-size: 22px !important;
        font-weight: 700 !important;
    }

    /* Butonlar - büyük dokunma alanı (mobil için) */
    .stButton > button {
        width: 100%;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #1a73e8, #0d47a1) !important;
        color: white !important;
        border: none !important;
        transition: all 0.2s ease !important;
        min-height: 52px; /* Mobil dokunma standardı */
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(26,115,232,0.4) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #64ffda, #00b4d8) !important;
        color: #0f1117 !important;
    }

    /* Form alanları - mobil uyumlu */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background-color: #1e2130 !important;
        border: 1px solid #2e3450 !important;
        border-radius: 10px !important;
        color: #e8eaf0 !important;
        font-size: 16px !important; /* iOS zoom'u engellemek için min 16px */
        padding: 12px !important;
        min-height: 48px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a1f2e !important;
        border-right: 1px solid #2e3450;
    }
    section[data-testid="stSidebar"] .stRadio > label {
        color: #8892b0 !important;
    }

    /* Tab butonları */
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 10px 16px;
        color: #8892b0;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a73e8 !important;
        color: white !important;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #2e3450;
    }

    /* Bilgi/uyarı kutuları */
    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 12px !important;
        font-size: 14px !important;
    }

    /* Mobil: sütunları dikey sırala */
    @media (max-width: 768px) {
        /* Sütunlar zaten centered layoutta iyi görünür */
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            font-size: 18px !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 12px !important;
            padding: 8px 10px !important;
        }
    }

    /* Ayırıcı çizgi */
    hr {
        border-color: #2e3450 !important;
        margin: 20px 0 !important;
    }

    /* Alt navigasyon barı (mobil hızlı erişim) */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #1a1f2e;
        border-top: 1px solid #2e3450;
        display: flex;
        justify-content: space-around;
        padding: 10px 0 16px 0;
        z-index: 999;
    }
    .bottom-nav a {
        text-decoration: none;
        color: #8892b0;
        font-size: 11px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
    }
    .bottom-nav a span.icon {
        font-size: 22px;
    }
    /* Ana içeriğe alt boşluk bırak (nav bar için) */
    .main .block-container {
        padding-bottom: 90px !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
        max-width: 720px !important;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "butce_veritabaniniz.json"

# --- VERİ YÖNETİMİ (ÖNBELLEK İLE HIZLANDIRILDI) ---
@st.cache_data(ttl=5)  # 5 saniye cache: tekrar yüklemeleri önler
def veri_yukle():
    if not os.path.exists(DATA_FILE):
        return {"gelirler": [], "giderler": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def veri_kaydet(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    st.cache_data.clear()  # Kaydedince cache'i temizle

app_data = veri_yukle()

# --- DATAFRAME HAZIRLA ---
def df_hazirla(data):
    ay_isimleri = {1:"Ocak", 2:"Şubat", 3:"Mart", 4:"Nisan", 5:"Mayıs", 6:"Haziran",
                   7:"Temmuz", 8:"Ağustos", 9:"Eylül", 10:"Ekim", 11:"Kasım", 12:"Aralık"}

    df_g = pd.DataFrame(data.get("gelirler", []))
    df_gi = pd.DataFrame(data.get("giderler", []))

    if not df_gi.empty:
        df_gi['tarih_dt'] = pd.to_datetime(df_gi['tarih'], format='%d.%m.%Y', errors='coerce')
        df_gi['Yıl'] = df_gi['tarih_dt'].dt.year.fillna(datetime.now().year).astype(int)
        df_gi['Ay_No'] = df_gi['tarih_dt'].dt.month.fillna(datetime.now().month).astype(int)
        df_gi['Ay'] = df_gi['Ay_No'].map(ay_isimleri)
        df_gi['Ay-Yıl'] = df_gi['Ay'] + " " + df_gi['Yıl'].astype(str)

    return df_g, df_gi

df_gelir, df_gider = df_hazirla(app_data)

toplam_gelir = df_gelir['tutar'].sum() if not df_gelir.empty else 0
toplam_gider = df_gider['tutar'].sum() if not df_gider.empty else 0
net_durum = toplam_gelir - toplam_gider

# --- YAN MENÜ ---
st.sidebar.title("🏦 Menü")
st.sidebar.markdown("---")
sayfa = st.sidebar.radio("İşlemler", [
    "📊 Finansal Özet",
    "➕ Yeni İşlem Ekle",
    "📈 Detaylı Analiz",
    "⚙️ Kayıtları Düzenle / Sil"
])

# =============================================
# MOBİL ALT NAVİGASYON BARI (Hızlı erişim)
# =============================================
st.markdown("""
<div class="bottom-nav">
    <a href="?sayfa=ozet"><span class="icon">📊</span>Özet</a>
    <a href="?sayfa=ekle"><span class="icon">➕</span>Ekle</a>
    <a href="?sayfa=analiz"><span class="icon">📈</span>Analiz</a>
    <a href="?sayfa=duzenle"><span class="icon">⚙️</span>Düzenle</a>
</div>
""", unsafe_allow_html=True)


# ================= 1. FİNANSAL ÖZET =================
if sayfa == "📊 Finansal Özet":
    st.title("💼 Finansal Durum")

    # Mobil: 3 kart dikey sıralanır, yan yana görünür
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gelir", f"₺{toplam_gelir:,.0f}")
    with col2:
        st.metric("Gider", f"₺{toplam_gider:,.0f}")
    with col3:
        delta_renk = "normal" if net_durum >= 0 else "inverse"
        st.metric("Net", f"₺{net_durum:,.0f}", delta=f"₺{net_durum:,.0f}", delta_color=delta_renk)

    st.markdown("---")

    # Küçük özet grafik (hızlı yüklensin diye basit)
    if not df_gider.empty:
        kat_ozet = df_gider.groupby('kategori')['tutar'].sum().nlargest(5).reset_index()
        fig = px.bar(
            kat_ozet, x='tutar', y='kategori', orientation='h',
            title="Top 5 Harcama Kategorisi",
            labels={'tutar': 'TL', 'kategori': ''},
            color='tutar', color_continuous_scale='Blues'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e8eaf0',
            height=280,
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False,
            coloraxis_showscale=False
        )
        fig.update_xaxes(gridcolor='#2e3450')
        fig.update_yaxes(gridcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Son 5 Harcama")
        son = df_gider[['tarih', 'kisi', 'kategori', 'tutar']].sort_values('tarih', ascending=False).head(5)
        st.dataframe(son, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz sisteme harcama kaydedilmemiş.")


# ================= 2. YENİ İŞLEM EKLE =================
elif sayfa == "➕ Yeni İşlem Ekle":
    st.title("➕ Yeni İşlem")

    # Mobilde tek sütun, tab ile ayır
    islem_turu = st.radio("İşlem Türü", ["💸 Gider", "💰 Gelir"], horizontal=True)
    st.markdown("---")

    if islem_turu == "💸 Gider":
        with st.form("gider_formu", clear_on_submit=True):
            st.subheader("Gider Girişi")
            gid_tutar = st.number_input("Tutar (₺)", min_value=0.0, step=50.0, placeholder="0.00")
            gid_kisi = st.selectbox("Harcamayı Yapan", ["Burak", "Kerime", "Ece", "Berkay", "Genel"])
            gid_kategori = st.selectbox("Kategori", [
                "Eğitim", "Akaryakıt", "Fatura", "Market", "Giyim",
                "Yemek", "Araç Bakım-Vergi", "İlaç", "Kredi Kartı Geçmiş Borç"
            ])
            gid_aciklama = st.text_input("Açıklama (isteğe bağlı)")
            gid_tarih = st.date_input("Tarih")

            kaydet = st.form_submit_button("💾 Gideri Kaydet", use_container_width=True)
            if kaydet:
                if gid_tutar > 0:
                    app_data["giderler"].append({
                        "tutar": gid_tutar, "kisi": gid_kisi,
                        "kategori": gid_kategori,
                        "aciklama": gid_aciklama or "Belirtilmedi",
                        "tarih": gid_tarih.strftime("%d.%m.%Y")
                    })
                    veri_kaydet(app_data)
                    st.success("✅ Gider kaydedildi!")
                    st.balloons()
                else:
                    st.error("Geçerli bir tutar giriniz.")

    else:
        with st.form("gelir_formu", clear_on_submit=True):
            st.subheader("Gelir Girişi")
            g_tutar = st.number_input("Tutar (₺)", min_value=0.0, step=100.0, placeholder="0.00")
            g_aciklama = st.text_input("Açıklama (Maaş, Prim vb.)")
            g_tarih = st.date_input("Tarih")

            kaydet = st.form_submit_button("💾 Geliri Kaydet", use_container_width=True)
            if kaydet:
                if g_tutar > 0:
                    app_data["gelirler"].append({
                        "tutar": g_tutar,
                        "aciklama": g_aciklama or "Belirtilmedi",
                        "tarih": g_tarih.strftime("%d.%m.%Y")
                    })
                    veri_kaydet(app_data)
                    st.success("✅ Gelir kaydedildi!")
                    st.balloons()
                else:
                    st.error("Geçerli bir tutar giriniz.")


# ================= 3. DETAYLI ANALİZ =================
elif sayfa == "📈 Detaylı Analiz":
    st.title("📈 Harcama Analizi")

    if df_gider.empty:
        st.warning("Analiz için önce gider verisi girmelisiniz.")
    else:
        LAYOUT = dict(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e8eaf0',
            margin=dict(l=0, r=0, t=40, b=60),
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )

        tab1, tab2, tab3 = st.tabs(["📅 Aylık", "📂 Kategori", "👤 Kişi"])

        with tab1:
            aylik = df_gider.groupby(['Yıl', 'Ay_No', 'Ay-Yıl'])['tutar'].sum().reset_index()
            aylik = aylik.sort_values(['Yıl', 'Ay_No'])
            fig = px.bar(aylik, x='Ay-Yıl', y='tutar',
                         title="Aylık Harcama Trendi",
                         labels={'tutar': '₺', 'Ay-Yıl': ''},
                         color='tutar', color_continuous_scale='Blues')
            fig.update_layout(**LAYOUT, height=320, xaxis_tickangle=-45, coloraxis_showscale=False)
            fig.update_xaxes(gridcolor='#2e3450')
            fig.update_yaxes(gridcolor='#2e3450')
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            kat = df_gider.groupby('kategori')['tutar'].sum().reset_index()
            fig_pie = px.pie(kat, values='tutar', names='kategori',
                             title="Kategori Dağılımı", hole=0.45)
            fig_pie.update_layout(**LAYOUT, height=340)
            fig_pie.update_traces(textfont_color='white')
            st.plotly_chart(fig_pie, use_container_width=True)

            # Sunburst — mobilde biraz küçük göster
            fig_sun = px.sunburst(df_gider, path=['kategori', 'kisi'], values='tutar',
                                  title="Kategori & Kişi Kırılımı")
            fig_sun.update_layout(**LAYOUT, height=340)
            st.plotly_chart(fig_sun, use_container_width=True)

        with tab3:
            kisi = df_gider.groupby('kisi')['tutar'].sum().reset_index()
            fig_k = px.bar(kisi.sort_values('tutar'), x='tutar', y='kisi',
                           orientation='h', title="Kişi Bazlı Harcama",
                           color='tutar', color_continuous_scale='Teal')
            fig_k.update_layout(**LAYOUT, height=300, coloraxis_showscale=False)
            fig_k.update_xaxes(gridcolor='#2e3450')
            st.plotly_chart(fig_k, use_container_width=True)

            kisi_ay = df_gider.groupby(['Ay-Yıl', 'kisi', 'Yıl', 'Ay_No'])['tutar'].sum().reset_index()
            kisi_ay = kisi_ay.sort_values(['Yıl', 'Ay_No'])
            fig_l = px.line(kisi_ay, x='Ay-Yıl', y='tutar', color='kisi',
                            markers=True, title="Aylık Kişi Trendi",
                            labels={'tutar': '₺', 'Ay-Yıl': ''})
            fig_l.update_layout(**LAYOUT, height=320, xaxis_tickangle=-45)
            fig_l.update_xaxes(gridcolor='#2e3450')
            fig_l.update_yaxes(gridcolor='#2e3450')
            st.plotly_chart(fig_l, use_container_width=True)


# ================= 4. DÜZENLE / SİL =================
elif sayfa == "⚙️ Kayıtları Düzenle / Sil":
    st.title("⚙️ Veri Yönetimi")
    st.info("Hücreye tıklayarak düzenleme yapabilir, satır seçip Delete ile silebilirsiniz. İşlem bitince Kaydet'e basın.")

    st.subheader("Gider Kayıtları")
    if not df_gider.empty:
        gider_saf = df_gider[['tarih', 'kisi', 'kategori', 'aciklama', 'tutar']]
        edited_gider = st.data_editor(gider_saf, num_rows="dynamic", use_container_width=True, key="gider_editor")
        if st.button("💾 Giderleri Kaydet", type="primary"):
            app_data["giderler"] = edited_gider.to_dict('records')
            veri_kaydet(app_data)
            st.success("Gider kayıtları güncellendi!")
            st.rerun()
    else:
        st.write("Kayıt yok.")

    st.markdown("---")
    st.subheader("Gelir Kayıtları")
    if not df_gelir.empty:
        edited_gelir = st.data_editor(df_gelir, num_rows="dynamic", use_container_width=True, key="gelir_editor")
        if st.button("💾 Gelirleri Kaydet", type="primary"):
            app_data["gelirler"] = edited_gelir.to_dict('records')
            veri_kaydet(app_data)
            st.success("Gelir kayıtları güncellendi!")
            st.rerun()
    else:
        st.write("Kayıt yok.")
