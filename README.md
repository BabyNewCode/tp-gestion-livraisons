# TP - Gestion des livraisons

TP d'algorithmie comparative (M2). Le but : gérer une liste de colis (ajout, recherche, tris) et préparer le chargement d'un camion de capacité limitée en maximisant la valeur transportée, avec la possibilité de favoriser les colis urgents.

Le détail des choix algorithmiques est dans `rapport.pdf`. Ce README sert surtout à lancer le projet et à avoir les infos principales sous la main.

## Langage : Python 3

On a choisi Python parce que le sujet porte sur les choix d'algos et leurs complexités, pas sur la gestion mémoire. En Python on écrit vite, on teste vite (`unittest` est fourni de base) et le benchmark se fait avec `time.perf_counter` sans rien installer.

Le revers, c'est la lenteur : une boucle Python est bien plus lente que du C. Ça se voit dans le benchmark (notre tri fusion est ~15x plus lent que `sorted()` qui est écrit en C), mais les **complexités** restent les mêmes et c'est elles qu'on analyse.

Aucune bibliothèque externe, uniquement la bibliothèque standard. Testé avec Python 3.14 (devrait marcher à partir de 3.8).

## Lancer le projet

Toutes les commandes se lancent **depuis la racine du projet** :

```bash
# le programme (menu)
python -m src.main

# les tests (26 tests)
python -m unittest -v

# le benchmark (~1 min, écrit resultats/benchmark.md)
python -m src.benchmark
python -m src.benchmark --rapide   # sans les cas les plus longs
```

Au démarrage, les 5 colis de l'exemple du sujet sont chargés. L'option 8 du menu permet de générer 100, 1 000, 10 000 ou 100 000 colis aléatoires pour tester à plus grande échelle.

## Structure

```
src/
  colis.py        modèle Colis + affichage en tableau
  gestion.py      collection de colis (dict id -> colis), recherche, tris
  tri.py          tri fusion codé à la main
  chargement.py   sac à dos : prog dynamique, glouton, force brute + règle de priorité
  generateur.py   génération de colis aléatoires (reproductible avec un seed)
  benchmark.py    mesures de temps de 100 à 100 000 colis
  main.py         menu console
tests/            tests unitaires (gestion, tri, chargement)
resultats/        sortie du benchmark
rapport.pdf       rapport (choix algorithmiques)
```

## Ce qu'on a choisi, en bref

| Opération | Solution | Temps | Espace |
|---|---|---|---|
| Ajouter un colis | insertion dans un dict (table de hachage) | O(1) moyen | O(n) au total |
| Rechercher par id | accès direct au dict | O(1) moyen | O(1) |
| Afficher trié (poids / valeur / priorité) | tri fusion maison, stable | O(n log n) | O(n) |
| Préparer le camion | sac à dos 0/1 en programmation dynamique | O(n·W) | O(W) + O(n·W) octets |
| (comparaison) | glouton sur le ratio valeur/poids | O(n log n) | O(n) |
| (vérification) | force brute, n ≤ 20 | O(2ⁿ·n) | O(n) |

W = capacité du camion en kg. Les poids sont donc des entiers, c'est nécessaire pour la programmation dynamique.

**Chargement optimal.** La programmation dynamique donne toujours la meilleure valeur possible (vérifié dans les tests contre la force brute sur 150 cas aléatoires). Le glouton va plus vite mais peut se tromper : sur l'exemple du sujet avec 9 kg, il prend B (meilleur ratio) et obtient 25, alors que C + D tiennent dans 9 kg pour 32.

**Priorité.** On optimise un score au lieu de la valeur brute :

```
score = valeur × (1 + α × (priorité − 1) / 4)
```

Priorité 1 → valeur normale, priorité 5 → valeur × (1 + α). Avec α = 0 on ignore la priorité, avec α = 1 un colis très urgent compte double. On a pris une règle multiplicative pour qu'un colis urgent mais sans valeur ne passe pas devant tout le reste. On considère que **5 = le plus urgent** (le sujet ne le précise pas).

## Résultats du benchmark (extrait)

Le détail complet est dans [resultats/benchmark.md](resultats/benchmark.md).

| n | recherche dict | recherche linéaire | tri fusion | PD (W = 500) |
|---|---|---|---|---|
| 100 | 0,1 µs | 1,7 µs | 0,1 ms | 5,5 ms |
| 1 000 | 0,1 µs | 13,6 µs | 2,0 ms | 37 ms |
| 10 000 | 0,1 µs | 148 µs | 26 ms | 354 ms |
| 100 000 | 0,1 µs | 1,8 ms | 353 ms | 3,6 s |

La recherche reste constante quel que soit n, ce qui confirme le choix du dict. Le chargement est l'opération la plus coûteuse : il grandit avec n **et** avec la capacité W (6,3 s pour 1 000 colis et W = 50 000). Le menu prévient avant de lancer une PD trop grosse.

## Limites connues

- La PD devient lourde quand n·W est grand (temps et mémoire). Pistes : passer au glouton au-delà d'un seuil (il atteint 99,9 à 100 % de l'optimum sur nos données aléatoires), compter les poids par tranches de 5 kg, ou borner W par le poids total des colis.
- Les tris sont recalculés à chaque affichage. Un cache invalidé à l'ajout éviterait de retrier pour rien.
- Les données ne sont pas sauvegardées entre deux lancements (le sujet ne le demandait pas).
