import streamlit as st

# Kameraadatok
CAMERA_SPECS = {
    "RGB": {
        "focal_length_mm": 24.5,
        "sensor_width_mm": 17.3,
        "image_width_px": 5280,
        "min_capture_interval_s": 1.0  # 1 mp képírási idő RGB-nél
    },
    "Multispektrális": {
        "focal_length_mm": 4.7,
        "sensor_width_mm": 6.4,
        "image_width_px": 2592,
        "min_capture_interval_s": 2.0,  # 2 mp képírási idő multispektrálisnál
        "correction_factor": 0.877
    }
}

MAX_PIXEL_ELMOZDULAS = 0.7
DRONE_MAX_SPEED = 15.0  # m/s
SAFETY_FACTOR = 0.9     # 10% biztonsági ráhagyás
AKKU_IDO_PERCBEN = 20   # perc/akku

def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10  # cm/px → mm/px

    if camera_type == "RGB":
        altitude_mm = (gsd_mm_px * specs["sensor_width_mm"] * specs["image_width_px"]) / specs["focal_length_mm"]
    else:
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs.get("correction_factor", 1.0)

    return altitude_mm / 1000  # mm → m

def calculate_max_speed(gsd_cm_px, shutter_speed_denominator, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_m = gsd_cm_px / 100  # cm/px → m/px
    shutter_speed = 1 / shutter_speed_denominator

    vmax_blur = gsd_m * MAX_PIXEL_ELMOZDULAS / shutter_speed
    vmax_write = (gsd_m * specs["image_width_px"]) / specs["min_capture_interval_s"]

    vmax = min(vmax_blur, vmax_write, DRONE_MAX_SPEED)
    vmax *= SAFETY_FACTOR
    return vmax

# Streamlit felület
st.title("AGRON Repüléstervezés")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
shutter_input = st.number_input("Add meg a záridő nevezőjét (pl. 800 az 1/800 záridőhöz):", min_value=1, value=800, step=1)
side_overlap_pct = st.number_input("Add meg az oldalirányú átfedést (%):", min_value=0, max_value=100, value=70, step=1)
front_overlap_pct = st.number_input("Add meg a soron belüli átfedést (%):", min_value=0, max_value=100, value=80, step=1)
terulet_ha = st.number_input("Add meg a felmérni kívánt területet (hektár):", min_value=0.1, value=10.0, step=0.1, format="%.1f")
tervezett_ido = st.number_input("Tervezett repülési idő (kontrollerből, percben):", min_value=1, value=20, step=1)

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_input, priority)
    max_speed = calculate_max_speed(gsd_input, shutter_input, priority)

    # Akkumulátor szükséglet számítása a tervezett idő alapján
    akku_szam = int((tervezett_ido + AKKU_IDO_PERCBEN - 1) // AKKU_IDO_PERCBEN)  # felfelé kerekítve

    st.success(f"A kívánt {gsd_input} cm/px GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter ({priority} kamera alapján)")
    st.info(f"Maximális repülési sebesség (záridő és írási idő figyelembevételével): {max_speed:.2f} m/s")
    st.info(f"Szükséges akkumulátorok száma (tervezett repülési idő alapján): {akku_szam} db")
