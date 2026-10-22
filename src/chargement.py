"""Préparation du camion = problème du sac à dos 0/1.

On a n colis (poids p_i, gain g_i) et une capacité W. On veut choisir un sous-ensemble
qui maximise la somme des gains avec somme des poids <= W. Chaque colis est pris
entièrement ou pas du tout (on ne coupe pas un colis en deux).

Trois approches sont codées pour pouvoir les comparer :
  - programmation dynamique : OPTIMALE, O(n.W)      -> c'est celle qu'on utilise
  - glouton (ratio gain/poids) : rapide O(n log n) mais PAS toujours optimal
  - force brute : teste les 2^n combinaisons, sert seulement à vérifier la PD sur de petits cas

Le "gain" est par défaut la valeur du colis. On garde une fonction en paramètre
pour pouvoir y brancher la priorité ensuite sans réécrire les algos.
"""

from dataclasses import dataclass, field

from .tri import tri_fusion


def gain_valeur(colis):
    return colis.valeur


@dataclass
class Chargement:
    methode: str
    capacite: int
    colis: list = field(default_factory=list)

    @property
    def poids_total(self):
        return sum(c.poids for c in self.colis)

    @property
    def valeur_totale(self):
        return sum(c.valeur for c in self.colis)


def _total_gain(colis, gain):
    return sum(gain(c) for c in colis)


def sac_a_dos_dp(colis, capacite, gain=gain_valeur):
    """Programmation dynamique.

    meilleur[w] = meilleur gain atteignable avec une capacité w en n'utilisant que
    les colis déjà vus. Pour chaque colis i (poids p, gain g) :
        meilleur[w] = max(meilleur[w], meilleur[w - p] + g)   pour w de W jusqu'à p
    On parcourt w à l'envers pour que chaque colis ne soit compté qu'une fois
    (sinon on serait dans le sac à dos "non borné").

    Pour retrouver QUELS colis ont été pris, on note pour chaque colis les capacités
    où il a amélioré le résultat (pris[i][w] = 1), puis on remonte depuis w = W.

    Temps  : O(n.W)
    Espace : O(W) pour le tableau des gains + O(n.W) octets pour les décisions
             (bytearray = 1 octet par case, bien plus léger qu'une liste de listes d'int).
    """
    if capacite <= 0:
        return Chargement("programmation dynamique", capacite)

    # un colis plus lourd que le camion ne pourra jamais être pris : on l'écarte direct
    candidats = [c for c in colis if c.poids <= capacite]

    meilleur = [0] * (capacite + 1)
    pris = []
    for c in candidats:
        p, g = c.poids, gain(c)
        decision = bytearray(capacite + 1)
        for w in range(capacite, p - 1, -1):
            avec = meilleur[w - p] + g
            if avec > meilleur[w]:
                meilleur[w] = avec
                decision[w] = 1
        pris.append(decision)

    # reconstruction : on remonte les colis du dernier au premier
    choisis = []
    w = capacite
    for i in range(len(candidats) - 1, -1, -1):
        if pris[i][w]:
            choisis.append(candidats[i])
            w -= candidats[i].poids
    choisis.reverse()
    return Chargement("programmation dynamique", capacite, choisis)


def sac_a_dos_glouton(colis, capacite, gain=gain_valeur):
    """Glouton : on trie par ratio gain/poids décroissant et on prend tant que ça rentre.
    Temps O(n log n) (le tri), espace O(n).
    Optimal pour le sac à dos FRACTIONNAIRE, mais pas pour le 0/1 : un "bon" colis
    peut laisser un trou que des colis moins rentables auraient mieux rempli."""
    tries = tri_fusion(colis, cle=lambda c: gain(c) / c.poids, decroissant=True)
    choisis, restant = [], capacite
    for c in tries:
        if c.poids <= restant:
            choisis.append(c)
            restant -= c.poids
    return Chargement("glouton (ratio)", capacite, choisis)


def sac_a_dos_force_brute(colis, capacite, gain=gain_valeur, n_max=20):
    """Teste les 2^n sous-ensembles. Temps O(2^n . n), espace O(n).
    Inutilisable au-delà d'une vingtaine de colis, sert de référence pour les tests."""
    n = len(colis)
    if n > n_max:
        raise ValueError(f"force brute limitée à {n_max} colis (2^{n} combinaisons sinon)")
    meilleur_gain, meilleur_masque = 0, 0
    for masque in range(1 << n):
        poids = g = 0
        for i in range(n):
            if masque >> i & 1:
                poids += colis[i].poids
                g += gain(colis[i])
        if poids <= capacite and g > meilleur_gain:
            meilleur_gain, meilleur_masque = g, masque
    choisis = [colis[i] for i in range(n) if meilleur_masque >> i & 1]
    return Chargement("force brute", capacite, choisis)
