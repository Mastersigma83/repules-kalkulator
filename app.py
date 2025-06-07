import streamlit as st

# Kamera paraméterek (Mavic 3M)
CAMERA_PARAMS = {
    "RGB": {
        "focal_length_mm": 24.5,
        "sensor_width_mm": 17.3,
        "image_width_px": 5280
    },
    "Multispectral": {
        "focal_length_mm": 4.7,
        "sensor_width_mm": 6.4,
        "image_width_px": 2592,
        "correction_factor": 0.877  # korábban validált korrekció
    }
}

# Repülési magasság számítása GSD alapján
def calculate_flight_altitude(gsd_cm_per_px, camera_type):
    gsd_mm_per_px = gsd_cm_per_px * 10  # cm/px → mm/px
    cam = CAMERA_PARAMS[camera_type]
    height_m = (gsd_mm_per_px * cam["focal_length_mm"] * cam["image_width_px"]) / cam["sensor_width_mm"] / 1000
    if "correction_factor" in cam:
        height_m *= cam["correction_factor"]
    return round(height_m, 2)

# Streamlit UI
st.title("DJI Mavic 3M – Repülési Magasság Kalkulátor")
st.markdown("Adja meg a kívánt GSD értéket (cm/pixel), és válassza ki a prioritást a repüléstervezéshez.")

drone = st.selectbox("Válassza ki a drónt:", ["DJI Mavic 3M"])
priority = st.radio("Melyik kamera prioritású?", ["RGB", "Multispectral"])
gsd = st.number_input("Cél GSD (cm/pixel):", min_value=0.1, step=0.1)

if st.button("Számolás"):
    altitude = calculate_flight_altitude(gsd, priority)
    st.success(f"A(z) {priority} kamera esetén a repülési magasság: **{altitude} méter**")
