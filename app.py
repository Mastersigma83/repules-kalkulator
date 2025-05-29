import math
import streamlit as st

# Kamera adatok
CAMERA_PARAMS = {
    "RGB": {
        "sensor_width_mm": 13.2,
        "image_width_px": 5280,
        "focal_length_mm": 10.26,
    },
    "Multispektrális": {
        "sensor_width_mm": 5.5,
        "image_width_px": 1280,
        "focal_length_mm": 5.74,
    }
}

# Felhasználói input
st.title("Drónos repüléstervező kalkulátor v2.1.2")

drone_mode = st.selectbox("Kamera mód", ["RGB", "RGB + Multispektrális"])
flight_focus = st.selectbox("Repülés fókusza", ["RGB", "Multispektrális"])

gsd_input = st.number_input("Cél GSD (cm/px)", min_value=0.1, step=0.1, value=5.0)
shutter_speed = st.number_input("Záridő (1/x formátumban)", min_value=1, value=1000)
overlap_side = st.number_input("Oldalirányú átfedés (%)", min_value=0, max_value=100, value=70)
overlap_forward = st.number_input("Előre irányú átfedés (%)", min_value=0, max_value=100, value=80)
area_ha = st.number_input("Térképezendő terület (ha)", min_value=0.1, value=10.0)
battery_count = st.number_input("Elérhető 100%-os akkumulátorok száma", min_value=1, value=2)

# Számítás
focus_camera = flight_focus
focus_params = CAMERA_PARAMS[focus_camera]
gsd_m = gsd_input / 100  # cm to m

# Repülési magasság számítása
f = focus_params["focal_length_mm"] / 1000
sw = focus_params["sensor_width_mm"] / 1000
iw = focus_params["image_width_px"]
altitude = (gsd_m * f * iw) / sw
altitude *= 0.927  # Biztonsági korrekció

# Max repülési sebesség
max_speed = gsd_m * shutter_speed
if max_speed > 15:
    max_speed = 15

# Repülési idő és akku
side_overlap_ratio = 1 - (overlap_side / 100)
forward_overlap_ratio = 1 - (overlap_forward / 100)
ground_swath = (altitude * sw / f)  # m
lane_spacing = ground_swath * side_overlap_ratio

if lane_spacing == 0:
    estimated_flight_time = 0
else:
    area_m2 = area_ha * 10000
    number_of_lanes = area_m2 / lane_spacing / ground_swath
    flight_distance = number_of_lanes * area_m2 / lane_spacing
    estimated_flight_time = flight_distance / max_speed / 60

battery_needed = math.ceil(estimated_flight_time / 25)

# Eredmények kiírása
st.subheader(f"Eredmények – {flight_focus} kamera alapján")
st.write(f"Repülési magasság: **{altitude:.1f} m**")
st.write(f"Maximális repülési sebesség: **{max_speed:.2f} m/s**")
st.write(f"Becsült repülési idő: **{estimated_flight_time:.1f} perc**")
st.write(f"Szükséges akkumulátor(ok): **{battery_needed} db**")

if drone_mode == "RGB + Multispektrális" and flight_focus == "RGB":
    # Másodlagos kamera (Multi)
    multi_params = CAMERA_PARAMS["Multispektrális"]
    multi_alt = (gsd_m * multi_params["focal_length_mm"] / 1000 * multi_params["image_width_px"]) / (multi_params["sensor_width_mm"] / 1000)
    multi_alt *= 0.927
    multi_gsd = (multi_alt * multi_params["sensor_width_mm"] / 1000) / (multi_params["focal_length_mm"] / 1000 * multi_params["image_width_px"])
    multi_gsd *= 100  # m to cm
    multi_speed = (multi_gsd / 100) * shutter_speed
    if multi_speed > 15:
        multi_speed = 15

    st.subheader("Multispektrális kamera kiegészítő adatok")
    st.write(f"A megadott RGB GSD-hez tartozó multispektrális GSD: **{multi_gsd:.2f} cm/px**")
    st.write(f"Multispektrális kamera maximális repülési sebesség: **{multi_speed:.2f} m/s**")
