import random
import unittest

from src.tri import tri_fusion
from src.gestion import GestionColis, colis_exemple
from src.generateur import generer_colis


class TestTriFusion(unittest.TestCase):
    def test_cas_limites(self):
        self.assertEqual(tri_fusion([]), [])
        self.assertEqual(tri_fusion([7]), [7])
        self.assertEqual(tri_fusion([2, 1]), [1, 2])

    def test_comme_sorted(self):
        rng = random.Random(0)
        for n in (3, 10, 101, 1000):
            t = [rng.randint(0, 50) for _ in range(n)]
            self.assertEqual(tri_fusion(t), sorted(t))
            self.assertEqual(tri_fusion(t, decroissant=True), sorted(t, reverse=True))

    def test_ne_modifie_pas_l_original(self):
        t = [3, 1, 2]
        tri_fusion(t)
        self.assertEqual(t, [3, 1, 2])

    def test_stable(self):
        colis = generer_colis(500, seed=3)
        res = tri_fusion(colis, cle=lambda c: c.priorite)
        # même résultat que sorted (stable aussi) -> à priorité égale, l'ordre d'origine est gardé
        self.assertEqual(res, sorted(colis, key=lambda c: c.priorite))
        res_desc = tri_fusion(colis, cle=lambda c: c.priorite, decroissant=True)
        self.assertEqual(res_desc, sorted(colis, key=lambda c: c.priorite, reverse=True))


class TestTrierPar(unittest.TestCase):
    def setUp(self):
        self.g = GestionColis()
        self.g.ajouter_plusieurs(colis_exemple())

    def test_poids(self):
        self.assertEqual([c.id for c in self.g.trier_par("poids")], [105, 102, 104, 101, 103])

    def test_valeur(self):
        self.assertEqual([c.id for c in self.g.trier_par("valeur")], [103, 104, 101, 105, 102])

    def test_priorite(self):
        self.assertEqual([c.id for c in self.g.trier_par("priorite")], [102, 104, 105, 101, 103])

    def test_critere_inconnu(self):
        with self.assertRaises(ValueError):
            self.g.trier_par("couleur")


if __name__ == "__main__":
    unittest.main()
