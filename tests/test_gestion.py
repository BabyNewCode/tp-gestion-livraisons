import unittest

from src.colis import Colis, tableau
from src.gestion import GestionColis, colis_exemple
from src.generateur import generer_colis


class TestGestion(unittest.TestCase):
    def setUp(self):
        self.g = GestionColis()
        self.g.ajouter_plusieurs(colis_exemple())

    def test_ajout_et_taille(self):
        self.assertEqual(len(self.g), 5)
        self.g.ajouter(Colis(200, 1, 1, 1, "Nantes"))
        self.assertEqual(len(self.g), 6)

    def test_doublon_refuse(self):
        with self.assertRaises(ValueError):
            self.g.ajouter(Colis(101, 1, 1, 1, "Paris"))

    def test_recherche(self):
        self.assertEqual(self.g.rechercher(103).destination, "Lyon")
        self.assertIsNone(self.g.rechercher(999))

    def test_recherche_lineaire_meme_resultat(self):
        for id_ in (101, 105, 999):
            self.assertEqual(self.g.rechercher(id_), self.g.recherche_lineaire(id_))

    def test_ordre_ajout(self):
        self.assertEqual([c.id for c in self.g.lister()], [101, 102, 103, 104, 105])

    def test_colis_invalides(self):
        with self.assertRaises(ValueError):
            Colis(1, 0, 10, 3, "Paris")
        with self.assertRaises(ValueError):
            Colis(1, 5, 10, 6, "Paris")

    def test_generateur(self):
        liste = generer_colis(1000, seed=42)
        self.assertEqual(len({c.id for c in liste}), 1000)
        self.assertEqual(liste, generer_colis(1000, seed=42))  # reproductible

    def test_tableau_limite(self):
        texte = tableau(generer_colis(50, seed=1), limite=10)
        self.assertIn("40 colis de plus", texte)


if __name__ == "__main__":
    unittest.main()
