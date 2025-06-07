import streamlit as st

# Kameraadatok
CAMERA_SPECS = {
    "RGB": {
        "focal_length_mm": 24.5,
        "sensor_width_mm": 17.3,
        "image_width_px": 5280,
        "min_interval_s": 1.0
    },
    "Multispektrális": {
        "focal_length_mm": 4.7,
        "sensor_width_mm": 6.4,
        "image_width_px": 2592,
        "correction_factor": 0.877,
        "min_interval_s": 2.0
    }
}

def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10

    if camera_type == "RGB":
        altitude_mm = (gsd_mm_px * specs["sensor_width_mm"] * specs["image_width_px"]) / specs["focal_length_mm"]
    else:
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs.get("correction_factor", 1.0)

    return altitude_mm / 1000

def calculate_max_speed_from_shutter(gsd_cm_px, shutter_base, camera_type):
    raw_speed = (shutter_base * gsd_cm_px) / 100  # cm/s → m/s
    limited_speed = raw_speed * 0.9  # 10% biztonsági korrekció

    # időalapú sebességkorlát kameratípus szerint
    specs = CAMERA_SPECS[camera_type]
    max_interval_speed = gsd_cm_px * specs["image_width_px"] * (1 - (overlap_alongtrack / 100)) / specs["min_interval_s"] / 100  # m/s

    return min(limited_speed, max_interval_speed, 15.0)

def estimate_flight_time(area_ha, speed_m_s, overlap_acrosstrack):
    effective_width_m = ground_swath_m * (1 - (overlap_acrosstrack / 100))
    effective_speed_m_s = speed_m_s
    area_m2 = area_ha * 10000
    total_distance_m = area_m2 / effective_width_m
    time_sec = total_distance_m / effective_speed_m_s
    return time_sec / 60

# Streamlit UI
st.title("DJI Mavic 3M Repülési Kalkulátor")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
shutter_base = st.number_input("Add meg a záridőt (pl. 1/800 esetén írd be: 800):", min_value=100, max_value=2000, value=800, step=10)
overlap_alongtrack = st.number_input("Soron belüli átfedés (%):", min_value=0, max_value=100, value=80)
overlap_acrosstrack = st.number_input("Sorok közötti átfedés (%):", min_value=0, max_value=100, value=70)
area_ha = st.number_input("Mekkora a felmérendő terület? (hektár):", min_value=0.1, max_value=1000.0, value=20.0, step=1.0)

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_input, priority)
    max_speed = calculate_max_speed_from_shutter(gsd_input, shutter_base, priority)
    ground_swath_m = gsd_input * CAMERA_SPECS[priority]["image_width_px"] / 100  # cm → m
    est_flight_time_min = estimate_flight_time(area_ha, max_speed, overlap_acrosstrack)

    st.success(f"📷 Kívánt {gsd_input} cm/px GSD eléréséhez szükséges repülési magasság: **{altitude:.1f} m**")
    st.info(f"🚀 Maximális repülési sebesség: **{max_speed:.2f} m/s**")
    st.info(f"⏱️ Becsült repülési idő a {area_ha} hektáros területhez: **{est_flight_time_min:.1f} perc**")
