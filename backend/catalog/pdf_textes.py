"""
Textes des PDF (sujet d'épreuve, fiche d'exercices, fiche de quiz, épreuve inédite) dans la langue du
contenu : un PDF du GCE est entièrement en anglais, celui d'un BEPC, d'un Probatoire ou d'un BAC en
français. Le contenu lui-même (énoncés, corrigés) est déjà dans sa langue ; ce module ne porte que
l'habillage - bandeau, accroche, légendes, mentions - que les gabarits et les générateurs
insèrent autour.

La langue est celle du CONTENU (`Subject.langue`, à défaut celle du cursus), jamais celle de l'élève
qui télécharge : un PDF circule hors plateforme, un sujet du GCE reste en anglais même s'il est ouvert
depuis une interface française.

    tx = textes_pdf(langue_du_contenu(subject=lesson.subject), site=settings.SITE_NAME)
    ... {{ tx.cta_titre }} ...
"""
import re

from .models import Langue

TEXTES = {
    "fr": {
        # Commun
        "scan_me": "Scanne-moi",
        "titre_corrige": "Corrigé",
        "un_repetiteur": "un répétiteur",
        # Sujet d'épreuve (catalog)
        "sujet_gratuit": "Sujet gratuit",
        "sujet_cta_titre": "Envie de vérifier tes réponses ?",
        "sujet_cta_corps": (
            "La correction complète de cette épreuve, avec la méthode expliquée pas à pas, est disponible sur {site} : "
            "15 000 FCFA par enfant jusqu'à l'examen, 12 000 FCFA pour chaque enfant supplémentaire de la même famille."
        ),
        "sujet_cta_lien": "Voir la correction",
        "sujet_qr_alt": "QR code vers la correction",
        "sujet_note_pied": "Sujet en libre accès, à partager. La correction reste réservée aux abonnés.",
        "meta_session": "Session {annee}",
        "meta_duree": "Durée : {valeur}",
        "meta_coefficient": "Coefficient : {valeur}",
        "meta_bareme": "Barème : {valeur} points",
        "meta_duree_min": "Durée : {valeur} min",
        "origines": {},
        # Fiche d'exercices (répétiteur)
        "fiche_brand": "Fiche d'exercices",
        "fiche_brand_corrige": "Corrigé (usage répétiteur)",
        "fiche_cta_titre": "Envie de plus d'exercices comme ceux-ci ?",
        "fiche_cta_corps": "Cours, corrigés d'annales et quiz pour le BEPC, le Probatoire et le BAC - sur {site}.",
        "fiche_note_pied": "Fiche préparée par {prepared_by}",
        "fiche_reserve": "Corrigé réservé à l'usage personnel de {prepared_by} - à ne pas distribuer aux élèves.",
        "fiche_suite_titre": "Prêt(e) pour la prochaine fiche ?",
        "fiche_suite_corps": "Génère une nouvelle fiche d'exercices en quelques secondes sur {site}.",
        "fiche_qr_alt_site": "QR code vers {site}",
        "fiche_qr_alt_outil": "QR code vers l'outil Fiches",
        # Fiche de quiz
        "quiz_brand": "Fiche de quiz",
        "quiz_brand_corrige": "Correction",
        "quiz_cta_titre": "Continue à t'entraîner",
        "quiz_cta_corps": "Refais un quiz en quelques secondes sur {site}.",
        "quiz_qr_alt": "QR code vers le quiz",
        "voir_cours": "Voir le cours complet →",
        # Épreuve inédite
        "inedite_brand": "Sujet - Épreuve inédite",
        "inedite_reserve": (
            "Document réservé aux abonnés Épreuves Inédites de {site} - le partage de ce document est une "
            "violation des conditions d'utilisation."
        ),
        "inedite_cta_titre": "Prêt(e) à passer l'épreuve ?",
        "inedite_cta_corps": "Lance ta tentative chronométrée et accède à la correction directement sur {site}.",
        "inedite_qr_alt": "QR code vers l'épreuve",
        # Cours (version « libre » : sans les exercices d'application, payants ; version « complète » : abonné)
        "cours_brand": "Cours",
        "cours_libre_cta_titre": "Les exercices d'application t'attendent",
        "cours_libre_cta_corps": (
            "Ce PDF contient le cours. Les exercices d'application, avec leurs solutions détaillées pas à pas, "
            "sont réservés aux abonnés de {site}."
        ),
        "cours_libre_cta_lien": "Voir les exercices",
        "cours_libre_note_pied": "Cours en libre accès, à partager. Les exercices d'application sont réservés aux abonnés.",
        "cours_complet_cta_titre": "Retrouve ce cours en ligne",
        "cours_complet_cta_corps": "Lis la version en ligne, marque ce que tu as compris et entraîne-toi avec le quiz sur {site}.",
        "cours_complet_cta_lien": "Ouvrir le cours",
        "cours_complet_note_pied": "Les exercices d'application sont réservés aux abonnés : merci de ne pas diffuser ce document.",
        "cours_qr_alt": "QR code vers le cours",
    },
    "en": {
        "scan_me": "Scan me",
        "titre_corrige": "Solution",
        "un_repetiteur": "a tutor",
        "sujet_gratuit": "Free paper",
        "sujet_cta_titre": "Want to check your answers?",
        "sujet_cta_corps": (
            "The full correction of this paper, with the method explained step by step, is available on {site}: "
            "15,000 FCFA per child until the exam, 12,000 FCFA for each additional child in the same family."
        ),
        "sujet_cta_lien": "View the correction",
        "sujet_qr_alt": "QR code to the correction",
        "sujet_note_pied": "Free-access paper, feel free to share. The correction is for subscribers only.",
        "meta_session": "Session {annee}",
        "meta_duree": "Duration: {valeur}",
        "meta_coefficient": "Coefficient: {valeur}",
        "meta_bareme": "Marks: {valeur}",
        "meta_duree_min": "Duration: {valeur} min",
        "origines": {
            "BLANC": "Mock exam",
            "SUJET_ZERO": "Specimen paper",
            "ETABLISSEMENT": "School paper",
            "AUTRE": "Other",
        },
        "fiche_brand": "Exercise sheet",
        "fiche_brand_corrige": "Solutions (tutor's copy)",
        "fiche_cta_titre": "Want more exercises like these?",
        "fiche_cta_corps": "Lessons, past paper solutions and quizzes for the GCE O Level and A Level - on {site}.",
        "fiche_note_pied": "Sheet prepared by {prepared_by}",
        "fiche_reserve": "Solutions for {prepared_by}'s personal use only - not to be handed out to students.",
        "fiche_suite_titre": "Ready for the next sheet?",
        "fiche_suite_corps": "Generate a new exercise sheet in seconds on {site}.",
        "fiche_qr_alt_site": "QR code to {site}",
        "fiche_qr_alt_outil": "QR code to the Sheets tool",
        "quiz_brand": "Quiz sheet",
        "quiz_brand_corrige": "Solutions",
        "quiz_cta_titre": "Keep practising",
        "quiz_cta_corps": "Take another quiz in seconds on {site}.",
        "quiz_qr_alt": "QR code to the quiz",
        "voir_cours": "View the full lesson →",
        "inedite_brand": "Paper - Original practice paper",
        "inedite_reserve": (
            "Document reserved for {site} Original Papers subscribers - sharing this document is a "
            "breach of the terms of use."
        ),
        "inedite_cta_titre": "Ready to sit the paper?",
        "inedite_cta_corps": "Start your timed attempt and access the correction directly on {site}.",
        "inedite_qr_alt": "QR code to the paper",
        "cours_brand": "Lesson",
        "cours_libre_cta_titre": "The practice exercises are waiting for you",
        "cours_libre_cta_corps": (
            "This PDF contains the lesson. The practice exercises, with their step-by-step solutions, "
            "are for {site} subscribers."
        ),
        "cours_libre_cta_lien": "See the exercises",
        "cours_libre_note_pied": "Free-access lesson, feel free to share. The practice exercises are for subscribers only.",
        "cours_complet_cta_titre": "Find this lesson online",
        "cours_complet_cta_corps": "Read the online version, mark what you have understood and practise with the quiz on {site}.",
        "cours_complet_cta_lien": "Open the lesson",
        "cours_complet_note_pied": "The practice exercises are for subscribers only: please do not share this document.",
        "cours_qr_alt": "QR code to the lesson",
    },
}


def langue_du_contenu(subject=None, cursus=None):
    """« en » pour un contenu du sous-système anglophone (matière GCE, à défaut cursus GCE), « fr » sinon."""
    if subject is not None and getattr(subject, "langue", None):
        return subject.langue
    if cursus is not None:
        return cursus.langue
    return Langue.FR


def textes_pdf(langue, **variables):
    """Les textes d'un PDF dans `langue`, `{variable}` remplacées. Les valeurs qui n'en portent pas sont
    laissées telles quelles ; une langue inconnue retombe sur le français."""
    textes = TEXTES.get(langue, TEXTES["fr"])
    rendu = {}
    for cle, valeur in textes.items():
        if isinstance(valeur, str):
            for nom, contenu in variables.items():
                valeur = valeur.replace("{" + nom + "}", str(contenu))
        rendu[cle] = valeur
    rendu["langue"] = langue if langue in TEXTES else "fr"
    return rendu


# Noms anglais des pays (le serveur ne connaît que le libellé français) : le bandeau d'un PDF du GCE
# dit « Cameroon », pas « Cameroun ». Un code absent retombe sur le libellé du serveur.
PAYS_EN = {
    "CM": "Cameroon", "SN": "Senegal", "CI": "Côte d'Ivoire", "BJ": "Benin", "TG": "Togo", "GA": "Gabon",
    "CG": "Congo", "CD": "DR Congo", "ML": "Mali", "BF": "Burkina Faso", "NE": "Niger", "TD": "Chad",
    "GN": "Guinea", "MG": "Madagascar", "CF": "Central African Republic", "GQ": "Equatorial Guinea",
    "BI": "Burundi", "RW": "Rwanda", "DJ": "Djibouti", "KM": "Comoros", "MR": "Mauritania",
    "MA": "Morocco", "DZ": "Algeria", "TN": "Tunisia", "HT": "Haiti",
}


def nom_pays(code, libelle, langue):
    """Le nom du pays dans la langue du PDF."""
    if langue == "en":
        return PAYS_EN.get((code or "").upper(), libelle)
    return libelle


# Repères de structure que l'ingestion a écrits en français dans le contenu du GCE (« **Exercice 3 (6 points)** »,
# « ### Rappel de méthode ») : le contenu est en anglais, pas ces repères. Réécrits à l'impression, sans toucher
# aux données ni à l'affichage du site.
_EXERCICE_RE = re.compile(r"^\*\*Exercice\b(.*)$", re.MULTILINE)
_POINTS_PARENTHESE_RE = re.compile(r"\(\s*(\d+(?:[.,]\d+)?)\s*(?:points?|pts?)\s*\)", re.IGNORECASE)
_POINTS_CROCHETS_RE = re.compile(r"\*\[\s*(\d+(?:[.,]\d+)?)\s*(?:points?|pts?)\s*\]\*", re.IGNORECASE)
_TITRES_EN = {
    "Corrigé": "Solution",
    "Rappel de méthode": "Method reminder",
    "Piège à éviter": "Common pitfall",
    "Conseil": "Tip",
}
_TITRE_RE = re.compile(r"^(#{2,4})\s+(" + "|".join(re.escape(t) for t in _TITRES_EN) + r")\s*$", re.MULTILINE)


def _marks(valeur):
    return "mark" if valeur.replace(",", ".") in ("1", "1.0", "1.00") else "marks"


def adapter_markdown(markdown_text, langue):
    """Le Markdown d'un PDF, repères de structure dans la langue du PDF. Sans effet en français."""
    if langue != "en" or not markdown_text:
        return markdown_text
    texte = _EXERCICE_RE.sub(lambda m: "**Exercise" + m.group(1), markdown_text)
    texte = _POINTS_PARENTHESE_RE.sub(lambda m: f"({m.group(1)} {_marks(m.group(1))})", texte)
    texte = _POINTS_CROCHETS_RE.sub(lambda m: f"*[{m.group(1)} {_marks(m.group(1))}]*", texte)
    return _TITRE_RE.sub(lambda m: f"{m.group(1)} {_TITRES_EN[m.group(2)]}", texte)
