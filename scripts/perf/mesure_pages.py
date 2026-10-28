"""Mesure reproductible du poids et du temps de chargement des pages d'EduKora.

Usage : venv/Scripts/python.exe scripts/perf/mesure_pages.py [--base http://localhost] [--profil lent|rapide]
                                                           [--sortie docs-perf/mesures.json]

Pour chaque scénario : octets sur le réseau (encodedDataLength CDP), octets décompressés,
nombre de requêtes, FCP, LCP, DOMContentLoaded, load. Chaque scénario est joué 3 fois, on
garde la médiane. « froid » = contexte neuf (aucun cache) ; « chaud » = 2e visite dans le
même contexte, service worker et cache HTTP conservés.
"""
import argparse, json, statistics, sys, time
from playwright.sync_api import sync_playwright

PROFILS = {
    # 400 kbit/s = 50 000 octets/s, latence 400 ms, CPU ralenti x4
    "lent": {"offline": False, "latency": 400, "downloadThroughput": 50_000, "uploadThroughput": 25_000, "cpu": 4},
    "rapide": {"offline": False, "latency": 20, "downloadThroughput": 5_000_000, "uploadThroughput": 2_000_000, "cpu": 1},
}
SCENARIOS = [
    ("accueil", "/"),
    ("pays", "/cm"),
    ("epreuves", "/cm/epreuves"),
    ("cours", "/cm/cours"),
    ("tarifs", "/tarifs"),
    ("accueil_en", "/en"),
]

JS_PERF = """() => new Promise(res => {
  const out = {fcp: null, lcp: null};
  for (const e of performance.getEntriesByType('paint')) if (e.name === 'first-contentful-paint') out.fcp = e.startTime;
  let lcp = null;
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) lcp = e.startTime; }).observe({type:'largest-contentful-paint', buffered:true}); } catch(e) {}
  setTimeout(() => {
    const nav = performance.getEntriesByType('navigation')[0] || {};
    out.lcp = lcp; out.dcl = nav.domContentLoadedEventEnd; out.load = nav.loadEventEnd;
    res(out);
  }, 300);
})"""


def visiter(ctx, base, chemin, profil, attente=2500):
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    cdp.send("Network.enable")
    p = PROFILS[profil]
    cdp.send("Network.emulateNetworkConditions", {k: p[k] for k in ("offline", "latency", "downloadThroughput", "uploadThroughput")})
    if p["cpu"] > 1:
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": p["cpu"]})
    reqs = {}
    def on_resp(r):
        reqs.setdefault(r["requestId"], {})["url"] = r["response"]["url"]
        reqs[r["requestId"]]["status"] = r["response"]["status"]
        reqs[r["requestId"]]["fromCache"] = r["response"].get("fromDiskCache") or r["response"].get("fromServiceWorker")
    def on_fin(r):
        reqs.setdefault(r["requestId"], {})["net"] = r["encodedDataLength"]
    def on_data(r):
        reqs.setdefault(r["requestId"], {})["dec"] = reqs.get(r["requestId"], {}).get("dec", 0) + r["dataLength"]
    cdp.on("Network.responseReceived", on_resp)
    cdp.on("Network.loadingFinished", on_fin)
    cdp.on("Network.dataReceived", on_data)
    t0 = time.time()
    page.goto(base + chemin, wait_until="load", timeout=180_000)
    page.wait_for_timeout(attente)
    perf = page.evaluate(JS_PERF)
    page.close()
    lignes = [v for v in reqs.values() if "url" in v]
    return {
        "net_octets": sum(v.get("net", 0) for v in lignes),
        "dec_octets": sum(v.get("dec", 0) for v in lignes),
        "requetes": len(lignes),
        "fcp_ms": perf["fcp"], "lcp_ms": perf["lcp"], "dcl_ms": perf["dcl"], "load_ms": perf["load"],
        "mur_s": round(time.time() - t0, 1),
        "detail": sorted(({"url": v["url"].replace(base, ""), "net": v.get("net", 0), "dec": v.get("dec", 0), "status": v.get("status")} for v in lignes), key=lambda x: -x["net"])[:12],
    }


def mediane(runs, cle):
    vals = [r[cle] for r in runs if r[cle] is not None]
    return round(statistics.median(vals)) if vals else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost")
    ap.add_argument("--profil", default="rapide", choices=PROFILS)
    ap.add_argument("--sortie", default=None)
    ap.add_argument("--repetitions", type=int, default=3)
    a = ap.parse_args()
    resultats = {}
    with sync_playwright() as pw:
        navigateur = pw.chromium.launch()
        for nom, chemin in SCENARIOS:
            froid, chaud = [], []
            for _ in range(a.repetitions):
                ctx = navigateur.new_context(viewport={"width": 390, "height": 800}, service_workers="allow")
                froid.append(visiter(ctx, a.base, chemin, a.profil))
                chaud.append(visiter(ctx, a.base, chemin, a.profil))
                ctx.close()
            resultats[nom] = {"chemin": chemin}
            for etat, runs in (("froid", froid), ("chaud", chaud)):
                resultats[nom][etat] = {c: mediane(runs, c) for c in ("net_octets", "dec_octets", "requetes", "fcp_ms", "lcp_ms", "dcl_ms", "load_ms")}
                resultats[nom][etat]["detail_run1"] = runs[0]["detail"]
            f, c = resultats[nom]["froid"], resultats[nom]["chaud"]
            print(f"{nom:11s} froid {f['net_octets']/1024:7.0f} Ko net / {f['dec_octets']/1024:7.0f} Ko déc / {f['requetes']:3d} req / FCP {f['fcp_ms']} / LCP {f['lcp_ms']}   "
                  f"chaud {c['net_octets']/1024:6.0f} Ko / {c['requetes']:3d} req / FCP {c['fcp_ms']} / LCP {c['lcp_ms']}", flush=True)
        navigateur.close()
    if a.sortie:
        with open(a.sortie, "w", encoding="utf-8") as fh:
            json.dump({"base": a.base, "profil": a.profil, "resultats": resultats}, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
