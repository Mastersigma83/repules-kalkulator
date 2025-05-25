import streamlit as st
import math

st.title("Repüléstervező kalkulátor")

st.markdown("""
Ez az alkalmazás segít beállítani a drónodat agrárfelmérésekhez / térképezéshez. 
""")

# Drónválasztás és kameramódok
available_drones = {
    "DJI Mavic 3 Multispectral": {
        "RGB": {
            "fokusz_mm": 24.0,
            "szenzor_szelesseg_mm": 17.3,
            "képszélesség_px": 5280,
            "min_írási_idő_s": 0.7,
            "korrekcio": 1.0
        },
        "Multispektrális": {
            "fokusz_mm": 25.0,
            "szenzor_szelesseg_mm": 6.4,
            "képszélesség_px": 1400,
            "min_írási_idő_s": 2.0,
            "korrekcio": 0.6
        }
    }
}

selected_drone_name = st.selectbox("Drón kiválasztása", list(available_drones.keys()))
kamera_mod = st.radio("Kameramód", ["Csak RGB", "RGB + multispektrális"])

# Globális konstansok
MAX_PIXEL_ELMOZDULAS = 0.7
AKKU_IDO_PERCBEN = 20
GSD_KORREKCIOS_SZORZO = 2.0  # hogy RGB-re kb. 19m jöjjön ki 0.52 cm/px-re
MULTI_GSD_KORREKCIOS_SZORZO = 1 / 0.56
DRON_MAX_SEBESSEG = 15.0  # m/s

multi = available_drones[selected_drone_name]["Multispektrális"]
min_gsd = (12 * multi["szenzor_szelesseg_mm"]) / (multi["fokusz_mm"] * multi["képszélesség_px"]) * 100

gsd_cm = st.number_input("Cél GSD (cm/pixel)", min_value=round(min_gsd, 2), value=2.0, step=0.1)
shutter_input = st.text_input("Záridő (1/x formátumban) (Terület felett, lefelé fordított kamerával – leolvasott érték!)", value="1000")
side_overlap_pct = st.selectbox("Oldalirányú átfedés (%)", options=list(range(60, 91)), index=10)
front_overlap_pct = st.selectbox("Soron belüli átfedés (%)", options=list(range(60, 91)), index=20)
terulet_ha = st.number_input("Felvételezni kívánt terület (hektár)", min_value=0.1, value=10.0, step=0.1, format="%.1f")
elerheto_akkuk = st.number_input("Elérhető 100%-os akkumulátorok (db)", min_value=1, value=1, step=1)

if st.button("▶️ Elméleti számítás indítása"):
    rgb = available_drones[selected_drone_name]["RGB"]
    multi = available_drones[selected_drone_name]["Multispektrális"]

    # Repülési magasság RGB-re
    repmag_rgb_cm = (gsd_cm * rgb["fokusz_mm"] * rgb["képszélesség_px"]) / rgb["szenzor_szelesseg_mm"] / GSD_KORREKCIOS_SZORZO
    repmag_rgb_m = repmag_rgb_cm / 100

    # Multispektrális GSD az RGB magasság alapján
    gsd_multi_cm = gsd_cm * MULTI_GSD_KORREKCIOS_SZORZO

    st.markdown("## Eredmények – Elméleti maximum")
    st.markdown(f"### RGB kamera")
    st.markdown(f"**Repülési magasság:** kb. {repmag_rgb_m:.1f} m")
    st.markdown(f"**Cél GSD:** {gsd_cm:.2f} cm/pixel")

    if kamera_mod == "RGB + multispektrális":
        st.markdown(f"### Multispektrális kamera")
        st.markdown(f"**A megadott RGB GSD-hez tartozó multispektrális GSD:** {gsd_multi_cm:.2f} cm/pixel")

    sebesseg_input = st.number_input(f"Add meg a tényleges repülési sebességet (m/s), max {DRON_MAX_SEBESSEG} m/s", min_value=0.5, max_value=DRON_MAX_SEBESSEG, step=0.1)

    kep_szelesseg_m = repmag_rgb_m * rgb["szenzor_szelesseg_mm"] / rgb["fokusz_mm"]
    savszel_m = kep_szelesseg_m * (1 - side_overlap_pct / 100)
    terulet_m2 = terulet_ha * 10000
    savok_szama = math.ceil(math.sqrt(terulet_m2) / savszel_m)
    savhossz_m = terulet_m2 / (savok_szama * savszel_m)
    teljes_ut_m = savok_szama * savhossz_m

    ido_sec = teljes_ut_m / sebesseg_input
    ido_min = ido_sec / 60
    ora = int(ido_min // 60)
    perc = int(ido_min % 60)
    ido_ora_perc = f"{ora} óra {perc} perc" if ido_min >= 60 else f"{ido_min:.1f} perc"
    akku_igeny = math.ceil(ido_min / AKKU_IDO_PERCBEN)

    st.markdown("### Tényleges beállítások alapján")
    st.markdown(f"**Sávszélesség:** kb. {savszel_m:.1f} m")
    st.markdown(f"**Becsült repülési idő:** ~{ido_ora_perc}")
    st.markdown(f"**Szükséges akkumulátor:** kb. {akku_igeny} db")

    if kamera_mod == "RGB + multispektrális":
        st.warning("Ha a Multi kamerák is használatban vannak, azok sebességkorlátját figyelembe kell venni, de az akkumulátorigényt az RGB szerint számoljuk!")

    if elerheto_akkuk >= akku_igeny:
        st.success(f"{elerheto_akkuk} akkumulátor elegendő ehhez a repüléshez.")
    else:
        max_ido = elerheto_akkuk * AKKU_IDO_PERCBEN
        hianyzo_akkuk = akku_igeny - elerheto_akkuk
        st.warning(f"Nincs elég akku: max. {max_ido:.1f} perc repülési idő áll rendelkezésre.")
        st.info(f"A repülés teljesítéséhez további {hianyzo_akkuk} akkumulátorra lenne szükség az RGB beállítások megtartásával.")
