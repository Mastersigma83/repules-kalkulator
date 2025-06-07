import streamlit as st
from math import ceil

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

# Repülési magasság számítása
def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10
    if camera_type == "RGB":
        altitude_mm = (gsd_mm_px * specs["sensor_width_mm"] * specs["image_width_px"]) / specs["focal_length_mm"]
    else:
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs.get("correction_factor", 1.0)
    return altitude_mm / 1000

# Max sebesség számítása
def calculate_max_speed(gsd_cm_px, shutter_speed, camera_type):
    raw_speed = (shutter_speed * gsd_cm_px) / 100
    limited_speed = min(raw_speed, 15)
    interval = 1 if camera_type == "RGB" else 2
    speed = limited_speed * interval
    return speed * 0.9  # 10% biztonság

# Becsült repülési idő (percben)
def estimate_flight_time(area_ha, speed_m_s, sidelap_pct, frontlap_pct, camera_type, gsd_cm_px):
    specs = CAMERA_SPECS[camera_type]
    coverage_width = specs["image_width_px"] * (1 - frontlap_pct / 100) * gsd_cm_px / 100
    coverage_length = speed_m_s * (1 - sidelap_pct / 100)
    coverage_area_per_sec = coverage_width * coverage_length
    total_area_m2 = area_ha * 10000
    return total_area_m2 / coverage_area_per_sec / 60

# Streamlit UI
st.title("AGRON Repüléstervezés")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_cm_px = st.number_input("Kívánt GSD (cm/px):", min_value=0.1, max_value=10.0, value=3.0)
shutter_speed = st.number_input("Záridő érték (pl. 1/800 → 800):", min_value=100, max_value=5000, value=800)
sidelap = st.number_input("Soron belüli átfedés (%):", min_value=0, max_value=100, value=80)
frontlap = st.number_input("Sorok közötti átfedés (%):", min_value=0, max_value=100, value=70)
area_ha = st.number_input("Felmérendő terület (hektár):", min_value=0.1, max_value=1000.0, value=10.0)

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_cm_px, priority)
    max_speed = calculate_max_speed(gsd_cm_px, shutter_speed, priority)
    est_time_min = estimate_flight_time(area_ha, max_speed, sidelap, frontlap, priority, gsd_cm_px)
    battery_time = 20  # perc
    batteries = ceil(est_time_min / battery_time)

    st.success(f"Repülési magasság: {altitude:.1f} m ({priority} kamera)")
    st.info(f"Maximális sebesség: {max_speed:.2f} m/s")
    st.info(f"Becsült repülési idő: {est_time_min:.1f} perc")
    st.warning(f"Szükséges akkumulátorok: {batteries} db (20 perc repülés/akku)")
