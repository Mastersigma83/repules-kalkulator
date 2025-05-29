import streamlit as st
import math

st.title("DJI Mavic 3 Multispectral – Repüléstervező kalkulátor (új verzió)")

# Kameraadatok
camera_specs = {
    "RGB": {
        "name": "RGB",
        "focal_length_mm": 24.0,
        "sensor_width_mm": 17.3,
        "image_width_px": 5280,
        "min_capture_interval_s": 0.7,
        "min_write_interval_s": 0.7
    },
    "Multispectral": {
        "name": "Multispektrális",
        "focal_length_mm": 25.0,
        "sensor_width_mm": 6.4,
        "image_width_px": 1400,
        "min_capture_interval_s": 2.0,
        "min_write_interval_s": 2.0
    }
}

# Választások
camera_mode = st.radio("Kameramód kiválasztása", ["RGB", "RGB + Multispektrális"])
main_focus = st.radio("Repülés fókusza (melyik kamerából származó kép a fontosabb?)", ["RGB", "Multispektrális"])

# Kamera beállítás az elsődleges fókusz alapján
main_camera = camera_specs[main_focus]
if camera_mode == "RGB + Multispektrális":
    weaker_camera = camera_specs["Multispectral"]

# Felhasználói bemenetek
gsd_cm = st.number_input("Cél GSD (cm/pixel)", min_value=0.1, value=2.0, step=0.1)
shutter_str = st.text_input("Záridő (1/x formátumban)", value="1000")
side_overlap_pct = st.slider("Oldalirányú átfedés (%)", min_value=60, max_value=90, value=70)
front_overlap_pct = st.slider("Soron belüli átfedés (%)", min_value=60, max_value=90, value=80)
area_ha = st.number_input("Térképezendő terület (hektár)", min_value=0.1, value=10.0, step=0.1)
battery_count = st.number_input("Elérhető 100%-os akkumulátorok (db)", min_value=1, value=1, step=1)

# Számítás
def calculate_flight_time_and_speed(camera, gsd_cm, shutter_str, side_overlap_pct, front_overlap_pct, area_ha):
    gsd_m = gsd_cm / 100
    shutter_speed = 1 / float(shutter_str)

    flight_height_m = (gsd_cm * camera["focal_length_mm"] * camera["image_width_px"]) / camera["sensor_width_mm"] / 100

    blur_limit_speed = gsd_m * 0.7 / shutter_speed
    write_limit_speed = gsd_m * camera["image_width_px"] / camera["min_write_interval_s"]
    max_speed_mps = min(blur_limit_speed, write_limit_speed, 15.0)

    swath_width_m = flight_height_m * camera["sensor_width_mm"] / camera["focal_length_mm"]
    effective_swath = swath_width_m * (1 - side_overlap_pct / 100)

    area_m2 = area_ha * 10000
    lines = math.ceil(math.sqrt(area_m2) / effective_swath)
    line_length = area_m2 / (lines * effective_swath)
    total_flight_path = lines * line_length

    flight_time_s = total_flight_path / max_speed_mps
    flight_time_min = flight_time_s / 60
    battery_duration_min = 20
    required_batteries = math.ceil(flight_time_min / battery_duration_min)

    return flight_height_m, max_speed_mps, flight_time_min, required_batteries

if st.button("Számítás"):
    height, speed, duration, batteries_needed = calculate_flight_time_and_speed(
        main_camera, gsd_cm, shutter_str, side_overlap_pct, front_overlap_pct, area_ha
    )

    st.markdown(f"### Eredmények: {main_camera['name']}")
    st.markdown(f"**Repülési magasság:** {height:.2f} m")
    st.markdown(f"**Maximális repülési sebesség:** {speed:.2f} m/s")
    st.markdown(f"**Repülési idő:** {duration:.1f} perc")
    st.markdown(f"**Szükséges akkumulátor:** {batteries_needed} db")

    if camera_mode == "RGB + Multispektrális" and main_focus == "RGB":
        multi_height, multi_speed, multi_duration, multi_batteries = calculate_flight_time_and_speed(
            weaker_camera, gsd_cm * (main_camera["sensor_width_mm"] / weaker_camera["sensor_width_mm"]),
            shutter_str, side_overlap_pct, front_overlap_pct, area_ha
        )
        st.markdown("### Multispektrális kamera (másodlagos)")
        st.markdown(f"**Repülési magasság:** {multi_height:.2f} m")
        st.markdown(f"**Maximális repülési sebesség:** {multi_speed:.2f} m/s")
        st.markdown(f"**Repülési idő:** {multi_duration:.1f} perc")
        st.markdown(f"**Szükséges akkumulátor:** {multi_batteries} db")
