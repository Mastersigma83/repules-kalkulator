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

# Repülési magasság számítása a GSD alapján
def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10  # cm/px → mm/px

    if camera_type == "RGB":
        altitude_mm = (gsd_mm_px * specs["sensor_width_mm"] * specs["image_width_px"]) / specs["focal_length_mm"]
    else:
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs.get("correction_factor", 1.0)

    return altitude_mm / 1000  # mm → m

# GSD visszaszámítása adott magasságból
def calculate_gsd_from_altitude(altitude_m, camera_type):
    specs = CAMERA_SPECS[camera_type]
    altitude_mm = altitude_m * 1000  # m → mm
    if camera_type == "RGB":
        gsd_mm_px = (altitude_mm * specs["focal_length_mm"]) / (specs["sensor_width_mm"] * specs["image_width_px"])
    else:
        gsd_mm_px = (altitude_mm * specs["sensor_width_mm"]) / (specs["focal_length_mm"] * specs["image_width_px"])
        gsd_mm_px *= specs.get("correction_factor", 1.0)
    return gsd_mm_px / 10  # mm/px → cm/px

# Streamlit UI
st.title("AGRON Repüléstervezés")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)

shutter_input = st.text_input("Add meg a záridő nevezőjét (pl. 800 az 1/800-hoz):", value="800")

side_overlap_pct = st.slider("Sorok közötti átfedés (%)", 50, 90, 70)
front_overlap_pct = st.slider("Soron belüli átfedés (%)", 50, 90, 80)

area_ha = st.number_input("Add meg a felmérni kívánt területet (hektár):", min_value=0.1, value=10.0, step=0.1, format="%.1f")

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_input, priority)
    st.success(f"A kívánt {gsd_input} cm/px GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter ({priority} kamera alapján)")

    # Multi prioritás esetén mutassuk meg az RGB GSD-t ugyanazon a magasságon
    if priority == "Multispektrális":
        rgb_gsd = calculate_gsd_from_altitude(altitude, "RGB")
        st.info(f"Ugyanezen a repülési magasságon az RGB kamera GSD-je kb.: {rgb_gsd:.2f} cm/px")
