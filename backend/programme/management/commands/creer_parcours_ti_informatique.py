"""
Parcours de la Série TI : remplace la ligne « Informatique » par les trois matières
propres à cette série (Programmation, Systèmes d'Information, Réseaux/Internet/Sécurité
- voir SUBJECT_FAMILIES dans catalog.models).

Cause : les modules officiels d'Informatique (Module 111-116 au Cameroun : HTML,
JavaScript, base de données simple, réseau local, infographie...) sont le programme du
TRONC COMMUN, partagé par les séries A/C/D/E/TI. /parcours/resume/ liste les matières
d'après Module.cursus, donc TI y voyait « Informatique » et aucune de ses trois vraies
matières (aucun Module officiel TI n'existe pour elles).

Ce que fait la commande, pour chaque cursus de Série TI (idempotente) :
  1. détache le cursus TI des modules d'Informatique (les autres séries ne changent
     pas : relation M2M, aucun module supprimé) ;
  2. crée, sous Programmation / Systèmes d'Information / Réseaux-Sécurité, des modules
     TI avec leurs savoirs (structure ci-dessous, dérivée des thèmes réellement présents
     dans les épreuves, cours et quiz TI déjà en base - PAS un programme officiel, à
     relire) ;
  3. rattache à ces savoirs les Tag dont le nom correspond (mots-clés ci-dessous), mais
     seulement ceux utilisés EXCLUSIVEMENT par du contenu de Série TI : un tag partagé
     avec une autre série (SQL, JavaScript...) garde son savoir de tronc commun pour ne
     pas casser leur parcours.

    python manage.py creer_parcours_ti_informatique            # simulation
    python manage.py creer_parcours_ti_informatique --apply
"""

import re

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Cours, Cursus, Question, Subject, Tag
from programme.models import Module, Savoir
from quiz.models import CompetenceItem

SERIE_LABEL = "TI"

# (code Subject, classe) -> [(titre, [savoirs])] ; classe déduite de l'Examen du cursus.
# Terminale : dérivé des thèmes des épreuves/cours/quiz TI. 1ère : les modules du tronc
# commun d'Informatique, simplement reclassés sous la bonne matière TI.
STRUCTURE = {
    "Tle": {
        "PROGRAMMATION": [
            ("Algorithmique et langage C", [
                "Algorithmes, algorigrammes et pseudo-code",
                "Langage C : types, entrées-sorties, structures de contrôle et tableaux",
                "Fonctions et récursivité",
            ]),
            ("Programmation web", [
                "HTML, CSS et formulaires",
                "JavaScript",
                "PHP et serveur web",
            ]),
        ],
        "SYSTEMES_INFORMATION": [
            ("Modélisation UML", [
                "Diagramme de cas d'utilisation",
                "Diagramme de classes",
                "Diagramme de séquence",
            ]),
            ("Bases de données", [
                "Modèle conceptuel et modèle relationnel (Merise)",
                "Langage SQL (définition et manipulation des données)",
            ]),
        ],
        "RESEAUX_SECURITE": [
            ("Réseaux locaux et adressage IP", [
                "Composants, câblage et topologies d'un réseau local",
                "Adressage IPv4, sous-réseaux et DHCP",
                "Diagnostic réseau (ipconfig, ping)",
            ]),
            ("Internet et cloud", [
                "Services et technologies d'Internet, recherche d'information",
                "Cloud computing et virtualisation",
            ]),
            ("Sécurité informatique", [
                "Menaces, cryptographie et bonnes pratiques de sécurité",
            ]),
        ],
    },
    "1ere": {
        "PROGRAMMATION": [
            ("Algorithmique et programmation statique", [
                "Utiliser les notions élémentaires de l'algorithmique",
                "Programmer les pages web statiques HTML",
                "Produire une feuille de style",
            ]),
            ("Infographie", [
                "Créer des boutons",
                "Créer des textes avec effets",
                "Créer des animations",
                "Retoucher une photo",
            ]),
            ("Projet informatique", ["Réaliser et publier un site web statique"]),
        ],
    },
}

# (code Subject, titre de module, intitulé de savoir) <- mots entiers cherchés dans Tag.name
# (minuscules). Premier savoir qui correspond gagne : les motifs spécifiques d'abord.
MOTS_CLES = [
    ("RESEAUX_SECURITE", "Sécurité informatique", "Menaces, cryptographie et bonnes pratiques de sécurité",
     ["sécurité", "chiffrement", "cryptographie", "malware", "virus", "cybercriminalité", "confidentialité",
      "intégrité", "disponibilité", "authentification", "sanctions pénales", "fake news", "désinformation"]),
    ("RESEAUX_SECURITE", "Internet et cloud", "Cloud computing et virtualisation",
     ["cloud", "virtualisation", "hyperviseur", "vmware", "paas", "saas", "iaas"]),
    ("RESEAUX_SECURITE", "Internet et cloud", "Services et technologies d'Internet, recherche d'information",
     ["moteur de recherche", "google", "opérateurs", "technologies d'accès", "protocoles internet",
      "courrier électronique", "partage de fichiers", "navigateur", "hébergement"]),
    ("RESEAUX_SECURITE", "Réseaux locaux et adressage IP", "Diagnostic réseau (ipconfig, ping)",
     ["ipconfig", "ping", "icmp", "diagnostic réseau", "test de connectivité", "loopback"]),
    ("RESEAUX_SECURITE", "Réseaux locaux et adressage IP", "Adressage IPv4, sous-réseaux et DHCP",
     ["sous-réseau", "adresse ip", "ipv4", "dhcp", "adresse mac", "vlsm", "adresse de diffusion",
      "nombre d'hôtes", "masque", "adressage", "classes d'adresses", "broadcast", "passerelle", "dns"]),
    ("RESEAUX_SECURITE", "Réseaux locaux et adressage IP", "Composants, câblage et topologies d'un réseau local",
     ["csma/cd", "ethernet", "câbles", "topologie", "wi-fi", "carte réseau", "routeur", "débit", "bande passante",
      "fibre optique", "routage", "modèle osi", "architecture réseau", "réseau physique"]),
    ("SYSTEMES_INFORMATION", "Modélisation UML", "Diagramme de cas d'utilisation",
     ["cas d'utilisation", "acteur", "include"]),
    ("SYSTEMES_INFORMATION", "Modélisation UML", "Diagramme de séquence", ["ligne de vie"]),
    ("SYSTEMES_INFORMATION", "Modélisation UML", "Diagramme de classes",
     ["uml", "diagramme de classes", "généralisation", "agrégation", "composition", "multiplicités", "attribut",
      "héritage", "visibilité", "association", "génie logiciel"]),
    ("SYSTEMES_INFORMATION", "Bases de données", "Langage SQL (définition et manipulation des données)",
     ["sql", "select", "where", "join", "insert into", "update", "create table", "alter table", "order by", "avg",
      "langage de manipulation de données", "langage de définition de données"]),
    ("SYSTEMES_INFORMATION", "Bases de données", "Modèle conceptuel et modèle relationnel (Merise)",
     ["base de données", "sgbd", "merise", "modèle relationnel", "clé primaire"]),
    ("PROGRAMMATION", "Programmation web", "PHP et serveur web",
     ["php", "apache", "serveur web", "wamp", "wampserver", "htdocs", "client-serveur", "application web",
      "mysql_connect", "http", "echo", "method", "get", "post", "serveur local"]),
    ("PROGRAMMATION", "Programmation web", "JavaScript", ["javascript", "onclick"]),
    ("PROGRAMMATION", "Programmation web", "HTML, CSS et formulaires",
     ["html", "css", "formulaire", "validation de formulaire", "balises", "form", "balises html"]),
    ("PROGRAMMATION", "Algorithmique et langage C", "Fonctions et récursivité",
     ["récursivité", "cas de base", "factorielle", "pile d'appels", "appel de fonction"]),
    ("PROGRAMMATION", "Algorithmique et langage C", "Langage C : types, entrées-sorties, structures de contrôle et tableaux",
     ["langage c", "scanf", "printf", "tableau", "boucle", "if", "do while", "#include", "stdio.h", "compilateur",
      "préprocesseur", "fonction main", "types entiers", "dépassement de capacité", "chaîne de caractères",
      "entrées-sorties", "constante"]),
    ("PROGRAMMATION", "Algorithmique et langage C", "Algorithmes, algorigrammes et pseudo-code",
     ["algorigramme", "pseudo-code", "algorithme", "trace d'exécution", "analyse d'algorithme"]),
]

_MOTIFS = [
    (code, module, savoir, [re.compile(r"(?<!\w)" + re.escape(mot) + r"(?!\w)") for mot in mots])
    for code, module, savoir, mots in MOTS_CLES
]


def _classe_du_cursus(cursus):
    """"Tle" pour un BAC, "1ere" pour un Probatoire (même convention que Module.classe)."""
    return "Tle" if cursus.examen == "BAC" else "1ere"


class Command(BaseCommand):
    help = "Remplace « Informatique » par Programmation / Systèmes d'Information / Réseaux dans le parcours TI."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Écrit réellement (sans : simulation).")

    def handle(self, *args, **options):
        appliquer = options["apply"]
        cursus_ti = list(Cursus.objects.filter(series__code=SERIE_LABEL).select_related("country", "series"))
        rapport = {"detaches": 0, "modules": 0, "savoirs": 0, "tags": 0}

        with transaction.atomic():
            savoir_par_cle = {}  # (country_id, code, module titre, savoir intitulé) -> Savoir
            for cursus in cursus_ti:
                classe = _classe_du_cursus(cursus)
                for module in Module.objects.filter(subject__country=cursus.country, subject__code="INFORMATIQUE", cursus=cursus):
                    rapport["detaches"] += 1
                    if appliquer:
                        module.cursus.remove(cursus)
                for code, modules in STRUCTURE.get(classe, {}).items():
                    subject = Subject.objects.get(country=cursus.country, code=code)
                    for m_idx, (titre, savoirs) in enumerate(modules, start=1):
                        module = Module.objects.filter(
                            subject=subject, classe=classe, serie_label=SERIE_LABEL, titre=titre,
                        ).first()
                        if module is None:
                            rapport["modules"] += 1
                            if not appliquer:
                                continue
                            module = Module.objects.create(
                                subject=subject, classe=classe, serie_label=SERIE_LABEL,
                                numero=f"TI{classe[0]}{code[:2]}{m_idx}", titre=titre, ordre=m_idx,
                            )
                        if appliquer:
                            module.cursus.add(cursus)
                            for s_idx, intitule in enumerate(savoirs, start=1):
                                savoir, cree = Savoir.objects.get_or_create(
                                    module=module, intitule=intitule, defaults={"ordre": s_idx},
                                )
                                rapport["savoirs"] += int(cree)
                                savoir_par_cle[(cursus.country_id, code, titre, intitule)] = savoir

            # Rattachement des tags exclusivement TI, uniquement pour le pays du contenu.
            if appliquer:
                for tag in Tag.objects.all().only("id", "name", "savoir_officiel_id"):
                    cible = self._cible(tag.name)
                    if cible is None:
                        continue
                    if not self._exclusif_ti(tag):
                        continue
                    savoirs = [s for (pays, c, m, i), s in savoir_par_cle.items() if (c, m, i) == cible]
                    if not savoirs:
                        continue
                    # Un tag n'a qu'un savoir : celui du pays où il est utilisé (un seul en pratique, CM).
                    if tag.savoir_officiel_id in {s.id for s in savoirs}:
                        continue
                    Tag.objects.filter(pk=tag.pk).update(savoir_officiel=self._savoir_du_pays(tag, savoirs))
                    rapport["tags"] += 1

            if not appliquer:
                transaction.set_rollback(True)

        self.stdout.write(f"{rapport['detaches']} rattachement(s) TI retiré(s) d'Informatique, "
                          f"{rapport['modules']} module(s) TI à créer, {rapport['savoirs']} savoir(s) créés, "
                          f"{rapport['tags']} tag(s) rattachés.")
        if not appliquer:
            self.stdout.write(self.style.WARNING("Simulation seule (--apply pour écrire)."))

    @staticmethod
    def _cible(nom):
        nom = nom.strip().lower()
        for code, module, savoir, motifs in _MOTIFS:
            if any(m.search(nom) for m in motifs):
                return code, module, savoir
        return None

    @staticmethod
    def _savoir_du_pays(tag, savoirs):
        # Le contenu TI n'existe aujourd'hui qu'au Cameroun ; à défaut, le premier savoir.
        cm = [s for s in savoirs if s.module.subject.country.code == "CM"]
        return (cm or savoirs)[0]

    @staticmethod
    def _exclusif_ti(tag):
        """Vrai si aucun contenu hors Série TI ne porte ce tag (Cours, quiz, questions)."""
        hors_ti_cours = Cours.objects.filter(tags=tag).exclude(cursus__series__code=SERIE_LABEL)
        hors_ti_quiz = CompetenceItem.objects.filter(theme=tag).exclude(cursus__series__code=SERIE_LABEL)
        hors_ti_questions = Question.objects.filter(themes=tag).exclude(exercise__lesson__cursus__series__code=SERIE_LABEL)
        return not (hors_ti_cours.exists() or hors_ti_quiz.exists() or hors_ti_questions.exists())
