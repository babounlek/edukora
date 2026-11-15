"""
Le bloc de fin et le QR d'en-tête, communs à tous les PDF (sujet, cours, fiche de quiz, fiche d'exercices, épreuve
inédite). Un PDF circule hors du site, imprimé ou photocopié : c'est sa dernière page et son en-tête qui ramènent le
lecteur vers EduKora.

Le bloc de fin existe en quatre tailles (gabarit `catalog/_pdf_fin.html`) :
  - « mini » : une ligne d'accroche et un petit QR, pour le peu de place qui reste sous le contenu ;
  - « bandeau » : l'accroche, le bouton et le QR ;
  - « demi » : le bandeau, un QR plus grand, l'adresse à taper et ce qu'on trouve sur le site ;
  - « pleine » : la demi, un QR encore plus grand, les autres sessions de l'épreuve et la ligne pour les parents.
`catalog.sujet_pdf.html_vers_pdf` garde la plus grande taille qui N'AJOUTE PAS de page au contenu : un élève paie ses
photocopies à la page, et une page de plus qui ne porte que de la publicité est la première qu'on saute. Si même la
mini ne tient pas, la page de plus est inévitable : elle reçoit alors la taille pleine, pour ne pas rester aux trois
quarts blanche. La place libre de la dernière page ne se calcule pas depuis le HTML (les sauts de page dépendent des
figures et des formules) : on imprime, on compte les pages, on compare.

Aucun lien court : il faudrait une redirection par identifiant, or les identifiants diffèrent entre la base locale et
la production, et une redirection en panne casserait d'un coup tous les QR déjà imprimés. Le QR porte l'adresse
directe, et le bloc dit quoi chercher sur le site à qui n'a pas d'appareil photo.
"""

import base64
import io
import re

import qrcode
from django.conf import settings

MINI = "mini"
BANDEAU = "bandeau"
DEMI = "demi"
PLEINE = "pleine"
# Du plus grand au plus petit : la première qui tient sans ajouter de page est la bonne.
TAILLES = (PLEINE, DEMI, BANDEAU, MINI)
# Bloc masqué : sert à compter les pages du contenu seul, jamais à produire le PDF livré.
SANS_BLOC = "aucun"

# Position du lien dans le PDF, ajoutée à l'adresse (`&pos=p1`) : dit lequel des deux QR ramène réellement du monde.
POSITION_ENTETE = "p1"
POSITION_FIN = "fin"
POSITION_AUTRES = "autres"

# Presque noir plutôt que le vert de la marque : une photocopie de photocopie éclaircit les gris moyens, et un QR pâle
# ne se lit plus.
_COULEUR_QR = "#0b2e22"

# Chromium écrit un objet « /Type /Page » par page (et « /Type /Pages » pour l'arbre, exclu ici).
_PAGE_RE = re.compile(rb"/Type\s*/Page(?![A-Za-z])")


def compter_pages(pdf_bytes):
    """Le nombre de pages d'un PDF produit par Chromium ; 0 si le fichier n'a pas la forme attendue."""
    return len(_PAGE_RE.findall(pdf_bytes))


def imprimer_a_la_bonne_taille(imprimer):
    """Le PDF dont le bloc de fin a la plus grande taille qui n'ajoute pas de page au contenu.

    `imprimer(taille)` rend les octets du PDF pour une taille donnée (voir catalog.sujet_pdf.html_vers_pdf, qui pose
    la taille sur <body data-fin="…"> puis imprime). Séparé du navigateur pour que la règle se teste sans Chromium."""
    pages_du_contenu = compter_pages(imprimer(SANS_BLOC))
    if not pages_du_contenu:
        # Compte illisible : on ne sait pas comparer, le bandeau reste le choix sûr.
        return imprimer(BANDEAU)
    for taille in TAILLES:
        pdf = imprimer(taille)
        if compter_pages(pdf) == pages_du_contenu:
            return pdf
    return imprimer(PLEINE)


def qr_data_uri(url):
    """QR code en data URI : jamais de service tiers pour une image générée à chaque PDF."""
    qr = qrcode.QRCode(border=2, box_size=10)
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color=_COULEUR_QR, back_color="#ffffff")
    tampon = io.BytesIO()
    image.save(tampon, format="PNG")
    return "data:image/png;base64," + base64.b64encode(tampon.getvalue()).decode("ascii")


def avec_position(url, position):
    return f"{url}{'&' if '?' in url else '?'}pos={position}"


def adresse_du_site():
    """« edukora.africa » : l'adresse telle qu'on la tape, sans le protocole."""
    return settings.PDF_SITE_URL.removeprefix("https://").removeprefix("http://")


def contexte_fin(
    tx, *, lien, titre, corps, bouton, qr_alt, legende,
    note_pied="", recherche="", adresse="", autres=(), autres_titre="", parents=False,
):
    """Le contexte `fin` attendu par `catalog/_pdf_fin.html` et `catalog/_pdf_entete_qr.html`.

    `lien` : l'adresse que le PDF doit rouvrir, déjà porteuse de son `?ref=`.
    `recherche` : ce qu'il faut chercher sur le site pour retrouver la même page sans le QR (le titre de l'épreuve, du
    cours) ; à défaut `adresse`, une adresse assez courte pour être tapée (« edukora.africa/cm »).
    `autres` : des liens voisins `{"libelle", "url"}` (les autres sessions d'une épreuve), montrés en taille pleine.
    `parents` : vrai pour un PDF qui sort des mains de l'élève (sujet, cours libre, fiche distribuée) ; un document
    réservé aux abonnés n'a pas à leur vendre l'abonnement.
    """
    site = adresse_du_site()
    lien_fin = avec_position(lien, POSITION_FIN)
    lien_entete = avec_position(lien, POSITION_ENTETE)
    if recherche:
        sans_appareil = tx["fin_sans_appareil_recherche"].replace("{adresse}", site).replace("{titre}", recherche)
    else:
        sans_appareil = tx["fin_sans_appareil_adresse"].replace("{adresse}", adresse or site)
    return {
        "titre": titre,
        "corps": corps,
        "bouton": bouton,
        "lien": lien_fin,
        "qr": qr_data_uri(lien_fin),
        "qr_alt": qr_alt,
        "scan_me": tx["scan_me"],
        "sans_appareil": sans_appareil,
        "aussi_titre": tx["fin_aussi_titre"],
        "aussi": tx["fin_aussi"],
        "autres_titre": autres_titre,
        "autres": list(autres),
        "parents": tx["fin_parents"] if parents else "",
        "note_pied": note_pied,
        "site": site,
        "entete": {"lien": lien_entete, "qr": qr_data_uri(lien_entete), "legende": legende},
    }
