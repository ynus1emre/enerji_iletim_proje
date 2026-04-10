import streamlit as st
import math
import cmath
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Enerji İletim Hesaplayıcı", layout="wide", page_icon="⚡")

# --- LOGO VE KLASÖR YOLU KONTROLÜ ---
# Kodun çalıştığı klasörü buluyoruz
base_path = os.path.dirname(__file__)
logo_path = os.path.join(base_path, "kou_logo.jpg")

# --- SOL YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        # Eğer logo yine bulunamazsa, uyarı yerine şık bir yazı gösteriyoruz
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
    st.divider()
    st.caption("Enerji İletimi Dersi Projesi Kısım 1")

# --- ANA EKRAN BAŞLIK ---
st.title("⚡ Enerji İletim Hatları Hesaplama Aracı")
st.subheader("154kV ve 400kV Hat Parametreleri")
st.divider()

# --- VERİTABANI VE SABİTLER ---
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

# --- GİRİŞ ALANLARI ---
col1, col2 = st.columns(2)

with col1:
    gerilim_secimi = st.selectbox("1. Gerilim Seviyesi", ["154 kV", "400 kV"])
    iletken_adi = st.selectbox("2. İletken Tipi", list(iletkenler_tablosu.keys()))

with col2:
    direk_secimi = st.selectbox("3. Direk Tipi", direkler)
    uzunluk_km = st.number_input("4. Hat Uzunluğu (km)", min_value=1.0, value=250.0, step=10.0)

st.divider()

# --- HESAPLAMA ---
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
        gmr_L_eq, gmr_C_eq, R_eq = math.sqrt(gmr_m * D_cift_devre), math.sqrt(
            r_yaricap_m * D_cift_devre), r_direnc_ohm_km / 2
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
