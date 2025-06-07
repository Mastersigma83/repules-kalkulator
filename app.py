import streamlit as st
import math

# Kameraadatok
CAMERA_SPECS = {
    "RGB": {
        "focal_length_mm": 24.5,
        "sensor_width_mm": 17.3,
        "image_width_px": 5280,
        "min_write_time_s": 1.0,
        "correction_factor": 1.0
    },
    "Multispektrális": {
        "focal_length_mm": 4.7,
        "sensor_width_mm": 6.4,
        "image_width_px": 1600,
        "min_write_time_s": 2.0,
        "correction_factor": 0.877
    }
}

MAX_DRONE_SPEED = 15.0
SAFETY_SPEED_FACTOR = 0.9
AKKU_FLIGHT_TIME_MIN = 20

def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10
    if camera_type == "RGB":
        altitude_mm = (gsd_mm_px * specs["sensor_width_mm"] * specs["image_width_px"]) / specs["focal_length_mm"]
    else:
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs["correction_factor"]
    return altitude_mm / 1000

def calculate_max_speed(gsd_cm_px, shutter_speed, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_m_px = gsd_cm_px / 100
    vmax_blur = (gsd_m_px * 0.7) / shutter_speed
    vmax_write = gsd_m_px * specs["image_width_px"] / specs["min_write_time_s"]
    vmax = min(vmax_blur, vmax_write)
    vmax *= SAFETY_SPEED_FACTOR
    vmax = min(vmax, MAX_DRONE_SPEED)
    return vmax

st.title("AGRON Repüléstervezés")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
shutter_input = st.number_input("Add meg a záridő nevezőjét (pl. 800 az 1/800-hoz):", min_value=1, value=800, step=1)
side_overlap_pct = st.number_input("Soron belüli átfedés (%)", min_value=50, max_value=95, value=80, step=1)
front_overlap_pct = st.number_input("Sorok közötti átfedés (%)", min_value=50, max_value=95, value=70, step=1)
area_ha = st.number_input("Add meg a felmérni kívánt terület nagyságát (hektár):", min_value=0.1, value=10.0, step=0.1, format="%.1f")

# Itt kérjük be a tervezett repülési időt a kontrollerből:
planned_flight_time = st.number_input("Tervezett repülési idő (percben, kontrollerből):", min_value=1.0, value=20.0, step=0.1)

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_input, priority)
    shutter_sec = 1 / shutter_input
    max_speed = calculate_max_speed(gsd_input, shutter_sec, priority)

    # Nem számoljuk a repülési időt, csak a user által megadott értéket használjuk az akkuk számításához
    needed_batteries = math.ceil(planned_flight_time / AKKU_FLIGHT_TIME_MIN)

    st.success(f"A kívánt {gsd_input} cm/px GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter ({priority} kamera alapján)")
    st.info(f"Maximális repülési sebesség (záridő és írási idő figyelembevételével): {max_speed:.2f} m/s")
    st.info(f"Szükséges akkumulátorok száma (tervezett repülési idő alapján): {needed_batteries} db")

    if priority == "Multispektrális":
        rgb_altitude = calculate_flight_altitude(gsd_input, "RGB")
        st.info(f"Az RGB kamera GSD-je ezen a magasságon: {(gsd_input * CAMERA_SPECS['RGB']['focal_length_mm'] * CAMERA_SPECS['RGB']['image_width_px']) / (CAMERA_SPECS['RGB']['sensor_width_mm'] * altitude * 1000):.2f} cm/px")
