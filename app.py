import streamlit as st

# Kamera paraméterek (rögzített értékek)
CAMERA_PARAMS = {
    "RGB": {
        "focal_length_mm": 24.5,
        "sensor_width_mm": 17.3,
        "image_width_px": 5280
    },
    "Multispektrális": {
        "focal_length_mm": 4.7,
        "sensor_width_mm": 6.4,
        "image_width_px": 2592,
        "correction_factor": 0.877  # Ez a tapasztalati korrekciós szorzó
    }
}

st.title("DJI Mavic 3M GSD → Repülési magasság kalkulátor")

# Drón kiválasztása
drone = st.selectbox("Válassz drónt:", ["DJI Mavic 3M"])

# Prioritás kiválasztása
priority = st.selectbox("Melyik kamera alapján számoljuk a GSD-t?", ["RGB", "Multispektrális"])

# Cél GSD megadása
gsd_cm = st.number_input("Cél GSD (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
gsd_mm = gsd_cm * 10  # mm/px

if st.button("Számítás"):
    # Kamera adatok betöltése
    cam = CAMERA_PARAMS[priority]
    f = cam["focal_length_mm"]
    s = cam["sensor_width_mm"]
    w = cam["image_width_px"]

    # Alap képlet: Magasság = (GSD * fókusztáv * kép szélesség) / szenzor szélesség
    height = (gsd_mm * f * w) / s

    # Multispektrális korrekció alkalmazása, ha kell
    if priority == "Multispektrális":
        height *= cam.get("correction_factor", 1.0)

    st.success(f"A szükséges repülési magasság: **{height:.1f} méter** ({priority} kamera alapján)")
