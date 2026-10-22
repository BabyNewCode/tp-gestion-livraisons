"""Génération de colis aléatoires pour tester à 100 / 1 000 / 10 000 / 100 000 colis."""

import random

from .colis import Colis, PRIORITE_MIN, PRIORITE_MAX

DESTINATIONS = ["Paris", "Lille", "Lyon", "Marseille", "Bordeaux", "Nantes", "Toulouse", "Strasbourg"]


def generer_colis(n, seed=None, id_depart=1000, poids_max=50, valeur_max=100):
    """Génère n colis avec des id uniques (consécutifs). O(n) en temps et en espace.
    Le seed permet de rejouer exactement les mêmes données (utile pour le benchmark)."""
    rng = random.Random(seed)
    return [
        Colis(
            id=id_depart + i,
            poids=rng.randint(1, poids_max),
            valeur=rng.randint(1, valeur_max),
            priorite=rng.randint(PRIORITE_MIN, PRIORITE_MAX),
            destination=rng.choice(DESTINATIONS),
        )
        for i in range(n)
    ]
