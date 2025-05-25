import streamlit as st
import math

st.title("jRepüléstervező kalkulátor")

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
GSD_KORREKCIOS_SZORZO = 1.13
DRON_MAX_SEBESSEG = 15.0  # m/s

multi = available_drones[selected_drone_name]["Multispektrális"]
min_gsd = (12 * multi["szenzor_szelesseg_mm"]) / (multi["fokusz_mm"] * multi["képszélesség_px"]) * 100

gsd_cm = st.number_input("Cél GSD (cm/pixel)", min_value=round(min_gsd, 2), value=2.0, step=0.1)
shutter_input = st.text_input("Záridő (1/x formátumban) (Terület felett, lefelé fordított kamerával – leolvasott érték!)", value="1000")
side_overlap_pct = st.selectbox("Oldalirányú átfedés (%)", options=list(range(60, 91)), index=10)
front_overlap_pct = st.selectbox("Soron belüli átfedés (%)", options=list(range(60, 91)), index=20)
terulet_ha = st.number_input("Felvételezni kívánt terület (hektár)", min_value=0.1, value=10.0, step=0.1, format="%.1f")
elerheto_akkuk = st.number_input("Elérhető 100%-os akkumulátorok (db)", min_value=1, value=1, step=1)

def szamol_magassag(gsd_cm_val, kamera):
    repmag_cm = (gsd_cm_val * kamera["fokusz_mm"] * kamera["képszélesség_px"] * GSD_KORREKCIOS_SZORZO) / kamera["szenzor_szelesseg_mm"]
    return repmag_cm / 100

def szamol_sebesseg(gsd_cm_val, kamera, shutter_input):
    gsd_m = gsd_cm_val / 100
    shutter_speed = 1 / float(shutter_input)
    vmax_blur = gsd_m * MAX_PIXEL_ELMOZDULAS / shutter_speed
    vmax_write = gsd_m * kamera["képszélesség_px"] / kamera["min_írási_idő_s"]
    vmax_mps = min(vmax_blur, vmax_write) * kamera["korrekcio"]
    return min(vmax_mps, DRON_MAX_SEBESSEG)

if st.button("▶️ Számítás indítása"):
    rgb = available_drones[selected_drone_name]["RGB"]
    multi = available_drones[selected_drone_name]["Multispektrális"]

    repmag_rgb = szamol_magassag(gsd_cm, rgb) / 2
    gsd_multi_cm = gsd_cm * (1 / 0.56)

    st.markdown("## Eredmények")
    st.markdown("### RGB kamera")
    st.markdown(f"**Repülési magasság:** kb. {repmag_rgb:.1f} m")

    vmax_rgb = szamol_sebesseg(gsd_cm, rgb, shutter_input)
    st.markdown(f"**Elméleti maximális repülési sebesség:** kb. {vmax_rgb:.2f} m/s")

    sebesseg_valos = st.number_input("Általad tervezett repülési sebesség (m/s)", min_value=1.0, max_value=vmax_rgb, value=round(vmax_rgb, 2), step=0.1)

    kep_szelesseg_m = repmag_rgb * rgb["szenzor_szelesseg_mm"] / rgb["fokusz_mm"]
    savszel_m = kep_szelesseg_m * (1 - side_overlap_pct / 100)
    terulet_m2 = terulet_ha * 10000
    savok_szama = math.ceil(math.sqrt(terulet_m2) / savszel_m)
    savhossz_m = terulet_m2 / (savok_szama * savszel_m)
    teljes_ut_m = savok_szama * savhossz_m
    ido_sec = teljes_ut_m / sebesseg_valos
    ido_min = ido_sec / 60
    ora = int(ido_min // 60)
    perc = int(ido_min % 60)
    ido_ora_perc = f"{ora} óra {perc} perc" if ido_min >= 60 else ""
    akku_igeny = math.ceil(ido_min / AKKU_IDO_PERCBEN)

    st.markdown(f"**Sávszélesség:** kb. {savszel_m:.1f} m")
    st.markdown(f"**Becsült repülési idő:** ~{ido_ora_perc if ido_min >= 60 else f'{ido_min:.1f} perc'}")
    st.markdown(f"**Szükséges akkumulátor:** kb. {akku_igeny} db")

    if kamera_mod == "RGB + multispektrális":
        st.markdown("### Multispektrális kamera")
        st.markdown(f"**A megadott RGB GSD-hez tartozó multispektrális GSD:** {gsd_multi_cm:.2f} cm/pixel")
        vmax_multi = szamol_sebesseg(gsd_multi_cm, multi, shutter_input)
        st.markdown(f"**Max. repülési sebesség (elmosódás nélkül):** {vmax_multi:.2f} m/s")
        st.warning("Ha a Multi kamerák is használatban vannak, azok sebességkorlátját figyelembe kell venni, de az akkumulátorigényt az RGB szerint számoljuk!")

    if elerheto_akkuk >= akku_igeny:
        st.success(f"{elerheto_akkuk} akkumulátor elegendő ehhez a repüléshez.")
    else:
        max_ido = elerheto_akkuk * AKKU_IDO_PERCBEN
        hianyzo_akkuk = akku_igeny - elerheto_akkuk
        st.warning(f"Nincs elég akku: max. {max_ido:.1f} perc repülési idő áll rendelkezésre.")
        st.info(f"A repülés teljesítéséhez további {hianyzo_akkuk} akkumulátorra lenne szükség az RGB beállítások megtartásával.")
