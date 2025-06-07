import streamlit as st

def calculate_flight_altitude(gsd_cm, focal_length_mm, image_width_px, sensor_width_mm):
    # Átváltjuk a GSD-t mm-re
    gsd_mm = gsd_cm * 10
    # Kiszámoljuk a repülési magasságot a véglegesített képlettel
    height_mm = (gsd_mm * focal_length_mm * image_width_px) / sensor_width_mm
    return height_mm / 1000  # vissza méterbe

st.title("Drón repülési magasság kalkulátor")

# Választás: drón
st.subheader("1. Válassz drónt")
drone = st.selectbox("Drón típusa", ["DJI Mavic 3M"])

# Választás: prioritás
st.subheader("2. Válassz prioritást")
priority = st.radio("Repülés prioritása", ["RGB", "Multispektrális"])

# Választás: cél GSD
st.subheader("3. Add meg a kívánt GSD-t (cm/pixel)")
gsd = st.number_input("Cél GSD (cm/px)", min_value=0.1, step=0.1)

# Kamera paraméterek rögzítése
if priority == "RGB":
    focal_length = 24.5  # mm
    image_width = 5280  # px
    sensor_width = 17.3  # mm
elif priority == "Multispektrális":
    focal_length = 4.7  # mm
    image_width = 2592  # px
    sensor_width = 6.4  # mm
    correction_factor = 0.877  # validált korrekciós szorzó

# Számítás és eredmény megjelenítése
if gsd:
    altitude = calculate_flight_altitude(gsd, focal_length, image_width, sensor_width)

    # Ha multispektrális prioritás, alkalmazzuk a korrekciós tényezőt
    if priority == "Multispektrális":
        altitude *= correction_factor

    st.success(f"A megadott GSD eléréséhez szükséges repülési magasság: {altitude:.1f} méter")
