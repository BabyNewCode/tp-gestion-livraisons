"""Programme principal : menu console pour tester tout le système.

Lancement depuis la racine du projet :
    python -m src.main
"""

import sys

from .chargement import sac_a_dos_dp, sac_a_dos_glouton, gain_priorite, gain_valeur
from .colis import Colis, tableau, PRIORITE_MIN, PRIORITE_MAX
from .gestion import GestionColis, colis_exemple
from .generateur import generer_colis

LIMITE_AFFICHAGE = 20
# au-delà de n*W cases, la PD commence à prendre plusieurs secondes (cf. benchmark)
SEUIL_ALERTE_PD = 50_000_000

MENU = """
===== GESTION DES LIVRAISONS =====
1. Afficher les colis
2. Ajouter un colis
3. Rechercher un colis
4. Organiser les colis
5. Préparer un camion
6. Afficher le chargement
7. Afficher les statistiques
8. Charger un jeu de données
0. Quitter"""


# --- petites fonctions de saisie ---------------------------------------------

def demander_entier(message, mini=None, maxi=None, defaut=None):
    while True:
        saisie = input(message).strip()
        if saisie == "" and defaut is not None:
            return defaut
        try:
            val = int(saisie)
        except ValueError:
            print("  -> il faut un nombre entier")
            continue
        if (mini is not None and val < mini) or (maxi is not None and val > maxi):
            print(f"  -> valeur attendue entre {mini} et {maxi if maxi is not None else '...'}")
            continue
        return val


def demander_float(message, mini=0.0, defaut=None):
    while True:
        saisie = input(message).strip().replace(",", ".")
        if saisie == "" and defaut is not None:
            return defaut
        try:
            val = float(saisie)
            if val >= mini:
                return val
        except ValueError:
            pass
        print(f"  -> nombre >= {mini} attendu")


def demander_oui_non(message, defaut=False):
    saisie = input(message).strip().lower()
    if saisie == "":
        return defaut
    return saisie in ("o", "oui", "y", "yes")


# --- actions du menu ---------------------------------------------------------

class Application:
    def __init__(self):
        self.gestion = GestionColis()
        self.gestion.ajouter_plusieurs(colis_exemple())
        self.chargement = None

    def afficher_colis(self):
        colis = self.gestion.lister()
        if not colis:
            print("Aucun colis.")
            return
        limite = None
        if len(colis) > LIMITE_AFFICHAGE and not demander_oui_non(
                f"{len(colis)} colis, tout afficher ? (o/N) "):
            limite = LIMITE_AFFICHAGE
        print(tableau(colis, limite))

    def ajouter_colis(self):
        id_colis = demander_entier("Identifiant : ", mini=0)
        if id_colis in self.gestion:
            print(f"Le colis {id_colis} existe déjà.")
            return
        poids = demander_entier("Poids (kg) : ", mini=1)
        valeur = demander_entier("Valeur : ", mini=0)
        priorite = demander_entier(f"Priorité ({PRIORITE_MIN}-{PRIORITE_MAX}, {PRIORITE_MAX} = urgent) : ",
                                   mini=PRIORITE_MIN, maxi=PRIORITE_MAX)
        destination = input("Destination : ").strip() or "Inconnue"
        self.gestion.ajouter(Colis(id_colis, poids, valeur, priorite, destination))
        print(f"Colis {id_colis} ajouté ({len(self.gestion)} colis au total).")

    def rechercher_colis(self):
        id_colis = demander_entier("Identifiant recherché : ")
        c = self.gestion.rechercher(id_colis)
        if c is None:
            print(f"Aucun colis avec l'id {id_colis}.")
        else:
            print(tableau([c]))

    def organiser_colis(self):
        print("Trier par : 1. poids   2. valeur   3. priorité")
        choix = demander_entier("Choix : ", mini=1, maxi=3)
        critere = {1: "poids", 2: "valeur", 3: "priorite"}[choix]
        sens_defaut = "croissant" if critere == "poids" else "décroissant"
        inverser = demander_oui_non(f"Ordre {sens_defaut} par défaut, inverser ? (o/N) ")
        decroissant = (critere != "poids") != inverser
        colis = self.gestion.trier_par(critere, decroissant)
        print(tableau(colis, LIMITE_AFFICHAGE if len(colis) > LIMITE_AFFICHAGE else None))

    def preparer_camion(self):
        if len(self.gestion) == 0:
            print("Aucun colis à charger.")
            return
        capacite = demander_entier("Capacité du camion (kg) [50] : ", mini=1, defaut=50)
        print("Méthode : 1. optimale (programmation dynamique)   2. rapide (glouton)")
        methode = demander_entier("Choix [1] : ", mini=1, maxi=2, defaut=1)
        gain = gain_valeur
        if demander_oui_non("Tenir compte de la priorité ? (o/N) "):
            alpha = demander_float("Poids de la priorité alpha (0 = ignorée, 1 = urgent compte double) [1] : ",
                                   defaut=1.0)
            gain = gain_priorite(alpha)

        colis = self.gestion.lister()
        if methode == 1 and len(colis) * capacite > SEUIL_ALERTE_PD:
            if not demander_oui_non(f"n x W = {len(colis) * capacite:,} : la PD risque d'être longue "
                                    "et gourmande en mémoire. Continuer ? (o/N) "):
                return
        algo = sac_a_dos_dp if methode == 1 else sac_a_dos_glouton
        self.chargement = algo(colis, capacite, gain)
        self.afficher_resume_chargement()

    def afficher_resume_chargement(self):
        ch = self.chargement
        print(f"\nMéthode : {ch.methode}")
        print(f"Colis chargés : {len(ch.colis)}")
        print(f"Poids : {ch.poids_total} / {ch.capacite} kg ({100 * ch.poids_total / ch.capacite:.1f} %)")
        print(f"Valeur transportée : {ch.valeur_totale}")
        if ch.gain is not gain_valeur:
            print(f"Score (valeur pondérée par la priorité) : {ch.score_total:.1f}")

    def afficher_chargement(self):
        if self.chargement is None:
            print("Aucun camion préparé (option 5).")
            return
        self.afficher_resume_chargement()
        print()
        colis = self.chargement.colis
        print(tableau(colis, LIMITE_AFFICHAGE if len(colis) > LIMITE_AFFICHAGE else None))

    def afficher_statistiques(self):
        colis = self.gestion.lister()
        n = len(colis)
        print(f"\nNombre de colis : {n}")
        if n == 0:
            return
        poids = sum(c.poids for c in colis)
        valeur = sum(c.valeur for c in colis)
        print(f"Poids total : {poids} kg (moyenne {poids / n:.1f} kg)")
        print(f"Valeur totale : {valeur} (moyenne {valeur / n:.1f})")

        # comptages en un seul passage, O(n)
        par_priorite = dict.fromkeys(range(PRIORITE_MAX, PRIORITE_MIN - 1, -1), 0)
        par_destination = {}
        for c in colis:
            par_priorite[c.priorite] += 1
            par_destination[c.destination] = par_destination.get(c.destination, 0) + 1
        print("Répartition par priorité : "
              + ", ".join(f"P{p}: {nb}" for p, nb in par_priorite.items()))
        print("Répartition par destination : "
              + ", ".join(f"{d}: {nb}" for d, nb in sorted(par_destination.items())))

        if self.chargement is not None:
            ch = self.chargement
            print(f"\nDernier chargement ({ch.methode}) :")
            print(f"  {len(ch.colis)}/{n} colis chargés, remplissage {100 * ch.poids_total / ch.capacite:.1f} %")
            part = f" ({100 * ch.valeur_totale / valeur:.1f} % de la valeur totale)" if valeur else ""
            print(f"  valeur chargée {ch.valeur_totale}{part}")
            print(f"  priorité moyenne chargée {ch.priorite_moyenne:.2f} "
                  f"(contre {sum(c.priorite for c in colis) / n:.2f} sur tous les colis)")

    def charger_donnees(self):
        print("1. Exemple du sujet (5 colis)   2. Générer des colis aléatoires")
        choix = demander_entier("Choix : ", mini=1, maxi=2)
        if choix == 1:
            liste = colis_exemple()
        else:
            n = demander_entier("Nombre de colis (ex : 100, 1000, 10000, 100000) : ", mini=1)
            seed = demander_entier("Seed (Entrée = 42) : ", defaut=42)
            liste = generer_colis(n, seed=seed)
        self.gestion = GestionColis()
        self.gestion.ajouter_plusieurs(liste)
        self.chargement = None
        print(f"{len(self.gestion)} colis chargés (les anciens ont été remplacés).")

    def lancer(self):
        actions = {
            1: self.afficher_colis,
            2: self.ajouter_colis,
            3: self.rechercher_colis,
            4: self.organiser_colis,
            5: self.preparer_camion,
            6: self.afficher_chargement,
            7: self.afficher_statistiques,
            8: self.charger_donnees,
        }
        while True:
            print(MENU)
            choix = demander_entier("Choix : ", mini=0, maxi=8)
            if choix == 0:
                print("Au revoir !")
                return
            print()
            actions[choix]()


def main():
    # pour que les accents s'affichent correctement dans la console Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        Application().lancer()
    except (KeyboardInterrupt, EOFError):
        print("\nAu revoir !")


if __name__ == "__main__":
    main()
