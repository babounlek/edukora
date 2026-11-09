"""Ressemblance de textes par séquences de mots (stdlib seule, sans Django).

Sert à comparer un PDF candidat au contenu DÉJÀ en base : le contrôle de doublons de `qualifier` ne regarde que les
fichiers des zones de dépôt, il ne voit donc pas une épreuve déjà ingérée (par exemple le sujet d'un collège présenté
comme le sujet national). Deux mesures complémentaires, en proportion de séquences communes :
  - `couvert_candidat` : part du candidat retrouvée dans le contenu de la base ;
  - `couvert_base`     : part du contenu de la base retrouvée dans le candidat.
Une épreuve identique donne deux valeurs proches de 1. Une épreuve qui ne fait que partager des formules de consigne
reste sous 0,15.
"""
import re
import unicodedata

LONGUEUR = 4          # mots par séquence
SEUIL_PLANCHER = 8    # moins de séquences communes : bruit, jamais retenu
SEUIL_DOUBLON = 0.5   # l'une des deux parts au moins : doublon probable
SEUIL_A_VERIFIER = 0.25


def mots(texte):
    """Minuscules, sans accents, lettres et chiffres seulement."""
    texte = unicodedata.normalize("NFD", str(texte or "").lower())
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", texte).split()


def sequences(texte, longueur=LONGUEUR):
    m = mots(texte)
    return {" ".join(m[i:i + longueur]) for i in range(len(m) - longueur + 1)}


def comparer(sequences_candidat, sequences_base):
    """(couvert_candidat, couvert_base, communes) ; (0, 0, 0) si l'un des deux est vide."""
    if not sequences_candidat or not sequences_base:
        return 0.0, 0.0, 0
    communes = len(sequences_candidat & sequences_base)
    return (round(communes / len(sequences_candidat), 2), round(communes / len(sequences_base), 2), communes)


def niveau(couvert_candidat, couvert_base, communes):
    """DOUBLON_BASE | A_VERIFIER | AUCUN, jamais une décision : l'humain tranche."""
    if communes < SEUIL_PLANCHER:
        return "AUCUN"
    haut = max(couvert_candidat, couvert_base)
    if haut >= SEUIL_DOUBLON:
        return "DOUBLON_BASE"
    if haut >= SEUIL_A_VERIFIER:
        return "A_VERIFIER"
    return "AUCUN"
