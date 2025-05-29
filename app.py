import streamlit as st
import math

# DJI Mavic 3 Multispectral kamera adatok
CAMERAS = {
    "RGB": {
        "fokusz_mm": 24.0,
        "szenzor_szelesseg_mm": 17.3,
        "képszélesség_px": 5280,
        "min_expo_ido": 0.7,
        "min_írási_idő": 0.7
    },
    "Multispektrális": {
        "fokusz_mm": 25.0,
        "szenzor_szelesseg_mm": 6.4,
        "képszélesség_px": 1400,
        "min_expo_ido": 1.5,
        "min_írási_idő": 2.0
    }
}

GSD_KORREKCIOS_SZORZO = 0.502  # DJI-hez igazított szorzó

st.title("Repüléstervező kalkulátor (új verzió)")

# Drón és kameramód választása
dron_tipus = st.selectbox("Drón típusa", ["DJI Mavic 3 Multispectral"])
kamera_mod = st.radio("Kameramód", ["RGB", "RGB + Multispektrális"])
fokusz_mod = st.radio("Melyik kamerára fókuszál a repülés?", ["RGB", "Multispektrális"])

# Kamera kiválasztása a fókusz szerint
fokusz_kamera = CAMERAS[fokusz_mod]

# Beviteli mezők
gsd_cm = st.number_input("Cél GSD (cm/pixel)", min_value=0.1, value=5.0, step=0.1)
záridő_input = st.text_input("Záridő (1/x formátumban)", value="1000")
oldal_atfedes = st.slider("Oldalirányú átfedés (%)", min_value=60, max_value=90, value=70)
sor_atfedes = st.slider("Soron belüli átfedés (%)", min_value=60, max_value=90, value=80)
terulet_ha = st.number_input("Térképezendő terület (hektár)", min_value=0.1, value=10.0, step=0.1)
akkuk_szama = st.number_input("Elérhető akkumulátorok száma (100%)", min_value=1, value=1, step=1)

if st.button("Számítás indítása"):
    gsd_m = gsd_cm / 100
    shutter = 1 / float(záridő_input)

    # Repülési magasság számítása korrekcióval
    repmag_cm = (gsd_cm * fokusz_kamera["fokusz_mm"] * fokusz_kamera["képszélesség_px"]) / fokusz_kamera["szenzor_szelesseg_mm"]
    repmag_cm *= GSD_KORREKCIOS_SZORZO
    repmag_m = repmag_cm / 100

    # Kamera pixel elmozdulás alapú max sebesség (egyszerűsített modell)
    MAX_PIXEL_ELMOZDULAS = 0.7
    vmax_blur = gsd_m * MAX_PIXEL_ELMOZDULAS / shutter

    st.subheader(f"Eredmények - {fokusz_mod} kamera alapján")
    st.markdown(f"**Számított repülési magasság:** {repmag_m:.2f} méter")
    st.markdown(f"**Elmosódás nélküli maximális repülési sebesség:** {vmax_blur:.2f} m/s")
