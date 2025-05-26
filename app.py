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

# Konstansok
MAX_PIXEL_ELMOZDULAS = 0.7
AKKU_IDO_PERCBEN = 20
GSD_KORREKCIOS_SZORZO = 2.0  # korrigált a DJI alapján
DRON_MAX_SEBESSEG = 15.0
MULTI_GSD_SZORZO = 1 / 0.56

# Beviteli mezők
selected_drone_name = st.selectbox("Drón kiválasztása", list(available_drones.keys()))
kamera_mod = st.radio("Kameramód", ["Csak RGB", "RGB + multispektrális"])
multi = available_drones[selected_drone_name]["Multispektrális"]
min_gsd = (12 * multi["szenzor_szelesseg_mm"]) / (multi["fokusz_mm"] * multi["képszélesség_px"]) * 100

gsd_cm = st.number_input("Cél GSD (cm/pixel)", min_value=round(min_gsd, 2), value=2.0, step=0.1)
shutter_input = st.text_input("Záridő (1/x formátumban) (Terület felett, lefelé fordított kamerával – leolvasott érték!)", value="1000")
side_overlap_pct = st.selectbox("Oldalirányú átfedés (%)", options=list(range(60, 91)), index=10)
front_overlap_pct = st.selectbox("Soron belüli átfedés (%)", options=list(range(60, 91)), index=20)
terulet_ha = st.number_input("Felvételezni kívánt terület (hektár)", min_value=0.1, value=10.0, step=0.1, format="%.1f")
elerheto_akkuk = st.number_input("Elérhető 100%-os akkumulátorok (db)", min_value=1, value=1, step=1)

# Számítási függvény
def szamol(kamera, gsd_cm_val, side_overlap_val, corrected=True):
    gsd_m = gsd_cm_val / 100
    repmag_cm = (gsd_cm_val * kamera["fokusz_mm"] * kamera["képszélesség_px"]) / kamera["szenzor_szelesseg_mm"]
    if corrected:
        repmag_cm /= GSD_KORREKCIOS_SZORZO
    repmag_m = repmag_cm / 100

    kep_szelesseg_m = repmag_m * kamera["szenzor_szelesseg_mm"] / kamera["fokusz_mm"]
    savszel_m = kep_szelesseg_m * (1 - side_overlap_val / 100)

    shutter_speed = 1 / float(shutter_input)
    vmax_blur = gsd_m * MAX_PIXEL_ELMOZDULAS / shutter_speed
    vmax_write = gsd_m * kamera["képszélesség_px"] / kamera["min_írási_idő_s"]
    vmax_mps = min(vmax_blur, vmax_write) * kamera["korrekcio"]
    vmax_mps = min(vmax_mps, DRON_MAX_SEBESSEG)

    terulet_m2 = terulet_ha * 10000
    savok_szama = math.ceil(math.sqrt(terulet_m2) / savszel_m)
    savhossz_m = terulet_m2 / (savok_szama * savszel_m)
    teljes_ut_m = savok_szama * savhossz_m

    ido_sec = teljes_ut_m / vmax_mps
    ido_min = ido_sec / 60

    ora = int(ido_min // 60)
    perc = int(ido_min % 60)
    ido_ora_perc = f"{ora} óra {perc} perc" if ido_min >= 60 else ""

    return {
        "repmag_m": repmag_m,
        "gsd_cm": gsd_cm_val,
        "savszel_m": savszel_m,
        "vmax_mps": vmax_mps,
        "teljes_ido_min": ido_min,
        "ido_ora_perc": ido_ora_perc,
        "akku_igeny": math.ceil(ido_min / AKKU_IDO_PERCBEN),
        "teljes_ut_m": teljes_ut_m  # ezt a multi időhöz újrahasznosítjuk
    }

# Számítás gomb
if st.button("▶️ Számítás indítása"):
    rgb = available_drones[selected_drone_name]["RGB"]
    eredmeny_rgb = szamol(rgb, gsd_cm, side_overlap_pct)

    st.markdown("## Eredmények")
    st.markdown("### RGB kamera")
    st.markdown(f"**Repülési magasság:** kb. {eredmeny_rgb['repmag_m']:.1f} m")
    st.markdown(f"**Sávszélesség:** kb. {eredmeny_rgb['savszel_m']:.1f} m")
    st.markdown(f"**Max. repülési sebesség:** kb. {eredmeny_rgb['vmax_mps']:.2f} m/s")
    if eredmeny_rgb['ido_ora_perc']:
        st.markdown(f"**Becsült repülési idő:** ~{eredmeny_rgb['ido_ora_perc']}")
    else:
        st.markdown(f"**Becsült repülési idő:** ~{eredmeny_rgb['teljes_ido_min']:.1f} perc")
    st.markdown(f"**Szükséges akkumulátor:** kb. {eredmeny_rgb['akku_igeny']} db")

    if kamera_mod == "RGB + multispektrális":
        st.markdown("### Multispektrális kamera")

        # GSD átszámítás RGB-ből
        multi_gsd = gsd_cm * MULTI_GSD_SZORZO

        # Multispektrális max sebesség újra számolva a GSD alapján
        shutter_speed = 1 / float(shutter_input)
        gsd_m_multi = multi_gsd / 100
        vmax_blur_multi = gsd_m_multi * MAX_PIXEL_ELMOZDULAS / shutter_speed
        vmax_write_multi = gsd_m_multi * multi["képszélesség_px"] / multi["min_írási_idő_s"]
        vmax_multi = min(vmax_blur_multi, vmax_write_multi) * multi["korrekcio"]
        vmax_multi = min(vmax_multi, DRON_MAX_SEBESSEG)

        # Multispektrális repülési idő RGB repmagasság alapján, multi kamerával
        repmag_m = eredmeny_rgb["repmag_m"]
        kep_szelesseg_m_multi = repmag_m * multi["szenzor_szelesseg_mm"] / multi["fokusz_mm"]
        savszel_m_multi = kep_szelesseg_m_multi * (1 - side_overlap_pct / 100)

        savok_szama = math.ceil(math.sqrt(terulet_ha * 10000) / savszel_m_multi)
        savhossz_m = (terulet_ha * 10000) / (savok_szama * savszel_m_multi)
        teljes_ut_m_multi = savok_szama * savhossz_m
        ido_sec_multi = teljes_ut_m_multi / vmax_multi
        ido_min_multi = ido_sec_multi / 60
        ora_m = int(ido_min_multi // 60)
        perc_m = int(ido_min_multi % 60)
        ido_ora_perc_m = f"{ora_m} óra {perc_m} perc" if ido_min_multi >= 60 else f"{ido_min_multi:.1f} perc"

        st.markdown(f"**A megadott RGB GSD-hez tartozó multispektrális GSD:** {multi_gsd:.2f} cm/pixel")
        st.markdown(f"**Max. repülési sebesség (elmosódás nélkül):** {vmax_multi:.2f} m/s")
        st.markdown(f"**Multi kamera teljes repülési idő (elméleti max sebességgel):** ~{ido_ora_perc_m}")
        st.warning("Ha a Multi kamerák is használatban vannak, azok sebességkorlátját figyelembe kell venni.")

    if elerheto_akkuk >= eredmeny_rgb['akku_igeny']:
        st.success(f"{elerheto_akkuk} akkumulátor elegendő ehhez a repüléshez.")
    else:
        hianyzo = eredmeny_rgb['akku_igeny'] - elerheto_akkuk
        st.warning(f"Nincs elég akku: további {hianyzo} akkumulátorra lenne szükség az RGB beállítások megtartásához.")
