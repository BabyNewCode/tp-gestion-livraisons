import unittest

from src.colis import Colis
from src.chargement import sac_a_dos_dp, sac_a_dos_glouton, sac_a_dos_force_brute
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


if __name__ == "__main__":
    unittest.main()
