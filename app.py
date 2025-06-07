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

# Repülési magasság számítása
def calculate_flight_altitude(gsd_cm_px, camera_type):
    specs = CAMERA_SPECS[camera_type]
    gsd_mm_px = gsd_cm_px * 10  # cm/px → mm/px

    if camera_type == "RGB":
        # RGB kamera képlete
        altitude_mm = (gsd_mm_px * specs["sensor_width_mm"] * specs["image_width_px"]) / specs["focal_length_mm"]
    else:
        # Multi kamera képlete korrekcióval
        altitude_mm = (gsd_mm_px * specs["focal_length_mm"] * specs["image_width_px"]) / specs["sensor_width_mm"]
        altitude_mm /= specs.get("correction_factor", 1.0)

    return altitude_mm / 1000  # mm → m

# Streamlit UI
st.title("AGRON Repüléstervezés")

drone = st.selectbox("Válaszd ki a drónt:", ["DJI Mavic 3M"])
priority = st.selectbox("Melyik kamerát vegyük alapul?", ["RGB", "Multispektrális"])
gsd_input = st.number_input("Add meg a kívánt GSD-t (cm/px):", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
shutter_speed = st.number_input("Add meg a záridő nevezőjét (pl. 800 = 1/800):", min_value=100, value=800)
front_overlap = st.number_input("Soron belüli átfedés (%):", min_value=0, max_value=100, value=80, step=1)
side_overlap = st.number_input("Sorok közötti átfedés (%):", min_value=0, max_value=100, value=70, step=1)
planned_flight_time = st.number_input("KOntrollerből kiolvasott repülési idő (perc):", min_value=1.0, value=20.0, step=1.0)

if st.button("Számítás indítása"):
    altitude = calculate_flight_altitude(gsd_input, priority)
    st.success(f"A kívánt {gsd_input:.1f} cm/px GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter ({priority} kamera alapján)")

    # Akkumulátor kalkuláció a megadott repülési idő alapján
    battery_minutes = 20
    akku_igeny = int(planned_flight_time / battery_minutes + 0.999)
    st.info(f"Szükséges akkumulátorok száma (20 perc/akku): {akku_igeny} db")
