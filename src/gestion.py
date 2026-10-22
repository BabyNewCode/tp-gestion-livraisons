"""Gestion de la collection de colis.

Choix de structure : un dictionnaire id -> Colis.
Un dict Python est une table de hachage, donc :
  - ajout       : O(1) en moyenne
  - recherche   : O(1) en moyenne (au lieu de O(n) avec une simple liste)
  - espace      : O(n)
Depuis Python 3.7 le dict garde l'ordre d'insertion, donc on peut aussi
afficher les colis dans l'ordre où ils ont été ajoutés sans liste en plus.
"""

from .colis import Colis


class GestionColis:
    def __init__(self):
        self._colis = {}

    def ajouter(self, colis: Colis):
        """O(1) en moyenne. Refuse les identifiants en double."""
        if colis.id in self._colis:
            raise ValueError(f"un colis avec l'id {colis.id} existe déjà")
        self._colis[colis.id] = colis

    def ajouter_plusieurs(self, liste):
        for c in liste:
            self.ajouter(c)

    def rechercher(self, id_colis):
        """O(1) en moyenne : accès direct par hachage de la clé."""
        return self._colis.get(id_colis)

    def recherche_lineaire(self, id_colis):
        """Version naïve en O(n), gardée uniquement pour la comparer dans le benchmark."""
        for c in self._colis.values():
            if c.id == id_colis:
                return c
        return None

    def lister(self):
        """Tous les colis, dans l'ordre d'ajout. O(n) (copie dans une liste)."""
        return list(self._colis.values())

    def __len__(self):
        return len(self._colis)

    def __contains__(self, id_colis):
        return id_colis in self._colis


def colis_exemple():
    """Les colis donnés dans le sujet."""
    return [
        Colis(101, 8, 20, 2, "Paris"),
        Colis(102, 3, 10, 5, "Lille"),
        Colis(103, 12, 40, 1, "Lyon"),
        Colis(104, 5, 25, 4, "Paris"),
        Colis(105, 2, 15, 3, "Lille"),
    ]
