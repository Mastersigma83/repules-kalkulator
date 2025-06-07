import streamlit as st

# Kameraadatok
CAMERA_SPECS = {
    "RGB": {
        "focal_length_mm": 24.5,
        "sensor_width_mm": 17.3,
        "image_width_px": 5280,
        "min_interval_sec": 1.0  # minimum 1 másodperc két kép között
    },
    "Multispektrális": {
        "focal_length_mm": 4.7,
        "sensor_width_mm": 6.4,
        "image_width_px": 2592,
        "correction_factor": 0.877,
        "min_interval_sec": 2.0  # minimum 2 másodperc két kép között
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

# Maximális repülési sebesség számítása
def calculate_max_speed(gsd_cm_px, shutter_value, camera_type):
    specs = CAMERA_SPECS[camera_type]
    base_speed = (shutter_value * gsd_cm_px) / 100  # cm/s → m/s
    max_speed = min(base_speed, 15)  # Felső korlát: 15 m/s

    # Kép intervallum alapján is limitálni kell:
    min_distance_between_photos_m = max_speed * specs["min_interval_sec"]
    adjusted_speed = min(max_speed, min_distance_between_photos_m / specs["min_interval_sec"])

    return adjusted_speed

# Streamlit felület
st.title("DJI Mavic 3M Repülési Magasság és Sebesség Kalkulátor")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)

shutter_value = st.number_input("Add meg a záridőt (pl. 1/800 esetén: 800):", min_value=100, max_value=5000, value=800, step=10)

# Átfedések bekérése
front_overlap = st.number_input("Soron belüli átfedés (%)", min_value=0, max_value=100, value=80, step=5)
side_overlap = st.number_input("Sorok közötti átfedés (%)", min_value=0, max_value=100, value=70, step=5)

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_input, priority)
    max_speed = calculate_max_speed(gsd_input, shutter_value, priority)

    st.success(f"A kívánt {gsd_input} cm/px GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter ({priority} kamera alapján)")
    st.info(f"A maximális javasolt repülési sebesség: {max_speed:.1f} m/s")
