import streamlit as st

# Kamera specifikációk
CAMERA_SPECS = {
    "RGB": {
        "focal_length_mm": 10.26,
        "sensor_width_mm": 17.3,
        "image_width_px": 5280,
        "min_shutter_s": 1/1000,
    },
    "Multispektrális": {
        "focal_length_mm": 5.74,
        "sensor_width_mm": 5.68,
        "image_width_px": 1280,
        "min_shutter_s": 1/100,
    },
}

# Korrekciós tényező (DJI által mért és számolt értékek közötti arány)
CORRECTION_FACTOR = 0.502

def calculate_flight_altitude(gsd_cm_pixel, focal_length_mm, sensor_width_mm, image_width_px):
    altitude_cm = (gsd_cm_pixel * focal_length_mm * image_width_px) / sensor_width_mm
    return (altitude_cm / 100) * CORRECTION_FACTOR  # méterre átszámítva és korrekcióval

def main():
    st.title("Repülési paraméter kalkulátor v2.1.1")

    drone_type = st.selectbox("Válassz drónt:", ["DJI Mavic 3 Multispectral"])
    camera_mode = st.radio("Kameramód:", ["RGB", "RGB + Multispektrális"])
    primary_camera = st.radio("Fókusz kamera (melyik alapján számolunk):", ["RGB", "Multispektrális"])

    gsd_cm_pixel = st.number_input("Cél GSD (cm/pixel):", min_value=0.1, step=0.1, value=4.0)
    shutter_speed = st.number_input("Záridő (pl. 1/1000 esetén 1000):", min_value=1, step=1, value=1000)
    sidelap_percent = st.number_input("Oldalirányú átfedés (%):", min_value=0, max_value=100, value=70)
    frontlap_percent = st.number_input("Soron belüli átfedés (%):", min_value=0, max_value=100, value=80)
    area_ha = st.number_input("Térképezendő terület (ha):", min_value=0.1, step=0.1, value=5.0)
    battery_count = st.number_input("Elérhető 100%-os akkumulátorok száma:", min_value=1, step=1, value=2)

    if st.button("Számolj"):
        # Fő kamera kiválasztása
        main_specs = CAMERA_SPECS[primary_camera]
        altitude = calculate_flight_altitude(
            gsd_cm_pixel,
            main_specs["focal_length_mm"],
            main_specs["sensor_width_mm"],
            main_specs["image_width_px"]
        )

        st.subheader("Eredmények")

        if camera_mode == "RGB + Multispektrális":
            if primary_camera == "Multispektrális":
                st.markdown("**Multispektrális kamera**")
                st.markdown(f"Repülési magasság: **{altitude:.1f} m**")
                st.markdown("**RGB kamera**")
                rgb_alt = calculate_flight_altitude(
                    gsd_cm_pixel,
                    CAMERA_SPECS["RGB"]["focal_length_mm"],
                    CAMERA_SPECS["RGB"]["sensor_width_mm"],
                    CAMERA_SPECS["RGB"]["image_width_px"]
                )
                st.markdown(f"Repülési magasság: **{rgb_alt:.1f} m**")
            else:
                st.markdown("**RGB kamera**")
                st.markdown(f"Repülési magasság: **{altitude:.1f} m**")
                st.markdown("**Multispektrális kamera**")
                multi_alt = calculate_flight_altitude(
                    gsd_cm_pixel,
                    CAMERA_SPECS["Multispektrális"]["focal_length_mm"],
                    CAMERA_SPECS["Multispektrális"]["sensor_width_mm"],
                    CAMERA_SPECS["Multispektrális"]["image_width_px"]
                )
                st.markdown(f"Repülési magasság: **{multi_alt:.1f} m**")
        else:
            st.markdown(f"**{primary_camera} kamera**")
            st.markdown(f"Repülési magasság: **{altitude:.1f} m**")

if __name__ == "__main__":
    main()
