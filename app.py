import streamlit as st

# Kamera paraméterek
CAMERA_PARAMS = {
    "DJI Mavic 3M": {
        "RGB": {
            "focal_length": 24.5,  # mm
            "image_width_px": 5280,
            "sensor_width_mm": 17.3,
        },
        "Multispektrális": {
            "focal_length": 4.7,  # mm
            "image_width_px": 2592,
            "sensor_width_mm": 6.4,
            "correction": 0.877,  # csak multispektrálisra
        },
    }
}

# GSD -> repülési magasság képlete

def calculate_flight_altitude(gsd_cm_per_px, focal_length_mm, image_width_px, sensor_width_mm, correction_factor=1.0):
    gsd_mm_per_px = gsd_cm_per_px * 10
    height_mm = (gsd_mm_per_px * sensor_width_mm * image_width_px) / focal_length_mm
    height_mm *= correction_factor
    return height_mm / 1000  # méterben

# Streamlit UI
st.title("Drón Repülési Magasság Kalkulátor")

selected_drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
camera_priority = st.radio("Melyik kamerára optimalizálsz?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Cél GSD (cm/pixel):", min_value=0.1, max_value=100.0, step=0.1)

if st.button("Számítás"):
    camera_params = CAMERA_PARAMS[selected_drone][camera_priority]
    focal_length = camera_params["focal_length"]
    image_width_px = camera_params["image_width_px"]
    sensor_width_mm = camera_params["sensor_width_mm"]
    correction = camera_params.get("correction", 1.0)

    altitude = calculate_flight_altitude(
        gsd_input,
        focal_length,
        image_width_px,
        sensor_width_mm,
        correction,
    )

    st.success(f"A szükséges repülési magasság: {altitude:.1f} méter")
