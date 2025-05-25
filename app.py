import streamlit as st
import math

st.title("Repüléstervező kalkulátor")

st.markdown("""
Ez az alkalmazás segít beállítani a drónod agrárfelmérésekhez / térképezéshez.
""")

# Drón paraméterek
available_drones = {
    "DJI Mavic 3 Multispectral": {
        "RGB": {
            "fokusz_mm": 24.0,
            "szenzor_szelesseg_mm": 17.3,
            "képszélesség_px": 5280,
            "min_írási_idő_s": 0.7,
            "korrekcio": 1.0
        },
        "Multispektrális": {
            "fokusz_mm": 25.0,
            "szenzor_szelesseg_mm": 6.4,
            "képszélesség_px": 1400,
            "min_írási_idő_s": 2.0,
            "korrekcio": 0.6
        }
    }
}

selected_drone_name = st.selectbox("Drón kiválasztása", list(available_drones.keys()))
kamera_mod = st.radio("Kameramód", ["Csak RGB", "RGB + multispektrális"])

# Állandók
MAX_PIXEL_ELMOZDULAS = 0.7
GSD_KORREKCIOS_SZORZO = 2.0  # korrekció osztással, hogy 0.52 -> ~19 m legyen
DRON_MAX_SEBESSEG = 15.0

multi = available_drones[selected_drone_name]["Multispektrális"]
min_gsd = (12 * multi["szenzor_szelesseg_mm"]) / (multi["fokusz_mm"] * multi["képszélesség_px"]) * 100

gsd_cm = st.number_input("Cél GSD (cm/pixel)", min_value=round(min_gsd, 2), value=2.0, step=0.1)
shutter_input = st.text_input("Záridő (1/x formátumban) (Terület felett, lefelé fordított kamerával – leolvasott érték!)", value="1000")

# Fő számítás
if st.button("▶️ Számítás indítása"):
    rgb = available_drones[selected_drone_name]["RGB"]
    multi = available_drones[selected_drone_name]["Multispektrális"]

    try:
        shutter_speed = 1 / float(shutter_input)
    except:
        st.error("Hibás záridőformátum")
        st.stop()

    # RGB repülési magasság
    repmag_cm = (gsd_cm * rgb["fokusz_mm"] * rgb["képszélesség_px"]) / rgb["szenzor_szelesseg_mm"] / GSD_KORREKCIOS_SZORZO
    repmag_m = repmag_cm / 100

    st.markdown("## Eredmények")
    st.markdown("### RGB kamera")
    st.markdown(f"**Repülési magasság:** kb. {repmag_m:.1f} m")

    if kamera_mod == "RGB + multispektrális":
        st.markdown("### Multispektrális kamera")

        # 1. RGB GSD-ből számított multispektrális GSD
        gsd_multi_cm = gsd_cm * (1 / 0.56)
        st.markdown(f"**A megadott RGB GSD-hez tartozó multispektrális GSD:** {gsd_multi_cm:.2f} cm/pixel")

        # 2. Multispektrális max repülési sebesség
        gsd_multi_m = gsd_multi_cm / 100
        vmax_blur = gsd_multi_m * MAX_PIXEL_ELMOZDULAS / shutter_speed
        vmax_write = gsd_multi_m * multi["képszélesség_px"] / multi["min_írási_idő_s"]
        vmax_mps = min(vmax_blur, vmax_write) * multi["korrekcio"]
        vmax_mps = min(vmax_mps, DRON_MAX_SEBESSEG)

        st.markdown(f"**Max. repülési sebesség (elmosódás nélkül):** {vmax_mps:.2f} m/s")
