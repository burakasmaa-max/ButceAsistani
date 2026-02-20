import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime

# Sayfa Ayarları (Geniş ekran, bankacılık teması)
st.set_page_config(page_title="Finansal Asistan", page_icon="🏦", layout="wide")

# Modern Arayüz İçin Özel CSS (Banka Uygulaması Görünümü)
st.markdown("""
<style>
    /* Metrik (Kart) Tasarımları */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        border-left: 6px solid #2e86de;
    }
    /* Buton Tasarımları */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Arka Plan ve Yazı Tipleri */
    .stApp {
        background-color: #f4f7f6;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "butce_veritabaniniz.json"

# --- VERİ YÖNETİMİ ---
def veri_yukle():
    if not os.path.exists(DATA_FILE):
        return {"gelirler": [], "giderler": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def veri_kaydet(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

app_data = veri_yukle()

# Verileri Pandas DataFrame'e Çevir ve Tarihleri Düzenle
df_gelir = pd.DataFrame(app_data.get("gelirler", []))
df_gider = pd.DataFrame(app_data.get("giderler", []))

# Giderler için tarih ayrıştırma (Aylık analiz için)
ay_isimleri = {1:"Ocak", 2:"Şubat", 3:"Mart", 4:"Nisan", 5:"Mayıs", 6:"Haziran", 
               7:"Temmuz", 8:"Ağustos", 9:"Eylül", 10:"Ekim", 11:"Kasım", 12:"Aralık"}

if not df_gider.empty:
    df_gider['tarih_dt'] = pd.to_datetime(df_gider['tarih'], format='%d.%m.%Y', errors='coerce')
    df_gider['Yıl'] = df_gider['tarih_dt'].dt.year.fillna(datetime.now().year).astype(int)
    df_gider['Ay_No'] = df_gider['tarih_dt'].dt.month.fillna(datetime.now().month).astype(int)
    df_gider['Ay'] = df_gider['Ay_No'].map(ay_isimleri)
    df_gider['Ay-Yıl'] = df_gider['Ay'] + " " + df_gider['Yıl'].astype(str)

# --- YAN MENÜ (SIDEBAR) TASARIMI ---
st.sidebar.title("🏦 Menü")
st.sidebar.markdown("---")
sayfa = st.sidebar.radio("İşlemler", [
    "📊 Finansal Özet", 
    "➕ Yeni İşlem Ekle", 
    "📈 Detaylı Analiz",
    "⚙️ Kayıtları Düzenle / Sil"
])

toplam_gelir = df_gelir['tutar'].sum() if not df_gelir.empty else 0
toplam_gider = df_gider['tutar'].sum() if not df_gider.empty else 0
net_durum = toplam_gelir - toplam_gider

# ================= 1. FİNANSAL ÖZET =================
if sayfa == "📊 Finansal Özet":
    st.title("Güncel Finansal Durum")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Toplam Gelir", f"₺ {toplam_gelir:,.2f}")
    with col2:
        st.metric("Toplam Gider", f"₺ {toplam_gider:,.2f}")
    with col3:
        st.metric("Net Bakiye (Kalan)", f"₺ {net_durum:,.2f}", delta=f"{net_durum:,.2f}")

    st.markdown("---")
    if not df_gider.empty:
        st.subheader("Son Gerçekleşen Harcamalar")
        son_islemler = df_gider[['tarih', 'kisi', 'kategori', 'aciklama', 'tutar']].copy()
        son_islemler = son_islemler.sort_values(by='tarih', ascending=False).head(5)
        st.dataframe(son_islemler, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz sistemde gösterilecek bir harcama bulunmuyor.")

# ================= 2. YENİ İŞLEM EKLE =================
elif sayfa == "➕ Yeni İşlem Ekle":
    st.title("Yeni İşlem Girişi")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("💸 Gider Girişi")
        with st.form("gider_formu", clear_on_submit=True):
            gid_tutar = st.number_input("Harcama Tutarı (TL):", min_value=0.0, step=50.0)
            gid_kisi = st.selectbox("Harcamayı Yapan / Kime Ait:", ["Burak", "Kerime", "Ece", "Berkay", "Genel"])
            gid_kategori = st.selectbox("Harcama Kategorisi:", ["Eğitim", "Akaryakıt", "Fatura", "Market", "Giyim", "Yemek", "Araç Bakım-Vergi", "İlaç", "Kredi Kartı Geçmiş Borç"])
            gid_aciklama = st.text_input("Açıklama / Detay:")
            gid_tarih = st.date_input("İşlem Tarihi:")
            
            if st.form_submit_button("Gideri Kaydet", use_container_width=True):
                if gid_tutar > 0:
                    yeni_gider = {
                        "tutar": gid_tutar,
                        "kisi": gid_kisi,
                        "kategori": gid_kategori,
                        "aciklama": gid_aciklama if gid_aciklama else "Belirtilmedi",
                        "tarih": gid_tarih.strftime("%d.%m.%Y")
                    }
                    app_data["giderler"].append(yeni_gider)
                    veri_kaydet(app_data)
                    st.success("Gider başarıyla sisteme işlendi!")
                else:
                    st.error("Lütfen geçerli bir tutar giriniz.")

    with col_g2:
        st.subheader("💰 Gelir Girişi")
        with st.form("gelir_formu", clear_on_submit=True):
            g_tutar = st.number_input("Gelir Tutarı (TL):", min_value=0.0, step=100.0)
            g_aciklama = st.text_input("Açıklama (Maaş, Prim vb.):")
            g_tarih = st.date_input("Kayıt Tarihi:")
            
            if st.form_submit_button("Geliri Kaydet", use_container_width=True):
                if g_tutar > 0:
                    yeni_gelir = {
                        "tutar": g_tutar,
                        "aciklama": g_aciklama if g_aciklama else "Belirtilmedi",
                        "tarih": g_tarih.strftime("%d.%m.%Y")
                    }
                    app_data["gelirler"].append(yeni_gelir)
                    veri_kaydet(app_data)
                    st.success("Gelir başarıyla sisteme işlendi!")
                else:
                    st.error("Lütfen geçerli bir tutar giriniz.")

# ================= 3. DETAYLI ANALİZ =================
elif sayfa == "📈 Detaylı Analiz":
    st.title("Çok Boyutlu Harcama Analizi")
    
    if df_gider.empty:
        st.warning("Analiz oluşturulabilmesi için sisteme gider verisi girmelisiniz.")
    else:
        tab1, tab2, tab3 = st.tabs(["📅 Aylık Analiz", "📂 Kategori Analizi", "👤 Kişi Analizi"])
        
        with tab1:
            aylik_gider = df_gider.groupby(['Yıl', 'Ay_No', 'Ay', 'Ay-Yıl'])['tutar'].sum().reset_index()
            aylik_gider = aylik_gider.sort_values(by=['Yıl', 'Ay_No'])
            
            fig_ay = px.bar(aylik_gider, x='Ay-Yıl', y='tutar', 
                            title="Aylara Göre Toplam Gider Trendi",
                            labels={'tutar': 'Harcama (TL)', 'Ay-Yıl': 'Dönem'},
                            text_auto='.2f', color='tutar', color_continuous_scale='Blues')
            fig_ay.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_ay, use_container_width=True)

        with tab2:
            col_kat1, col_kat2 = st.columns(2)
            with col_kat1:
                kat_gider = df_gider.groupby('kategori')['tutar'].sum().reset_index()
                fig_kat_pie = px.pie(kat_gider, values='tutar', names='kategori', 
                                     title="Giderlerin Kategorilere Dağılımı", hole=0.4)
                st.plotly_chart(fig_kat_pie, use_container_width=True)
            with col_kat2:
                # Sunburst Grafiği (Kategori içinde kim ne kadar harcamış)
                fig_sunburst = px.sunburst(df_gider, path=['kategori', 'kisi'], values='tutar',
                                           title="Kategori ve Kişi Kırılımı")
                st.plotly_chart(fig_sunburst, use_container_width=True)

        with tab3:
            col_kisi1, col_kisi2 = st.columns(2)
            kisi_gider = df_gider.groupby('kisi')['tutar'].sum().reset_index()
            with col_kisi1:
                fig_kisi_bar = px.bar(kisi_gider.sort_values('tutar'), x='tutar', y='kisi', 
                                      orientation='h', title="Kişilere Göre Toplam Harcama",
                                      color='tutar', color_continuous_scale='Teal')
                st.plotly_chart(fig_kisi_bar, use_container_width=True)
            with col_kisi2:
                # Zaman içinde kişilerin harcama trendi
                kisi_aylik = df_gider.groupby(['Ay-Yıl', 'kisi', 'Yıl', 'Ay_No'])['tutar'].sum().reset_index()
                kisi_aylik = kisi_aylik.sort_values(by=['Yıl', 'Ay_No'])
                fig_kisi_line = px.line(kisi_aylik, x='Ay-Yıl', y='tutar', color='kisi', 
                                        markers=True, title="Kişilerin Aylık Harcama Trendi")
                st.plotly_chart(fig_kisi_line, use_container_width=True)

# ================= 4. KAYITLARI DÜZENLE / SİL =================
elif sayfa == "⚙️ Kayıtları Düzenle / Sil":
    st.title("Veri Yönetimi ve Düzeltme")
    st.info("💡 **Nasıl Silinir/Düzenlenir?** Tablodaki herhangi bir hücreye tıklayıp veriyi değiştirebilirsiniz. Bir satırı silmek için o satırın sol tarafındaki kutucuğu işaretleyip klavyenizden 'Delete' tuşuna basabilir veya sağ üst köşede beliren çöp kutusu simgesine tıklayabilirsiniz. İşlemleriniz bitince en alttaki **Kaydet** butonuna basmayı unutmayın.")
    
    st.subheader("Gider Kayıtları")
    if not df_gider.empty:
        # Görsel kolonları (Ay, Yıl vb.) dahil etmeden sadece saf veriyi düzenletelim
        gider_saf = df_gider[['tarih', 'kisi', 'kategori', 'aciklama', 'tutar']]
        edited_gider = st.data_editor(gider_saf, num_rows="dynamic", use_container_width=True, key="gider_editor")
        
        if st.button("Gider Değişikliklerini Kaydet", type="primary"):
            app_data["giderler"] = edited_gider.to_dict('records')
            veri_kaydet(app_data)
            st.success("Gider kayıtları başarıyla güncellendi!")
            st.rerun()
    else:
        st.write("Silinecek veya düzenlenecek gider kaydı yok.")

    st.markdown("---")
    
    st.subheader("Gelir Kayıtları")
    if not df_gelir.empty:
        edited_gelir = st.data_editor(df_gelir, num_rows="dynamic", use_container_width=True, key="gelir_editor")
        
        if st.button("Gelir Değişikliklerini Kaydet", type="primary"):
            app_data["gelirler"] = edited_gelir.to_dict('records')
            veri_kaydet(app_data)
            st.success("Gelir kayıtları başarıyla güncellendi!")
            st.rerun()
    else:
        st.write("Silinecek veya düzenlenecek gelir kaydı yok.")