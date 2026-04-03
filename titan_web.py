import streamlit as st
import pandas as pd
import numpy as np
import math
import re

# ==========================================
# VIP TASARIM & CSS (AÇIK TEMA / LIGHT MODE)
# ==========================================
st.set_page_config(page_title="TITAN PRO V.20 - GOD MODE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Genel Arka Plan ve Metin Rengi (Aydınlık) */
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    
    /* Girdi Kutuları */
    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input { 
        background-color: #ffffff !important; 
        color: #0f172a !important; 
        border: 2px solid #cbd5e1 !important; 
        border-radius: 8px; 
        padding: 10px; 
        font-size: 15px; 
        font-weight: bold;
    }
    
    /* Genel Buton Tasarımı */
    div.stButton > button { 
        background-color: #2563eb; 
        color: white; 
        border-radius: 8px; 
        height: 50px; 
        font-weight: bold; 
        font-size: 16px !important; 
        border: none; 
        width: 100%; 
        text-transform: uppercase; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover { background-color: #1d4ed8; }
    
    /* Sekmeler (Tabs) */
    .stTabs [data-baseweb="tab-list"] { background-color: #e2e8f0; border-radius: 12px; padding: 5px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { color: #475569; font-weight: bold; font-size: 14px; }
    .stTabs [aria-selected="true"] { background: #ea580c !important; color: white !important; border-radius: 8px; }
    
    /* Bilgi ve Sonuç Kutuları */
    .b-success { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 8px; font-weight: bold; margin-bottom: 20px; border: 2px solid #86efac; }
    .b-trap { background-color: #fee2e2; color: #991b1b; padding: 15px; border-radius: 8px; font-weight: bold; margin-bottom: 10px; border: 2px solid #fca5a5; }
    .b-value { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 8px; font-weight: bold; margin-bottom: 10px; border: 2px solid #86efac; }
    .b-info { background-color: #f1f5f9; color: #334155; padding: 15px; border-radius: 8px; font-style: italic; margin-bottom: 10px; border: 2px solid #cbd5e1;}
    
    .kaos-red-box { background-color: #ffe4e6; color: #9f1239; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #e11d48; }
    .kaos-yellow-box { background-color: #fef9c3; color: #854d0e; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #ca8a04; }
    .kahin-box { background-color: #dcfce7; color: #166534; padding: 15px; border-radius: 8px; font-weight: bold; border-left: 5px solid #22c55e; margin-bottom: 20px; }
    
    .rev-top { background-color: #e0e7ff; color: #1e3a8a; padding: 12px; border-radius: 8px; font-size: 15px; font-weight: bold; margin-bottom: 10px; border: 1px solid #bfdbfe;}
    .rev-alert { background-color: #ffe4e6; color: #be123c; padding: 15px; border-radius: 8px; margin-bottom: 10px; border: 2px solid #f43f5e; font-size: 18px; font-weight: 900; text-align: center; }
    
    .god-stat-box { background-color: white; border-radius: 10px; padding: 20px; text-align: center; border: 2px solid #cbd5e1; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;}
    .god-stat-title { font-size: 16px; font-weight: bold; color: #475569; margin-bottom: 10px; }
    .god-stat-value { font-size: 40px; font-weight: 900; color: #ea580c; }
    
    .custom-table { width: 100%; border-collapse: collapse; font-size: 13px; color: #0f172a; margin-bottom: 20px; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
    .custom-table th { padding: 12px 8px; background-color: #f1f5f9; border-bottom: 2px solid #cbd5e1; color: #0f172a; text-align: left; font-weight: bold;}
    .custom-table td { padding: 10px 8px; border-bottom: 1px solid #e2e8f0; }

    /* Birebir Oranlar Banner */
    .birebir-banner { background: linear-gradient(135deg, #7c3aed, #4f46e5); color: white; padding: 10px 16px; border-radius: 8px; font-weight: bold; font-size: 14px; margin-bottom: 12px; text-align: center; letter-spacing: 0.5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# VERİ MOTORU
# ==========================================
@st.cache_data
def load_data_final():
    try:
        df = pd.read_excel("ORAN ANALİZ TABLOSU.xlsb", sheet_name="Sayfa1", engine="pyxlsb")
        # Sadece sayısal sütunları çevir — metin sütunlarını (iyms gibi) atlıyoruz
        # col 20 = İY/MS sonuç (1/2, 2/1, 1/1 vb.) — string kalmalı, dönüştürme!
        SAYI_SUTUNLAR = [4,5,6,7,8,9,10,11,12,13,14,15,24,25,26,27,28,29,36,37,38,39,40,41]
        for c in SAYI_SUTUNLAR:
            if c < len(df.columns):
                try:
                    df.iloc[:, c] = pd.to_numeric(
                        df.iloc[:, c].astype(str).str.replace(',', '.', regex=False).str.strip(),
                        errors='coerce'
                    ).fillna(0.0)
                except:
                    pass
        return df
    except Exception as e:
        st.error(f"Veri yükleme hatası: {str(e)}")
        return None

df_master = load_data_final()

# ==========================================
# GET_MATCHES - TAM EŞLEŞME (EXACT MATCH) İLE DÜZELTİLDİ
# birebir_mod=True ise MS tam eşleşme, İY de tam eşleşme (toleranssız)
# ==========================================
def get_matches(ms_val, iy_val, tolerans_degeri, lig_val="TÜM LİGLER", ev_sahibi="", deplasman="", birebir_mod=False):
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
            # ✅ BİREBİR MOD: ±0.005 tolerans (float hassasiyet sorununu aşar, görsel birebir eşleşme)
            exact_mask = (
                (np.abs(m1 - d1) <= 0.05) &
                (np.abs(m0 - d0) <= 0.05) &
                (np.abs(m2 - d2) <= 0.05)
            )
            temp['Benzerlik'] = np.where(exact_mask, 100.0, 0.0)
            sonuclar = temp[exact_mask].copy()
        else:
            dist = ((m1 - d1)**2 + (m0 - d0)**2 + (m2 - d2)**2)**0.5
            temp['Benzerlik'] = np.round((1 - (dist / 0.5)) * 100, 1)
            temp.loc[(m1 == d1) & (m0 == d0) & (m2 == d2), 'Benzerlik'] = 100.0
            sonuclar = temp[temp['Benzerlik'] >= tolerans_degeri].copy()

        if lig_val != "TÜM LİGLER":
            mask = sonuclar.iloc[:, 0].astype(str).str.upper().str.contains(lig_val.upper(), na=False)
            sonuclar = sonuclar[mask]
        
        # TAM EŞLEŞME (EXACT MATCH) - LİLLESTRÖM GELMEZ
        if ev_sahibi and ev_sahibi.strip():
            ev_clean = ev_sahibi.strip().upper()
            ev_filtre = sonuclar.iloc[:, 2].astype(str).str.strip().str.upper() == ev_clean
            sonuclar = sonuclar[ev_filtre]
        if deplasman and deplasman.strip():
            dep_clean = deplasman.strip().upper()
            dep_filtre = sonuclar.iloc[:, 3].astype(str).str.strip().str.upper() == dep_clean
            sonuclar = sonuclar[dep_filtre]
        
        if iy_val and len(iy_val.strip()) > 2:
            iy_cl = iy_val.replace(',', '.').strip()
            if ' ' in iy_cl and '-' not in iy_cl: iy_cl = '-'.join(iy_cl.split())
            i1, i0, i2 = map(float, iy_cl.split('-'))
            if birebir_mod:
                # ✅ BİREBİR MOD: İY oranı da ±0.005 tolerans (float sorununu aşar)
                sonuclar = sonuclar[
                    (np.abs(sonuclar.iloc[:, 10] - i1) <= 0.05) &
                    (np.abs(sonuclar.iloc[:, 11] - i0) <= 0.05) &
                    (np.abs(sonuclar.iloc[:, 12] - i2) <= 0.05)
                ]
            else:
                sonuclar = sonuclar[
                    (sonuclar.iloc[:, 10].between(i1-0.1, i1+0.1)) & 
                    (sonuclar.iloc[:, 11].between(i0-0.1, i0+0.1)) & 
                    (sonuclar.iloc[:, 12].between(i2-0.1, i2+0.1))
                ]
        return sonuclar
    except Exception as e:
        return None

def poisson_prob(lmbda, k): 
    return (math.exp(-lmbda) * (lmbda**k)) / math.factorial(k)

# ==========================================
# ANA ARAYÜZ (SEKMELER)
# ==========================================
st.markdown("<h2 style='text-align: center; color: #ea580c; margin-bottom: 5px;'>🚜 TITAN PRO V.20</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size:12px; margin-bottom:20px; font-weight:bold;'>AÇIK TEMA | ÜNYE MERKEZ KOMUTA | VIP MOBILE</p>", unsafe_allow_html=True)

if df_master is None: 
    st.error("❌ Veritabanı okunamadı! 'ORAN ANALİZ TABLOSU.xlsb' dosyasını kontrol et.")
    st.stop()

ligler_listesi = ["TÜM LİGLER"] + sorted(df_master.iloc[:, 0].dropna().astype(str).unique().tolist())

tabs = st.tabs(["🚜 Buldozer", "🔄 1/2 Avcısı", "🎯 Poisson", "⚔️ Kaos", "🌐 Toplu Bülten", "🧠 YZ Uzman Modu"])

# ------------------------------------------
# TAB 1: BULDOZER - BİREBİR ORAN CHECKBOX EKLENDİ
# ------------------------------------------
with tabs[0]:
    st.markdown("<h3 style='color:#0f172a;'>🎯 HASSAS FİLTRELEME</h3>", unsafe_allow_html=True)
    
    col_ms, col_iy = st.columns(2)
    with col_ms:
        ms_in = st.text_input("MS Oranları (1-X-2) *", placeholder="1.85-3.10-2.45", key="m1")
    with col_iy:
        iy_in = st.text_input("İY Oranları (Opsiyonel)", placeholder="Örn: 2.40-2.10-3.30", key="i1")

    # ✅ YENİ: BİREBİR ORANLAR CHECKBOX (session_state ile korunuyor)
    if "birebir1" not in st.session_state:
        st.session_state["birebir1"] = False

    birebir_checkbox = st.checkbox(
        "🎯 Sadece Birebir Oranlar (MS tam eşleşme | İY girilmişse o da tam eşleşme)",
        key="birebir1"
    )
    birebir_checkbox = st.session_state["birebir1"]

    # Checkbox işaretliyse banner göster + slider'ı kilitle
    if birebir_checkbox:
        st.markdown("<div class='birebir-banner'>🔒 BİREBİR MOD AKTİF — Tolerans %100'e kilitlendi. Sadece oranı birebir eşleşen maçlar getirilecek.</div>", unsafe_allow_html=True)

    st.markdown("**🏆 TAKIM FİLTRELERİ (Opsiyonel)**", unsafe_allow_html=True)
    col_ev, col_dep = st.columns(2)
    with col_ev:
        ev_sahibi_in = st.text_input("Ev Sahibi Takım", placeholder="Örn: LİLLE", key="ev1")
    with col_dep:
        deplasman_in = st.text_input("Deplasman Takım", placeholder="Örn: PSG", key="dep1")
    
    col1, col2 = st.columns(2)
    lig_sel = col1.selectbox("Lig Seç", ligler_listesi, key="lig1")

    # Slider: birebir mod aktifse kilitli göster (%100), değilse normal
    if birebir_checkbox:
        col2.slider("Hassasiyet (%) — 🔒 Kilitli", 60, 100, 100, key="t1", disabled=True)
        tol1 = 100  # Kullanılmaz ama tanımlı olsun
    else:
        tol1 = col2.slider("Hassasiyet (%)", 60, 100, 85, key="t1")

    st.markdown("**⚽ GOL ORANLARI (Opsiyonel)**", unsafe_allow_html=True)
    col_kg, col_iy05, col_iy15 = st.columns(3)
    with col_kg:
        kg_in = st.text_input("MS KG VAR Oranı", placeholder="Örn: 1.55", key="kg1")
    with col_iy05:
        iy05_in = st.text_input("İY 0.5 Üst - Alt", placeholder="Örn: 1.25-3.10", key="iy051")
    with col_iy15:
        iy15_in = st.text_input("İY 1.5 Üst - Alt", placeholder="Örn: 2.10-1.60", key="iy151")

    if st.button("🔥 ANALİZ ET (BULDOZER) 🔥", key="btn1"):
        if not ms_in:
            st.error("❌ MS Oranları zorunlu!")
        else:
            res = get_matches(
                ms_in, iy_in, tol1, lig_sel,
                ev_sahibi_in, deplasman_in,
                birebir_mod=birebir_checkbox
            )
            if res is not None and len(res) > 0:
                # KG VAR filtresi (col 38)
                if kg_in:
                    try:
                        kg_f = float(kg_in.replace(',', '.'))
                        res = res[res.iloc[:, 38].between(kg_f-0.05, kg_f+0.05)]
                    except: pass
                # İY 0.5 Üst-Alt filtresi (col 24=üst, 25=alt)
                if iy05_in and '-' in iy05_in:
                    try:
                        u05, a05 = map(float, iy05_in.replace(',', '.').split('-'))
                        res = res[res.iloc[:, 24].between(u05-0.05, u05+0.05) & res.iloc[:, 25].between(a05-0.05, a05+0.05)]
                    except: pass
                # İY 1.5 Üst-Alt filtresi (col 26=üst, 27=alt)
                if iy15_in and '-' in iy15_in:
                    try:
                        u15, a15 = map(float, iy15_in.replace(',', '.').split('-'))
                        res = res[res.iloc[:, 26].between(u15-0.05, u15+0.05) & res.iloc[:, 27].between(a15-0.05, a15+0.05)]
                    except: pass
                toplam = len(res)

                if birebir_checkbox:
                    st.markdown(f"<div class='b-success'>🎯 BİREBİR Eşleşen Maç: {toplam} adet (Oranlar birebir aynı)</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='b-success'>✅ Eşleşen Maç: {toplam} adet</div>", unsafe_allow_html=True)
                
                ms_cl = ms_in.replace(',', '.').strip()
                if ' ' in ms_cl and '-' not in ms_cl: ms_cl = '-'.join(ms_cl.split())
                d1, d0, d2 = map(float, ms_cl.split('-'))
                
                skor_ms = res.iloc[:, 17].astype(str)
                ms1_say, ms0_say, ms2_say, ust_say, kg_say, iki_kg_say = 0,0,0,0,0,0
                s_dict = {}
                for s in skor_ms:
                    if "-" in s:
                        try:
                            e, d = map(int, s.split("-")); s_dict[s] = s_dict.get(s, 0) + 1
                            if e > d: ms1_say+=1
                            elif e == d: ms0_say+=1
                            else: ms2_say+=1
                            if (e+d) > 2.5: ust_say+=1
                            if e>0 and d>0: kg_say+=1
                        except: pass
                
                for idx, r in res.iterrows():
                    try: m, i = str(r.iloc[17]), str(r.iloc[16])
                    except: continue
                    if "-" in m and "-" in i:
                        try: me, md, ie, id = int(m.split("-")[0]), int(m.split("-")[1]), int(i.split("-")[0]), int(i.split("-")[1])
                        except: continue
                        if ie>0 and id>0 and (me-ie)>0 and (md-id)>0: iki_kg_say+=1
                
                p1, p0, p2 = round(ms1_say/toplam*100,1), round(ms0_say/toplam*100,1), round(ms2_say/toplam*100,1)
                imp1 = round(1/d1*100,1)
                
                if (p1-imp1) < -15: 
                    st.markdown(f"<div class='b-trap'>⚠️ MS1 TUZAK! Şirket favori gösteriyor (%{imp1}) ama arşivde patlamış (%{p1}).</div>", unsafe_allow_html=True)
                elif (p1-imp1) > 15: 
                    st.markdown(f"<div class='b-value'>💎 MS1 DEĞERLİ ORAN (VALUE)! Şirket şans vermemiş (%{imp1}) ama arşivde çok gelmiş (%{p1}).</div>", unsafe_allow_html=True)
                else: 
                    st.markdown("<div class='b-info'>ℹ️ Oranlar geçmiş verilerle uyumlu, bariz bir tuzak tespit edilmedi.</div>", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("MS 1", f"%{p1}")
                c2.metric("MS X", f"%{p0}")
                c3.metric("MS 2", f"%{p2}")
                
                st.markdown("<hr>", unsafe_allow_html=True)
                e_c_s = sorted(s_dict.items(), key=lambda x: x[1], reverse=True)[0][0] if s_dict else "N/A"
                c4, c5, c6 = st.columns(3)
                c4.metric("2.5 ÜST", f"%{round(ust_say/toplam*100,1)}")
                c5.metric("KG VAR", f"%{round(kg_say/toplam*100,1)}")
                c6.metric("En Çok Çıkan Skor", e_c_s)
                
                st.markdown("### 🔥 Kaos Senaryoları", unsafe_allow_html=True)
                iyms = res.iloc[:, 20].astype(str).str.strip()
                c12, c21 = (iyms == "1/2").sum(), (iyms == "2/1").sum()
                rev_yuzde = round(((c12 + c21) / toplam) * 100, 1)
                kaos_yuzde = round((iki_kg_say/toplam)*100, 1)
                
                st.markdown(f"<div class='kaos-red-box'><b style='font-size: 15px;'>TERS DÖNME İHTİMALİ (1/2 veya 2/1): %{rev_yuzde}</b><br><span style='font-size: 13px;'>({c12} Kez 1/2 | {c21} Kez 2/1)</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='kaos-yellow-box'><b style='font-size: 15px;'>HER İKİ YARI KG VAR: %{kaos_yuzde}</b> <span style='font-size: 13px;'>({iki_kg_say} Kez Çıkmış)</span></div>", unsafe_allow_html=True)
                
                st.markdown("### 🔍 Maç Listesi (Eşleşenler)", unsafe_allow_html=True)
                html_list = "<table class='custom-table'><tr><th>LİG</th><th>TARİH</th><th>EV SAHİBİ</th><th>DEPLASMAN</th><th>İY</th><th>MS</th><th>BENZERLİK</th></tr>"
                for _, r in res.iloc[::-1].head(50).iterrows():
                    try:
                        b_val = float(r.get('Benzerlik', 100.0))
                    except:
                        b_val = 100.0
                    b_color = "#16a34a" if b_val >= 95 else ("#ca8a04" if b_val >= 85 else "#dc2626")
                    html_list += (
                        f"<tr>"
                        f"<td>{str(r.iloc[0])[:12]}</td>"
                        f"<td>{str(r.iloc[1]).split(' ')[0]}</td>"
                        f"<td><b>{str(r.iloc[2])[:12]}</b></td>"
                        f"<td><b>{str(r.iloc[3])[:12]}</b></td>"
                        f"<td style='color:#ea580c; font-weight:bold;'>{r.iloc[16]}</td>"
                        f"<td style='color:#16a34a; font-weight:bold;'>{r.iloc[17]}</td>"
                        f"<td style='color:{b_color}; font-weight:bold; text-align:center;'>%{b_val:.1f}</td>"
                        f"</tr>"
                    )
                html_list += "</table>"
                st.markdown(html_list, unsafe_allow_html=True)
            else: 
                if birebir_checkbox:
                    st.warning("❌ BİREBİR eşleşen maç bulunamadı. Oranları kontrol et veya birebir modu kapat.")
                else:
                    st.warning("❌ SIFIR EŞLEŞME. Toleransı artır veya filtre azalt!")

# ------------------------------------------
# TAB 2: 1/2 AVCISI
# ------------------------------------------
with tabs[1]:
    with st.form("form2"):
        ms_r = st.text_input("MS Oranları (1-X-2) *", placeholder="2.10-3.15-2.45")
        iy_r = st.text_input("İY Oranları (Opsiyonel)", placeholder="2.50-2.00-3.00")
        tol2 = st.slider("Hassasiyet (%)", 70, 100, 92, key="t2")
        btn_r = st.form_submit_button("🧨 JACKPOT'U ARA")

    if btn_r:
        if not ms_r:
            st.error("❌ MS Oranları zorunlu!")
        else:
            res = get_matches(ms_r, iy_r, tol2)
            if res is not None and len(res) > 0:
                tot = len(res)
                iyms = res.iloc[:, 20].astype(str).str.strip()
                c12, c21 = (iyms == "1/2").sum(), (iyms == "2/1").sum()
                kaos_pot = round(((c12 + c21) / tot) * 100, 1)
                st.markdown(f"<div class='rev-top'>🔍 Taranan Toplam Benzer Maç: {tot} adet</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='rev-alert'>🚨 TERS DÖNME POTANSİYELİ: %{kaos_pot}</div>", unsafe_allow_html=True)
                if (c12+c21) > 0:
                    st.markdown("### 📋 Ters Dönen Maçlar", unsafe_allow_html=True)
                    html_list = "<table class='custom-table'><tr><th>MAÇ</th><th>MS</th><th>SONUÇ</th></tr>"
                    for _, r in res[iyms.isin(["1/2", "2/1"])].iterrows(): 
                        html_list += f"<tr><td>{str(r.iloc[2])[:15]} - {str(r.iloc[3])[:15]}</td><td>{r.iloc[17]}</td><td style='color:#e11d48; font-weight:bold;'>{r.iloc[20]}</td></tr>"
                    html_list += "</table>"
                    st.markdown(html_list, unsafe_allow_html=True)
            else: 
                st.warning("❌ Eşleşme bulunamadı!")

# ------------------------------------------
# TAB 3: POISSON
# ------------------------------------------
with tabs[2]:
    with st.form("form3"):
        ms_p = st.text_input("MS Oranları (1-X-2) *", placeholder="Örn: 1.85-3.10-2.45")
        tol3 = st.slider("Hassasiyet (%)", 60, 100, 78, key="t3")
        btn_p = st.form_submit_button("🧮 SKOR İHTİMALLERİNİ HESAPLA")

    if btn_p:
        if not ms_p:
            st.error("❌ MS Oranları zorunlu!")
        else:
            res = get_matches(ms_p, "", tol3)
            if res is not None and len(res) > 0:
                ev_g, dep_g, g_mac = 0, 0, 0
                for s in res.iloc[:, 17].astype(str):
                    if "-" in s:
                        try: 
                            e, d = map(int, s.split("-")); ev_g+=e; dep_g+=d; g_mac+=1
                        except: pass
                
                if g_mac > 0:
                    xg_home = ev_g / g_mac; xg_away = dep_g / g_mac
                    prob_dict = {}
                    for e in range(5):
                        for d in range(5):
                            prob_e = poisson_prob(xg_home, e) if e<4 else 1-sum(poisson_prob(xg_home, i) for i in range(4))
                            prob_d = poisson_prob(xg_away, d) if d<4 else 1-sum(poisson_prob(xg_away, i) for i in range(4))
                            prob_total = (prob_e * prob_d) * 100
                            score_str = f"{'4+' if e==4 else e}-{'4+' if d==4 else d}"
                            prob_dict[score_str] = prob_total
                            
                    top_3_scores = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)[:3]

                    st.markdown(f"<h3 style='color:#0f172a; text-align:center;'>🎯 POISSON DAĞILIMI ({g_mac} Maç)</h3>", unsafe_allow_html=True)
                    colA, colB = st.columns(2)
                    colA.metric("Ev Sahibi xG", f"{xg_home:.2f}")
                    colB.metric("Deplasman xG", f"{xg_away:.2f}")
                    
                    st.markdown("### 🔥 EN YÜKSEK İHTİMALLİ 3 SKOR")
                    for s, p in top_3_scores:
                        st.success(f"Skor: **{s}** ➔ İhtimal: **%{p:.1f}**")
            else: 
                st.warning("❌ Eşleşme bulunamadı!")

# ------------------------------------------
# TAB 4: KAOS ÜÇGENİ
# ------------------------------------------
with tabs[3]:
    with st.form("form4"):
        ms_k = st.text_input("MS Oranları (1-X-2) *", placeholder="2.10-3.15-2.45")
        kg_k = st.text_input("KG VAR Oranı (Opsiyonel)", placeholder="Örn: 1.65")
        tol4 = st.slider("Hassasiyet (%)", 70, 100, 78, key="t4")
        btn_k = st.form_submit_button("🌪️ 1.Y VE 2.Y KG ARA")

    if btn_k:
        if not ms_k:
            st.error("❌ MS Oranları zorunlu!")
        else:
            res = get_matches(ms_k, "", tol4)
            if res is not None and len(res) > 0:
                if kg_k:
                    try:
                        kg_f = float(kg_k.replace(',', '.'))
                        res = res[res.iloc[:, 38].between(kg_f-0.05, kg_f+0.05)]
                    except: pass
                
                tot = len(res)
                if tot == 0:
                    st.warning("❌ KG filtresiyle eşleşme kalmadı!")
                else:
                    iki_kg = 0; iy_kg = 0; y2_kg = 0
                    for idx, row in res.iterrows():
                        try: m, i = str(row.iloc[17]), str(row.iloc[16])
                        except: continue
                        if "-" in m and "-" in i:
                            try: 
                                me, md = map(int, m.split("-"))
                                ie, id = map(int, i.split("-"))
                                if ie>0 and id>0: iy_kg += 1
                                if (me-ie)>0 and (md-id)>0: y2_kg += 1
                                if ie>0 and id>0 and (me-ie)>0 and (md-id)>0: iki_kg += 1
                            except: pass
                    
                    st.metric("Taranan Maç", tot)
                    st.metric("İlk Yarı KG VAR", f"%{round(iy_kg/tot*100,1)}")
                    st.metric("İkinci Yarı KG VAR", f"%{round(y2_kg/tot*100,1)}")
                    yuzde_iki = round((iki_kg/tot)*100, 1)
                    if yuzde_iki > 15: 
                        st.error(f"🚨 JACKPOT! HER İKİ YARI KG VAR İHTİMALİ: %{yuzde_iki}")
                    else: 
                        st.info(f"Her İki Yarı KG VAR İhtimali: %{yuzde_iki} (Riskli)")
            else: 
                st.warning("❌ Eşleşme bulunamadı!")

# ------------------------------------------
# TAB 5: TOPLU BÜLTEN
# ------------------------------------------
with tabs[4]:
    st.markdown("<h3 style='color:#0f172a;'>🌐 BÜLTEN TARAMA ROBOTU (KAHİN)</h3>", unsafe_allow_html=True)
    bulten_text = st.text_area("Maçları ve Oranları Buraya Yapıştır:", height=150)
    toplu_tol = st.slider("Toplu Tarama Hassasiyeti (%)", 60, 100, 85, key="tt1")
    
    if st.button("🚀 TOPLU BÜLTENİ ANALİZ ET", key="btn_bulten"):
        if not bulten_text: 
            st.warning("Kutuya bir şeyler yapıştırman lazım!")
        else:
            ms_cl = bulten_text.replace(',', '.')
            oran_objeleri = list(re.finditer(r'(\d+\.\d{2})\s+(\d+\.\d{2})\s+(\d+\.\d{2})', ms_cl))
            if not oran_objeleri: 
                st.error("❌ Metin içinde MS(1-X-2) üçlü oranı bulunamadı.")
            else:
                st.success(f"✅ {len(oran_objeleri)} maç tespit edildi! İşleniyor...")
                
                yasakli_kelimeler = {"HND", "VAR", "YOK", "ÇŞ", "MS", "KG", "ÜST", "ALT", "TEK", "ÇİFT", 
                                     "HANDİKAP", "GOL", "MBS", "KOD", "CANLI", "KUPON", "ORAN", "IDDAA", 
                                     "İDDAA", "NESİNE", "MACKOLIK", "MAÇKOLİK", "BUGÜN", "YARIN", "DAKİKA", 
                                     "POPÜLER", "BÜLTEN", "KUPONDAŞ", "X", "V", "I", "B", "LİGİ", "LİG", 
                                     "KUPASI", "ŞAMPİYONASI", "LIG", "LIGI", "DÜELLO", "KİM", "KAZANIR", "YARI"}
                
                last_end = 0
                son_gecerli_mac = "BİLİNMEYEN MAÇ"
                islenen_maclar = set()
                
                for idx, match_obj in enumerate(oran_objeleri):
                    d1, d0, d2 = match_obj.groups()
                    ms_val = f"{d1}-{d0}-{d2}"
                    
                    start_idx = max(last_end, match_obj.start() - 300)
                    text_before_odds = ms_cl[start_idx:match_obj.start()].replace('\n', ' ').strip()
                    last_end = match_obj.end()
                    
                    kelimeler = text_before_odds.split()
                    temiz_kelimeler = []
                    
                    for k in reversed(kelimeler):
                        if len(temiz_kelimeler) >= 6: break
                        k_upper = k.upper()
                        k_clean = re.sub(r'[^\w\s]', '', k_upper)
                        if k_clean in yasakli_kelimeler: continue
                        if any(char.isdigit() for char in k): continue
                        if re.search(r'[A-ZĞÜŞİÖÇa-zğüşıöç]', k) or k == '-':
                            if len(k_clean) == 1 and k_clean in ['X', 'V', 'I', 'B']: continue
                            temiz_kelimeler.append(k_upper)
                    
                    if len(temiz_kelimeler) > 0:
                        temiz_kelimeler.reverse()
                        mac_ismi = " ".join(temiz_kelimeler)
                        mac_ismi = re.sub(r'^[-\s]+|[-\s]+$', '', mac_ismi)
                    else:
                        mac_ismi = ""
                        
                    if len(mac_ismi) < 3:
                        mac_ismi = son_gecerli_mac
                    else:
                        son_gecerli_mac = mac_ismi
                    
                    if mac_ismi in islenen_maclar and "MAÇ" not in mac_ismi: continue 
                    islenen_maclar.add(mac_ismi)
                    
                    res = get_matches(ms_val, "", toplu_tol)
                    
                    with st.expander(f"📌 {mac_ismi} | Oran: {ms_val.replace('-', ' ')}", expanded=False):
                        if res is not None and len(res) > 0:
                            toplam = len(res)
                            st.write(f"✅ Eşleşen Arşiv Maçı: **{toplam}** Adet")
                            
                            ms1_s, ms0_s, ms2_s, ust_s, kg_s = 0,0,0,0,0
                            for _, row in res.iterrows():
                                s_ms = str(row.iloc[17]).strip()
                                if "-" in s_ms:
                                    try:
                                        e, d = map(int, s_ms.split("-"))
                                        if e > d: ms1_s+=1
                                        elif e == d: ms0_s+=1
                                        else: ms2_s+=1
                                        if (e+d) > 2.5: ust_s+=1
                                        if e>0 and d>0: kg_s+=1
                                    except: pass
                            
                            p1, p0, p2 = round(ms1_s/toplam*100,1), round(ms0_s/toplam*100,1), round(ms2_s/toplam*100,1)
                            p_ust, p_kg = round(ust_s/toplam*100,1), round(kg_s/toplam*100,1)
                            
                            col_a, col_b, col_c = st.columns(3)
                            col_a.metric("MS 1", f"%{p1}")
                            col_b.metric("MS X", f"%{p0}")
                            col_c.metric("MS 2", f"%{p2}")
                            col_d, col_e = st.columns(2)
                            col_d.metric("2.5 ÜST", f"%{p_ust}")
                            col_e.metric("KG VAR", f"%{p_kg}")
                            
                            st.markdown("**Geçmiş 5 Maç:**")
                            html_list = "<table class='custom-table'><tr><th>LİG</th><th>EV SAHİBİ</th><th>DEPLASMAN</th><th>MS</th></tr>"
                            for _, r in res.iloc[::-1].head(5).iterrows():
                                html_list += f"<tr><td>{str(r.iloc[0])[:12]}</td><td>{str(r.iloc[2])[:12]}</td><td>{str(r.iloc[3])[:12]}</td><td style='color:#16a34a;'>{r.iloc[17]}</td></tr>"
                            html_list += "</table>"
                            st.markdown(html_list, unsafe_allow_html=True)
                        else:
                            st.warning("Arşivde bu orana ait yeterli eşleşme bulunamadı.")

# ------------------------------------------
# TAB 6: YZ UZMAN MODU (5 BAŞLI EJDERHA + MİLİMETRİK FİLTRE)
# ------------------------------------------
with tabs[5]:
    st.markdown("<h3 style='text-align: center; color: #0f172a;'>🧠 YZ UZMAN MODU (Milimetrik Sniper)</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #475569; font-size:14px;'>Neyi arıyorsan onu seç. Makine sadece o konuya, MİLİMETRİK toleransla odaklanır.</p>", unsafe_allow_html=True)

    with st.form("god_form"):
        col_g1, col_g2 = st.columns(2)
        ms_god = col_g1.text_input("MS 1-X-2 (Zorunlu) *", placeholder="Örn: 2.10-3.15-2.45")
        iy_god = col_g2.text_input("İY 1-X-2 (Opsiyonel)", placeholder="Örn: 2.70-2.00-3.00")
        
        cs_god = st.text_input("Çifte Şans 1X-12-X2 (Opsiyonel)", placeholder="Örn: 1.25-1.35-1.45")
        
        st.markdown("**🏆 TAKIM FİLTRELERİ (Opsiyonel)**", unsafe_allow_html=True)
        col_ev_ml, col_dep_ml = st.columns(2)
        with col_ev_ml:
            ev_sahibi_ml = st.text_input("Ev Sahibi Takım", placeholder="Örn: LİLLE", key="ev_ml")
        with col_dep_ml:
            deplasman_ml = st.text_input("Deplasman Takım", placeholder="Örn: PSG", key="dep_ml")
        
        st.markdown("**🌍 LİG SEÇ (Filtrele)**", unsafe_allow_html=True)
        lig_ml = st.selectbox("Lig", ligler_listesi, key="lig_ml")
        
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        mode_secim = st.selectbox("🎯 Hangi Uzman Motoru Çalışsın?", [
            "🛡️ STANDART (Taraf / Gol)",
            "🔥 JACKPOT (1/2 - 2/1)",
            "⚔️ KAOS (İki Yarı KG)",
            "🎯 SKOR (Tam İsabet)",
            "🚀 6+ GOL (Katliam Radarı)"
        ])

        birebir_skor = st.checkbox(
            "🎯 SKOR Modunda Sadece Birebir Oranlar (MS + İY tam eşleşme)",
            key="birebir_skor"
        )
        
        btn_god = st.form_submit_button("🚀 MİLİMETRİK ANALİZİ BAŞLAT")

    if btn_god:
        if not ms_god:
            st.error("❌ Lütfen MS Oranlarını girin!")
        else:
            with st.spinner("⏳ Hedefe Kilitleniyor (Sadece Safkan Şablonlar Aranıyor)..."):
                try:
                    ms_cl = ms_god.replace(',', '.').strip()
                    if ' ' in ms_cl and '-' not in ms_cl: ms_cl = '-'.join(ms_cl.split())
                    d1, d0, d2 = map(float, ms_cl.split('-'))
                    
                    df_train_full = df_master.copy()
                    
                    # LİG FİLTRESİ
                    if lig_ml != "TÜM LİGLER":
                        mask = df_train_full.iloc[:, 0].astype(str).str.upper().str.contains(lig_ml.upper(), na=False)
                        df_train_full = df_train_full[mask]
                        if len(df_train_full) == 0:
                            st.error(f"❌ Seçilen ligde ({lig_ml}) hiç maç bulunamadı!")
                            st.stop()
                    
                    # TAKIM FİLTRELERİ - TAM EŞLEŞME (EXACT MATCH)
                    if ev_sahibi_ml and ev_sahibi_ml.strip():
                        ev_clean = ev_sahibi_ml.strip().upper()
                        ev_filtre = df_train_full.iloc[:, 2].astype(str).str.strip().str.upper() == ev_clean
                        df_train_full = df_train_full[ev_filtre]
                        if len(df_train_full) == 0:
                            st.error(f"❌ '{ev_sahibi_ml}' takımına ait maç bulunamadı!")
                            st.stop()
                    if deplasman_ml and deplasman_ml.strip():
                        dep_clean = deplasman_ml.strip().upper()
                        dep_filtre = df_train_full.iloc[:, 3].astype(str).str.strip().str.upper() == dep_clean
                        df_train_full = df_train_full[dep_filtre]
                        if len(df_train_full) == 0:
                            st.error(f"❌ '{deplasman_ml}' takımına ait maç bulunamadı!")
                            st.stop()
                    
                    def get_safe_float_col(col_index):
                        return pd.to_numeric(df_train_full.iloc[:, col_index].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)

                    ms_mesafe = (get_safe_float_col(4) - d1)**2 + (get_safe_float_col(5) - d0)**2 + (get_safe_float_col(6) - d2)**2
                    
                    iy_mesafe = 0
                    if iy_god:
                        try:
                            iy_cl = iy_god.replace(',', '.').replace(' ', '-').strip()
                            i1, i0, i2 = map(float, iy_cl.split('-'))
                            iy_mesafe = (get_safe_float_col(10) - i1)**2 + (get_safe_float_col(11) - i0)**2 + (get_safe_float_col(12) - i2)**2
                        except: pass
                            
                    cs_mesafe = 0
                    if cs_god:
                        try:
                            cs_cl = cs_god.replace(',', '.').replace(' ', '-').strip()
                            c1, c0, c2 = map(float, cs_cl.split('-'))
                            cs_mesafe = (get_safe_float_col(7) - c1)**2 + (get_safe_float_col(8) - c0)**2 + (get_safe_float_col(9) - c2)**2
                        except: pass

                    # MİLİMETRİK FİLTRELEME
                    if "STANDART" in mode_secim:
                        df_train_full['Mesafe'] = np.sqrt((ms_mesafe + iy_mesafe + cs_mesafe).astype(float))
                        df_train = df_train_full.sort_values('Mesafe').head(100).copy()
                        df_train = df_train[df_train['Mesafe'] <= 1.0] 
                    elif "JACKPOT" in mode_secim or "KAOS" in mode_secim:
                        df_train_full['Mesafe'] = np.sqrt((ms_mesafe + (iy_mesafe * 2.0) + cs_mesafe).astype(float))
                        df_train = df_train_full.sort_values('Mesafe').head(150).copy()
                        df_train = df_train[df_train['Mesafe'] <= 0.6]
                    elif "SKOR" in mode_secim:
                        df_train_full['Mesafe'] = np.sqrt((ms_mesafe + iy_mesafe + cs_mesafe).astype(float))
                        if birebir_skor:
                            # BİREBİR MOD: MS ±0.05, İY girilmişse o da ±0.05
                            ms_birebir = (
                                (np.abs(get_safe_float_col(4) - d1) <= 0.05) &
                                (np.abs(get_safe_float_col(5) - d0) <= 0.05) &
                                (np.abs(get_safe_float_col(6) - d2) <= 0.05)
                            )
                            df_train = df_train_full[ms_birebir].copy()
                            if iy_god:
                                try:
                                    iy_cl2 = iy_god.replace(',', '.').replace(' ', '-').strip()
                                    i1b, i0b, i2b = map(float, iy_cl2.split('-'))
                                    iy_birebir = (
                                        (np.abs(get_safe_float_col(10)[ms_birebir] - i1b) <= 0.05) &
                                        (np.abs(get_safe_float_col(11)[ms_birebir] - i0b) <= 0.05) &
                                        (np.abs(get_safe_float_col(12)[ms_birebir] - i2b) <= 0.05)
                                    )
                                    df_train = df_train[iy_birebir.values]
                                except: pass
                            df_train['Mesafe'] = df_train_full.loc[df_train.index, 'Mesafe']
                        else:
                            df_train = df_train_full.sort_values('Mesafe').head(150).copy()
                            df_train = df_train[df_train['Mesafe'] <= 0.8]
                    elif "6+ GOL" in mode_secim:
                        df_train_full['Mesafe'] = np.sqrt((ms_mesafe + iy_mesafe + cs_mesafe).astype(float))
                        df_train = df_train_full.sort_values('Mesafe').head(150).copy()
                        df_train = df_train[df_train['Mesafe'] <= 0.8]

                    toplam_mac = len(df_train)

                    if toplam_mac == 0:
                        st.error(f"❌ Arşivde bu orana ait MİLİMETRİK eşleşen maç bulunamadı! (Lig: {lig_ml}) Başka oran veya lig dene.")
                    else:
                        w_ms1 = w_ms0 = w_ms2 = w_ust = w_alt = w_kgvar = w_kgyok = w_rev = w_kaos = w_arti_alti = 0.0
                        total_weight = 0.0
                        score_weights = {}
                        
                        count_12 = count_21 = count_kaos_match = count_arti_alti = 0
                        liste_html = ""

                        for _, row in df_train.iterrows():
                            w = 1.0 / ((row['Mesafe']**2) + 0.0001) 
                            
                            s_ms = str(row.iloc[17]).strip()
                            s_iy = str(row.iloc[16]).strip()
                            iyms = str(row.iloc[20]).strip()
                            
                            gecerli = hit_rev = hit_kaos = hit_arti = False

                            if '-' in s_ms:
                                try:
                                    e, d = map(int, s_ms.split('-'))
                                    if e > d: w_ms1 += w
                                    elif e == d: w_ms0 += w
                                    else: w_ms2 += w
                                    if (e+d) > 2.5: w_ust += w
                                    else: w_alt += w
                                    if e>0 and d>0: w_kgvar += w
                                    else: w_kgyok += w
                                    if (e+d) >= 6:
                                        w_arti_alti += w; hit_arti = True; count_arti_alti += 1
                                    
                                    score_str = f"{e if e<4 else '4+'}-{d if d<4 else '4+'}"
                                    score_weights[score_str] = score_weights.get(score_str, 0.0) + w
                                    gecerli = True
                                except: pass
                            
                            if iyms == '1/2': w_rev += w; hit_rev = True; count_12 += 1
                            elif iyms == '2/1': w_rev += w; hit_rev = True; count_21 += 1
                            
                            if '-' in s_ms and '-' in s_iy:
                                try:
                                    e, d = map(int, s_ms.split('-'))
                                    ie, id = map(int, s_iy.split('-'))
                                    if (ie>0 and id>0) and ((e-ie)>0 and (d-id)>0): 
                                        w_kaos += w; hit_kaos = True; count_kaos_match += 1
                                except: pass
                            
                            if gecerli: total_weight += w

                            lig_str = str(row.iloc[0])[:12] + ".." if len(str(row.iloc[0])) > 12 else str(row.iloc[0])
                            tarih_str = str(row.iloc[1]).split(" ")[0]
                            ev_str = str(row.iloc[2])[:12] + ".." if len(str(row.iloc[2])) > 12 else str(row.iloc[2])
                            dep_str = str(row.iloc[3])[:12] + ".." if len(str(row.iloc[3])) > 12 else str(row.iloc[3])
                            
                            try:
                                mes_val = float(row['Mesafe'])
                                b_god = max(0.0, min(100.0, round((1 - (mes_val / 0.8)) * 100, 1)))
                            except:
                                b_god = 100.0
                            bc_god = "#16a34a" if b_god >= 90 else ("#ca8a04" if b_god >= 70 else "#dc2626")

                            r_html = (
                                f"<tr><td>{lig_str}</td><td>{tarih_str}</td>"
                                f"<td><b>{ev_str}</b></td><td><b>{dep_str}</b></td>"
                                f"<td style='color:#ea580c;'>{s_iy}</td>"
                                f"<td style='color:#16a34a;'>{s_ms}</td>"
                                f"<td style='color:{bc_god}; font-weight:bold; text-align:center;'>%{b_god:.1f}</td>"
                                f"</tr>"
                            )

                            if ("STANDART" in mode_secim and gecerli) or \
                               ("JACKPOT" in mode_secim and hit_rev) or \
                               ("KAOS" in mode_secim and hit_kaos) or \
                               ("SKOR" in mode_secim and gecerli) or \
                               ("6+ GOL" in mode_secim and hit_arti):
                                liste_html += r_html

                        if total_weight > 0:
                            prob_ms1 = (w_ms1 / total_weight) * 100
                            prob_ms0 = (w_ms0 / total_weight) * 100
                            prob_ms2 = (w_ms2 / total_weight) * 100
                            prob_ust = (w_ust / total_weight) * 100
                            prob_alt = (w_alt / total_weight) * 100
                            prob_kg_var = (w_kgvar / total_weight) * 100
                            prob_kg_yok = (w_kgyok / total_weight) * 100
                            prob_rev = min((w_rev / total_weight) * 100 * 3.5, 95.0)   
                            prob_kaos = min((w_kaos / total_weight) * 100 * 3.5, 95.0) 
                            prob_arti_alti = min((w_arti_alti / total_weight) * 100 * 4.0, 95.0) 
                            top_5_scores = sorted([(k, (v/total_weight)*100) for k, v in score_weights.items()], key=lambda x: x[1], reverse=True)[:5]
                        else:
                            prob_ms1 = prob_ms0 = prob_ms2 = prob_ust = prob_alt = prob_kg_var = prob_kg_yok = prob_rev = prob_kaos = prob_arti_alti = 0.0
                            top_5_scores = [("N/A", 0.0)]
                            
                        while len(top_5_scores) < 5: top_5_scores.append(("N/A", 0.0))

                        takim_bilgi = ""
                        if ev_sahibi_ml: takim_bilgi += f" Ev: {ev_sahibi_ml}"
                        if deplasman_ml: takim_bilgi += f" Dep: {deplasman_ml}"
                        
                        st.success(f"✅ İncelenen Safkan Maç: {toplam_mac} | Lig: {lig_ml}{takim_bilgi}")

                        if "STANDART" in mode_secim:
                            colA, colB, colC = st.columns(3)
                            colA.metric("MS 1", f"%{prob_ms1:.1f}")
                            colB.metric("MS X", f"%{prob_ms0:.1f}")
                            colC.metric("MS 2", f"%{prob_ms2:.1f}")
                            st.write("---")
                            colD, colE, colF = st.columns(3)
                            colD.metric("2.5 ÜST", f"%{prob_ust:.1f}")
                            colE.metric("2.5 ALT", f"%{prob_alt:.1f}")
                            colF.metric("KG VAR", f"%{prob_kg_var:.1f}")

                        elif "JACKPOT" in mode_secim:
                            st.markdown(f"<div class='god-stat-box'><div class='god-stat-title'>🔥 TERS DÖNME İHTİMALİ (1/2 - 2/1)</div><div class='god-stat-value'>%{prob_rev:.1f}</div><div style='margin-top:10px; color:#64748b; font-weight:bold;'>Arşivde Tam Olarak: {count_12} Adet 1/2 | {count_21} Adet 2/1 Bulundu.</div></div>", unsafe_allow_html=True)

                        elif "KAOS" in mode_secim:
                            st.markdown(f"<div class='god-stat-box'><div class='god-stat-title'>⚔️ İKİ YARI DA KG VAR İHTİMALİ</div><div class='god-stat-value' style='color:#ca8a04;'>%{prob_kaos:.1f}</div><div style='margin-top:10px; color:#64748b; font-weight:bold;'>Arşivde Tam Olarak: {count_kaos_match} Adet Kaos Maçı Bulundu.</div></div>", unsafe_allow_html=True)

                        elif "SKOR" in mode_secim:
                            st.markdown("<div class='god-stat-box'><div class='god-stat-title'>🎯 EN GÜÇLÜ 5 SKOR İHTİMALİ</div>", unsafe_allow_html=True)
                            for s, p in top_5_scores:
                                st.write(f"**Skor {s.replace('4+','4')}** ➔ %{p:.1f}")
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                        elif "6+ GOL" in mode_secim:
                            st.markdown(f"<div class='god-stat-box'><div class='god-stat-title'>🚀 6+ GOL İHTİMALİ (KATLİAM)</div><div class='god-stat-value' style='color:#16a34a;'>%{prob_arti_alti:.1f}</div><div style='margin-top:10px; color:#64748b; font-weight:bold;'>Arşivde Tam Olarak: {count_arti_alti} Adet 6+ GOL Biten Maç Bulundu.</div></div>", unsafe_allow_html=True)

                        st.markdown("### 🔍 KANIT: Geçmiş Maç Listesi", unsafe_allow_html=True)
                        if not liste_html:
                            st.info("Bu mod için arşivde olay gerçekleşmemiş (Örn: Hiç 1/2 bitmemiş). Şablon temiz.")
                        else:
                            st.markdown(f"<div style='overflow-x:auto;'><table class='custom-table'><tr><th>LİG</th><th>TARİH</th><th>EV SAHİBİ</th><th>DEPLASMAN</th><th>İY</th><th>MS</th><th>BENZERLİK</th></tr>{liste_html}</table></div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Hesaplama Hatası: {str(e)}")
