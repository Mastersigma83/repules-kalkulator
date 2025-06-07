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

# Repülési magasság számítása

def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10  # cm/px → mm/px

    if camera_type == "RGB":
        altitude_mm = (gsd_mm_px * specs["sensor_width_mm"] * specs["image_width_px"]) / specs["focal_length_mm"]
    else:
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs.get("correction_factor", 1.0)

    return altitude_mm / 1000  # mm → m

# Maximális sebesség számítása fényviszony és kameratípus alapján

def calculate_max_speed(gsd_cm_px, shutter_speed, camera_type):
    base_speed = (gsd_cm_px * shutter_speed) / 100
    if camera_type == "RGB":
        max_interval = 1
    else:
        max_interval = 2
    max_speed = min(base_speed / max_interval, 15)
    return max_speed * 0.9  # 10%-os biztonsági korrekció

# Repülési idő kalkuláció

def estimate_flight_time(area_ha, speed_mps, front_overlap, side_overlap):
    area_m2 = area_ha * 10000
    effective_speed = speed_mps * (1 - front_overlap)
    coverage_rate = effective_speed * (1 - side_overlap)
    if coverage_rate <= 0:
        return float('inf')
    time_sec = area_m2 / coverage_rate
    return time_sec / 60  # perc

# Akkumulátor szükséglet

def estimate_battery_count(time_min, battery_life_min=20):
    return math.ceil(time_min / battery_life_min)

# Streamlit felület
st.set_page_config(page_title="AGRON Repüléstervezés")
st.title("AGRON Repüléstervezés")
st.markdown("""
<style>
    div[data-baseweb="select"] > div {
        cursor: pointer;
    }
    div[role="textbox"] {
        caret-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
shutter_speed = st.number_input("Add meg a záridő nevezőjét (pl. 800 = 1/800):", min_value=100, max_value=2000, value=800, step=50)
front_overlap_pct = st.number_input("Soron belüli átfedés (%):", min_value=0, max_value=100, value=80, step=5)
side_overlap_pct = st.number_input("Sorok közötti átfedés (%):", min_value=0, max_value=100, value=70, step=5)
area_input = st.number_input("Add meg a felmérni kívánt területet (hektár):", min_value=0.1, max_value=1000.0, value=10.0, step=0.1)

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_input, priority)
    max_speed = calculate_max_speed(gsd_input, shutter_speed, priority)
    front_overlap = front_overlap_pct / 100
    side_overlap = side_overlap_pct / 100
    flight_time = estimate_flight_time(area_input, max_speed, front_overlap, side_overlap)
    battery_count = estimate_battery_count(flight_time)

    st.success(f"A kívánt {gsd_input} cm/px GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter ({priority} kamera alapján)")
    st.info(f"Maximális repülési sebesség: {max_speed:.2f} m/s")
    st.info(f"Becsült repülési idő: {flight_time:.2f} perc")
    st.info(f"Szükséges akkumulátorok száma (20 perc/akku): {battery_count} db")
