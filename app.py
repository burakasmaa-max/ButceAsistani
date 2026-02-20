import streamlit as st
import pandas as pd
import plotly.express as px
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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

* { font-family: 'Plus Jakarta Sans', sans-serif !important; }

.stApp { background-color: #f0f4f8; }

.main .block-container {
    max-width: 480px !important;
    padding: 1rem 1rem 110px 1rem !important;
    margin: 0 auto;
}

h1 { font-size: 1.6rem !important; color: #1e293b !important; font-weight: 700 !important; }
h2 { font-size: 1.2rem !important; color: #1e293b !important; font-weight: 700 !important; }
h3 { font-size: 1rem !important;   color: #1e293b !important; font-weight: 600 !important; }

div[data-testid="metric-container"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 12px !important;
    border-left: 4px solid #3b82f6;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
}
div[data-testid="metric-container"] label {
    font-size: 11px !important;
    color: #64748b !important;
    font-weight: 600 !important;
    text-transform: uppercase;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-size: 1.3rem !important;
    color: #1e293b !important;
    font-weight: 700 !important;
}

.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    min-height: 48px !important;
    background: #3b82f6 !important;
    color: white !important;
    border: none !important;
    box-shadow: none !important;
    transition: background 0.15s !important;
}
.stButton > button:hover {
    background: #2563eb !important;
    transform: none !important;
    box-shadow: none !important;
}

input, .stTextInput input, .stNumberInput input {
    font-size: 16px !important;
    border-radius: 10px !important;
    border: 1.5px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #1e293b !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #64748b !important;
    background: #e2e8f0 !important;
}
.stTabs [aria-selected="true"] {
    background: #3b82f6 !important;
    color: white !important;
}

section[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"]   { display: none !important; }

/* Alt nav container */
div[data-testid="stBottom"] {
    background: #ffffff !important;
    border-top: 1.5px solid #e2e8f0 !important;
    box-shadow: 0 -3px 12px rgba(0,0,0,0.08) !important;
    padding: 4px 0 8px 0 !important;
}
div[data-testid="stBottom"] .stButton > button {
    background: transparent !important;
    color: #94a3b8 !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    min-height: 54px !important;
    border-radius: 0 !important;
    padding: 2px !important;
    line-height: 1.3 !important;
}
div[data-testid="stBottom"] .stButton > button:hover {
    background: #eff6ff !important;
    color: #3b82f6 !important;
}

.stDataFrame { border-radius: 10px; overflow: hidden; }
.stAlert { border-radius: 10px !important; font-size: 14px !important; }
hr { border-color: #e2e8f0 !important; margin: 14px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── VERİ YÖNETİMİ ────────────────────────────────────────────────
DATA_FILE = "butce_veritabaniniz.json"

@st.cache_data(ttl=3)
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

app_data    = veri_yukle()
df_gelir, df_gider = df_hazirla(app_data)

toplam_gelir = df_gelir['tutar'].sum() if not df_gelir.empty else 0
toplam_gider = df_gider['tutar'].sum() if not df_gider.empty else 0
net_durum    = toplam_gelir - toplam_gider

CHART = dict(
    plot_bgcolor='#ffffff', paper_bgcolor='#f0f4f8',
    font_color='#1e293b', margin=dict(l=0, r=0, t=36, b=0),
    legend=dict(bgcolor='rgba(255,255,255,0.8)'),
)

# ═══════════════════════════════════════════════════════
# SAYFALAR
# ═══════════════════════════════════════════════════════

if sayfa == "anasayfa":
    st.title("🏦 Finansal Asistan")
    st.caption("Aile bütçenizi kolayca takip edin.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Gelir",  f"₺{toplam_gelir:,.0f}")
    with col2: st.metric("Gider",  f"₺{toplam_gider:,.0f}")
    with col3: st.metric("Net",    f"₺{net_durum:,.0f}")

    st.markdown("---")
    st.markdown("### Hızlı İşlem")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Gider Ekle", use_container_width=True):
            st.session_state.sayfa = "ekle"; st.rerun()
    with c2:
        if st.button("📈 Analiz", use_container_width=True):
            st.session_state.sayfa = "analiz"; st.rerun()

    if not df_gider.empty:
        st.markdown("### Son Harcamalar")
        son = df_gider[['tarih','kisi','kategori','tutar']].sort_values('tarih', ascending=False).head(5)
        st.dataframe(son, use_container_width=True, hide_index=True)

elif sayfa == "ozet":
    st.title("📊 Finansal Özet")

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Gelir",  f"₺{toplam_gelir:,.0f}")
    with col2: st.metric("Gider",  f"₺{toplam_gider:,.0f}")
    with col3:
        st.metric("Net", f"₺{net_durum:,.0f}",
                  delta=f"₺{net_durum:,.0f}",
                  delta_color="normal" if net_durum >= 0 else "inverse")

    st.markdown("---")
    if not df_gider.empty:
        kat_ozet = df_gider.groupby('kategori')['tutar'].sum().nlargest(5).reset_index()
        fig = px.bar(kat_ozet, x='tutar', y='kategori', orientation='h',
                     title="Top 5 Kategori", labels={'tutar':'₺','kategori':''})
        fig.update_traces(marker_color='#3b82f6', marker_line_width=0)
        fig.update_layout(**CHART, height=260)
        fig.update_xaxes(gridcolor='#e2e8f0', tickfont=dict(color='#64748b'))
        fig.update_yaxes(gridcolor='rgba(0,0,0,0)', tickfont=dict(color='#1e293b'))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Son 5 Harcama")
        son = df_gider[['tarih','kisi','kategori','tutar']].sort_values('tarih', ascending=False).head(5)
        st.dataframe(son, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz harcama kaydı yok.")

elif sayfa == "ekle":
    st.title("➕ Yeni İşlem")
    tur = st.radio("İşlem türü", ["💸 Gider", "💰 Gelir"], horizontal=True)
    st.markdown("---")

    if tur == "💸 Gider":
        with st.form("gider_form", clear_on_submit=True):
            tutar    = st.number_input("Tutar (₺)", min_value=0.0, step=50.0)
            kisi     = st.selectbox("Kişi", ["Burak","Kerime","Ece","Berkay","Genel"])
            kategori = st.selectbox("Kategori", [
                "Eğitim","Akaryakıt","Fatura","Market","Giyim",
                "Yemek","Araç Bakım-Vergi","İlaç","Kredi Kartı Geçmiş Borç"])
            aciklama = st.text_input("Açıklama (isteğe bağlı)")
            tarih    = st.date_input("Tarih")
            if st.form_submit_button("💾 Kaydet", use_container_width=True):
                if tutar > 0:
                    app_data["giderler"].append({
                        "tutar": tutar, "kisi": kisi, "kategori": kategori,
                        "aciklama": aciklama or "Belirtilmedi",
                        "tarih": tarih.strftime("%d.%m.%Y")
                    })
                    veri_kaydet(app_data)
                    st.success("✅ Gider kaydedildi!")
                    st.balloons()
                else:
                    st.error("Geçerli bir tutar giriniz.")
    else:
        with st.form("gelir_form", clear_on_submit=True):
            tutar    = st.number_input("Tutar (₺)", min_value=0.0, step=100.0)
            aciklama = st.text_input("Açıklama (Maaş, Prim vb.)")
            tarih    = st.date_input("Tarih")
            if st.form_submit_button("💾 Kaydet", use_container_width=True):
                if tutar > 0:
                    app_data["gelirler"].append({
                        "tutar": tutar,
                        "aciklama": aciklama or "Belirtilmedi",
                        "tarih": tarih.strftime("%d.%m.%Y")
                    })
                    veri_kaydet(app_data)
                    st.success("✅ Gelir kaydedildi!")
                    st.balloons()
                else:
                    st.error("Geçerli bir tutar giriniz.")

elif sayfa == "analiz":
    st.title("📈 Analiz")

    if df_gider.empty:
        st.warning("Analiz için önce gider verisi giriniz.")
    else:
        tab1, tab2, tab3 = st.tabs(["📅 Aylık", "📂 Kategori", "👤 Kişi"])

        with tab1:
            aylik = df_gider.groupby(['Yıl','Ay_No','Ay-Yıl'])['tutar'].sum().reset_index()
            aylik = aylik.sort_values(['Yıl','Ay_No'])
            fig = px.bar(aylik, x='Ay-Yıl', y='tutar',
                         title="Aylık Harcama", labels={'tutar':'₺','Ay-Yıl':''})
            fig.update_traces(marker_color='#3b82f6', marker_line_width=0)
            fig.update_layout(**CHART, height=300, xaxis_tickangle=-45)
            fig.update_xaxes(gridcolor='#e2e8f0')
            fig.update_yaxes(gridcolor='#e2e8f0')
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            kat = df_gider.groupby('kategori')['tutar'].sum().reset_index()
            fig2 = px.pie(kat, values='tutar', names='kategori',
                          title="Kategori Dağılımı", hole=0.4)
            fig2.update_layout(**CHART, height=320)
            st.plotly_chart(fig2, use_container_width=True)

            fig3 = px.sunburst(df_gider, path=['kategori','kisi'], values='tutar',
                               title="Kategori & Kişi")
            fig3.update_layout(**CHART, height=320)
            st.plotly_chart(fig3, use_container_width=True)

        with tab3:
            kisi = df_gider.groupby('kisi')['tutar'].sum().reset_index()
            fig4 = px.bar(kisi.sort_values('tutar'), x='tutar', y='kisi',
                          orientation='h', title="Kişi Bazlı",
                          labels={'tutar':'₺','kisi':''})
            fig4.update_traces(marker_color='#06b6d4', marker_line_width=0)
            fig4.update_layout(**CHART, height=280)
            fig4.update_xaxes(gridcolor='#e2e8f0')
            st.plotly_chart(fig4, use_container_width=True)

            kisi_ay = df_gider.groupby(['Ay-Yıl','kisi','Yıl','Ay_No'])['tutar'].sum().reset_index()
            kisi_ay = kisi_ay.sort_values(['Yıl','Ay_No'])
            fig5 = px.line(kisi_ay, x='Ay-Yıl', y='tutar', color='kisi',
                           markers=True, title="Aylık Kişi Trendi",
                           labels={'tutar':'₺','Ay-Yıl':''})
            fig5.update_layout(**CHART, height=300, xaxis_tickangle=-45)
            fig5.update_xaxes(gridcolor='#e2e8f0')
            fig5.update_yaxes(gridcolor='#e2e8f0')
            st.plotly_chart(fig5, use_container_width=True)

elif sayfa == "duzenle":
    st.title("⚙️ Veri Yönetimi")
    st.info("Hücreye tıklayıp düzenleyin, satır seçip Delete ile silin.")

    st.markdown("### Gider Kayıtları")
    if not df_gider.empty:
        gider_saf = df_gider[['tarih','kisi','kategori','aciklama','tutar']]
        edited_g = st.data_editor(gider_saf, num_rows="dynamic",
                                  use_container_width=True, key="ed_gider")
        if st.button("💾 Giderleri Kaydet", type="primary", use_container_width=True):
            app_data["giderler"] = edited_g.to_dict('records')
            veri_kaydet(app_data)
            st.success("Güncellendi!")
            st.rerun()
    else:
        st.write("Kayıt yok.")

    st.markdown("---")
    st.markdown("### Gelir Kayıtları")
    if not df_gelir.empty:
        edited_gelir = st.data_editor(df_gelir, num_rows="dynamic",
                                      use_container_width=True, key="ed_gelir")
        if st.button("💾 Gelirleri Kaydet", type="primary", use_container_width=True):
            app_data["gelirler"] = edited_gelir.to_dict('records')
            veri_kaydet(app_data)
            st.success("Güncellendi!")
            st.rerun()
    else:
        st.write("Kayıt yok.")

# ═══════════════════════════════════════════════════════
# ALT NAVİGASYON
# ═══════════════════════════════════════════════════════
aktif = st.session_state.sayfa

try:
    # Streamlit >= 1.37: st.bottom() ekranın en altına sabitler
    bottom = st.bottom()
except AttributeError:
    # Eski sürüm fallback
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
            # Aktif sekmeyi vurgula
            btn_label = f"**{icon}**\n{label}" if aktif == key else f"{icon}\n{label}"
            if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
                st.session_state.sayfa = key
                st.rerun()
