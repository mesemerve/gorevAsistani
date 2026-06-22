# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import random

# --- 1. AYARLAR ---
# Streamlit Cloud -> Manage App -> Settings -> Secrets kısmında tanımladığından emin ol
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Yapılandırma
genai.configure(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Kodlama Macerası", page_icon="🎮", layout="wide")

# CSS: Tepe Boşluğunu Sıfırla
st.markdown("<style>.block-container {padding-top: 1rem !important;}</style>", unsafe_allow_html=True)

# --- 2. OTURUM YÖNETİMİ ---
if "ogrenci_adi" not in st.session_state:
    st.session_state.ogrenci_adi = None
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "rozetler" not in st.session_state:
    st.session_state.rozetler = []

# --- 3. GİRİŞ EKRANI ---
if st.session_state.ogrenci_adi is None:
    st.title("🎮 KODLAMA MACERASI: AKADEMİ")
    st.subheader("Maceraya Katılmak İçin Kullanıcı Adını Yaz!")
    
    girilen_ad = st.text_input("Kullanıcı Adı (Örn: Ahmet_06):", max_chars=20).strip()
    
    if st.button("🚀 Giriş Yap / Kaydol"):
        if girilen_ad:
            try:
                veri = supabase.table("ogrenciler").select("*").eq("isim", girilen_ad).execute()
                if len(veri.data) > 0:
                    st.session_state.ogrenci_adi = veri.data[0]["isim"]
                    st.session_state.xp = veri.data[0]["xp"]
                    st.session_state.rozetler = veri.data[0]["rozetler"]
                    st.success(f"Tekrar hoş geldin, {girilen_ad}!")
                else:
                    yeni_veri = {"isim": girilen_ad, "xp": 0, "rozetler": []}
                    supabase.table("ogrenciler").insert(yeni_veri).execute()
                    st.session_state.ogrenci_adi = girilen_ad
                    st.session_state.xp = 0
                    st.session_state.rozetler = []
                    st.success(f"Profilin oluşturuldu, {girilen_ad}! Macera başlıyor.")
                st.rerun()
            except Exception as e:
                st.error(f"Veritabanı hatası: {e}")
        else:
            st.warning("Lütfen kullanıcı adı girin.")
    st.stop()

# --- 4. ANA UYGULAMA ---
st.title("🎮 KODLAMA MACERASI: AKADEMİ")
st.write(f"Hoş geldin, **{st.session_state.ogrenci_adi}**!")

sol_kolon, bosluk, sag_kolon = st.columns([5, 1, 3])

with sol_kolon:
    st.subheader("🤖 Dijital Rehberini Seç")
    avatar = st.selectbox("Sana kim rehberlik etsin?", ["Siber Kedi Pixel", "Kerem Usta"])
    avatar_isim = "Siber Kedi Pixel" if "Pixel" in avatar else "Kerem Usta"
    avatar_tarz = "Neşeli, ipucu veren" if "Pixel" in avatar else "Tecrübeli, usta-çırak dili"

    sekme1, sekme2 = st.tabs(["🚀 Görev Al", "🔍 Kodunu Denetlet"])

    with sekme1:
        yas = st.selectbox("Seviyeniz:", ["İlkokul", "Ortaokul", "Lise"])
        ilgi = st.text_input("İlgi alanın:")
        if st.button("🎲 Görevi Başlat"):
            if ilgi:
                with st.spinner("Görev hazırlanıyor..."):
                    try:
                        talimat = f"Sen {avatar_isim}'sin. Karakterin: {avatar_tarz}. {yas} seviyesindeki bir öğrenciye {ilgi} ile ilgili kodlama görevi yaz."
                        model = genai.GenerativeModel("gemini-1.5-flash-latest")
                        response = model.generate_content(talimat)
                        st.success("🎯 Görev Haritası Yüklendi!")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Yapay zeka hatası: {e}")

    with sekme2:
        st.subheader("💻 Hacker Terminali")
        kod_dili = st.radio("Dil:", ["Python", "Scratch"], horizontal=True)
        ogrenci_kodu = st.text_area("Kodlarını Buraya Yaz:", height=200)
        
        if st.button("⚡ Kodumu Test Et"):
            if ogrenci_kodu:
                with st.spinner("Analiz ediliyor..."):
                    try:
                        kontrol = f"Sen {avatar_isim}'sin. Öğrenci {kod_dili} dilinde şu kodu yazdı: {ogrenci_kodu}. Kod doğruysa 'BAŞARILI' ile başla, değilse düzeltme yap."
                        model = genai.GenerativeModel("gemini-1.5-flash-latest")
                        response = model.generate_content(kontrol)
                        sonuc = response.text
                        
                        st.info(f"📝 {avatar_isim} Geri Bildirimi:")
                        st.write(sonuc)
                        
                        puan = 5
                        rozet = None
                        if "BAŞARILI" in sonuc.upper():
                            st.balloons()
                            puan = random.randint(30, 50)
                            st.success(f"🎉 GÖREV BAŞARILI! {puan} XP Kazandın!")
                            if "🏅 Hata_Avcısı" not in st.session_state.rozetler: rozet = "🏅 Hata_Avcısı"
                        else:
                            st.warning("⚡ Biraz daha çalışmalısın! +5 XP.")

                        # Güncelleme
                        yeni_xp = st.session_state.xp + puan
                        data = {"xp": yeni_xp}
                        if rozet:
                            st.session_state.rozetler.append(rozet)
                            data["rozetler"] = st.session_state.rozetler
                        
                        supabase.table("ogrenciler").update(data).eq("isim", st.session_state.ogrenci_adi).execute()
                        st.session_state.xp = yeni_xp
                        st.rerun()
                    except Exception as e:
                        st.error(f"İşlem yapılamadı: {e}")
            else:
                st.warning("Kod kutusuna bir şey yazmalısın.")

with sag_kolon:
    st.subheader("📊 Senin Durumun")
    st.metric("⚡ Puanın", f"{st.session_state.xp} XP")
    if st.session_state.rozetler:
        st.write("🏅 **Rozetler:** " + " ".join(st.session_state.rozetler))
    
    st.write("---")
    st.subheader("🏆 Liderlik Tablosu")
    try:
        tum_sinif = supabase.table("ogrenciler").select("isim", "xp").order("xp", desc=True).execute()
        for sira, ogrenci in enumerate(tum_sinif.data, start=1):
            st.write(f"{sira}. {ogrenci['isim']}: {ogrenci['xp']} XP")
    except:
        st.write("Sıralama yüklenemedi.")
