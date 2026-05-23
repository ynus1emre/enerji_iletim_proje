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
# SEKME 1: TEKİL HESAPLAYICI (KISIM 1) - DOKUNULMADI
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
# SEKME 2: GRUP 7 PROJE KISIM 2
# ==========================================
with tab2:
    st.markdown("## 📊 Kısım 2: Grup 7 Hat ve Sistem Hesaplamaları")
    
    # --- GRUP 7 SABİTLERİ ---
    f = 50.0; w = 2 * np.pi * f
    R_drake, L_drake, C_drake = 0.0405, 0.582e-3, 19.85e-9  
    R_rail, L_rail, C_rail = 0.03417, 0.9982e-3, 11.40e-9   
    
    # -------------------------------------------------------------------------
    # BÖLÜM 2.1: MANUEL KULLANICI GİRİŞLİ TEKİL ANALİZ 
    # -------------------------------------------------------------------------
    st.markdown("### 🎛️ Tekil Senaryo Simülatörü")
    with st.container():
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            manuel_senaryo = st.radio("📌 Hesaplama Senaryosunu Seçin:", ["154 kV - TA1 Çift Devre (Drake)", "400 kV - 3B1 Tek Devre 2'li Demet (Rail)"])
        with col_m2:
            manuel_l = st.number_input("📏 Hat Uzunluğu (km)", value=100.0, step=10.0)
            manuel_pf = st.number_input("⚡ Güç Katsayısı", value=0.95, step=0.01)
            manuel_pf_tip = st.selectbox("🔄 Katsayı Tipi", ["Endüktif", "Kapasitif"])
            
        tekil_hesapla_btn = st.button("⚙️ Tekil Senaryoyu Hesapla", type="primary", use_container_width=True)

    # Butona basıldığında çalışacak tekil hesaplama bloğu
    if tekil_hesapla_btn:
        if "154" in manuel_senaryo:
            R_m, L_m, C_m, U2_m = R_drake, L_drake, C_drake, 154000
        else:
            R_m, L_m, C_m, U2_m = R_rail, L_rail, C_rail, 400000

        Z_m = complex(R_m, w*L_m); Y_m = complex(0, w*C_m)
        gamma_m = np.sqrt(Z_m * Y_m); Zc_m = np.sqrt(Z_m / Y_m)
        A_m = np.cosh(gamma_m * manuel_l); B_m = Zc_m * np.sinh(gamma_m * manuel_l)
        C_param_m = (1/Zc_m) * np.sinh(gamma_m * manuel_l); D_m = A_m

        V2_m = U2_m / np.sqrt(3)
        Q_sign_m = -1 if manuel_pf_tip == "Kapasitif" else 1
        Z_sur_m = np.sqrt(L_m/C_m)
        S2_VA_m = (U2_m**2) / Z_sur_m
        P2_m = S2_VA_m * manuel_pf
        Q2_m = Q_sign_m * S2_VA_m * np.sin(np.arccos(manuel_pf))
        I2_m = np.conj(complex(P2_m, Q2_m) / (3 * V2_m))

        V1_m = A_m*V2_m + B_m*I2_m
        I1_m = C_param_m*V2_m + D_m*I2_m

        U1_kV_m = abs(V1_m) * np.sqrt(3) / 1000
        I1_A_m = abs(I1_m)
        P1_MW_m = (3 * V1_m * np.conj(I1_m)).real / 1e6
        Q1_MVAr_m = (3 * V1_m * np.conj(I1_m)).imag / 1e6
        verim_m = (P2_m / (P1_MW_m * 1e6)) * 100
        reg_m = (((abs(V1_m)/abs(A_m)) - V2_m) / V2_m) * 100

        # UI: Parametre Kutucukları
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("#### 📌 Temel Parametreler")
            st.code(f"R (AA Direnci) : {R_m:.4f} ohm/km\nL (Endüktans)  : {L_m*1000:.4f} mH/km\nC (Kapasitans) : {C_m*1e9:.4f} nF/km\nZ (Seri Emp.)  : {Z_m.real:.4f} + j{Z_m.imag:.4f} ohm/km\nY (Paralel Ad.): {Y_m.real:.4f} + j{Y_m.imag:.6f} S/km", language="text")
        with col_p2:
            st.markdown("#### 📏 Uzun Hat (A,B,C,D)")
            st.code(f"A Parametresi  : {A_m.real:.5f} + j{A_m.imag:.5f}\nB Parametresi  : {B_m.real:.4f} + j{B_m.imag:.4f} ohm\nC Parametresi  : {C_param_m.real:.6f} + j{C_param_m.imag:.6f} S\nD Parametresi  : {D_m.real:.5f} + j{D_m.imag:.5f}", language="text")

        # UI: Metrik Kartları
        st.markdown("### 📊 Hat Performans Analizi")
        st.markdown("#### Hat Başı Değerleri ve Performans")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Hat Başı Gerilimi (V1)", f"{round(U1_kV_m, 2)} kV")
        m2.metric("Hat Başı Akımı (I1)", f"{round(I1_A_m, 2)} A")
        m3.metric("Aktif Güç (P1)", f"{round(P1_MW_m, 2)} MW")
        m4.metric("Hat Verimi", f"% {round(verim_m, 2)}")
        st.write(f"**Regülasyon:** % {round(reg_m, 2)} | **Reaktif Güç:** {round(Q1_MVAr_m, 2)} MVAr | **Güç Katsayısı:** {manuel_pf}")

        # UI: Tekil Analiz Grafikleri (YENİ EKLENEN KISIM)
        st.markdown("#### Hat Boyunca Değişim Grafikleri")
        x_vals_m = np.linspace(0, manuel_l, 11)
        v_list_m, p_list_m, q_list_m = [], [], []
        
        for x in x_vals_m:
            Ax = np.cosh(gamma_m * x)
            Bx = Zc_m * np.sinh(gamma_m * x)
            Cx = (1/Zc_m) * np.sinh(gamma_m * x)
            Vx_ara = Ax*V2_m + Bx*I2_m
            Ix_ara = Cx*V2_m + Ax*I2_m
            
            v_list_m.append(abs(Vx_ara)*np.sqrt(3)/1000)
            p_list_m.append((3 * Vx_ara * np.conj(Ix_ara)).real / 1e6)
            q_list_m.append((3 * Vx_ara * np.conj(Ix_ara)).imag / 1e6)

        fig_m, ax_m = plt.subplots(1, 3, figsize=(18, 4))
        
        ax_m[0].plot(x_vals_m, v_list_m, '-bo', lw=2, markersize=6)
        ax_m[0].set_title("Gerilim Değişimi (10 Nokta)")
        ax_m[0].set_xlabel("Hat Başından Uzaklık (km)")
        ax_m[0].set_ylabel("Gerilim (kV)")
        ax_m[0].grid(True)

        ax_m[1].plot(x_vals_m, p_list_m, '-go', lw=2, markersize=6)
        ax_m[1].set_title("Aktif Güç Değişimi (10 Nokta)")
        ax_m[1].set_xlabel("Hat Başından Uzaklık (km)")
        ax_m[1].set_ylabel("Aktif Güç (MW)")
        ax_m[1].grid(True)

        ax_m[2].plot(x_vals_m, q_list_m, '-ro', lw=2, markersize=6)
        ax_m[2].set_title("Reaktif Güç Değişimi (10 Nokta)")
        ax_m[2].set_xlabel("Hat Başından Uzaklık (km)")
        ax_m[2].set_ylabel("Reaktif Güç (MVAr)")
        ax_m[2].grid(True)

        st.pyplot(fig_m)

        # UI: Seri Kompanzasyon Performansı
        st.markdown("#### Seri Kompanzasyon Performansı")
        for comp_ratio, load_mult in [(0.30, 1), (0.50, 1), (0.30, 10), (0.50, 10)]:
            X_L_m = w*L_m
            X_C_comp_m = comp_ratio * X_L_m
            Z_comp_m = complex(R_m, X_L_m - X_C_comp_m)
            gamma_c_m = np.sqrt(Z_comp_m * Y_m)
            Zc_c_m = np.sqrt(Z_comp_m / Y_m)
            A_c_m = np.cosh(gamma_c_m * manuel_l)
            B_c_m = Zc_c_m * np.sinh(gamma_c_m * manuel_l)
            C_c_m = (1/Zc_c_m) * np.sinh(gamma_c_m * manuel_l)
            
            S2_comp_m = load_mult * S2_VA_m
            I2_comp_m = np.conj((complex(S2_comp_m*manuel_pf, Q_sign_m*S2_comp_m*np.sin(np.arccos(manuel_pf)))) / (3*V2_m))
            V1_comp_m = A_c_m*V2_m + B_c_m*I2_comp_m
            I1_comp_m = C_c_m*V2_m + A_c_m*I2_comp_m
            P1_c_m = (3 * V1_comp_m * np.conj(I1_comp_m)).real
            verim_c_m = ((S2_comp_m*manuel_pf) / P1_c_m) * 100
            reg_c_m = (((abs(V1_comp_m)/abs(A_c_m)) - V2_m) / V2_m) * 100

            icon = "🟢" if load_mult == 1 else "🔴"
            load_str = "Normal Yükte (S2)" if load_mult == 1 else "Aşırı Yükte (10xS2)"
            st.markdown(f"**{icon} {load_str}:** %{int(comp_ratio*100)} Komp. ➔ Verim: %{round(verim_c_m, 2)} | Regülasyon: %{round(reg_c_m, 2)}")

    st.divider()

    # -------------------------------------------------------------------------
    # BÖLÜM 2.2: TOPLU 7 KOŞUL ANALİZİ VE GRAFİKLER
    # -------------------------------------------------------------------------
    st.markdown("### 📑 Grup 7 Toplu Rapor Üretici (7 Koşul)")
    
    if st.button("🚀 Tüm 7 Koşulu Analiz Et ve Raporla", use_container_width=True, type="secondary"):
        with st.spinner("Tüm koşullar hesaplanıyor, tablolar ve grafikler oluşturuluyor..."):
            
            kosullar = [
                (1, 154, 100, 0.95, -1, "154 kV - TA1 Çift Devre (Drake)"),
                (2, 154, 150, 0.95, 1, "154 kV - TA1 Çift Devre (Drake)"),
                (3, 154, 100, 0.95, 1, "154 kV - TA1 Çift Devre (Drake)"),
                (4, 400, 200, 0.85, 1, "400 kV - 3B1 Tek Devre 2'li Demet (Rail)"),
                (5, 400, 250, 0.85, 1, "400 kV - 3B1 Tek Devre 2'li Demet (Rail)"),
                (6, 400, 200, 0.85, -1, "400 kV - 3B1 Tek Devre 2'li Demet (Rail)"),
                (7, 400, 250, 0.85, -1, "400 kV - 3B1 Tek Devre 2'li Demet (Rail)")
            ]
            
            sonuclar_A, sonuclar_D, grafik_datalari = [], [], []
            
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
                    
                Z = complex(R, w*L); Y = complex(0, w*C)
                Zc = np.sqrt(Z/Y); gamma = np.sqrt(Z*Y)
                
                A = np.cosh(gamma * l); B = Zc * np.sinh(gamma * l)
                C_param = (1/Zc) * np.sinh(gamma * l); D = A
                
                Z_sur = np.sqrt(L/C); S2_VA = (U2**2) / Z_sur
                P2 = S2_VA * pf; Q2 = Q_sign * S2_VA * np.sin(np.arccos(pf)) 
                I2 = np.conj(complex(P2, Q2) / (3 * V2))
                
                V1 = A*V2 + B*I2; I1 = C_param*V2 + D*I2
                
                U1_kV = abs(V1) * np.sqrt(3) / 1000
                I1_A = abs(I1)
                S1 = 3 * V1 * np.conj(I1)
                P1_MW = S1.real / 1e6; Q1_MVAr = S1.imag / 1e6
                verim = (P2 / S1.real) * 100
                V2_bosta = abs(V1) / abs(A)
                reg = ((V2_bosta - V2) / V2) * 100
                
                sonuclar_A.append({
                    "Koşul": f"{k_no}", "Gerilim / İletken": f"{iletken}", "Uzunluk": f"{l} km",
                    "Güç Katsayısı": f"{pf} {pf_str}", "Hat Başı Gerilimi U1 (kV)": round(U1_kV, 2),
                    "Hat Başı Akımı I1 (A)": round(I1_A, 2), "Aktif Güç P1 (MW)": round(P1_MW, 2),
                    "Reaktif Güç Q1 (MVAr)": round(Q1_MVAr, 2), "Verim (%)": round(verim, 2), "Regülasyon (%)": round(reg, 2)
                })
                
                for comp_ratio in [0.30, 0.50]:
                    X_C_comp = comp_ratio * (w*L)
                    Z_comp = complex(R, (w*L) - X_C_comp)
                    gamma_c = np.sqrt(Z_comp * Y); Zc_c = np.sqrt(Z_comp / Y)
                    A_c = np.cosh(gamma_c * l); B_c = Zc_c * np.sinh(gamma_c * l); C_c = (1/Zc_c) * np.sinh(gamma_c * l)
                    
                    for load_mult in [1, 10]:
                        S2_comp = load_mult * S2_VA
                        I2_comp = np.conj((complex(S2_comp*pf, Q_sign*S2_comp*np.sin(np.arccos(pf)))) / (3*V2))
                        V1_comp = A_c*V2 + B_c*I2_comp; I1_comp = C_c*V2 + A_c*I2_comp
                        P1_c = (3 * V1_comp * np.conj(I1_comp)).real
                        verim_c = ((S2_comp*pf) / P1_c) * 100
                        reg_c = (((abs(V1_comp)/abs(A_c)) - V2) / V2) * 100
                        
                        sonuclar_D.append({
                            "Koşul": f"{k_no}", "Kompanzasyon": f"%{int(comp_ratio*100)}", "Yük Durumu": f"{load_mult}xS2",
                            "Verim (%)": round(verim_c, 2), "Regülasyon (%)": round(reg_c, 2)
                        })

                grafik_datalari.append({
                    "k_no": k_no, "iletken": iletken, "l": l, "pf": pf, "pf_str": pf_str,
                    "gamma": gamma, "Zc": Zc, "V2": V2, "I2": I2, "C_param": C_param, 
                    "A": A, "B": B, "D": D, "S2_VA": S2_VA, "Q_sign": Q_sign
                })

            # Tablolar
            st.success("✅ Toplu Analiz Başarıyla Tamamlandı!")
            st.markdown("### 📋 A Şıkkı: Nominal Yükleme (SIL) Tablosu")
            st.dataframe(pd.DataFrame(sonuclar_A), use_container_width=True)
            
            st.markdown("### 📋 D Şıkkı: Seri Kompanzasyon Tablosu")
            st.dataframe(pd.DataFrame(sonuclar_D), use_container_width=True)
            st.divider()

            # Grafikler ve Yorumlar
            st.markdown("### 📉 Koşullara Özel Değişim ve P-V Eğrileri")
            
            # Her Koşul İçin Özel Yorum Sözlüğü
            yorumlar = {
                1: "154 kV seviyesinde ve 100 km gibi orta uzunluktaki bu hatta, endüktif yük çekimi (0.95) beklendiği gibi doğal bir gerilim düşümüne sebep olmuştur. Hat kararlı sınırlar içindedir.",
                2: "150 km'ye uzayan hatta kapasitif yüklenme, Ferranti etkisini belirginleştirerek hat sonu gerilimini kaynak geriliminin üzerine taşımıştır. Negatif regülasyon gözlenmektedir.",
                3: "Kısa mesafeli (100 km) kapasitif yüklenme senaryosunda hafif bir Ferranti etkisi görülmektedir. Hat sonu gerilimi tolere edilebilir bir artış göstermiştir.",
                4: "400 kV EHV (Ekstra Yüksek Gerilim) ve 200 km uzunluğundaki hatta aşırı kapasitif (0.85) yüklenme, ciddi bir Ferranti etkisine yol açmıştır. Sistemin reaktif güç dengesi zorlanmaktadır.",
                5: "250 km kritik hat uzunluğunda şiddetli kapasitif etki (0.85), tehlikeli boyutlarda aşırı gerilim (overvoltage) yaratmaktadır. Seri/şönt kompanzasyon sistemleri kesinlikle devrede olmalıdır.",
                6: "Ağır endüktif yüklenme (0.85), 400 kV sistemin gerilim profilini aşağı çekmiştir. Yüksek aktif ve reaktif güç transferi, hat kayıplarını artırmakta ve pozitif regülasyon yaratmaktadır.",
                7: "250 km uzunluğunda yoğun endüktif güç akışı, hat sonu geriliminde çökme eğilimi (voltage collapse) riskini artırmaktadır. Gerilim stabilitesi için P-V burun eğrisi marjları daralmıştır."
            }
            
            for g_data in grafik_datalari:
                st.markdown(f"#### 🔹 Koşul {g_data['k_no']}: {g_data['iletken']}, {g_data['l']}km, {g_data['pf']} {g_data['pf_str']}")
                st.info(f"**Teknik Analiz:** {yorumlar[g_data['k_no']]}")

                x_vals = np.linspace(0, g_data['l'], 11)
                v_list, p_list, q_list = [], [], []
                for x in x_vals:
                    Ax = np.cosh(g_data['gamma'] * x); Bx = g_data['Zc'] * np.sinh(g_data['gamma'] * x); Cx = (1/g_data['Zc']) * np.sinh(g_data['gamma'] * x)
                    Vx_ara = Ax*g_data['V2'] + Bx*g_data['I2']; Ix_ara = Cx*g_data['V2'] + Ax*g_data['I2']
                    v_list.append(abs(Vx_ara)*np.sqrt(3)/1000)
                    p_list.append((3 * Vx_ara * np.conj(Ix_ara)).real / 1e6)
                    q_list.append((3 * Vx_ara * np.conj(Ix_ara)).imag / 1e6)

                k_loads = np.linspace(0.1, 1.5, 15)
                P1_curve, V1_curve = [], []
                for k_l in k_loads:
                    S2_step = k_l * g_data['S2_VA']
                    I2_step = np.conj((complex(S2_step*g_data['pf'], g_data['Q_sign']*S2_step*np.sin(np.arccos(g_data['pf'])))) / (3*g_data['V2']))
                    V1_step = g_data['A']*g_data['V2'] + g_data['B']*I2_step; I1_step = g_data['C_param']*g_data['V2'] + g_data['D']*I2_step
                    V1_curve.append(abs(V1_step) * np.sqrt(3) / 1000); P1_curve.append((3 * V1_step * np.conj(I1_step)).real / 1e6)

                fig, ax = plt.subplots(2, 2, figsize=(16, 12))
                ax[0, 0].plot(x_vals, v_list, '-bo', lw=2, markersize=6); ax[0, 0].set_title("Gerilim Değişimi (10 Nokta)"); ax[0, 0].set_xlabel("Hat Başından Uzaklık (km)"); ax[0, 0].set_ylabel("Gerilim (kV)"); ax[0, 0].grid(True)
                ax[0, 1].plot(x_vals, p_list, '-go', lw=2, markersize=6); ax[0, 1].set_title("Aktif Güç Değişimi (10 Nokta)"); ax[0, 1].set_xlabel("Hat Başından Uzaklık (km)"); ax[0, 1].set_ylabel("Aktif Güç (MW)"); ax[0, 1].grid(True)
                ax[1, 0].plot(x_vals, q_list, '-ro', lw=2, markersize=6); ax[1, 0].set_title("Reaktif Güç Değişimi (10 Nokta)"); ax[1, 0].set_xlabel("Hat Başından Uzaklık (km)"); ax[1, 0].set_ylabel("Reaktif Güç (MVAr)"); ax[1, 0].grid(True)
                ax[1, 1].plot(P1_curve, V1_curve, '-k*', lw=2, markersize=8); ax[1, 1].set_title("P-V Burun Eğrisi"); ax[1, 1].set_xlabel("Hat Başı Aktif Gücü P1 (MW)"); ax[1, 1].set_ylabel("Hat Başı Gerilimi V1 (kV)"); ax[1, 1].grid(True)
                plt.tight_layout(); st.pyplot(fig); st.markdown("<br>", unsafe_allow_html=True)
