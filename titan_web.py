import streamlit as st
import pandas as pd
import numpy as np
import math
import re
from datetime import datetime

# ==========================================
# VIP TASARIM & CSS (SABİT)
# ==========================================
st.set_page_config(page_title="TITAN PRO V.21 - ANALYTICS MODE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    
    /* Bilgi ve Sonuç Kutuları */
    .b-success { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 8px; font-weight: bold; margin-bottom: 20px; border: 2px solid #86efac; }
    .b-trap { background-color: #fee2e2; color: #991b1b; padding: 15px; border-radius: 8px; font-weight: bold; margin-bottom: 10px; border: 2px solid #fca5a5; }
    .b-value { background-color: #eff6ff; color: #1e40af; padding: 15px; border-radius: 8px; font-weight: bold; margin-bottom: 10px; border: 2px solid #bfdbfe; }
    
    .god-stat-box { background-color: white; border-radius: 10px; padding: 20px; text-align: center; border: 2px solid #cbd5e1; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;}
    .god-stat-value { font-size: 40px; font-weight: 900; color: #ea580c; }
    
    .custom-table { width: 100%; border-collapse: collapse; font-size: 13px; color: #0f172a; margin-bottom: 20px; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
    .custom-table th { padding: 12px 8px; background-color: #f1f5f9; border-bottom: 2px solid #cbd5e1; color: #0f172a; text-align: left; font-weight: bold;}
    .custom-table td { padding: 10px 8px; border-bottom: 1px solid #e2e8f0; }
    
    div.stButton > button { 
        background-color: #2563eb; color: white; border-radius: 8px; height: 50px; font-weight: bold; width: 100%; 
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# MATEMATİKSEL MOTOR & YARDIMCI FONKSİYONLAR
# ==========================================

def calculate_weight(date_val):
    """Maçın tarihine göre ağırlık hesaplar (Yeni maçlar daha değerli)"""
    try:
        match_date = pd.to_datetime(date_val)
        days_diff = (datetime.now() - match_date).days
        # Logaritmik azalma: Son 1 yıl yüksek ağırlık
        weight = 1 / (1 + (days_diff / 365))
        return weight
    except:
        return 1.0

def calculate_confidence(sample_size):
    """Örneklem sayısına göre güven yüzdesi hesaplar"""
    if sample_size == 0: return "Veri Yok"
    if sample_size < 5: return "Çok Düşük (Riskli)"
    if sample_size < 15: return "Orta (Dikkatli)"
    if sample_size < 30: return "Yüksek"
    return "Çok Yüksek (Güvenilir)"

def get_implied_probability(odds):
    """Oranı olasılığa çevirir (1/oran)"""
    try:
        return (1 / float(odds)) * 100
    except:
        return 0

# ==========================================
# AKILLI VERİ YÜKLEME (HATASIZ VERSİYON)
# ==========================================
@st.cache_data
def load_data_final():
    try:
        df = pd.read_excel("ORAN ANALİZ TABLOSU.xlsb", sheet_name="Sayfa1", engine="pyxlsb")
        
        # Sayısal olması gereken sütunların indeksleri
        SAYI_SUTUNLAR = [4,5,6,7,8,9,10,11,12,13,14,15,24,25,26,27,28,29,36,37,38,39,40,41]
        
        for c in SAYI_SUTUNLAR:
            if c < len(df.columns):
                col_data = df.iloc[:, c]
                # SÜTUN ZATEN SAYISALSA dokunma, sadece boşlukları doldur
                if pd.api.types.is_numeric_dtype(col_data):
                    df.iloc[:, c] = col_data.fillna(0.0)
                else:
                    # SÜTUN METİNSE, virgülleri noktaya çevir ve sayıya zorla
                    df.iloc[:, c] = pd.to_numeric(
                        col_data.astype(str).str.replace(',', '.', regex=False).str.strip(), 
                        errors='coerce'
                    ).fillna(0.0)
        return df
    except Exception as e:
        st.error(f"Veri yükleme hatası: {str(e)}")
        return None

df_master = load_data_final()

# ==========================================
# GELİŞMİŞ MAÇ BULMA FONKSİYONU
# ==========================================
def get_matches_advanced(ms_val, iy_val, tolerans_degeri, lig_val="TÜM LİGLER", birebir_mod=False):
    if df_master is None: return None
    try:
        ms_cl = ms_val.replace(',', '.').strip()
        if ' ' in ms_cl and '-' not in ms_cl: ms_cl = '-'.join(ms_cl.split())
        d1, d0, d2 = map(float, ms_cl.split('-'))
        
        temp = df_master.copy()
        m1 = temp.iloc[:, 4].astype(float).values
        m0 = temp.iloc[:, 5].astype(float).values
        m2 = temp.iloc[:, 6].astype(float).values

        if birebir_mod:
            mask = (np.abs(m1 - d1) <= 0.05) & (np.abs(m0 - d0) <= 0.05) & (np.abs(m2 - d2) <= 0.05)
        else:
            dist = np.sqrt((m1 - d1)**2 + (m0 - d0)**2 + (m2 - d2)**2)
            mask = (1 - (dist / 0.5)) * 100 >= tolerans_degeri
            
        sonuclar = temp[mask].copy()

        if lig_val != "TÜM LİGLER":
            mask_lig = sonuclar.iloc[:, 0].astype(str).str.upper().str.contains(lig_val.upper(), na=False)
            sonuclar = sonuclar[mask_lig]
        
        # Tarih ağırlıklandırmasını ekle
        sonuclar['Weight'] = sonuclar.iloc[:, 1].apply(calculate_weight)
        
        return sonuclar
    except Exception as e:
        return None

# ==========================================
# ANA ARAYÜZ
# ==========================================
st.markdown("<h2 style='text-align: center; color: #ea580c;'>🚜 TITAN PRO V.21 - ANALYTICS</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size:12px;'>AĞIRLIKLANDIRILMIŞ VERİ ANALİZİ | GÜVEN ENDEKSLİ TAHMİN</p>", unsafe_allow_html=True)

if df_master is None: 
    st.error("❌ Veritabanı okunamadı! 'ORAN ANALİZ TABLOSU.xlsb' dosyasını kontrol et.")
    st.stop()

ligler_listesi = ["TÜM LİGLER"] + sorted(df_master.iloc[:, 0].dropna().astype(str).unique().tolist())
tabs = st.tabs(["🎯 Stratejik Analiz", "🔄 Jackpot Avcısı", "🧠 YZ Uzman Modu"])

# ------------------------------------------
# TAB 1: STRATEJİK ANALİZ
# ------------------------------------------
with tabs[0]:
    st.markdown("### 🎯 HASSAS ANALİZ PANELİ")
    col_ms, col_iy = st.columns(2)
    with col_ms:
        ms_in = st.text_input("MS Oranları (1-X-2) *", placeholder="1.85-3.10-2.45")
    with col_iy:
        iy_in = st.text_input("İY Oranları (Opsiyonel)", placeholder="2.40-2.10-3.30")

    col_l, col_t = st.columns(2)
    lig_sel = col_l.selectbox("Lig Seç", ligler_listesi)
    tol1 = col_t.slider("Hassasiyet (%)", 60, 100, 85)
    
    birebir_checkbox = st.checkbox("🎯 Sadece Birebir Oranlar")

    if st.button("🔥 ANALİZ ET"):
        if not ms_in:
            st.error("❌ MS Oranları zorunlu!")
        else:
            res = get_matches_advanced(ms_in, iy_in, tol1, lig_sel, birebir_checkbox)
            
            if res is not None and len(res) > 0:
                toplam = len(res)
                sum_weights = res['Weight'].sum()
                
                # Ağırlıklı istatistik hesaplama
                w_ms1 = w_ms0 = w_ms2 = w_ust = w_kg = 0.0
                
                for _, row in res.iterrows():
                    w = row['Weight']
                    skor = str(row.iloc[17])
                    if "-" in skor:
                        try:
                            e, d = map(int, skor.split("-"))
                            if e > d: w_ms1 += w
                            elif e == d: w_ms0 += w
                            else: w_ms2 += w
                            if (e+d) > 2.5: w_ust += w
                            if e>0 and d>0: w_kg += w
                        except: pass
                
                p1, p0, p2 = (w_ms1/sum_weights)*100, (w_ms0/sum_weights)*100, (w_ms2/sum_weights)*100
                p_ust, p_kg = (w_ust/sum_weights)*100, (w_kg/sum_weights)*100
                
                # Value Analizi
                d1, d0, d2 = map(float, ms_in.replace(',', '.').split('-'))
                imp_p1 = get_implied_probability(d1)
                value_diff = p1 - imp_p1
                
                # Sonuçlar
                st.markdown(f"<div class='b-success'>✅ Eşleşen Maç: {toplam} | Güven Endeksi: {calculate_confidence(toplam)}</div>", unsafe_allow_html=True)
                
                if value_diff > 10:
                    st.markdown(f"<div class='b-value'>💎 VALUE ALERT! Arşiv %{p1:.1f} diyor, İddaa %{imp_p1:.1f} diyor. (Sürpriz Değeri Yüksek)</div>", unsafe_allow_html=True)
                elif value_diff < -10:
                    st.markdown(f"<div class='b-trap'>⚠️ TUZAK ORAN! İddaa favori gösteriyor ama arşiv geçmişi zayıf.</div>", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                c1.metric("MS 1 (Ağırlıklı)", f"%{p1:.1f}")
                c2.metric("MS X (Ağırlıklı)", f"%{p0:.1f}")
                c3.metric("MS 2 (Ağırlıklı)", f"%{p2:.1f}")
                
                c4, c5 = st.columns(2)
                c4.metric("2.5 ÜST", f"%{p_ust:.1f}")
                c5.metric("KG VAR", f"%{p_kg:.1f}")

                st.markdown("### 🔍 Kanıt Listesi (En Güncel Maçlar)")
                html_list = "<table class='custom-table'><tr><th>LİG</th><th>TARİH</th><th>MAÇ</th><th>SKOR</th><th>ETKİ (WEIGHT)</th></tr>"
                for _, r in res.sort_values('Weight', ascending=False).head(15).iterrows():
                    html_list += f"<tr><td>{r.iloc[0]}</td><td>{r.iloc[1]}</td><td>{r.iloc[2]} - {r.iloc[3]}</td><td>{r.iloc[17]}</td><td>{r['Weight']:.2f}</td></tr>"
                html_list += "</table>"
                st.markdown(html_list, unsafe_allow_html=True)
            else:
                st.warning("❌ Eşleşme bulunamadı. Toleransı artırmayı deneyin.")

# ------------------------------------------
# TAB 2 & 3: Diğer Modlar (Şablon)
# ------------------------------------------
with tabs[1]:
    st.info("Jackpot Avcısı modu, aynı ağırlıklandırma mantığıyla çalışır. Analiz panelini kullanabilirsiniz.")

with tabs[2]:
    st.markdown("### 🧠 YZ Uzman Modu")
    st.write("Sistem artık 'Tüm Maçlar' yerine 'Ağırlıklı Maçlar' üzerinden skor tahmini yapmaktadır.")
