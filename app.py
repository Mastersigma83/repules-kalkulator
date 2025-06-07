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
GSD_KORREKCIOS_SZORZO = 0.927  # Biztonsági korrekció, ha kell
DRON_MAX_SEBESSEG = 15.0
MULTI_GSD_SZORZO = 1 / 0.56  # multispektrális GSD szorzó az RGB-hez képest

# Repülési magasság számítása
def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10  # cm/px → mm/px

    if camera_type == "RGB":
        # Külön képlet az RGB kamerához
        altitude_mm = (gsd_mm_px * specs["sensor_width_mm"] * specs["image_width_px"]) / specs["focal_length_mm"]
    else:
        # Eredeti képlet multispektrálishoz, korrekcióval
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs.get("correction_factor", 1.0)

    altitude_mm *= GSD_KORREKCIOS_SZORZO  # biztonsági korrekció
    return altitude_mm / 1000  # mm → m

# Sebesség számítása (max 15 m/s, biztonsági 10%-os ráhagyással, fotózási idő alapján)
def calculate_max_speed(gsd_cm_px, shutter_speed_1x, camera_type):
    gsd_m_px = gsd_cm_px / 100
    shutter_speed = 1 / shutter_speed_1x

    # Maximális sebesség az elmozdulás limit miatt
    vmax_blur = gsd_m_px * MAX_PIXEL_ELMOZDULAS / shutter_speed

    # Minimális záridő a memóriakártya írása miatt
    min_write_time_s = 1.0 if camera_type == "RGB" else 2.0

    specs = CAMERA_SPECS[camera_type]
    vmax_write = gsd_m_px * specs["image_width_px"] / min_write_time_s

    vmax = min(vmax_blur, vmax_write)
    vmax *= 0.9  # 10%-os biztonsági ráhagyás
    vmax = min(vmax, DRON_MAX_SEBESSEG)

    return vmax

# Felület
st.title("DJI Mavic 3M Repülési Kalkulátor")

# Inputok
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

    # Ha prioritás multi, számoljuk vissza az RGB GSD-t az adott magasságból
    if priority == "Multispektrális":
        multi_altitude = altitude

        rgb_specs = CAMERA_SPECS["RGB"]
        rgb_gsd_cm_px = (multi_altitude * rgb_specs["sensor_width_mm"] * rgb_specs["image_width_px"]) / rgb_specs["focal_length_mm"] / 10  # mm->cm

        st.markdown("### Az RGB kamera GSD-je a multispektrális kamera repülési magasságán:")
        st.success(f"{rgb_gsd_cm_px:.2f} cm/pixel")
