import streamlit as st

# Oldal cím és stílus
st.set_page_config(page_title="AGRON Repüléstervezés", layout="centered")
st.markdown("""
    <style>
    select, input[type=number] {
        caret-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

# Repülési magasság számítása
def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10  # cm/px → mm/px
    if camera_type == "RGB":
        altitude_mm = (gsd_mm_px * specs["sensor_width_mm"] * specs["image_width_px"]) / specs["focal_length_mm"]
    else:
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs.get("correction_factor", 1.0)
    return altitude_mm / 1000  # mm → m

# Cím
st.title("AGRON Repüléstervezés")

# Alapbeállítások bekérése
drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Mi a prioritás a repülés során?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)

# Csak ha mindhárom mező meg van adva, folytatjuk
if drone and priority and gsd_input:
    shutter_speed = st.number_input("Add meg a záridőt (pl. 1/800 → írd be: 800):", min_value=100, max_value=5000, value=800, step=10)
    overlap_in = st.slider("Soron belüli átfedés (%)", 50, 95, 80)
    overlap_out = st.slider("Sorok közötti átfedés (%)", 50, 95, 70)
    area_ha = st.number_input("Felmérendő terület (hektár):", min_value=0.1, max_value=500.0, value=10.0, step=0.1)

    # Magasság
    altitude = calculate_flight_altitude(gsd_input, priority)

    # Maximális sebesség fényviszony alapján
    max_speed_light = (gsd_input * shutter_speed) / 100
    max_speed_light *= 0.9  # 10% biztonsági korrekció

    # Kiírási idő miatti sebességkorlát
    min_interval = 1 if priority == "RGB" else 2
    max_speed_storage = altitude / min_interval  # elméleti, de helyettesíthető fix értékkel
    max_speed = min(max_speed_light, 15, max_speed_storage)

    # Felmérési idő közelítéssel (tapasztalati adat alapján finomhangolt)
    from math import ceil
    if priority == "RGB":
        minutes = (area_ha * 2.87) / max_speed
    else:
        minutes = (area_ha * 3.0) / max_speed
    battery_need = ceil(minutes / 20)

    # Eredmények
    st.markdown(f"""
    ### Eredmények:
    - **Szükséges repülési magasság:** `{altitude:.1f} m`
    - **Maximális repülési sebesség (fényviszony + írási idő alapján):** `{max_speed:.2f} m/s`
    - **Becsült repülési idő:** `{minutes:.0f} perc`
    - **Szükséges akkumulátorok száma:** `{battery_need} db`
    """)
