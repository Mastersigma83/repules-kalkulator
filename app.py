import streamlit as st

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

# Maximális sebesség számítása
def calculate_max_speed(gsd_cm_px, shutter_speed, camera_type):
    base_speed = (gsd_cm_px * shutter_speed) / 100
    base_speed *= 0.9  # biztonsági tartalék
    max_limit = 15

    # sebességkorlát a kamera alapján
    if camera_type == "RGB":
        max_allowed = 1 * base_speed
    else:
        max_allowed = 0.5 * base_speed

    return min(base_speed, max_allowed, max_limit)

# Becsült idő számítása finomított modell alapján
def estimate_flight_time(area_ha, altitude_m, speed_mps):
    if altitude_m <= 50:
        area_per_min = 0.35 * speed_mps
    elif altitude_m <= 80:
        area_per_min = 0.55 * speed_mps
    elif altitude_m <= 100:
        area_per_min = 0.70 * speed_mps
    else:
        area_per_min = 0.85 * speed_mps

    total_minutes = area_ha / area_per_min
    return total_minutes

# Streamlit UI
st.title("AGRON Repüléstervezés")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
shutter_speed = st.number_input("Add meg a záridőt (pl. 800 az 1/800-hoz):", min_value=100, max_value=2000, value=800, step=50)
overlap_inline = st.number_input("Soron belüli átfedés (%):", min_value=0, max_value=100, value=80, step=5)
overlap_between = st.number_input("Sorok közötti átfedés (%):", min_value=0, max_value=100, value=70, step=5)
area_input = st.number_input("Add meg a felmérendő területet (hektár):", min_value=0.1, max_value=1000.0, value=10.0, step=0.1)

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_input, priority)
    speed = calculate_max_speed(gsd_input, shutter_speed, priority)
    time_minutes = estimate_flight_time(area_input, altitude, speed)
    battery_count = (time_minutes / 20)

    st.success(f"A kívánt {gsd_input} cm/px GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter")
    st.info(f"Becsült maximális repülési sebesség: {speed:.2f} m/s")
    st.warning(f"Becsült repülési idő: {time_minutes:.1f} perc")
    st.error(f"Szükséges akkumulátorok száma (20 perc/akku): {battery_count:.1f}")
