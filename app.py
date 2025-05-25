import streamlit as st
import math

st.title("🚁 Repüléstervező kalkulátor")

st.markdown("""
Ez az alkalmazás segít kiszámolni, hogy adott terület, 
repülési magasság és kamera paraméterek mellett teljesíthető-e a repülés 
a rendelkezésre álló akkumulátorokkal.
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
GSD_KORREKCIOS_SZORZO = 2.1

multi = available_drones[selected_drone_name]["Multispektrális"]
min_gsd = (12 * multi["szenzor_szelesseg_mm"]) / (multi["fokusz_mm"] * multi["képszélesség_px"]) * 100

gsd_cm = st.number_input("Cél GSD (cm/pixel)", min_value=round(min_gsd, 2), value=2.0, step=0.1)
shutter_input = st.text_input("Záridő (1/x formátumban)", value="1000")
side_overlap_pct = st.slider("Oldalirányú átfedés (%)", min_value=60, max_value=90, value=70)
front_overlap_pct = st.slider("Soron belüli átfedés (%)", min_value=60, max_value=90, value=80)
terulet_ha = st.number_input("Felvételezni kívánt terület (hektár)", min_value=0.1, value=10.0, step=0.1)
elerheto_akkuk = st.number_input("Elérhető 100%-os akkumulátorok (db)", min_value=1, value=1, step=1)

def szamol(kamera, gsd_cm_val, side_overlap_val):
    gsd_m = gsd_cm_val / 100
    repmag_cm = (gsd_cm_val * kamera["fokusz_mm"] * kamera["képszélesség_px"]) / kamera["szenzor_szelesseg_mm"] / GSD_KORREKCIOS_SZORZO
    repmag_m = repmag_cm / 100
    kep_szelesseg_m = repmag_m * kamera["szenzor_szelesseg_mm"] / kamera["fokusz_mm"]
    savszel_m = kep_szelesseg_m * (1 - side_overlap_val / 100)

    shutter_speed = 1 / float(shutter_input)
    vmax_blur = gsd_m * MAX_PIXEL_ELMOZDULAS / shutter_speed
    vmax_write = gsd_m * kamera["képszélesség_px"] / kamera["min_írási_idő_s"]
    vmax_mps = min(vmax_blur, vmax_write) * kamera["korrekcio"]

    terulet_m2 = terulet_ha * 10000
    savok_szama = math.ceil(math.sqrt(terulet_m2) / savszel_m)
    savhossz_m = terulet_m2 / (savok_szama * savszel_m)
    teljes_ut_m = savok_szama * savhossz_m

    ido_sec = teljes_ut_m / vmax_mps
    ido_min = ido_sec / 60
    return {
        "gsd_cm": gsd_cm_val,
        "side_overlap": side_overlap_val,
        "repmag_m": repmag_m,
        "savszel_m": savszel_m,
        "vmax_mps": vmax_mps,
        "teljes_ido_min": ido_min,
        "akku_igeny": math.ceil(ido_min / AKKU_IDO_PERCBEN)
    }

if st.button("▶️ Számítás indítása"):
    rgb = available_drones[selected_drone_name]["RGB"]
    multi = available_drones[selected_drone_name]["Multispektrális"]

    eredmenyek = [("RGB", szamol(rgb, gsd_cm, side_overlap_pct))]

    if kamera_mod == "RGB + multispektrális":
        eredmenyek.append(("Multispektrális", szamol(multi, gsd_cm, side_overlap_pct)))
        fo_kamera = eredmenyek[-1][1]
    else:
        fo_kamera = eredmenyek[0][1]

    for nev, eredeti in eredmenyek:
        st.subheader(f"Eredmények – {nev} kamera")
        ido_min = eredeti['teljes_ido_min']
        ido_szoveg = f"{ido_min:.1f} perc"
        if ido_min >= 60:
            ora = int(ido_min // 60)
            perc = int(ido_min % 60)
            ido_szoveg += f" ({ora} óra {perc} perc)"

        st.markdown(
            f"**Repülési magasság:** {eredeti['repmag_m']:.1f} m  
"
            f"**Sávszélesség:** {eredeti['savszel_m']:.1f} m  
"
            f"**Max. repülési sebesség:** {eredeti['vmax_mps']:.2f} m/s  
"
            f"**Becsült repülési idő:** {ido_szoveg}  
"
            f"**Szükséges akkumulátor:** {eredeti['akku_igeny']} db"
        )

    if kamera_mod == "RGB + multispektrális":
        st.warning("Ha a Multi kamerák is használatban vannak, azok eredményét kell elsődlegesen figyelembe venni!")

    if elerheto_akkuk >= fo_kamera['akku_igeny']:
        st.success(f"{elerheto_akkuk} akkumulátor elegendő ehhez a repüléshez.")
    else:
        max_ido = elerheto_akkuk * AKKU_IDO_PERCBEN
        st.warning(f"Nincs elég akku: max. {max_ido:.1f} perc repülési idő áll rendelkezésre.")

        side_kompromisszum = None
        for ovlp in range(int(side_overlap_pct)-1, 59, -1):
            adat = szamol(multi, gsd_cm, ovlp)
            if adat["teljes_ido_min"] <= max_ido:
                side_kompromisszum = adat
                break

        if side_kompromisszum:
            st.info("Javasolt kompromisszum: oldalsó átfedés csökkentése (multi alapján)")
            st.markdown(
                f"**Oldalsó átfedés:** {side_kompromisszum['side_overlap']}%  \n"
                f"**GSD marad:** {side_kompromisszum['gsd_cm']} cm/pixel  \n"
                f"**Repidő:** {side_kompromisszum['teljes_ido_min']:.1f} perc"
            )
        else:
            gsd_kompromisszum = None
            gsd_cand = gsd_cm + 0.1
            while gsd_cand < 100:
                adat = szamol(multi, round(gsd_cand, 1), 60)
                if adat["teljes_ido_min"] <= max_ido:
                    gsd_kompromisszum = adat
                    break
                gsd_cand += 0.1

            if gsd_kompromisszum:
                st.info("Javasolt kompromisszum: GSD növelése 60% oldalsó átfedéssel (multi alapján)")
                st.markdown(
                    f"**GSD:** {gsd_kompromisszum['gsd_cm']:.1f} cm/pixel  \n"
                    f"**Repidő:** {gsd_kompromisszum['teljes_ido_min']:.1f} perc"
                )
            else:
                st.error("Még GSD növeléssel sem teljesíthető a repülés ennyi akkuval a multispektrális kamerával.")
