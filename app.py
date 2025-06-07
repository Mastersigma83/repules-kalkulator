import streamlit as st

# Kamera paraméterek (Mavic 3 Multispectral)
RGB_PARAMS = {
    "focal_length": 24.5,       # mm
    "sensor_width": 17.3,       # mm
    "image_width": 5280         # px
}

MULTI_PARAMS = {
    "focal_length": 4.7,        # mm
    "sensor_width": 6.4,        # mm
    "image_width": 2592,        # px
    "correction_factor": 0.877
}

# GSD → repülési magasság számítása
def calculate_altitude(gsd_cm_per_px, camera_params, use_correction=False):
    gsd_mm_per_px = gsd_cm_per_px * 10  # cm → mm
    altitude = (gsd_mm_per_px * camera_params["focal_length"] * camera_params["image_width"]) / \
               (camera_params["sensor_width"] * 1000)
    if use_correction and "correction_factor" in camera_params:
        altitude *= camera_params["correction_factor"]
    return round(altitude, 2)

# Streamlit UI
st.title("Repülési Magasság Kalkulátor")

drone_type = st.selectbox("Válassz drónt:", ["DJI Mavic 3M"])
priority = st.radio("Melyik kamerára optimalizálsz?", ["RGB", "Multispektrális"])
gsd = st.number_input("Cél GSD (cm/pixel):", min_value=0.1, step=0.1)

if st.button("Számítás"):
    if priority == "RGB":
        altitude = calculate_altitude(gsd, RGB_PARAMS)
        st.success(f"RGB kamera esetén a repülési magasság: {altitude} méter")
    else:
        altitude = calculate_altitude(gsd, MULTI_PARAMS, use_correction=True)
        st.success(f"Multispektrális kamera esetén a repülési magasság: {altitude} méter")
