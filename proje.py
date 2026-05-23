import streamlit as st
import math
import cmath
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Enerji İletim Hesaplayıcı", layout="wide", page_icon="⚡")

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

    st.title("👨‍💻 Proje Ekibi")
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
    st.caption("Enerji İletimi Dersi Projesi Kısım 1 paces ve 2")

# --- ANA EKRAN BAŞLIK ---
st.title("⚡ Enerji İletim Hatları Hesaplama Aracı")
st.subheader("154kV ve 400kV Hat Parametreleri ve Analizleri")
st.divider()

# --- UYGULAMAYI SEKMELERE BÖLME ---
tab1, tab2 = st.tabs(["🧮 Kısım 1: Tekil Hesaplayıcı", "📊 Kısım 2: Grup 7 Toplu Analiz"])

# ==========================================
# SEKME 1: TEKİL HESAPLAYICI (KISIM 1)
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
# SEKME 2: GRUP 7 PROJE KISIM 2 ÇÖZÜMLERİ
# ==========================================
with tab2:
    st.markdown("### 🎯 Kısım 2: Grup 7 Özel Analizleri (7 Koşul)")
    st.info("Bu modül, raporunuzda istenen A, B, C ve D şıklarını 7 grup koşulu için sıralı olarak hesaplar, tabloları oluşturur ve P-V / Gerilim grafiklerini çizer.")
    
    if st.button("🚀 Tüm Analizleri Başlat ve Çizdir", use_container_width=True, type="primary"):
        with st.spinner("Hesaplamalar yapılıyor ve grafikler çiziliyor... Lütfen bekleyin."):
            
            # Hat Sabitleri (Önceki Doğrulanmış Hesaplamalardan)
            f = 50.0; w = 2 * np.pi * f
            R_drake, L_drake, C_drake = 0.0405, 0.582e-3, 19.85e-9  # Çift Devre TA1
            R_rail, L_rail, C_rail = 0.03417, 0.9982e-3, 11.40e-9   # Tek Devre 2'li Demet 3B1
            
            # Koşullar Matrisi 7 Kişiye Çıkarıldı ve Sıralandı
            kosullar = [
                (1, 154, 100, 0.95, -1, "Drake (Çift)"),
                (2, 154, 150, 0.95, 1, "Drake (Çift)"),
                (3, 154, 100, 0.95, 1, "Drake (Çift)"),
                (4, 400, 200, 0.85, 1, "Rail (Tek 2'li)"),
                (5, 400, 250, 0.85, 1, "Rail (Tek 2'li)"),  # Bahadır Yılmaz için eklenen yeni koşul
                (6, 400, 200, 0.85, -1, "Rail (Tek 2'li)"),
                (7, 400, 250, 0.85, -1, "Rail (Tek 2'li)")
            ]
            
            sonuclar_A = []
            sonuclar_D = []
            
            for kosul in kosullar:
                k_no, U2_kV, l, pf, pf_type, iletken = kosul
                U2 = U2_kV * 1000
                V2 = U2 / np.sqrt(3)
                pf_str = "Kapasitif" if pf_type == 1 else "Endüktif"
                
                # Parametre Atama
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
                
                # --- A ŞIKKI HESAPLAMALARI ---
                Z_sur = np.sqrt(L/C)
                S2_VA = (U2**2) / Z_sur
                P2 = S2_VA * pf
                Q2 = pf_type * S2_VA * np.sin(np.arccos(pf))
                I2 = np.conj(complex(P2, Q2) / (3 * V2))
                
                V1 = A*V2 + B*I2
                I1 = C_param*V2 + D*I2
                
                U1_kV = abs(V1) * np.sqrt(3) / 1000
                S1 = 3 * V1 * np.conj(I1)
                P1_MW = S1.real / 1e6
                Q1_MVAr = S1.imag / 1e6
                verim = (P2 / S1.real) * 100
                V2_bosta = abs(V1) / abs(A)
                reg = ((V2_bosta - V2) / V2) * 100
                
                sonuclar_A.append({
                    "Koşul": f"{k_no}",
                    "Gerilim / İletken": f"{U2_kV}kV / {iletken}",
                    "Uzunluk": f"{l} km",
                    "Güç Katsayısı": f"{pf} {pf_str}",
                    "Hat Başı Gerilimi U1 (kV)": round(U1_kV, 2),
                    "Aktif Güç P1 (MW)": round(P1_MW, 2),
                    "Reaktif Güç Q1 (MVAr)": round(Q1_MVAr, 2),
                    "Verim (%)": round(verim, 2),
                    "Regülasyon (%)": round(reg, 2)
                })
                
                # --- D ŞIKKI HESAPLAMALARI ---
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
                        I2_comp = np.conj((complex(S2_comp*pf, pf_type*S2_comp*np.sin(np.arccos(pf)))) / (3*V2))
                        
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

                # --- GRAFİK ÇİZİMLERİ (B VE C ŞIKKI) ---
                st.markdown(f"#### 📈 Koşul {k_no}: {U2_kV}kV, {iletken}, {l}km, {pf} {pf_str}")
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
                
                # B Şıkkı: Hat Profili
                x_vals = np.linspace(0, l, 11)
                Vx_vals = []
                for x in x_vals:
                    Ax = np.cosh(gamma * x)
                    Bx = Zc * np.sinh(gamma * x)
                    Vx = abs(Ax*V2 + Bx*I2) * np.sqrt(3) / 1000
                    Vx_vals.append(Vx)
                
                ax1.plot(l - x_vals, Vx_vals, '-bo', linewidth=2)
                ax1.set_title("B Şıkkı: Hat Boyunca Gerilim Profili")
                ax1.set_xlabel("Hat Başından Uzaklık (km)")
                ax1.set_ylabel("Gerilim (kV)")
                ax1.invert_xaxis()
                ax1.grid(True)
                
                # C Şıkkı: P-V Eğrisi
                k_loads = np.arange(0.1, 1.6, 0.1)
                P1_curve, V1_curve = [], []
                for k_l in k_loads:
                    S2_step = k_l * S2_VA
                    # np.np.sin hatası np.sin olarak tamamen düzeltildi:
                    I2_step = np.conj((complex(S2_step*pf, pf_type*S2_step*np.sin(np.arccos(pf)))) / (3*V2))
                    V1_step = A*V2 + B*I2_step
                    I1_step = C_param*V2 + D*I2_step
                    V1_curve.append(abs(V1_step) * np.sqrt(3) / 1000)
                    P1_curve.append((3 * V1_step * np.conj(I1_step)).real / 1e6)
                
                ax2.plot(P1_curve, V1_curve, '-r*', linewidth=2)
                ax2.set_title("C Şıkkı: P-V (Burun) Eğrisi (0.1S2 - 1.5S2)")
                ax2.set_xlabel("Hat Başı Aktif Gücü P1 (MW)")
                ax2.set_ylabel("Hat Başı Gerilimi V1 (kV)")
                ax2.grid(True)
                
                st.pyplot(fig)
                st.divider()

            # --- TABLOLARI EKRANA BASMA ---
            st.success("Tüm hesaplamalar başarıyla tamamlandı! Tabloları aşağıdan inceleyip raporunuza kopyalayabilirsiniz.")
            
            st.markdown("### 📋 A Şıkkı: Nominal Yükleme (SIL) Tablosu")
            df_A = pd.DataFrame(sonuclar_A)
            st.dataframe(df_A, use_container_width=True)
            
            st.markdown("### 📋 D Şıkkı: Seri Kompanzasyon (%30 ve %50) Tablosu")
            df_D = pd.DataFrame(sonuclar_D)
            st.dataframe(df_D, use_container_width=True)
