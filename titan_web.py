import streamlit as st
import pandas as pd
import numpy as np
import math
import re
from datetime import datetime
import os

# ==========================================
# VIP TASARIM & CSS
# ==========================================
st.set_page_config(page_title="TITAN PRO V.22 - FINAL", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Segoe UI', sans-serif; }
    .b-success { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 8px; font-weight: bold; border: 2px solid #86efac; }
    .b-trap { background-color: #fee2e2; color: #991b1b; padding: 15px; border-radius: 8px; font-weight: bold; border: 2px solid #fca5a5; }
    .b-value { background-color: #eff6ff; color: #1e40af; padding: 15px; border-radius: 8px; font-weight: bold; border: 2px solid #bfdbfe; }
    .custom-table { width: 100%; border-collapse: collapse; font-size: 13px; background-color: white; }
    .custom-table th { padding: 12px 8px; background-color: #f1f5f9; border-bottom: 2px solid #cbd5e1; text-align: left; }
    .custom-table td { padding: 10px 8px; border-bottom: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# KURŞUN GEÇİRMEZ VERİ YÜKLEME (ULTRA SAFE)
# ==========================================
@st.cache_data
def load_data_final():
    filename = "data.xlsb" 
    try:
        if not os.path.exists(filename):
            st.error(f"❌ DOSYA BULUNAMADI! GitHub'da '{filename}' dosyası yok.")
            return None
        
        # Dosyayı oku
        df = pd.read_excel(filename, sheet_name="Sayfa1", engine="pyxlsb")
        
        # Sayısal olması gereken sütunlar
        SAYI_SUTUNLAR = [4,5,6,7,8,9,10,11,12,13,14,15,24,25,26,27,28,29,36,37,38,39,40,41]
        
        for c in SAYI_SUTUNLAR:
            if c < len(df.columns):
                # TOPLU ÇEVİRİ YERİNE TEK TEK (LAMBDA) ÇEVİRİ YAPALIM
                # Bu yöntem Pandas'ın 'Invalid value for dtype str' hatasını %100 engeller.
                df.iloc[:, c] = df.iloc[:, c].apply(
                    lambda x: str(x).replace(',', '.').strip() if pd.notnull(x) else "0.0"
                )
                # Şimdi güvenle sayıya çevirebiliriz
                df.iloc[:, c] = pd.to_numeric(df.iloc[:, c], errors='coerce').fillna(0.0)
        
        return df

    except Exception as e:
        st.error(f"❌ KRİTİK HATA: {str(e)}")
        return None

# ==========================================
# ANALİZ FONKSİYONLARI
# ==========================================
def calculate_weight(date_val):
    try:
        match_date = pd.to_datetime(date_val)
        days_diff = (datetime.now() - match_date).days
        return 1 / (1 + (days_diff / 365))
    except: return 1.0

def calculate_confidence(sample_size):
    if sample_size == 0: return "Veri Yok"
    if sample_size < 5: return "Çok Düşük"
    if sample_size < 15: return "Orta"
    return "Yüksek"

def get_implied_probability(odds):
    try: return (1 / float(odds)) * 100
    except: return 0

def get_matches_advanced(ms_val, iy_val, tolerans_degeri, lig_val="TÜM LİGLER", birebir_mod=False):
    if df_master is None: return None
    try:
        ms_cl = ms_val.replace(',', '.').strip()
        if ' ' in ms_cl and '-' not in ms_cl: ms_cl = '-'.join(ms_cl.split())
        d1, d0, d2 = map(float, ms_cl.split('-'))
        
        temp = df_master.copy()
        m1, m0, m2 = temp.iloc[:, 4].values, temp.iloc[:, 5].values, temp.iloc[:, 6].values

        if birebir_mod:
            mask = (np.abs(m1 - d1) <= 0.05) & (np.abs(m0 - d0) <= 0.05) & (np.abs(m2 - d2) <= 0.05)
        else:
            dist = np.sqrt((m1 - d1)**2 + (m0 - d0)**2 + (m2 - d2)**2)
            mask = (1 - (dist / 0.5)) * 100 >= tolerans_degeri
            
        sonuclar = temp[mask].copy()

        if lig_val != "TÜM LİGLER":
            sonuclar = sonuclar[sonuclar.iloc[:, 0].astype(str).str.upper().str.contains(lig_val.upper(), na=False)]
        
        sonuclar['Weight'] = sonuclar.iloc[:, 1].apply(calculate_weight)
        return sonuclar
    except: return None

# ==========================================
# ANA ARAYÜZ
# ==========================================
st.markdown("<h2 style='text-align: center; color: #ea580c;'>🚜 TITAN PRO V.22 - FINAL</h2>", unsafe_allow_html=True)

df_master = load_data_final()

if df_master is None: 
    st.stop()

ligler_listesi = ["TÜM LİGLER"] + sorted(df_master.iloc[:, 0].dropna().astype(str).unique().tolist())
tabs = st.tabs(["🎯 Analiz", "🔄 Jackpot", "🧠 YZ"])

with tabs[0]:
    ms_in = st.text_input("MS Oranları (1-X-2)", placeholder="1.85-3.10-2.45")
    lig_sel = st.selectbox("Lig Seç", ligler_listesi)
    tol1 = st.slider("Hassasiyet (%)", 60, 100, 85)
    birebir_checkbox = st.checkbox("🎯 Birebir Oranlar")

    if st.button("🔥 ANALİZ ET"):
        if not ms_in:
            st.error("MS Oranları giriniz!")
        else:
            res = get_matches_advanced(ms_in, "", tol1, lig_sel, birebir_checkbox)
            if res is not None and len(res) > 0:
                toplam = len(res)
                sum_weights = res['Weight'].sum()
                w_ms1 = w_ms0 = w_ms2 = 0.0
                for _, row in res.iterrows():
                    w = row['Weight']
                    skor = str(row.iloc[17])
                    if "-" in skor:
                        try:
                            e, d = map(int, skor.split("-"))
                            if e > d: w_ms1 += w
                            elif e == d: w_ms0 += w
                            else: w_ms2 += w
                        except: pass
                p1, p0, p2 = (w_ms1/sum_weights)*100, (w_ms0/sum_weights)*100, (w_ms2/sum_weights)*100
                st.markdown(f"<div class='b-success'>✅ Eşleşen: {toplam} | Güven: {calculate_confidence(toplam)}</div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                c1.metric("MS 1", f"%{p1:.1f}")
                c2.metric("MS X", f"%{p0:.1f}")
                c3.metric("MS 2", f"%{p2:.1f}")
                
                html_list = "<table class='custom-table'><tr><th>LİG</th><th>TARİH</th><th>MAÇ</th><th>SKOR</th></tr>"
                for _, r in res.sort_values('Weight', ascending=False).head(10).iterrows():
                    html_list += f"<tr><td>{r.iloc[0]}</td><td>{r.iloc[1]}</td><td>{r.iloc[2]} - {r.iloc[3]}</td><td>{r.iloc[17]}</td></tr>"
                html_list += "</table>"
                st.markdown(html_list, unsafe_allow_html=True)
            else:
                st.warning("Eşleşme bulunamadı.")

with tabs[1]:
    st.info("Analiz panelini kullanarak ters dönme ihtimallerini görebilirsiniz.")

with tabs[2]:
    st.info("Ağırlıklı analiz sistemi devrededir.")
