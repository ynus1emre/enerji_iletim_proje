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
tab1, tab2 = st.tabs(["🧮 Kısım 1: Hat Parametre Hesapları", "📊 Kısım 2: Hat ve Sistem Hesaplamaları"])

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
# SEKME 2: 7 MADDELİK ÖZEL DİNAMİK ANALİZ
# ==========================================
with tab2:
    st.markdown("### 📊 Kısım 2: Hat ve Sistem Hesaplamaları")
    
    # Madde 2: Özel İletken/Direk İsimlendirmeleri
    data_map_k2 = {
        "154 kV - TA1 Çift Devre (Drake)": (0.0405, 0.582e-3, 19.85e-9),
        "400 kV - 3B1 Tek Devre 2'li Demet (Rail)": (0.03417, 0.9982e-3, 11.40e-9)
    }

    # Madde 3: Dinamik Manuel Giriş Paneli
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1:
            iletken_k2 = st.selectbox("İletken / Direk Tipi", list(data_map_k2.keys()))
            l_km = st.number_input("Mesafe (km)", value=100.0, step=10.0)
        with c2:
            pf_val = st.slider("Güç Katsayısı (cosφ)", 0.8, 1.0, 0.95)
            pf_tip = st.radio("Güç Durumu", ["Endüktif", "Kapasitif"])
        with c3:
            u_kv = st.number_input("Hat Sonu Gerilimi (kV)", value=154.0)
            btn = st.button("🚀 Analiz Et", type="primary", use_container_width=True)

    if btn:
        # Arka plan hesaplamaları
        R_k2, L_k2, C_k2 = data_map_k2[iletken_k2]
        f = 50.0; w = 2 * np.pi * f
        U2 = u_kv * 1000
        V2 = U2 / np.sqrt(3)
        Q_sign = 1 if pf_tip == "Endüktif" else -1
        
        Z_k2 = complex(R_k2, w*L_k2)
        Y_k2 = complex(0, w*C_k2)
        gamma_k2 = np.sqrt(Z_k2 * Y_k2)
        Zc_k2 = np.sqrt(Z_k2 / Y_k2)
        
        A_k2 = np.cosh(gamma_k2 * l_km)
        B_k2 = Zc_k2 * np.sinh(gamma_k2 * l_km)
        C_param_k2 = (1/Zc_k2) * np.sinh(gamma_k2 * l_km)
        D_k2 = A_k2
        
        Z_sur = np.sqrt(L_k2/C_k2)
        S2_VA = (U2**2) / Z_sur
        P2 = S2_VA * pf_val
        Q2 = Q_sign * S2_VA * np.sin(np.arccos(pf_val))
        I2 = np.conj(complex(P2, Q2) / (3 * V2))
        
        V1 = A_k2*V2 + B_k2*I2
        I1 = C_param_k2*V2 + D_k2*I2
        
        U1_kV = abs(V1) * np.sqrt(3) / 1000
        I1_A = abs(I1)
        P1_MW = (3 * V1 * np.conj(I1)).real / 1e6
        Q1_MVAr = (3 * V1 * np.conj(I1)).imag / 1e6
        verim = (P2 / (P1_MW * 1e6)) * 100
        reg = (((abs(V1)/abs(A_k2)) - V2) / V2) * 100

        # Madde 5: Metrik Kartları
        st.markdown("---")
        st.markdown("### 📈 Hat Performans Analizi")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Hat Başı Gerilimi (V1)", f"{round(U1_kV, 2)} kV")
        m2.metric("Hat Başı Akımı (I1)", f"{round(I1_A, 2)} A")
        m3.metric("Aktif Güç (P1)", f"{round(P1_MW, 2)} MW")
        m4.metric("Hat Verimi", f"% {round(verim, 2)}")
        st.write(f"**Regülasyon:** % {round(reg, 2)} | **Reaktif Güç:** {round(Q1_MVAr, 2)} MVAr")

        # Madde 6: Duruma Özel Teknik Mühendislik Yorumu
        yorum_metni = "Ferranti etkisi (kapasitif reaktansın baskın olması) nedeniyle hat sonu gerilimi hat başından yüksek çıkmış ve negatif regülasyon oluşmuştur." if pf_tip == "Kapasitif" else "Endüktif güç çekimi nedeniyle hat boyunca gerilim düşümü yaşanmış ve pozitif regülasyon oluşmuştur."
        st.info(f"**Teknik Analiz:** Seçilen {iletken_k2} hattı, {l_km} km mesafede {pf_tip} yük karakteristiği göstermektedir. {yorum_metni}")

        # Madde 4: 3'lü Grafik Paneli ve "Değişim" İfadesi
        x_vals = np.linspace(0, l_km, 50)
        v_list, p_list, q_list = [], [], []
        
        for x in x_vals:
            Ax = np.cosh(gamma_k2 * x)
            Bx = Zc_k2 * np.sinh(gamma_k2 * x)
            Cx = (1/Zc_k2) * np.sinh(gamma_k2 * x)
            Vx_ara = Ax*V2 + Bx*I2
            Ix_ara = Cx*V2 + Ax*I2
            v_list.append(abs(Vx_ara)*np.sqrt(3)/1000)
            p_list.append((3 * Vx_ara * np.conj(Ix_ara)).real / 1e6)
            q_list.append((3 * Vx_ara * np.conj(Ix_ara)).imag / 1e6)

        fig, ax = plt.subplots(1, 3, figsize=(18, 5))
        ax[0].plot(x_vals, v_list, 'b', lw=2)
        ax[0].set_title("Gerilim Değişimi (kV)")
        ax[0].set_xlabel("Mesafe (km)")
        ax[0].grid(True)

        ax[1].plot(x_vals, p_list, 'g', lw=2)
        ax[1].set_title("Aktif Güç Değişimi (MW)")
        ax[1].set_xlabel("Mesafe (km)")
        ax[1].grid(True)

        ax[2].plot(x_vals, q_list, 'r', lw=2)
        ax[2].set_title("Reaktif Güç Değişimi (MVAr)")
        ax[2].set_xlabel("Mesafe (km)")
        ax[2].grid(True)

        st.pyplot(fig)

        # Madde 7: Tabloya Hat Başı Akımı (I1) Eklenmesi
        st.markdown("### 📋 Özet Parametre Tablosu")
        df_ozet = pd.DataFrame({
            "Parametre": ["Gerilim V1 (kV)", "Hat Başı Akımı I1 (A)", "Aktif Güç P1 (MW)", "Reaktif Güç Q1 (MVAr)", "Regülasyon (%)", "Verim (%)"],
            "Değer": [round(U1_kV, 2), round(I1_A, 2), round(P1_MW, 2), round(Q1_MVAr, 2), round(reg, 2), round(verim, 2)]
        })
        st.dataframe(df_ozet, use_container_width=True)
