import streamlit as st
import math

st.title("Drón repülési idő kalkulátor - Mavic 3 Multispectral")

# --- Kameraadatok (RGB és Multispektrális) ---
kamera_adatok = {
    "RGB": {
        "fokusz_mm": 24.0,
        "szenzor_szelesseg_mm": 17.3,
        "képszélesség_px": 5280,
        "min_írási_idő_s": 0.7
    },
    "Multispektrális": {
        "fokusz_mm": 25.0,
        "szenzor_szelesseg_mm": 6.4,
        "képszélesség_px": 1400,
        "min_írási_idő_s": 2.0
    }
}

# --- Beviteli mezők ---
kamera_mod = st.radio("Kameramód kiválasztása", ["RGB", "RGB + Multispektrális"])
fokusz_kamera = st.radio("Melyik kamerát tekintjük fókusznak?", ["RGB", "Multispektrális"])

kamera = kamera_adatok[fokusz_kamera]

gsd_cm = st.number_input("Cél GSD (cm/pixel)", min_value=0.5, value=2.0, step=0.1)
shutter_input = st.text_input("Záridő (1/x formátumban, pl. 1000)", value="1000")
side_overlap = st.slider("Oldalirányú átfedés (%)", min_value=60, max_value=90, value=70)
front_overlap = st.slider("Soron belüli átfedés (%)", min_value=60, max_value=90, value=80)
terulet_ha = st.number_input("Térképezendő terület (hektár)", min_value=0.1, value=10.0, step=0.1)
elerheto_akkuk = st.number_input("Elérhető 100%-os akkuk (db)", min_value=1, value=1, step=1)

# --- Számítási logika ---
def repulesi_ido_szamitas(kamera, gsd_cm, shutter, side_overlap, terulet_ha, sebesseg):
    terulet_m2 = terulet_ha * 10_000
    gsd_m = gsd_cm / 100

    # Repülési magasság kiszámítása a GSD alapján
    repmag_cm = (gsd_cm * kamera["fokusz_mm"] * kamera["képszélesség_px"]) / kamera["szenzor_szelesseg_mm"]
    repmag_m = repmag_cm / 100

    # Képszélesség és sávszélesség
    kep_szelesseg_m = repmag_m * kamera["szenzor_szelesseg_mm"] / kamera["fokusz_mm"]
    savszel_m = kep_szelesseg_m * (1 - side_overlap / 100)

    sorok_szama = math.ceil(math.sqrt(terulet_m2) / savszel_m)
    sor_hossz_m = terulet_m2 / (sorok_szama * savszel_m)
    teljes_ut_m = sorok_szama * sor_hossz_m

    ido_sec = teljes_ut_m / sebesseg
    ido_min = ido_sec / 60

    ora = int(ido_min // 60)
    perc = int(ido_min % 60)
    ido_szoveg = f"{ora} óra {perc} perc" if ora else f"{perc} perc"
    return repmag_m, ido_min, ido_szoveg

# --- Számítás indítása ---
if st.button("Számítás indítása"):
    shutter = 1 / float(shutter_input)

    # Kamera alapján sebesség (egyszerűsítve: RGB = gyorsabb, Multi = lassabb)
    rgb_seb = 8.0  # m/s
    multi_seb = rgb_seb / 2  # ha mindkét kamera megy

    if kamera_mod == "RGB":
        vegso_seb = rgb_seb
    else:
        vegso_seb = multi_seb

    repmag_m, ido_min, ido_szoveg = repulesi_ido_szamitas(
        kamera, gsd_cm, shutter, side_overlap, terulet_ha, vegso_seb
    )

    st.markdown(f"### Repülési magasság: **{repmag_m:.1f} m**")
    st.markdown(f"### Becsült repülési idő: **{ido_szoveg}**")
    st.markdown(f"### Szükséges akkuk: **{math.ceil(ido_min / 20)} db** (1 akku = 20 perc repülési idő)")
