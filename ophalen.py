#!/usr/bin/env python3
"""Haalt de opgavenboekjes en correctievoorschriften op van examenblad.nl (alle examens die op examenvault.nl
gelinkt worden, zie examenpaginas.json in de site-bron). Overslaan wat er al staat. Twee downloads tegelijk."""
import json, os, subprocess, sys, time, concurrent.futures as cf, importlib.util
SITE = "/Volumes/ExamenvaultBouw/examenvault-site"
HIER = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("el", f"{SITE}/examenlinks.py"); el = importlib.util.module_from_spec(spec); spec.loader.exec_module(el)
SLUG = {"Wiskunde A": "wiskunde-a", "Wiskunde B": "wiskunde-b", "Natuurkunde": "natuurkunde", "Scheikunde": "scheikunde",
        "Biologie": "biologie", "Nederlands": "nederlands", "Engels": "engels", "Economie": "economie", "Bedrijfseconomie": "bedrijfseconomie"}
NAAM = {"o": "opgaven", "c": "correctievoorschrift"}
taken = []
for k in json.load(open(f"{SITE}/examenpaginas.json")):
    vak, jt = k.split("|"); jaar, tv = map(int, jt.split("-"))
    basis = el.url(el.VAKCODE[vak], jaar, tv)[:-2]
    for s in "oc":
        pad = f"{HIER}/vwo/{SLUG[vak]}/{jaar}-{tv}-{NAAM[s]}.pdf"
        taken.append((f"{basis}-{s}", pad))

def haal(t):
    url, pad = t
    if os.path.exists(pad) and os.path.getsize(pad) > 1000: return pad, "al aanwezig"
    os.makedirs(os.path.dirname(pad), exist_ok=True)
    for poging in range(3):
        r = subprocess.run(["curl", "-sL", "-m", "180", "-A", "Mozilla/5.0 (examenvault.nl; eigen kopie)", "-o", pad + ".deel",
                            "-w", "%{http_code} %{content_type}", url], capture_output=True, text=True).stdout
        if r.startswith("200") and "pdf" in r:
            os.replace(pad + ".deel", pad); time.sleep(0.4); return pad, "ok"
        time.sleep(3)
    if os.path.exists(pad + ".deel"): os.remove(pad + ".deel")
    return pad, f"MISLUKT {r}"
uit = {}
with cf.ThreadPoolExecutor(2) as ex:
    for i, (pad, st) in enumerate(ex.map(haal, taken), 1):
        uit[st.split()[0]] = uit.get(st.split()[0], 0) + 1
        if st.startswith("MISLUKT"): print(pad, st, flush=True)
        if i % 25 == 0: print(f"{i}/{len(taken)}", uit, flush=True)
print("klaar", uit, flush=True)
