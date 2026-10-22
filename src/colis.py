"""Modèle d'un colis."""

from dataclasses import dataclass

PRIORITE_MIN = 1
PRIORITE_MAX = 5  # 5 = le plus urgent


@dataclass
class Colis:
    id: int
    poids: int      # en kg, entier (nécessaire pour le sac à dos en prog dynamique)
    valeur: int
    priorite: int   # de 1 (pas pressé) à 5 (très urgent)
    destination: str

    def __post_init__(self):
        if self.poids <= 0:
            raise ValueError("le poids doit être > 0")
        if self.valeur < 0:
            raise ValueError("la valeur ne peut pas être négative")
        if not PRIORITE_MIN <= self.priorite <= PRIORITE_MAX:
            raise ValueError(f"la priorité doit être entre {PRIORITE_MIN} et {PRIORITE_MAX}")

    def ligne(self):
        return f"{self.id:>8} {self.poids:>6} {self.valeur:>7} {self.priorite:>9}   {self.destination}"


ENTETE = f"{'ID':>8} {'Poids':>6} {'Valeur':>7} {'Priorité':>9}   Destination"


def tableau(colis, limite=None):
    """Renvoie la liste de colis sous forme de tableau texte.
    `limite` permet de ne pas afficher 100 000 lignes dans le terminal."""
    lignes = [ENTETE, "-" * len(ENTETE)]
    a_afficher = colis if limite is None else colis[:limite]
    lignes += [c.ligne() for c in a_afficher]
    if limite is not None and len(colis) > limite:
        lignes.append(f"... ({len(colis) - limite} colis de plus)")
    return "\n".join(lignes)
