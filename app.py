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

# Repülési magasság számítása GSD alapján
def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10  # cm/px → mm/px

    if camera_type == "RGB":
        # RGB kamera magasság számítása helyes egységekkel
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
    else:
        # Multispektrális kamera magasság számítása korrekcióval
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs.get("correction_factor", 1.0)

    return altitude_mm / 1000  # mm → m

# GSD számítás adott magasságból
def calculate_gsd(altitude_m, camera_type):
    specs = CAMERA_SPECS[camera_type]
    # Egységek: altitude m → mm, vissza cm
    gsd_mm_px = (altitude_m * 1000 * specs["sensor_width_mm"]) / (specs["focal_length_mm"] * specs["image_width_px"])
    gsd_cm_px = gsd_mm_px / 10
    return gsd_cm_px

# Streamlit UI
st.title("AGRON Repüléstervezés")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_input, priority)
    st.success(f"A kívánt {gsd_input} cm/px GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter ({priority} kamera alapján)")

    # Ha prioritás multispektrális, akkor mutassuk az RGB GSD-t ezen a magasságon
    if priority == "Multispektrális":
        rgb_gsd = calculate_gsd(altitude, "RGB")
        st.info(f"Az RGB kamera GSD-je ezen a magasságon: {rgb_gsd:.2f} cm/px")
