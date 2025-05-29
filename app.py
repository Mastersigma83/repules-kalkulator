import streamlit as st
import math

st.set_page_config(page_title="Drónos Repülési Kalkulátor V2.1", layout="centered")

st.title("Drónos Repülési Kalkulátor – DJI Mavic 3 Multispectral")

# --- Kamera adatok (fixen beégetve a DJI Mavic 3M alapján) ---
RGB_SENSOR_WIDTH_MM = 13.2
RGB_SENSOR_RESOLUTION = 5280
RGB_FOCAL_LENGTH_MM = 10.3
RGB_SHUTTER_WRITE_DELAY_S = 2.0  # 2 mp per kép (shutter + írás)

MULTI_SENSOR_WIDTH_MM = 5.36
MULTI_SENSOR_RESOLUTION = 1280
MULTI_FOCAL_LENGTH_MM = 5.74
MULTI_SHUTTER_WRITE_DELAY_S = 2.0  # 2 mp per kép (shutter + írás)

KORREKCIO_RGB_MAGASSAG = 0.502

# --- Bemenetek ---
st.sidebar.header("Repülési beállítások")

kamera_mod = st.sidebar.selectbox("Kamera mód:", ["RGB", "RGB + Multi"])
fokusz_mod = st.sidebar.selectbox("Repülés fókusza:", ["RGB", "Multispektrális"])
gsd_cm = st.sidebar.number_input("Cél GSD (cm/pixel):", min_value=0.1, max_value=100.0, value=5.0)
shutter = st.sidebar.number_input("Záridő (1/x):", min_value=100, max_value=10000, value=1000)
oldal_atfedes = st.sidebar.slider("Oldalirányú átfedés (%):", 0, 100, 70)
soron_atfedes = st.sidebar.slider("Soron belüli átfedés (%):", 0, 100, 80)
terulet_ha = st.sidebar.number_input("Térképezendő terület (ha):", min_value=0.1, max_value=500.0, value=10.0)
akku_darab = st.sidebar.number_input("Akkumulátorok száma:", min_value=1, max_value=10, value=2)

# --- Használt kamera ---
kamera = "RGB" if kamera_mod == "RGB" or fokusz_mod == "RGB" else "Multi"

def calc_gsd_altitude(sensor_width_mm, resolution_px, focal_length_mm, gsd_cm):
    gsd_m = gsd_cm / 100
    altitude = (gsd_m * focal_length_mm * resolution_px) / sensor_width_mm
    return altitude * KORREKCIO_RGB_MAGASSAG

def calc_max_speed(gsd_cm, shutter_speed):
    gsd_m = gsd_cm / 100
    return gsd_m * shutter_speed

# --- Fókusz szerinti kamera paraméterek ---
if kamera == "RGB":
    altitude = calc_gsd_altitude(RGB_SENSOR_WIDTH_MM, RGB_SENSOR_RESOLUTION, RGB_FOCAL_LENGTH_MM, gsd_cm)
    max_speed = calc_max_speed(gsd_cm, shutter)
    delay = RGB_SHUTTER_WRITE_DELAY_S
else:
    altitude = calc_gsd_altitude(MULTI_SENSOR_WIDTH_MM, MULTI_SENSOR_RESOLUTION, MULTI_FOCAL_LENGTH_MM, gsd_cm)
    max_speed = calc_max_speed(gsd_cm, shutter)
    delay = MULTI_SHUTTER_WRITE_DELAY_S

# --- Repülési idő kalkuláció ---
# Egyszerűsített sorhossz/átfedés alapú becslés
sorok_szama = math.ceil(math.sqrt((terulet_ha * 10000) / (altitude * (1 - oldal_atfedes / 100) * max_speed)))
ido_per_sor = (terulet_ha * 10000) / (max_speed * sorok_szama)
repulesi_ido_min = (ido_per_sor * sorok_szama) / 60

# --- Eredmények ---
st.subheader(f"Eredmények ({kamera} fókuszú repülés)")

st.markdown(f"**Számított repülési magasság:** {altitude:.1f} m")
st.markdown(f"**Maximális repülési sebesség:** {max_speed:.2f} m/s")
st.markdown(f"**Becsült repülési idő:** {repulesi_ido_min:.1f} perc")
st.markdown(f"**Szükséges akkumulátor:** ~{math.ceil(repulesi_ido_min / 30)} db")

# --- Multi kamera esetén további infók ---
if kamera_mod == "RGB + Multi":
    st.subheader("Multispektrális kamera adatok (kiegészítő információ)")

    multi_gsd = gsd_cm / 0.56
    multi_max_speed = calc_max_speed(multi_gsd, shutter)

    st.markdown(f"**A megadott RGB GSD-hez tartozó multispektrális GSD:** {multi_gsd:.2f} cm/pixel")
    st.markdown(f"**Ajánlott maximális repülési sebesség multispektrális kamerához:** {multi_max_speed:.2f} m/s")
