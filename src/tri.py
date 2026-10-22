"""Tri fusion (merge sort) codé à la main.

Pourquoi le tri fusion :
  - O(n log n) dans TOUS les cas (pas de pire cas en O(n²) comme le tri rapide)
  - stable : deux colis de même poids gardent leur ordre relatif, ce qui permet
    d'enchaîner des tris (ex : par destination puis par priorité)
  - simple à expliquer et à prouver

Complexité :
  - temps  : O(n log n). log n niveaux de découpe, chaque niveau fait O(n) comparaisons à la fusion
  - espace : O(n) pour le tampon de fusion + O(log n) pour la pile de récursion

Remarque : sorted() de Python utilise Timsort (fusion + insertion, aussi stable et O(n log n)),
mais en C donc bien plus rapide. On s'en sert uniquement comme référence dans le benchmark.
"""


def tri_fusion(elements, cle=lambda x: x, decroissant=False):
    """Renvoie une NOUVELLE liste triée selon cle(x). La liste d'origine n'est pas modifiée."""
    res = list(elements)
    if len(res) < 2:
        return res
    tampon = [None] * len(res)  # alloué une seule fois et réutilisé à chaque fusion
    cles = [cle(x) for x in res]  # on calcule les clés une seule fois (n appels au lieu de n log n)
    tampon_cles = [None] * len(res)
    _tri(res, cles, tampon, tampon_cles, 0, len(res), decroissant)
    return res


def _tri(t, k, tmp, tmp_k, debut, fin, decroissant):
    """Trie t[debut:fin] (et k en parallèle)."""
    if fin - debut < 2:
        return
    milieu = (debut + fin) // 2
    _tri(t, k, tmp, tmp_k, debut, milieu, decroissant)
    _tri(t, k, tmp, tmp_k, milieu, fin, decroissant)
    # petite optimisation : si les deux moitiés sont déjà dans l'ordre, rien à fusionner
    if (k[milieu - 1] >= k[milieu]) if decroissant else (k[milieu - 1] <= k[milieu]):
        return
    _fusion(t, k, tmp, tmp_k, debut, milieu, fin, decroissant)


def _fusion(t, k, tmp, tmp_k, debut, milieu, fin, decroissant):
    i, j, pos = debut, milieu, debut
    while i < milieu and j < fin:
        # on prend à gauche en cas d'égalité -> c'est ça qui rend le tri stable
        if (k[i] >= k[j]) if decroissant else (k[i] <= k[j]):
            tmp[pos], tmp_k[pos] = t[i], k[i]
            i += 1
        else:
            tmp[pos], tmp_k[pos] = t[j], k[j]
            j += 1
        pos += 1
    # on recopie ce qui reste d'un des deux côtés
    while i < milieu:
        tmp[pos], tmp_k[pos] = t[i], k[i]
        i += 1
        pos += 1
    while j < fin:
        tmp[pos], tmp_k[pos] = t[j], k[j]
        j += 1
        pos += 1
    t[debut:fin] = tmp[debut:fin]
    k[debut:fin] = tmp_k[debut:fin]
