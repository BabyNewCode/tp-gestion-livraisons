import unittest

from src.colis import Colis
from src.chargement import (sac_a_dos_dp, sac_a_dos_glouton, sac_a_dos_force_brute,
                            gain_priorite, gain_valeur)
from src.generateur import generer_colis

# exemple du sujet (A, B, C, D -> ids 1, 2, 3, 4)
A = Colis(1, 8, 20, 5, "Paris")
B = Colis(2, 6, 25, 1, "Paris")
C = Colis(3, 5, 18, 4, "Paris")
D = Colis(4, 4, 14, 3, "Paris")
EXEMPLE = [A, B, C, D]


class TestSacADos(unittest.TestCase):
    def test_exemple_sujet_capacite_15(self):
        res = sac_a_dos_dp(EXEMPLE, 15)
        self.assertEqual(res.valeur_totale, 57)  # B + C + D
        self.assertEqual({c.id for c in res.colis}, {2, 3, 4})

    def test_glouton_pas_optimal(self):
        # capacité 9 : le glouton prend B (meilleur ratio) et il ne reste que 3 kg -> 25
        # alors que C + D = 9 kg pour 32
        self.assertEqual(sac_a_dos_glouton(EXEMPLE, 9).valeur_totale, 25)
        self.assertEqual(sac_a_dos_dp(EXEMPLE, 9).valeur_totale, 32)

    def test_cas_limites(self):
        self.assertEqual(sac_a_dos_dp([], 50).colis, [])
        self.assertEqual(sac_a_dos_dp(EXEMPLE, 0).colis, [])
        self.assertEqual(sac_a_dos_dp(EXEMPLE, 3).colis, [])  # tout est trop lourd
        self.assertEqual(sac_a_dos_dp(EXEMPLE, 100).valeur_totale, 77)  # tout rentre

    def test_dp_egale_force_brute(self):
        # la PD doit trouver exactement la même valeur que la force brute
        for seed in range(30):
            colis = generer_colis(12, seed=seed, poids_max=20)
            for cap in (0, 10, 25, 50, 80):
                dp = sac_a_dos_dp(colis, cap)
                fb = sac_a_dos_force_brute(colis, cap)
                self.assertEqual(dp.valeur_totale, fb.valeur_totale, f"seed={seed} cap={cap}")
                self.assertLessEqual(dp.poids_total, cap)

    def test_glouton_jamais_meilleur(self):
        for seed in range(30):
            colis = generer_colis(50, seed=seed)
            dp = sac_a_dos_dp(colis, 100)
            gl = sac_a_dos_glouton(colis, 100)
            self.assertLessEqual(gl.valeur_totale, dp.valeur_totale)
            self.assertLessEqual(gl.poids_total, 100)


class TestPriorite(unittest.TestCase):
    def test_formule(self):
        g = gain_priorite(alpha=1)
        self.assertEqual(g(B), 25)          # priorité 1 -> valeur inchangée
        self.assertEqual(g(A), 40)          # priorité 5 -> x2
        self.assertAlmostEqual(g(C), 31.5)  # priorité 4 -> x1.75

    def test_alpha_zero_comme_valeur(self):
        g = gain_priorite(alpha=0)
        for seed in range(10):
            colis = generer_colis(40, seed=seed)
            self.assertEqual(sac_a_dos_dp(colis, 120, g).valeur_totale,
                             sac_a_dos_dp(colis, 120, gain_valeur).valeur_totale)

    def test_exemple_sujet_capacite_13(self):
        # sans priorité : B + C (valeur 43) ; avec priorité : A + C (A est très urgent)
        sans = sac_a_dos_dp(EXEMPLE, 13)
        avec = sac_a_dos_dp(EXEMPLE, 13, gain_priorite(alpha=1))
        self.assertEqual({c.id for c in sans.colis}, {2, 3})
        self.assertEqual({c.id for c in avec.colis}, {1, 3})
        self.assertAlmostEqual(avec.score_total, 71.5)
        self.assertGreater(avec.priorite_moyenne, sans.priorite_moyenne)

    def test_dp_optimale_avec_priorite(self):
        g = gain_priorite(alpha=2)
        for seed in range(15):
            colis = generer_colis(12, seed=seed, poids_max=20)
            self.assertAlmostEqual(sac_a_dos_dp(colis, 40, g).score_total,
                                   sac_a_dos_force_brute(colis, 40, g).score_total)

    def test_alpha_negatif_refuse(self):
        with self.assertRaises(ValueError):
            gain_priorite(-1)


if __name__ == "__main__":
    unittest.main()
