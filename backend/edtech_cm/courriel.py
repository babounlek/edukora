"""
Le gabarit commun des e-mails EduKora : bandeau vert au logo, liseré or, carte blanche, bouton, pied de page.

Un message s'écrit une seule fois, en blocs (paragraphes, listes, encarts, intertitres, code), et on en tire les deux
versions envoyées ensemble : le texte brut, toujours joint (vieux Outlook, lecteurs d'écran, aperçus de notification ne
lisent que lui), et le HTML (templates/emails/edukora.html). Les deux ne peuvent donc pas dire des choses différentes.

Avant ce module, seuls le rappel quotidien et les relances d'absence avaient une mise en forme ; la relance d'un paiement
raté, la fin d'abonnement, le bilan des parents ou le reçu de paiement partaient en texte brut, sans logo, et
ressemblaient à un message frauduleux au moment précis où l'on parle d'argent.
"""

from dataclasses import dataclass, field

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import escape
from django.utils.safestring import mark_safe

FR = "fr"
EN = "en"

# Les textes fixes du gabarit, dans les deux langues.
_FIXES = {
    FR: {
        "slogan": "Réussis ton examen",
        "secours": "Le bouton ne s'affiche pas ? Copie ce lien dans ton navigateur :",
        "question_texte": "Une question ? Réponds simplement à ce message.",
        "question_html": "Une question ? Réponds simplement à ce message ou écris à",
        "deux_points": " : ",
    },
    EN: {
        "slogan": "Pass your exam",
        "secours": "Can't see the button? Copy this link into your browser:",
        "question_texte": "A question? Just reply to this message.",
        "question_html": "A question? Just reply to this message or write to",
        "deux_points": ": ",
    },
}


def montant_fcfa(valeur):
    """« 2 000 » : les milliers séparés par une espace, comme sur le site."""
    return f"{int(valeur):,}".replace(",", " ")


def prenom(user):
    nom = (getattr(user, "full_name", "") or getattr(user, "pseudo", "") or "").strip()
    return nom.split()[0] if nom else ""


def salutation(user, langue=FR):
    """« Bonjour Awa, » / « Hello Awa, », sans prénom quand le compte n'en a pas."""
    p = prenom(user)
    if langue == EN:
        return f"Hello {p}," if p else "Hello,"
    return f"Bonjour {p}," if p else "Bonjour,"


def _avec_gras(texte, gras):
    """Le paragraphe échappé, `gras` (un extrait du texte) en gras dans le HTML."""
    if not gras or gras not in texte:
        return escape(texte)
    avant, _, apres = texte.partition(gras)
    return mark_safe(f"{escape(avant)}<strong>{escape(gras)}</strong>{escape(apres)}")


@dataclass
class Courriel:
    """
    Un e-mail EduKora. `apercu` ne sert qu'au HTML (la ligne grise affichée sous l'objet dans la boîte de réception) ;
    tout le reste figure dans les deux versions. Le titre ouvre le message : il ne répète pas le premier paragraphe.
    """

    langue: str = FR
    salutation: str = ""
    titre: str = ""
    apercu: str = ""
    blocs: list = field(default_factory=list)
    bouton: tuple | None = None  # (texte, lien)
    apres_bouton: list = field(default_factory=list)
    raison: str = ""
    arret: tuple | None = None  # (texte, lien) : le lien d'arrêt en un clic
    question: bool = True

    def __post_init__(self):
        if self.langue not in _FIXES:
            self.langue = FR

    # ------------------------------------------------------------------ construction

    def paragraphe(self, texte, *, gras=""):
        self.blocs.append({"type": "paragraphe", "texte": texte, "html": _avec_gras(texte, gras)})
        return self

    def liste(self, elements):
        """Une liste à puces : « - élément » dans le texte brut."""
        if elements:
            self.blocs.append({"type": "liste", "elements": list(elements)})
        return self

    def encart(self, lignes):
        """Les faits mis en avant (fond vert pâle, filet or) : une ligne par fait."""
        if lignes:
            self.blocs.append({"type": "encart", "lignes": list(lignes)})
        return self

    def intertitre(self, texte):
        self.blocs.append({"type": "intertitre", "texte": texte})
        return self

    def code(self, texte):
        """Un code à recopier, en grand et en chasse fixe."""
        self.blocs.append({"type": "code", "texte": texte})
        return self

    # ------------------------------------------------------------------ rendu

    def texte(self):
        f = _FIXES[self.langue]
        sections = []
        if self.salutation:
            sections.append(self.salutation)
        if self.titre:
            sections.append(self.titre)
        for bloc in self.blocs:
            if bloc["type"] == "paragraphe":
                sections.append(bloc["texte"])
            elif bloc["type"] == "liste":
                sections.append("\n".join(f"- {e}" for e in bloc["elements"]))
            elif bloc["type"] == "encart":
                sections.append("\n".join(bloc["lignes"]))
            elif bloc["type"] == "intertitre":
                sections.append(f"■ {bloc['texte']}")
            elif bloc["type"] == "code":
                sections.append(bloc["texte"])
        if self.bouton:
            sections.append(f"{self.bouton[0]}{f['deux_points']}{self.bouton[1]}")
        sections.extend(self.apres_bouton)
        if self.question:
            sections.append(f["question_texte"])
        pied = [ligne for ligne in (
            self.raison, f"{self.arret[0]}{f['deux_points']}{self.arret[1]}" if self.arret else "",
        ) if ligne]
        if pied:
            sections.append("\n".join(pied))
        return "\n\n".join(sections)

    def html(self):
        return render_to_string("emails/edukora.html", {
            "c": self, "f": _FIXES[self.langue], "site_name": settings.SITE_NAME, "site_url": settings.FRONTEND_URL,
            "support_email": settings.SUPPORT_EMAIL,
        })
