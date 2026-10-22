# Résultats du benchmark

Python 3.14.7, données aléatoires (seed 42), poids 1-50 kg, valeur 1-100, priorité 1-5.


## 1. Ajout et recherche par identifiant

Temps de recherche = moyenne sur 200 recherches.

| n | ajout des n colis | recherche dict (1 id) | recherche linéaire (1 id) | gain du dict |
|---|---|---|---|---|
| 100 | 11.5 µs | 0.1 µs | 1.7 µs | x21 |
| 1 000 | 96.7 µs | 0.1 µs | 13.6 µs | x151 |
| 10 000 | 1.2 ms | 0.1 µs | 148.2 µs | x1 656 |
| 100 000 | 14.8 ms | 0.1 µs | 1.8 ms | x19 773 |

## 2. Tri des colis (par poids)

| n | tri fusion maison | sorted() (Timsort, C) | rapport | tri fusion, déjà trié |
|---|---|---|---|---|
| 100 | 113.0 µs | 7.6 µs | x15 | 27.4 µs |
| 1 000 | 2.0 ms | 126.4 µs | x16 | 252.0 µs |
| 10 000 | 25.7 ms | 1.8 ms | x14 | 3.1 ms |
| 100 000 | 353.4 ms | 19.7 ms | x18 | 41.4 ms |

## 3. Chargement du camion, n variable (W = 500 kg)

| n | PD | glouton | valeur PD | valeur glouton | glouton / optimum | mémoire décisions |
|---|---|---|---|---|---|---|
| 100 | 5.5 ms | 191.1 µs | 2631 | 2631 | 100.00 % | 0.1 Mo |
| 1 000 | 36.8 ms | 2.5 ms | 7870 | 7859 | 99.86 % | 0.5 Mo |
| 10 000 | 353.5 ms | 28.6 ms | 21911 | 21911 | 100.00 % | 5.0 Mo |
| 100 000 | 3.59 s | 405.9 ms | 44081 | 44081 | 100.00 % | 50.1 Mo |

## 4. Chargement du camion, W variable (n = 1 000 colis)

| capacité W | PD | glouton | valeur PD | valeur glouton | glouton / optimum |
|---|---|---|---|---|---|
| 100 | 5.8 ms | 2.1 ms | 3200 | 3200 | 100.00 % |
| 1 000 | 84.6 ms | 1.8 ms | 11500 | 11497 | 99.97 % |
| 10 000 | 1.10 s | 2.8 ms | 36028 | 36027 | 100.00 % |
| 50 000 | 6.31 s | 2.0 ms | 51696 | 51696 | 100.00 % |
