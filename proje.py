import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import cmath

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Grup 7 Enerji İletim Projesi", layout="wide")
st.title("⚡ Enerji İletim Hatları Hesaplama Aracı")

# --- PARAMETRELER ---
f = 50.0; w = 2 * np.pi * f
data_map = {
    "154 kV - TA1 Çift Devre (Drake)": (0.0405, 0.582e-3, 19.85e-9),
    "400 kV - 3B1 Tek Devre 2'li Demet (Rail)": (0.03417, 0.9982e-3, 11.40e-9)
}

tab1, tab2 = st.tabs(["🧮 Kısım 1: Hat Parametreleri", "📊 Kısım 2: Hat ve Sistem Hesaplamaları"])

# --- KISIM 1: PARAMETRE HESAPLAYICI ---
with tab1:
    st.markdown("### 🧮 Hat Sabitleri (R, L, C) ve ABCD Parametreleri")
    col1, col2 = st.columns(2)
    with col1:
        iletken_k1 = st.selectbox("İletken Tipi (Kısım 1)", list(data_map.keys()))
        uzunluk_k1 = st.number_input("Hat Uzunluğu (km) (Kısım 1)", value=250.0)
    
    if st.button("Parametreleri Hesapla"):
        R, L, C = data_map[iletken_k1]
        Z = complex(R, w*L); Y = complex(0, w*C)
        gamma = cmath.sqrt(Z*Y); Zc = cmath.sqrt(Z/Y)
        A = cmath.cosh(gamma * uzunluk_k1)
        B = Zc * cmath.sinh(gamma * uzunluk_k1)
        C_p = cmath.sinh(gamma * uzunluk_k1) / Zc
        
        st.success("Parametreler hesaplandı!")
        st.code(f"R: {R:.4f} Ω/km | L: {L*1000:.4f} mH/km | C: {C*1e9:.4f} nF/km")
        st.code(f"A: {A:.4f} | B: {B:.2f} Ω | C: {C_p:.6f} S")

# --- KISIM 2: SİSTEM ANALİZİ ---
with tab2:
    st.markdown("### 📊 Kısım 2: Hat ve Sistem Hesaplamaları")
    with st.expander("🛠️ Analiz Parametrelerini Ayarla"):
        c1, c2, c3 = st.columns(3)
        with c1:
            iletken_k2 = st.selectbox("İletken / Direk Tipi", list(data_map.keys()))
            l_km = st.number_input("Mesafe (km)", value=100.0)
        with c2:
            pf_val = st.slider("Güç Katsayısı (cosφ)", 0.8, 1.0, 0.95)
            pf_tip = st.radio("Güç Durumu", ["Endüktif", "Kapasitif"])
        with c3:
            u_kv = st.number_input("Hat Sonu Gerilimi (kV)", value=154.0)
            btn = st.button("🚀 Analiz Et", type="primary")

    if btn:
        R, L, C = data_map[iletken_k2]
        U2 = u_kv * 1000; V2 = U2 / np.sqrt(3); Q_sign = 1 if pf_tip == "Endüktif" else -1
        Z = complex(R, w*L); Y = complex(0, w*C)
        gamma = np.sqrt(Z*Y); Zc = np.sqrt(Z/Y)
        A = np.cosh(gamma * l_km); B = Zc * np.sinh(gamma * l_km)
        C_param = (1/Zc) * np.sinh(gamma * l_km); D = A
        
        # Güç
        Z_sur = np.sqrt(L/C); S2_VA = (U2**2) / Z_sur
        P2 = S2_VA * pf_val; Q2 = Q_sign * S2_VA * np.sin(np.arccos(pf_val))
        I2 = np.conj(complex(P2, Q2) / (3 * V2)); V1 = A*V2 + B*I2; I1 = C_param*V2 + D*I2
        
        # Görselleştirme
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("V1 (kV)", f"{round(abs(V1)*np.sqrt(3)/1000, 2)}")
        c2.metric("I1 (A)", f"{round(abs(I1), 2)}")
        c3.metric("P1 (MW)", f"{round((3*V1*np.conj(I1)).real/1e6, 2)}")
        c4.metric("Verim (%)", f"{round((P2 / (3*V1*np.conj(I1)).real)*100, 2)}")
        
        st.info(f"**Teknik Analiz:** {iletken_k2} hattı {l_km} km'de {pf_tip} karakteristik göstermektedir.")
        
        # Grafikler
        x = np.linspace(0, l_km, 50)
        v_l, p_l, q_l = [], [], []
        for val in x:
            Ax = np.cosh(gamma * val); Bx = Zc * np.sinh(gamma * val)
            Vx = Ax*V2 + Bx*I2; Ix = C_param*val*V2 + A*val*I2
            v_l.append(abs(Vx)*np.sqrt(3)/1000); p_l.append((3*Vx*np.conj(Ix)).real/1e6); q_l.append((3*Vx*np.conj(Ix)).imag/1e6)
        
        fig, ax = plt.subplots(1, 3, figsize=(16, 4))
        ax[0].plot(x, v_l, 'b'); ax[0].set_title("Gerilim Değişimi"); ax[0].grid(True)
        ax[1].plot(x, p_l, 'g'); ax[1].set_title("Aktif Güç Değişimi"); ax[1].grid(True)
        ax[2].plot(x, q_l, 'r'); ax[2].set_title("Reaktif Güç Değişimi"); ax[2].grid(True)
        st.pyplot(fig)
        
        st.table(pd.DataFrame({"Parametre": ["Gerilim (kV)", "Akım (A)", "Aktif Güç (MW)", "Reaktif Güç (MVAr)"], 
                               "Değer": [round(abs(V1)*np.sqrt(3)/1000, 2), round(abs(I1), 2), round((3*V1*np.conj(I1)).real/1e6, 2), round((3*V1*np.conj(I1)).imag/1e6, 2)]}))
