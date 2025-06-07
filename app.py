import streamlit as st
import math

# Kameraadatok
CAMERA_SPECS = {
    "RGB": {
        "focal_length_mm": 24.5,
        "sensor_width_mm": 17.3,
        "image_width_px": 5280
    },
    "Multispektrális": {
        "focal_length_mm": 4.7,
        "sensor_width_mm": 6.4,
        "image_width_px": 2592,
        "correction_factor": 0.877
    }
}

# Konstansok
MAX_PIXEL_ELMOZDULAS = 0.7
AKKU_IDO_PERCBEN = 20
GSD_KORREKCIOS_SZORZO = 0.927  # Biztonsági korrekció
DRON_MAX_SEBESSEG = 15.0

# Repülési magasság számítása
def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10  # cm/px → mm/px

    if camera_type == "RGB":
        altitude_mm = (gsd_mm_px * specs["sensor_width_mm"] * specs["image_width_px"]) / specs["focal_length_mm"]
    else:
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs.get("correction_factor", 1.0)

    altitude_mm *= GSD_KORREKCIOS_SZORZO  # biztonsági korrekció
    return altitude_mm / 1000  # mm → m

# Sebesség számítása
def calculate_max_speed(gsd_cm_px, shutter_speed_1x, camera_type):
    gsd_m_px = gsd_cm_px / 100
    shutter_speed = 1 / shutter_speed_1x

    vmax_blur = gsd_m_px * MAX_PIXEL_ELMOZDULAS / shutter_speed

    min_write_time_s = 1.0 if camera_type == "RGB" else 2.0

    specs = CAMERA_SPECS[camera_type]
    vmax_write = gsd_m_px * specs["image_width_px"] / min_write_time_s

    vmax = min(vmax_blur, vmax_write)
    vmax *= 0.9  # 10%-os biztonsági ráhagyás
    vmax = min(vmax, DRON_MAX_SEBESSEG)

    return vmax

# Streamlit felület
st.title("DJI Mavic 3M Repülési Kalkulátor")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
shutter_input = st.number_input("Záridő (1/x formátumban, pl. 800):", min_value=1, value=1000, step=1)

if st.button("Számítás indítása"):

    altitude = calculate_flight_altitude(gsd_input, priority)
    max_speed = calculate_max_speed(gsd_input, shutter_input, priority)

    st.markdown(f"### {priority} kamera alapján")
    st.success(f"A kívánt {gsd_input} cm/px GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter")
    st.info(f"Megengedett maximális repülési sebesség: {max_speed:.2f} m/s")

    # Multispektrális prioritás esetén nincs visszaszámolt RGB GSD kiírás
