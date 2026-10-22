"""Mesures de temps quand le nombre de colis augmente (partie 6 du sujet).

Lancement depuis la racine du projet :
    python -m src.benchmark            (tout, ~1 min)
    python -m src.benchmark --rapide   (sans les plus gros cas de la PD)

Les résultats sont écrits dans resultats/benchmark.md.
"""

import os
import random
import sys
import time

from .chargement import sac_a_dos_dp, sac_a_dos_glouton
from .gestion import GestionColis
from .generateur import generer_colis
from .tri import tri_fusion

TAILLES = [100, 1_000, 10_000, 100_000]
SEED = 42


def chrono(f, repetitions=1):
    """Meilleur temps sur plusieurs répétitions (le min limite le bruit du système)."""
    meilleur = float("inf")
    for _ in range(repetitions):
        t = time.perf_counter()
        f()
        meilleur = min(meilleur, time.perf_counter() - t)
    return meilleur


def fmt(s):
    if s < 1e-3:
        return f"{s * 1e6:.1f} µs"
    if s < 1:
        return f"{s * 1e3:.1f} ms"
    return f"{s:.2f} s"


def tableau_md(entetes, lignes):
    out = ["| " + " | ".join(entetes) + " |", "|" + "---|" * len(entetes)]
    out += ["| " + " | ".join(str(x) for x in l) + " |" for l in lignes]
    return "\n".join(out)


def bench_ajout_recherche():
    lignes = []
    for n in TAILLES:
        colis = generer_colis(n, seed=SEED)
        g = GestionColis()
        t_ajout = chrono(lambda: GestionColis().ajouter_plusieurs(colis), 3)
        g.ajouter_plusieurs(colis)
        rng = random.Random(SEED)
        ids = [rng.choice(colis).id for _ in range(200)]  # 200 recherches d'ids existants
        t_dict = chrono(lambda: [g.rechercher(i) for i in ids], 5) / len(ids)
        t_lin = chrono(lambda: [g.recherche_lineaire(i) for i in ids], 1) / len(ids)
        lignes.append([f"{n:,}".replace(",", " "), fmt(t_ajout), fmt(t_dict), fmt(t_lin),
                       f"x{t_lin / t_dict:,.0f}".replace(",", " ")])
    return tableau_md(["n", "ajout des n colis", "recherche dict (1 id)",
                       "recherche linéaire (1 id)", "gain du dict"], lignes)


def bench_tri():
    lignes = []
    for n in TAILLES:
        colis = generer_colis(n, seed=SEED)
        rep = 5 if n <= 10_000 else 2
        t_fusion = chrono(lambda: tri_fusion(colis, cle=lambda c: c.poids), rep)
        t_sorted = chrono(lambda: sorted(colis, key=lambda c: c.poids), rep)
        # tri fusion sur données déjà triées -> l'optimisation "moitiés déjà en ordre" joue
        deja_tries = tri_fusion(colis, cle=lambda c: c.poids)
        t_trie = chrono(lambda: tri_fusion(deja_tries, cle=lambda c: c.poids), rep)
        lignes.append([f"{n:,}".replace(",", " "), fmt(t_fusion), fmt(t_sorted),
                       f"x{t_fusion / t_sorted:.0f}", fmt(t_trie)])
    return tableau_md(["n", "tri fusion maison", "sorted() (Timsort, C)",
                       "rapport", "tri fusion, déjà trié"], lignes)


def bench_chargement_n(capacite, rapide):
    lignes = []
    for n in TAILLES:
        if rapide and n == 100_000:
            continue
        colis = generer_colis(n, seed=SEED)
        res = {}
        t_dp = chrono(lambda: res.__setitem__("dp", sac_a_dos_dp(colis, capacite)))
        t_gl = chrono(lambda: res.__setitem__("gl", sac_a_dos_glouton(colis, capacite)))
        v_dp, v_gl = res["dp"].valeur_totale, res["gl"].valeur_totale
        memoire = n * (capacite + 1)  # octets du tableau de décisions (borne haute)
        lignes.append([f"{n:,}".replace(",", " "), fmt(t_dp), fmt(t_gl), v_dp, v_gl,
                       f"{100 * v_gl / v_dp:.2f} %", f"{memoire / 1e6:.1f} Mo"])
    return tableau_md(["n", "PD", "glouton", "valeur PD", "valeur glouton",
                       "glouton / optimum", "mémoire décisions"], lignes)


def bench_chargement_w(n, rapide):
    lignes = []
    colis = generer_colis(n, seed=SEED)
    capacites = [100, 1_000, 10_000] if rapide else [100, 1_000, 10_000, 50_000]
    for w in capacites:
        res = {}
        t_dp = chrono(lambda: res.__setitem__("dp", sac_a_dos_dp(colis, w)))
        t_gl = chrono(lambda: res.__setitem__("gl", sac_a_dos_glouton(colis, w)))
        v_dp, v_gl = res["dp"].valeur_totale, res["gl"].valeur_totale
        lignes.append([f"{w:,}".replace(",", " "), fmt(t_dp), fmt(t_gl), v_dp, v_gl,
                       f"{100 * v_gl / v_dp:.2f} %"])
    return tableau_md(["capacité W", "PD", "glouton", "valeur PD", "valeur glouton",
                       "glouton / optimum"], lignes)


def main():
    rapide = "--rapide" in sys.argv
    sections = []

    print("1/4 ajout + recherche...")
    sections.append("## 1. Ajout et recherche par identifiant\n\n"
                    "Temps de recherche = moyenne sur 200 recherches.\n\n" + bench_ajout_recherche())
    print("2/4 tri...")
    sections.append("## 2. Tri des colis (par poids)\n\n" + bench_tri())
    print("3/4 chargement, n variable...")
    sections.append("## 3. Chargement du camion, n variable (W = 500 kg)\n\n"
                    + bench_chargement_n(500, rapide))
    print("4/4 chargement, W variable...")
    sections.append("## 4. Chargement du camion, W variable (n = 1 000 colis)\n\n"
                    + bench_chargement_w(1_000, rapide))

    entete = (f"# Résultats du benchmark\n\nPython {sys.version.split()[0]}, "
              f"données aléatoires (seed {SEED}), poids 1-50 kg, valeur 1-100, priorité 1-5.\n")
    contenu = entete + "\n\n" + "\n\n".join(sections) + "\n"

    dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resultats")
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, "benchmark.md")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(contenu)
    print(f"-> écrit dans {chemin}")


if __name__ == "__main__":
    main()
