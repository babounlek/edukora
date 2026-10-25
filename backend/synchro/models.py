"""
Journal de la chaîne de synchronisation des contenus (voir deploy/SPEC-SYNC-CONTENU.md §5).

Trois tables, toutes additives et sans clé étrangère vers l'activité des élèves :
  - LotSynchro      : un lot reçu, son état et son rapport ;
  - OperationSynchro: une ligne par contenu et par lot, ce qui rend un lot rejouable sans effet ;
  - ContenuSynchro  : la dernière version appliquée de chaque contenu synchronisé (identité,
                      empreinte de la source, empreinte de l'état en base, fichiers écrits).
"""
from django.db import models


class StatutLot(models.TextChoices):
    RECU = "recu", "Reçu"
    VERIFIE = "verifie", "Vérifié"
    PRET = "pret", "Prêt à être appliqué"
    EN_COURS = "en_cours", "En cours de synchronisation"
    REUSSI = "reussi", "Réussi"
    REUSSI_AVEC_AVERTISSEMENTS = "reussi_avec_avertissements", "Réussi avec avertissements"
    PARTIEL = "partiel", "Partiel"
    ECHOUE = "echoue", "Échoué"
    A_VERIFIER = "a_verifier", "Résultat à vérifier"


STATUTS_TERMINES_REUSSIS = (StatutLot.REUSSI, StatutLot.REUSSI_AVEC_AVERTISSEMENTS)


class ResultatOperation(models.TextChoices):
    EN_ATTENTE = "en_attente", "En attente"
    CREE = "cree", "Créé"
    MIS_A_JOUR = "mis_a_jour", "Mis à jour"
    INCHANGE = "inchange", "Inchangé"
    RETIRE = "retire", "Retiré (REJETE)"
    REINTEGRE = "reintegre", "Réintégré"
    GARDE_PROD = "garde_prod", "Version de production conservée"
    IGNORE_DEDOUBLONNE = "ignore_dedoublonne", "Non créé : doublon d'un contenu existant"
    CONFLIT_VERSION = "conflit_version", "Conflit : la production a avancé"
    CONFLIT_ETAT = "conflit_etat", "Conflit : modifié en production"
    CONFLIT_IDENTITE = "conflit_identite", "Conflit : identité changée"
    ADOPTION_A_CONFIRMER = "adoption_a_confirmer", "Contenu existant non journalisé : approbation requise"
    STRUCTURE_MODIFIEE = "structure_modifiee", "Structure modifiée : suppression implicite refusée"
    REJETE_VALIDATION = "rejete_validation", "Rejeté par la porte de validation"
    CORRECTION_HORS_PERIMETRE = "correction_hors_perimetre", "Correction hors périmètre : aucun champ synchronisé ne change"
    ERREUR = "erreur", "Erreur"

    @classmethod
    def termines(cls):
        return [v for v in cls.values if v != cls.EN_ATTENTE]


class LotSynchro(models.Model):
    batch_id = models.CharField(max_length=64, unique=True)
    nom = models.CharField(max_length=200, blank=True)
    statut = models.CharField(max_length=30, choices=StatutLot.choices, default=StatutLot.RECU)
    schema_sync = models.PositiveSmallIntegerField(default=1)
    sha256_archive = models.CharField(max_length=64, blank=True)
    sha256_manifeste = models.CharField(max_length=64, blank=True)
    dossier = models.CharField(max_length=500, blank=True, help_text="Dossier du lot extrait, tel que lu par le moteur.")
    options = models.JSONField(default=dict, blank=True)
    compteurs = models.JSONField(default=dict, blank=True)
    rapport = models.JSONField(default=dict, blank=True)
    erreur = models.TextField(blank=True)
    pid = models.IntegerField(null=True, blank=True)
    battement_le = models.DateTimeField(null=True, blank=True)
    recu_le = models.DateTimeField(auto_now_add=True)
    debut_le = models.DateTimeField(null=True, blank=True)
    fin_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-recu_le"]

    def __str__(self):
        return f"{self.batch_id} ({self.statut})"


class OperationSynchro(models.Model):
    lot = models.ForeignKey(LotSynchro, on_delete=models.CASCADE, related_name="operations")
    type = models.CharField(max_length=16)
    id_stable = models.CharField(max_length=255)
    operation = models.CharField(max_length=16, help_text="Opération demandée par le manifeste.")
    resultat = models.CharField(max_length=30, choices=ResultatOperation.choices, default=ResultatOperation.EN_ATTENTE)
    detail = models.JSONField(default=dict, blank=True)
    debut_le = models.DateTimeField(null=True, blank=True)
    fin_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["lot", "type", "id_stable"]
        constraints = [
            models.UniqueConstraint(fields=["lot", "type", "id_stable"], name="unique_operation_par_lot_et_contenu"),
        ]

    def __str__(self):
        return f"{self.lot_id} {self.type}:{self.id_stable} -> {self.resultat}"


class ContenuSynchro(models.Model):
    type = models.CharField(max_length=16)
    id_stable = models.CharField(max_length=255)
    cle_naturelle = models.JSONField(default=dict, blank=True)
    objet_pk = models.BigIntegerField(help_text="Clé primaire de l'objet pédagogique synchronisé.")
    empreinte_source = models.CharField(max_length=64)
    empreinte_etat = models.CharField(max_length=64)
    version = models.PositiveIntegerField(default=1)
    fichiers = models.JSONField(default=dict, blank=True, help_text="{id de figure: {chemin, sha256}} écrits par la dernière application.")
    dernier_lot = models.ForeignKey(LotSynchro, null=True, blank=True, on_delete=models.SET_NULL, related_name="contenus")
    applique_le = models.DateTimeField()

    class Meta:
        ordering = ["type", "id_stable"]
        constraints = [
            models.UniqueConstraint(fields=["type", "id_stable"], name="unique_contenu_synchro_par_identite"),
            models.UniqueConstraint(fields=["type", "objet_pk"], name="unique_contenu_synchro_par_objet"),
        ]

    def __str__(self):
        return f"{self.type}:{self.id_stable} v{self.version}"
