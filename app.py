import streamlit as st

# Kameraadatok
CAMERA_SPECS = {
    "RGB": {
        "focal_length_mm": 24.5,
        "sensor_width_mm": 17.3,
        "image_width_px": 5280,
        "min_capture_interval_s": 1.0  # minimum 1 mp két kép között
    },
    "Multispektrális": {
        "focal_length_mm": 4.7,
        "sensor_width_mm": 6.4,
        "image_width_px": 2592,
        "correction_factor": 0.877,
        "min_capture_interval_s": 2.0  # minimum 2 mp két kép között
    }
}

MAX_PIXEL_ELMOZDULAS = 0.7  # pixel elmozdulás, ami még elfogadható
DRONE_MAX_SPEED = 15.0      # maximális repülési sebesség m/s
SAFETY_FACTOR = 0.9         # 10% biztonsági ráhagyás

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

# Maximális sebesség számítása a GSD, záridő és a képírási idő alapján
def calculate_max_speed(gsd_cm_px, shutter_speed_denominator, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_m = gsd_cm_px / 100  # cm/px → m/px
    shutter_speed = 1 / shutter_speed_denominator  # pl. 1/800 -> 0.00125 s
    vmax_blur = gsd_m * MAX_PIXEL_ELMOZDULAS / shutter_speed

    # max sebesség az írási idő miatt (képkészítési interval)
    vmax_write = gsd_m / specs["min_capture_interval_s"]

    vmax = min(vmax_blur, vmax_write, DRONE_MAX_SPEED)

    # 10% biztonsági ráhagyás
    vmax *= SAFETY_FACTOR

    return vmax

# Streamlit UI
st.title("AGRON Repüléstervezés")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
shutter_speed_den = st.number_input("Add meg a záridő nevezőjét (pl. 800 = 1/800):", min_value=100, value=800)
front_overlap = st.number_input("Soron belüli átfedés (%):", min_value=0, max_value=100, value=80)
side_overlap = st.number_input("Sorok közötti átfedés (%):", min_value=0, max_value=100, value=70)
planned_flight_time = st.number_input("Tervezett repülési idő (perc):", min_value=1.0, value=20.0, step=1.0)

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_input, priority)
    max_speed = calculate_max_speed(gsd_input, shutter_speed_den, priority)
    st.success(f"A kívánt {gsd_input:.1f} cm/px GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter ({priority} kamera alapján)")
    st.info(f"Maximális repülési sebesség (záridő és írási idő figyelembevételével): {max_speed:.2f} m/s")

    battery_minutes = 20
    akku_igeny = int(planned_flight_time / battery_minutes + 0.999)
    st.info(f"Szükséges akkumulátorok száma (20 perc/akku): {akku_igeny} db")
