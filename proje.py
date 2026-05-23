import streamlit as st
import math
import cmath
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Enerji İletim Hesaplayıcı | Grup 7", layout="wide", page_icon="⚡")

# --- LOGO VE KLASÖR YOLU KONTROLÜ ---
base_path = os.path.dirname(__file__)
logo_path = os.path.join(base_path, "kou_logo.jpg")

# --- SOL YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.markdown("### 🏛️ KOCAELİ ÜNİVERSİTESİ")
        st.caption("Elektrik Mühendisliği Bölümü")
        st.info("Not: 'kou_logo.jpg' dosyası bulunamadı.")

    st.title("👨‍💻 Grup 7 Proje Ekibi")
    st.divider()
    st.markdown("👥 **Grup Üyeleri:**")
    st.markdown("1. Yunus Emre Koca - 230206019")
    st.markdown("2. Kürşad Çelik - 230206011")
    st.markdown("3. Göktuğ Emir Göktaş - 230206079")
    st.markdown("4. Enes Faruk Kelleveziroğlu - 240206001")
    st.markdown("5. Faruk Sevim - 190206047")
    st.markdown("6. Kağan Özmen - 190206031")
    st.markdown("7. Bahadır Yılmaz - 200206093")
    st.divider()
    st.caption("Enerji İletimi Dersi Projesi Kısım 1 ve 2")

# --- ANA EKRAN BAŞLIK ---
st.title("⚡ Enerji İletim Hatları Hesaplama Aracı")
st.subheader("Grup 7 Özel: 154kV Drake ve 400kV Rail Hat Analizleri")
st.divider()

# --- UYGULAMAYI SEKMELERE BÖLME ---
tab1, tab2 = st.tabs(["🧮 Kısım 1: Hat Parametre Hesapları", "📊 Kısım 2: Grup 7 Hat ve Sistem Hesaplamaları"])

# ==========================================
# SEKME 1: TEKİL HESAPLAYICI (KISIM 1) - HİÇ DOKUNULMADI
# ==========================================
with tab1:
    freq = 50.0
    omega = 2 * math.pi * freq
    epsilon_0 = 8.854e-12
    demet_d = 0.45

    iletkenler_tablosu = {
        "Hawk": {"cap_inc": 0.858, "gmr_ft": 0.0289, "r_ohm_mil": 0.2120},
        "Drake": {"cap_inc": 1.108, "gmr_ft": 0.0373, "r_ohm_mil": 0.1284},
        "Cardinal": {"cap_inc": 1.196, "gmr_ft": 0.0402, "r_ohm_mil": 0.1082},
        "Pheasant": {"cap_inc": 1.382, "gmr_ft": 0.0466, "r_ohm_mil": 0.0821},
        "Rail": {"cap_inc": 1.165, "gmr_ft": 0.0386, "r_ohm_mil": 0.1092},
        "Partridge": {"cap_inc": 0.642, "gmr_ft": 0.0217, "r_ohm_mil": 0.3792},
        "Ostrich": {"cap_inc": 0.680, "gmr_ft": 0.0229, "r_ohm_mil": 0.3372},
        "Grosbeak": {"cap_inc": 0.990, "gmr_ft": 0.0335, "r_ohm_mil": 0.1596}
    }

    direkler = [
        "Tip 1: Tek Devre (Demet Yok)",
        "Tip 2: Tek Devre (3'lü Demet)",
        "Tip 3: Çift Devre (Demet Yok)",
        "Tip 4: Çift Devre (2'li Demet)"
    ]

    col1, col2 = st.columns(2)
    with col1:
        gerilim_secimi = st.selectbox("1. Gerilim Seviyesi", ["154 kV", "400 kV"])
        iletken_adi = st.selectbox("2. İletken Tipi", list(iletkenler_tablosu.keys()))
    with col2:
        direk_secimi = st.selectbox("3. Direk Tipi", direkler)
        uzunluk_km = st.number_input("4. Hat Uzunluğu (km)", min_value=1.0, value=250.0, step=10.0)

    if st.button("🚀 Parametreleri Hesapla", use_container_width=True):
        veri = iletkenler_tablosu[iletken_adi]
        r_yaricap_m = (veri["cap_inc"] * 25.4 / 2) / 1000
        gmr_m = veri["gmr_ft"] * 0.3048
        r_direnc_ohm_km = veri["r_ohm_mil"] / 1.60934

        if "154" in gerilim_secimi:
            D_ab, D_bc, D_ca, D_cift_devre = 4.0, 4.0, 8.0, 7.0
        else:
            D_ab, D_bc, D_ca, D_cift_devre = 8.5, 8.5, 17.0, 12.0

        GMD = (D_ab * D_bc * D_ca) ** (1 / 3)

        if "Tip 1" in direk_secimi:
            gmr_L_eq, gmr_C_eq, R_eq = gmr_m, r_yaricap_m, r_direnc_ohm_km
        elif "Tip 2" in direk_secimi:
            gmr_L_eq = (gmr_m * demet_d * demet_d) ** (1 / 3)
            gmr_C_eq = (r_yaricap_m * demet_d * demet_d) ** (1 / 3)
            R_eq = r_direnc_ohm_km / 3
        elif "Tip 3" in direk_secimi:
            gmr_L_eq, gmr_C_eq, R_eq = math.sqrt(gmr_m * D_cift_devre), math.sqrt(r_yaricap_m * D_cift_devre), r_direnc_ohm_km / 2
        else:
            gmr_L_eq = math.sqrt(math.sqrt(gmr_m * demet_d) * D_cift_devre)
            gmr_C_eq = math.sqrt(math.sqrt(r_yaricap_m * demet_d) * D_cift_devre)
            R_eq = r_direnc_ohm_km / 4

        L_mH_km = 0.2 * math.log(GMD / gmr_L_eq)
        C_nF_km = ((2 * math.pi * epsilon_0) / math.log(GMD / gmr_C_eq)) * 1000 * 1e9
        Z_ohm_km = complex(R_eq, omega * (L_mH_km * 1e-3))
        Y_S_km = complex(0, omega * (C_nF_km * 1e-9))

        gamma = cmath.sqrt(Z_ohm_km * Y_S_km)
        Zc = cmath.sqrt(Z_ohm_km / Y_S_km)

        A = cmath.cosh(gamma * uzunluk_km)
        D = A
        B = Zc * cmath.sinh(gamma * uzunluk_km)
        C_param = cmath.sinh(gamma * uzunluk_km) / Zc

        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.markdown("### 📌 Temel Parametreler")
            st.code(f"R (AA Direnci) : {R_eq:.4f} ohm/km\n"
                    f"L (Endüktans)  : {L_mH_km:.4f} mH/km\n"
                    f"C (Kapasitans) : {C_nF_km:.4f} nF/km\n"
                    f"Z (Seri Emp.)  : {Z_ohm_km.real:.4f} + j{Z_ohm_km.imag:.4f} ohm/km\n"
                    f"Y (Paralel Ad.): 0.0000 + j{Y_S_km.imag:.6f} S/km", language="text")
        with col_res2:
            st.markdown("### 📏 Uzun Hat (A,B,C,D)")
            st.code(f"A Parametresi  : {A.real:.5f} + j{A.imag:.5f}\n"
                    f"B Parametresi  : {B.real:.4f} + j{B.imag:.4f} ohm\n"
                    f"C Parametresi  : {C_param.real:.6f} + j{C_param.imag:.6f} S\n"
                    f"D Parametresi  : {D.real:.5f} + j{D.imag:.5f}", language="text")


# ==========================================
# SEKME 2: GRUP 7 PROJE KISIM 2 (TOPLU TABLOLAR VE GRAFİKLER)
# ==========================================
with tab2:
    st.markdown("### 🎯 Kısım 2: Grup 7 Toplu Hat ve Sistem Analizleri")
    st.info("Bu modül, Grup 7'ye özel tahsis edilen 154kV (Drake) ve 400kV (Rail) 7 adet koşulu aynı anda hesaplar, ana tabloları oluşturur (Hat Başı Akımı I1 dahil) ve her bir koşul için detaylı P-V / Gerilim grafiklerini teknik yorumlarıyla birlikte listeler.")
    
    if st.button("🚀 Tüm 7 Koşulu Analiz Et ve Raporla", use_container_width=True, type="primary"):
        with st.spinner("Tüm koşullar hesaplanıyor, tablolar ve grafikler oluşturuluyor..."):
            
            f = 50.0; w = 2 * np.pi * f
            R_drake, L_drake, C_drake = 0.0405, 0.582e-3, 19.85e-9  
            R_rail, L_rail, C_rail = 0.03417, 0.9982e-3, 11.40e-9   
            
            # Format: (Koşul No, Gerilim(kV), Uzunluk(km), Güç Katsayısı, 1=Kapasitif / -1=Endüktif, İletken)
            kosullar = [
                (1, 154, 100, 0.95, -1, "Drake (Çift)"),
                (2, 154, 150, 0.95, 1, "Drake (Çift)"),
                (3, 154, 100, 0.95, 1, "Drake (Çift)"),
                (4, 400, 200, 0.85, 1, "Rail (Tek 2'li)"),
                (5, 400, 250, 0.85, 1, "Rail (Tek 2'li)"),
                (6, 400, 200, 0.85, -1, "Rail (Tek 2'li)"),
                (7, 400, 250, 0.85, -1, "Rail (Tek 2'li)")
            ]
            
            sonuclar_A = []
            sonuclar_D = []
            grafik_datalari = []
            
            for kosul in kosullar:
                k_no, U2_kV, l, pf, pf_type, iletken = kosul
                U2 = U2_kV * 1000
                V2 = U2 / np.sqrt(3)
                
                pf_str = "Kapasitif" if pf_type == 1 else "Endüktif"
                Q_sign = -1 if pf_type == 1 else 1
                
                if "Drake" in iletken:
                    R, L, C = R_drake, L_drake, C_drake
                else:
                    R, L, C = R_rail, L_rail, C_rail
                    
                Z = complex(R, w*L)
                Y = complex(0, w*C)
                Zc = np.sqrt(Z/Y)
                gamma = np.sqrt(Z*Y)
                
                A = np.cosh(gamma * l)
                B = Zc * np.sinh(gamma * l)
                C_param = (1/Zc) * np.sinh(gamma * l)
                D = A
                
                # A Şıkkı Hesaplamaları
                Z_sur = np.sqrt(L/C)
                S2_VA = (U2**2) / Z_sur
                P2 = S2_VA * pf
                Q2 = Q_sign * S2_VA * np.sin(np.arccos(pf)) 
                I2 = np.conj(complex(P2, Q2) / (3 * V2))
                
                V1 = A*V2 + B*I2
                I1 = C_param*V2 + D*I2
                
                U1_kV = abs(V1) * np.sqrt(3) / 1000
                I1_A = abs(I1)
                S1 = 3 * V1 * np.conj(I1)
                P1_MW = S1.real / 1e6
                Q1_MVAr = S1.imag / 1e6
                verim = (P2 / S1.real) * 100
                V2_bosta = abs(V1) / abs(A)
                reg = ((V2_bosta - V2) / V2) * 100
                
                # Tablo A için veri ekleme (Hat Başı Akımı dahil)
                sonuclar_A.append({
                    "Koşul": f"{k_no}",
                    "Gerilim / İletken": f"{U2_kV}kV / {iletken}",
                    "Uzunluk": f"{l} km",
                    "Güç Katsayısı": f"{pf} {pf_str}",
                    "Hat Başı Gerilimi U1 (kV)": round(U1_kV, 2),
                    "Hat Başı Akımı I1 (A)": round(I1_A, 2),
                    "Aktif Güç P1 (MW)": round(P1_MW, 2),
                    "Reaktif Güç Q1 (MVAr)": round(Q1_MVAr, 2),
                    "Verim (%)": round(verim, 2),
                    "Regülasyon (%)": round(reg, 2)
                })
                
                # D Şıkkı Hesaplamaları (Kompanzasyon)
                for comp_ratio in [0.30, 0.50]:
                    X_L = w*L
                    X_C_comp = comp_ratio * X_L
                    Z_comp = complex(R, X_L - X_C_comp)
                    gamma_c = np.sqrt(Z_comp * Y)
                    Zc_c = np.sqrt(Z_comp / Y)
                    
                    A_c = np.cosh(gamma_c * l)
                    B_c = Zc_c * np.sinh(gamma_c * l)
                    C_c = (1/Zc_c) * np.sinh(gamma_c * l)
                    
                    for load_mult in [1, 10]:
                        S2_comp = load_mult * S2_VA
                        I2_comp = np.conj((complex(S2_comp*pf, Q_sign*S2_comp*np.sin(np.arccos(pf)))) / (3*V2))
                        
                        V1_comp = A_c*V2 + B_c*I2_comp
                        I1_comp = C_c*V2 + A_c*I2_comp
                        
                        P1_c = (3 * V1_comp * np.conj(I1_comp)).real
                        verim_c = ((S2_comp*pf) / P1_c) * 100
                        reg_c = (((abs(V1_comp)/abs(A_c)) - V2) / V2) * 100
                        
                        sonuclar_D.append({
                            "Koşul": f"{k_no}",
                            "Kompanzasyon": f"%{int(comp_ratio*100)}",
                            "Yük Durumu": f"{load_mult}xS2",
                            "Verim (%)": round(verim_c, 2),
                            "Regülasyon (%)": round(reg_c, 2)
                        })

                # Grafikler için veriyi sakla
                grafik_datalari.append({
                    "k_no": k_no, "U2_kV": U2_kV, "iletken": iletken, "l": l, "pf": pf, "pf_str": pf_str,
                    "pf_type": pf_type, "gamma": gamma, "Zc": Zc, "V2": V2, "I2": I2, "C_param": C_param, "A": A
                })

            # --- 1. KISIM: DEV TABLOLARIN EKRANA BASILMASI ---
            st.success("✅ Tüm hesaplamalar başarıyla tamamlandı!")
            
            st.markdown("### 📋 A Şıkkı: Nominal Yükleme (SIL) Tablosu")
            df_A = pd.DataFrame(sonuclar_A)
            st.dataframe(df_A, use_container_width=True)
            
            st.markdown("### 📋 D Şıkkı: Seri Kompanzasyon (%30 ve %50) Tablosu")
            df_D = pd.DataFrame(sonuclar_D)
            st.dataframe(df_D, use_container_width=True)
            
            st.divider()

            # --- 2. KISIM: HER KOŞUL İÇİN ÖZEL GRAFİK VE YORUMLAR ---
            st.markdown("### 📉 Koşullara Özel Değişim Grafikleri ve Mühendislik Yorumları")
            
            for g_data in grafik_datalari:
                st.markdown(f"#### 🔹 Koşul {g_data['k_no']}: {g_data['U2_kV']}kV, {g_data['iletken']}, {g_data['l']}km, {g_data['pf']} {g_data['pf_str']}")
                
                # Yorum Kutusu
                yorum_metni = "Ferranti etkisi (kapasitif reaktansın baskın olması) nedeniyle hat sonu gerilimi hat başından yüksek çıkmış ve negatif regülasyon oluşmuştur." if g_data['pf_type'] == 1 else "Endüktif güç çekimi nedeniyle hat boyunca gerilim düşümü yaşanmış ve pozitif regülasyon oluşmuştur."
                st.info(f"**Teknik Analiz:** Seçilen {g_data['iletken']} hattı, {g_data['l']} km mesafede {g_data['pf_str']} yük karakteristiği göstermektedir. {yorum_metni}")

                # 3'lü Değişim Grafiği (B ve C Şıkları Harmanlanmış)
                x_vals = np.linspace(0, g_data['l'], 50)
                v_list, p_list, q_list = [], [], []
                
                for x in x_vals:
                    Ax = np.cosh(g_data['gamma'] * x)
                    Bx = g_data['Zc'] * np.sinh(g_data['gamma'] * x)
                    Cx = (1/g_data['Zc']) * np.sinh(g_data['gamma'] * x)
                    Vx_ara = Ax*g_data['V2'] + Bx*g_data['I2']
                    Ix_ara = Cx*g_data['V2'] + Ax*g_data['I2']
                    
                    v_list.append(abs(Vx_ara)*np.sqrt(3)/1000)
                    p_list.append((3 * Vx_ara * np.conj(Ix_ara)).real / 1e6)
                    q_list.append((3 * Vx_ara * np.conj(Ix_ara)).imag / 1e6)

                fig, ax = plt.subplots(1, 3, figsize=(18, 4))
                
                ax[0].plot(x_vals, v_list, 'b', lw=2)
                ax[0].set_title("Gerilim Değişimi (kV)")
                ax[0].set_xlabel("Hat Başından Uzaklık (km)")
                ax[0].grid(True)

                ax[1].plot(x_vals, p_list, 'g', lw=2)
                ax[1].set_title("Aktif Güç Değişimi (MW)")
                ax[1].set_xlabel("Hat Başından Uzaklık (km)")
                ax[1].grid(True)

                ax[2].plot(x_vals, q_list, 'r', lw=2)
                ax[2].set_title("Reaktif Güç Değişimi (MVAr)")
                ax[2].set_xlabel("Hat Başından Uzaklık (km)")
                ax[2].grid(True)

                st.pyplot(fig)
                st.markdown("<br>", unsafe_allow_html=True)
