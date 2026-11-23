from datetime import timedelta

from django.utils import timezone

from catalog.models import Subject

from .etude import enregistrer_marque, noter_revue, notes_a_revoir
from .models import NoteLibre
from .test_etude import _Base


class NotesLibresTests(_Base):
    def _creer(self, note="Pythagore : a² + b² = c²", **extra):
        return self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": note, **extra}, format="json")

    def test_a_free_note_is_created_and_listed_in_the_carnet_with_its_subject(self):
        reponse = self._creer(citation="Quelle est la formule ?")
        self.assertEqual(reponse.status_code, 201)
        carnet = self.client.get("/access/etude/carnet/").data
        self.assertEqual(len(carnet), 1)
        self.assertEqual(carnet[0]["genre"], "libre")
        self.assertEqual(carnet[0]["matiere"], self.subject.label)
        self.assertEqual(carnet[0]["citation"], "Quelle est la formule ?")

    def test_an_empty_or_too_long_note_is_refused(self):
        self.assertEqual(self._creer(note="   ").status_code, 400)
        self.assertEqual(self._creer(note="x" * 2001).status_code, 400)

    def test_an_unknown_subject_is_refused(self):
        reponse = self.client.post("/access/etude/notes/", {"subject": 999999, "note": "a"}, format="json")
        self.assertEqual(reponse.status_code, 400)

    def test_update_and_delete_only_touch_my_own_note(self):
        pk = self._creer().data["id"]
        self.assertEqual(self.client.put(f"/access/etude/notes/{pk}/", {"note": "Corrigée"}, format="json").data["note"], "Corrigée")
        autre = self.client.__class__()
        from users.models import User
        intrus = User.objects.create_user(phone_number="677500009", password="x")
        autre.force_authenticate(user=intrus)
        self.assertEqual(autre.delete(f"/access/etude/notes/{pk}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/access/etude/notes/{pk}/").status_code, 204)
        self.assertFalse(NoteLibre.objects.exists())

    def test_anonymous_cannot_create_notes(self):
        anonyme = self.client.__class__()
        self.assertIn(anonyme.post("/access/etude/notes/", {"subject": self.subject.pk, "note": "a"}, format="json").status_code, (401, 403))


class RevisionDesNotesTests(_Base):
    def test_a_new_note_is_due_and_a_signet_without_text_is_not(self):
        enregistrer_marque(self.profil, self.cours, "regle", signet=True)
        enregistrer_marque(self.profil, self.lesson, "exercice-1", note="Refaire")
        NoteLibre.objects.create(profil=self.profil, subject=self.subject, note="Formule")
        total, notes = notes_a_revoir(self.profil)
        self.assertEqual(total, 2)
        self.assertEqual({n["genre"] for n in notes}, {"marque", "libre"})

    def test_remembering_schedules_the_note_and_forgetting_brings_it_back_tomorrow(self):
        note = NoteLibre.objects.create(profil=self.profil, subject=self.subject, note="Formule")
        noter_revue(self.profil, "libre", note.pk, True)
        note.refresh_from_db()
        self.assertEqual(note.revision_palier, 1)
        self.assertEqual(note.revision_due, timezone.localdate() + timedelta(days=3))
        self.assertEqual(notes_a_revoir(self.profil)[0], 0)

        note.revision_due = timezone.localdate()
        note.save()
        noter_revue(self.profil, "libre", note.pk, False)
        note.refresh_from_db()
        self.assertEqual(note.revision_palier, 0)
        self.assertEqual(note.revision_due, timezone.localdate() + timedelta(days=1))

    def test_an_early_review_of_a_known_note_changes_nothing(self):
        note = NoteLibre.objects.create(profil=self.profil, subject=self.subject, note="Formule")
        noter_revue(self.profil, "libre", note.pk, True)
        note.refresh_from_db()
        avant = (note.revision_palier, note.revision_due)
        noter_revue(self.profil, "libre", note.pk, True)
        note.refresh_from_db()
        self.assertEqual((note.revision_palier, note.revision_due), avant)

    def test_api_review_and_due_list(self):
        pk = self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": "Formule"}, format="json").data["id"]
        self.assertEqual(self.client.get("/access/etude/notes/a-revoir/").data["total"], 1)
        self.assertEqual(self.client.post("/access/etude/notes/revue/", {"genre": "libre", "id": pk, "savais": True}, format="json").status_code, 200)
        self.assertEqual(self.client.get("/access/etude/notes/a-revoir/").data["total"], 0)
        self.assertEqual(self.client.post("/access/etude/notes/revue/", {"genre": "libre", "id": 99999, "savais": True}, format="json").status_code, 404)


class QuotaEtMatiereTests(_Base):
    def _notes(self, n, subject=None):
        return [NoteLibre.objects.create(profil=self.profil, subject=subject or self.subject, note=f"n{i}") for i in range(n)]

    def test_only_five_new_notes_are_offered_per_day(self):
        notes = self._notes(8)
        total, liste = notes_a_revoir(self.profil)
        self.assertEqual((total, len(liste)), (5, 5))

        for note in liste:
            noter_revue(self.profil, "libre", note["id"], True)
        # Les cinq vues ont fait leur quota du jour : plus de nouvelle ce jour-là.
        self.assertEqual(notes_a_revoir(self.profil)[0], 0)
        self.assertEqual(NoteLibre.objects.filter(revision_debut=timezone.localdate()).count(), 5)
        self.assertEqual(len(notes), 8)

    def test_a_note_already_due_is_not_counted_in_the_daily_quota(self):
        due = self._notes(1)[0]
        due.revision_due = timezone.localdate() - timedelta(days=2)
        due.revision_debut = timezone.localdate() - timedelta(days=9)
        due.save()
        self._notes(6)
        total, liste = notes_a_revoir(self.profil)
        self.assertEqual(total, 6)  # 1 due + 5 nouvelles
        self.assertEqual(liste[0]["id"], due.pk)  # les rappels d'abord

    def test_reviewing_one_subject_is_not_capped_and_only_returns_that_subject(self):
        autre = Subject.objects.exclude(pk=self.subject.pk).first()
        self._notes(8)
        self._notes(2, subject=autre)
        total, liste = notes_a_revoir(self.profil, matiere_id=self.subject.pk)
        self.assertEqual((total, len(liste)), (8, 8))
        reponse = self.client.get(f"/access/etude/notes/a-revoir/?matiere={autre.pk}")
        self.assertEqual(reponse.data["total"], 2)
