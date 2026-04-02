import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pyotp
import os

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="MEF Global Sigorta - Yönetim Paneli",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ÖZEL CSS TASARIMI (Logosuz ve Ortalanmış Giriş Ekranı) ---
st.markdown("""
<style>
    /* Genel Arka Plan */
    .stApp {
        background-color: #f0f2f5;
    }
    
    /* GİRİŞ EKRANI KURUMSAL ÜST BAŞLIK */
    .kurumsal-header {
        background-color: #1e3a8a; /* Kurumsal Koyu Mavi */
        padding: 40px 20px;
        border-radius: 15px 15px 0 0;
        margin-bottom: 0px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        
        /* İçerikleri milimetrik ORTALIYORUZ */
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }

    /* Yazılar */
    .kurumsal-header h2 {
        color: white !important;
        margin: 0 !important;
        font-weight: 700 !important;
        font-size: 28px !important;
        text-align: center !important;
        width: 100%;
    }

    .kurumsal-header h4 {
        color: #e2e8f0 !important;
        margin: 10px 0 0 0 !important;
        font-weight: 400 !important;
        opacity: 0.9;
        font-size: 16px !important;
        text-align: center !important;
        width: 100%;
    }

    /* Giriş Kartı */
    .login-box {
        background-color: white;
        padding: 40px;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        border-top: none;
        margin-bottom: 50px;
    }
    
    /* Metrik Kartları Tasarımı */
    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
    }
    
    /* Buton Tasarımları */
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- KLASÖR VE DOSYA KONTROLLERİ (İnternet Uyumlu Güncelleme) ---
# Dosyaları artık masaüstünde değil, uygulamanın çalıştığı ana klasörde tutuyoruz.
EXCEL_DOSYASI = "police_veritabani.xlsx"
KURULUM_DOSYASI = "auth_durumu.txt"

# --- EXCEL VERİ TABANI AYARLARI ---
if not os.path.exists(EXCEL_DOSYASI):
    df_bos = pd.DataFrame(columns=[
        'Police No', 'Musteri Adi Soyadi', 'Plaka', 'Police Türü', 
        'Sigorta Şirketi', 'Acente', 'Net Prim (TL)', 'Brüt Prim (TL)', 'Komisyon (TL)',
        'Tanzim Tarihi', 'Başlangıç Tarihi', 'Bitiş Tarihi'
    ])
    df_bos.to_excel(EXCEL_DOSYASI, index=False)

def verileri_yukle():
    return pd.read_excel(EXCEL_DOSYASI)

def veri_kaydet(yeni_satir):
    df_mevcut = verileri_yukle()
    df_yeni = pd.DataFrame([yeni_satir])
    df_guncel = pd.concat([df_mevcut, df_yeni], ignore_index=True)
    df_guncel.to_excel(EXCEL_DOSYASI, index=False)

otp_secret = "JBSWY3DPEHPK3PXP" 
totp = pyotp.TOTP(otp_secret)

# --- GİRİŞ EKRANLARI ---
def sifre_kontrol():
    if "giris_yapildi" not in st.session_state:
        st.session_state.giris_yapildi = False
    if "sifre_dogrulandi" not in st.session_state:
        st.session_state.sifre_dogrulandi = False

    # 1. ADIM: ŞİFRE EKRANI
    if not st.session_state.sifre_dogrulandi:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("""
            <div class='kurumsal-header'>
                <h2>MEF Global Sigorta</h2>
                <h4>Yönetim Paneli Girişi</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='login-box'>", unsafe_allow_html=True)
            with st.form("giris_formu"):
                kullanici = st.text_input("👤 Kullanıcı Adı", placeholder="Kullanıcı adınızı girin")
                sifre = st.text_input("🔑 Şifre", type="password", placeholder="Şifrenizi girin")
                st.write("")
                buton = st.form_submit_button("Devam Et ➡️", use_container_width=True)
                if buton:
                    if kullanici == "admin" and sifre == "mef123":
                        st.session_state.sifre_dogrulandi = True
                        st.rerun()
                    else:
                        st.error("❌ Hatalı kullanıcı adı veya şifre!")
            st.markdown("</div>", unsafe_allow_html=True)
        return False

    # 2. ADIM: 2FA KODU EKRANI
    elif st.session_state.sifre_dogrulandi and not st.session_state.giris_yapildi:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("""
            <div class='kurumsal-header'>
                <h2>İki Faktörlü Doğrulama</h2>
                <h4>Kurulum ve Giriş</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='login-box'>", unsafe_allow_html=True)
            if not os.path.exists(KURULUM_DOSYASI):
                st.warning("📣 Bu anahtarı telefonunuzdaki Google Authenticator uygulamasına BİR KEZ ekleyin.")
                st.info(f"Anahtar kod: *{otp_secret}*")
                if st.button("Kurulumu Tamamladım, Anahtarı Gizle 🕵️‍♂️", use_container_width=True):
                    with open(KURULUM_DOSYASI, "w") as f:
                        f.write("Kurulum Tamamlandi")
                    st.success("Kurulum başarıyla kaydedildi!")
                    st.rerun()
                st.divider()
            with st.form("auth_formu"):
                kod = st.text_input("📱 Telefonunuzdaki 6 Haneli Kodu Giriniz", max_chars=6, placeholder="000000")
                st.write("")
                onayla = st.form_submit_button("Giriş Yap ✅", use_container_width=True)
                if onayla:
                    if totp.verify(kod):
                        st.session_state.giris_yapildi = True
                        st.rerun()
                    else:
                        st.error("❌ Geçersiz veya süresi dolmuş kod!")
            st.markdown("</div>", unsafe_allow_html=True)
        return False
        
    return True

# --- ASIL PROGRAM (PANELE GİRİŞ) ---
if sifre_kontrol():
    st.markdown("<h1 style='margin-bottom: 0px;'>MEF Global Sigorta</h1><h3 style='margin-top: -10px; color: #64748b; font-weight: 400;'>Poliçe Takip ve Yönetim Sistemi</h3>", unsafe_allow_html=True)
    st.divider()
    
    df_policeler = verileri_yukle()

    # --- YENİ POLİÇE EKLEME ALANI (SOL MENÜ) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>➕ Yeni Poliçe</h2>", unsafe_allow_html=True)
        st.write("")
        with st.form("police_formu", clear_on_submit=True):
            police_no = st.text_input("📄 Poliçe Numarası")
            musteri = st.text_input("👤 Müşteri Adı Soyadı")
            plaka = st.text_input("🚗 Araç Plakası (Varsa)")
            tur = st.selectbox("📋 Poliçe Türü", ["Trafik", "Kasko", "DASK", "Sağlık", "Konut", "Diğer"])
            sirketler_listesi = ["ZURICH_ZIPPLUS", "VHV", "UNICO_CORE", "TURKNIPPON", "TURKIYE_KATILIM", "SEKER", "REFERANS", "RAY", "QUICK_PORTAL", "PRIVE", "NEOVA", "MAGDEBURGPORTAL", "KORU", "HEPIYI", "HDI", "GIG", "CORPUS", "BEREKET", "AXA", "ATLAS", "ANKARA", "ANADOLU", "HDI_PLUS", "SOMPO", "DOGA", "ALLIANZ", "AK", "MAPFRE", "TURKIYE"]
            sirket = st.selectbox("🏢 Sigorta Şirketi", sirketler_listesi)
            acenteler_listesi = ["MEF GLOBAL SIGORTA", "LIKE SIGORTA", "IXIR SIGORTA", "SIGORTACOM SIGORTA", "VOLDEM SIGORTA", "STORY SIGORTA", "ADYA SIGORTA"]
            acente = st.selectbox("🤝 Acente", acenteler_listesi)
            
            col_prim1, col_prim2 = st.columns(2)
            with col_prim1:
                net_prim = st.number_input("💰 Net Prim (TL)", min_value=0.0, step=100.0)
                komisyon = st.number_input("💸 Komisyon (TL)", min_value=0.0, step=50.0)
            with col_prim2:
                brut_prim = st.number_input("💵 Brüt Prim (TL)", min_value=0.0, step=100.0)
                
            tanzim = st.date_input("📅 Tanzim Tarihi", datetime.now())
            col_tarih1, col_tarih2 = st.columns(2)
            with col_tarih1:
                baslangic = st.date_input("🏁 Başlangıç", datetime.now())
            with col_tarih2:
                bitis = st.date_input("🔚 Bitiş", datetime.now() + timedelta(days=365))
                
            st.write("")
            submit = st.form_submit_button("Poliçeyi Kaydet 💾", use_container_width=True)
            
            if submit:
                if police_no and musteri:
                    yeni_veri = {
                        'Police No': police_no,
                        'Musteri Adi Soyadi': musteri,
                        'Plaka': plaka if plaka else "-",
                        'Police Türü': tur,
                        'Sigorta Şirketi': sirket,
                        'Acente': acente,
                        'Net Prim (TL)': net_prim,
                        'Brüt Prim (TL)': brut_prim,
                        'Komisyon (TL)': komisyon,
                        'Tanzim Tarihi': tanzim.strftime('%Y-%m-%d'),
                        'Başlangıç Tarihi': baslangic.strftime('%Y-%m-%d'),
                        'Bitiş Tarihi': bitis.strftime('%Y-%m-%d')
                    }
                    veri_kaydet(yeni_veri)
                    st.success("✅ Poliçe başarıyla kaydedildi!")
                    st.rerun() 
                else:
                    st.error("⚠️ Lütfen Poliçe No ve Müşteri Adı alanlarını boş bırakmayın.")

    # --- POLİÇE LİSTELEME VE FİLTRELEME ALANI ---
    st.markdown("<h3 style='margin-top: 20px;'>📊 Mevcut Poliçeler ve Filtreleme</h3>", unsafe_allow_html=True)
    df_goster = df_policeler.copy()
    col_ara, col_bas, col_bit = st.columns([2, 1, 1])
    
    with col_ara:
        arama = st.text_input("🔍 Ara (Müşteri, Plaka veya Poliçe No)", placeholder="Müşteri adı veya plaka yazın...")
    
    # Dinamik Tarih Filtreleme (Bulunulan Ayın Başı ve Sonu)
    simdi = datetime.now()
    ayin_basi = datetime(simdi.year, simdi.month, 1)
    
    with col_bas:
        filtre_baslangic = st.date_input("📅 Filtre Başlangıç", ayin_basi)
    with col_bit:
        filtre_bitis = st.date_input("📅 Filtre Bitiş", simdi.date())

    # Filtreleme İşlemleri
    if not df_goster.empty:
        df_goster['Tanzim Tarihi DT'] = pd.to_datetime(df_goster['Tanzim Tarihi'])
        bas_dt = pd.to_datetime(filtre_baslangic)
        bit_dt = pd.to_datetime(filtre_bitis)
        df_goster = df_goster[(df_goster['Tanzim Tarihi DT'] >= bas_dt) & (df_goster['Tanzim Tarihi DT'] <= bit_dt)]
        df_goster = df_goster.drop(columns=['Tanzim Tarihi DT'])
        
        if arama:
            df_goster = df_goster[
                df_goster['Musteri Adi Soyadi'].str.contains(arama, case=False, na=False) |
                df_goster['Police No'].str.contains(str(arama), case=False, na=False) |
                df_goster['Plaka'].str.contains(arama, case=False, na=False)
            ]

    # Metrikleri ve Tabloyu Ekrana Basma
    if not df_goster.empty:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Toplam Net Prim", f"{df_goster['Net Prim (TL)'].sum():,.2f} TL")
        with col_m2:
            st.metric("Toplam Brüt Prim", f"{df_goster['Brüt Prim (TL)'].sum():,.2f} TL")
        with col_m3:
            st.metric("Kazanılan Komisyon", f"{df_goster['Komisyon (TL)'].sum():,.2f} TL")
        with col_m4:
            st.metric("Kayıtlı Poliçe", f"{len(df_goster)} Adet")
        
        st.write("")
        st.divider()
        st.dataframe(df_goster, use_container_width=True)
    else:
        st.info("ℹ️ Bu tarih aralığında veya arama kriterinde bir poliçe bulunamadı.")