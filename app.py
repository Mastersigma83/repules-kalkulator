import streamlit as st

# Kamera paraméterek (mm-ben vagy pixelben)
CAMERA_PARAMS = {
    "DJI Mavic 3M": {
        "RGB": {
            "focal_length": 24.5,  # mm
            "sensor_width": 17.3,  # mm
            "image_width": 5280  # pixel
        },
        "Multispektrális": {
            "focal_length": 4.7,  # mm
            "sensor_width": 6.4,  # mm
            "image_width": 2592,  # pixel
            "correction_factor": 0.877
        }
    }
}

def calculate_altitude(gsd_cm_per_px, focal_length, sensor_width, image_width, correction_factor=1.0):
    gsd_mm_per_px = gsd_cm_per_px * 10
    altitude_mm = (gsd_mm_per_px * sensor_width * image_width) / focal_length
    return (altitude_mm / 1000) * correction_factor

st.title("Repülési magasság kalkulátor")

# 1. Drón kiválasztása
drone_model = st.selectbox("Válassz drónt:", ["DJI Mavic 3M"])

# 2. Prioritás kiválasztása
priority_camera = st.radio("Melyik kamerára szeretnél kalkulálni?", ["RGB", "Multispektrális"])

# 3. Cél GSD beírása (cm/pixel)
gsd_input = st.number_input("Add meg a cél GSD-t (cm/pixel):", min_value=0.1, step=0.1)

if st.button("Számítás indítása"):
    params = CAMERA_PARAMS[drone_model][priority_camera]
    focal = params["focal_length"]
    sensor = params["sensor_width"]
    width = params["image_width"]
    correction = params.get("correction_factor", 1.0)

    altitude_m = calculate_altitude(gsd_input, focal, sensor, width, correction)
    st.success(f"A(z) {priority_camera} kamera számított repülési magassága: {altitude_m:.1f} m")
