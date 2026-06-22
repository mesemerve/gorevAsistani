# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import random
import os

# --- 1. BAĞLANTI AYARLARI (Buraları Doldurun) ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Stabil kütüphane için yapay zeka yapılandırması
genai.configure(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- TARAYICI AYARLARI ---
st.set_page_config(page_title="Kodlama Macerasi", page_icon="🎮", layout="wide")

# Tepe Boşluğunu Sıfırlayan CSS
st.markdown("<style>.block-container {padding-top: 1rem !important; padding-bottom: 0rem !important;}</style>", unsafe_allow_html=True)

# --- GİRİŞ / OTURUM YÖNETİMİ ---
if "ogrenci_adi" not in st.session_state:
    st.session_state.ogrenci_adi = None
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "rozetler" not in st.session_state:
    st.session_state.rozetler = []

# --- EKRAN 1: GİRİŞ EKRANI (Eğer Giriş Yapılmadıysa) ---
if st.session_state.ogrenci_adi is None:
    st.title("🎮 KODLAMA MACERASI: AKADEMİ")
    st.subheader("Maceraya Katılmak İçin Kullanıcı Adını Yaz!")
    
    girilen_ad = st.text_input("Kullanıcı Adı (Örn: Ahmet_06, Selin_Kodcu):", max_chars=20).strip()
    
    if st.button("🚀 Giriş Yap / Kaydol"):
        if girilen_ad:
            try:
                # Veritabanında bu öğrenci var mı kontrol et
                veri = supabase.table("ogrenciler").select("*").eq("isim", girilen_ad).execute()
                
                if len(veri.data) > 0:
                    # Öğrenci zaten var, verilerini buluttan çek
                    st.session_state.ogrenci_adi = veri.data[0]["isim"]
                    st.session_state.xp = veri.data[0]["xp"]
                    st.session_state.rozetler = veri.data[0]["rozetler"]
                    st.success("Tekrar hoş geldin, " + girilen_ad + "! Kaldığın yerden devam ediyorsun.")
                else:
                    # Yeni öğrenci, veritabanına kaydet
                    yeni_veri = {"isim": girilen_ad, "xp": 0, "rozetler": []}
                    supabase.table("ogrenciler").insert(yeni_veri).execute()
                    st.session_state.ogrenci_adi = girilen_ad
                    st.session_state.xp = 0
                    st.session_state.rozetler = []
                    st.success("Profilin başarıyla oluşturuldu, " + girilen_ad + "! Macera başlıyor.")
                
                st.rerun()
            except Exception as e:
                st.error("Veritabanı bağlantı hatası: " + str(e))
        else:
            st.warning("Lütfen geçerli bir kullanıcı adı girin.")
            
    st.stop() # Giriş yapana kadar aşağıdaki ana sayfa kodlarını çalıştırma

# --- EKRAN 2: ANA UYGULAMA (Giriş Yapıldıysa Çalışacak) ---
st.title("🎮 KODLAMA MACERASI: AKADEMİ")
st.write("Hoş geldin, **" + st.session_state.ogrenci_adi + "**! Kodları çöz, puanları topla, rakiplerini anlık geç!")
st.write("---")

# Üç Sütunlu Canlı Düzen
sol_kolon, bosluk_kolonu, sag_kolon = st.columns([5, 1, 3])

with sol_kolon:
    # --- AVATAR / REHBER SEÇİMİ ---
    st.subheader("🤖 Dijital Rehberini Seç")
    avatar = st.selectbox(
        "Sana hangi yapay zeka karakteri rehberlik etsin?",
        ["Siber Kedi Pixel (Eğlenceli)", "Kerem Usta (Deneyimli)"]
    )

    if "Pixel" in avatar:
        avatar_isim = "Siber Kedi Pixel"
        avatar_tarz = "Konusurken neseli ol, arada miyav de. Ogrenciye minik patilerinle ipuclari birak."
    else:
        avatar_isim = "Kerem Usta"
        avatar_tarz = "Eski bir bas muhendis gibi konus. Tatli-sert ol, usta cirak dili kullan."

    st.divider()

    # Sekmeler
    sekme1, sekme2 = st.tabs(["🚀 Görev Al", "🔍 Kodunu Denetlet"])

    with sekme1:
        st.subheader("🎯 Yeni Bir Görev Keşfet")
        yas_grubu = st.selectbox(
            "Seviyeniz:",
            ["Ilkokul (Scratch)", "Ortaokul (Temel Python)", "Lise (Ileri Python)"]
        )
        ilgi_alani = st.text_input("İlgi alanın ne? (Örn: Uzay, Futbol):", placeholder="Yazın...")

        if st.button("🎲 Görevi Başlat"):
            if ilgi_alani:
                with st.spinner("Lütfen bekleyin..."):
                    try:
                        talimat = "Sen bir oyun karakterisin. Ismin: " + avatar_isim + ". Karakter tarzin: " + avatar_tarz + ". " + yas_grubu + " seviyesindeki bir ogrenci icin '" + ilgi_alani + "' ile ilgili hikayeli bir kodlama gorevi yaz. Cevabini GÖREV SENARYOSU, YAPILMASI GEREKENLER and REHBER İPUCU basliklariyla KESINLIKLE TURKCE olarak ver."
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(kontrol_talimati)
                        sonuc_metni = response.text
                        st.success("🎯 Görev Haritası Yüklendi!")
                        st.write(response.text)
                    except Exception as e:
                        st.error("Yapay zeka hatası: " + str(e))
            else:
                st.warning("Lütfen önce ilgi alanınızı yazın.")

    with sekme2:
        st.subheader("💻 Hacker Terminali")
        kod_dili = st.radio("Kodlama Dili:", ["Python", "Scratch"], horizontal=True)
        
        ogrenci_kodu = st.text_area(
            "Kodlarını Buraya Yaz / Yapıştır:", 
            height=200, 
            placeholder="Kodları buraya ekleyin..."
        )
        
        if st.button("⚡ Kodumu Test Et"):
            if ogrenci_kodu:
                with st.spinner("Analiz ediliyor..."):
                     kontrol_talimati = "Sen bir oyun karakterisin. Ismin: " + avatar_isim + ". Karakter tarzin: " + avatar_tarz + ". Ogrenci sana sunu gonderdi: " + kod_dili + ". Kod: " + ogrenci_kodu + ". Eger kod dogruysa cevaba KESINLIKLE 'BAŞARILI' kelimesiyle basla. Hata varsa Sokratik yontemle sorular sorarak TURKCE yardim et, kodu direkt verme."
                     sonuc_metni=""
                     try:
                       
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(kontrol_talimati)
                        sonuc_metni = response.text
                        
                        st.info("📝 " + avatar_isim + " Geri Bildirimi:")
                        st.write(sonuc_metni)
                        
                        # Skor Değişimi Hesaplama
                        puan_degisimi = 5
                        rozet_ekle = None
                        
                        if "BAŞARILI" in sonuc_metni.upper() or "TEBRİK" in sonuc_metni.upper():
                            st.balloons() 
                            puan_degisimi = random.randint(30, 50)
                            st.success("🎉 GÖREV BAŞARILI! " + str(puan_degisimi) + " XP Kazandın!")
                            
                            if "🏅 Hata_Avcısı" not in st.session_state.rozetler:
                                rozet_ekle = "🏅 Hata_Avcısı"
                            elif "🏅 Kod_Ustası" not in st.session_state.rozetler:
                                rozet_ekle = "🏅 Kod_Ustası"
                        else:
                            st.warning("⚡ Kod üzerinde biraz daha çalışmalısın! Deneme Bonusu: +5 XP Kazandın.")
                        
                        # --- BULUT VERİTABANINI GÜNCELLEME ---
                        yeni_toplam_xp = st.session_state.xp + puan_degisimi
                        guncelleme_verisi = {"xp": yeni_toplam_xp}
                        
                        if rozet_ekle and rozet_ekle not in st.session_state.rozetler:
                            st.session_state.rozetler.append(rozet_ekle)
                            st.toast("Yeni Rozet Açıldı: " + rozet_ekle + "!", icon="🏆")
                            guncelleme_verisi["rozetler"] = st.session_state.rozetler
                            
                        # Supabase Güncelleme Sorgusu
                        supabase.table("ogrenciler").update(guncelleme_verisi).eq("isim", st.session_state.ogrenci_adi).execute()
                        
                        # Yerel Hafızayı Güncelle ve Sayfayı Yenile
                        st.session_state.xp = yeni_toplam_xp
                        st.rerun()
                        
                    except Exception as e:
                        st.error("İşlem gerçekleştirilemedi: " + str(e))
            else:
                st.warning("Denetlemek için önce kod kutusuna bir şeyler yazmalısın.")

# --- ORTADAKİ BOŞ SÜTUN ---
with bosluk_kolonu:
    st.write("")

# --- EN SAĞDAKİ SÜTUN (Eşzamanlı Canlı Skor Paneli) ---
with sag_kolon:
    st.subheader("📊 Senin Durumun")
    
    skor_1, skor_2 = st.columns(2)
    with skor_1:
        st.metric(label="⚡ Puanın", value=str(st.session_state.xp) + " XP")
    with skor_2:
        seviye = (st.session_state.xp // 100) + 1
        st.metric(label="🛡️ Seviyen", value="Seviye " + str(seviye))
        
    if st.session_state.rozetler:
        st.write("🏅 **Rozetlerin:** " + " ".join(st.session_state.rozetler))
        
    st.write("---")
    
    st.subheader("🏆 Canlı Liderlik Tablosu")
    st.write("Sınıf İçi Eşzamanlı Sıralama:")
    
    try:
        # BULUTTAN TÜM ÖĞRENCİLERİN ANLIK PUANLARINI ÇEK
        tum_sinif = supabase.table("ogrenciler").select("isim", "xp").order("xp", desc=True).execute()
        
        # Veritabanından gelen canlı listeyi ekrana bas
        for sira, ogrenci in enumerate(tum_sinif.data, start=1):
            if sira == 1: madalya = "🥇"
            elif sira == 2: madalya = "🥈"
            elif sira == 3: madalya = "🥉"
            else: madalya = "👤"
                
            kullanici_ismi = ogrenci["isim"]
            puanı = ogrenci["xp"]
            
            # Eğer satırdaki kişi o an ekranı açan öğrenciyse onu vurgula
            if kullanici_ismi == st.session_state.ogrenci_adi:
                st.markdown("**" + madalya + " " + str(sira) + ". " + kullanici_ismi + ": " + str(puanı) + " XP** 👈")
            else:
                st.write(madalya + " " + str(sira) + ". " + kullanici_ismi + ": " + str(puanı) + " XP")
                
    except Exception as e:
        st.write("Sıralama şu an güncellenemiyor...")
