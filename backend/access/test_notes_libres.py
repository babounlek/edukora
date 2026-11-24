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


class EpinglerTests(_Base):
    def test_pinning_flags_the_note_without_moving_it_in_time(self):
        note = NoteLibre.objects.create(profil=self.profil, subject=self.subject, note="Formule")
        avant = NoteLibre.objects.get(pk=note.pk).updated_at
        reponse = self.client.post("/access/etude/notes/epingler/", {"genre": "libre", "id": note.pk, "epingle": True}, format="json")
        self.assertEqual(reponse.data, {"epingle": True})
        note.refresh_from_db()
        self.assertTrue(note.epingle)
        self.assertEqual(note.updated_at, avant)
        carnet = self.client.get("/access/etude/carnet/").data
        self.assertTrue(carnet[0]["epingle"])

    def test_a_section_note_can_be_pinned_and_someone_elses_cannot(self):
        enregistrer_marque(self.profil, self.cours, "regle", note="À retenir")
        marque = self.profil.marques_etude.get()
        self.assertEqual(self.client.post("/access/etude/notes/epingler/", {"genre": "marque", "id": marque.pk, "epingle": True}, format="json").status_code, 200)
        from users.models import User
        intrus = User.objects.create_user(phone_number="677500008", password="x")
        autre = self.client.__class__()
        autre.force_authenticate(user=intrus)
        self.assertEqual(autre.post("/access/etude/notes/epingler/", {"genre": "marque", "id": marque.pk, "epingle": False}, format="json").status_code, 404)


class DossiersEtPagesTests(_Base):
    def _note(self, texte, **extra):
        return NoteLibre.objects.create(profil=self.profil, subject=self.subject, note=texte, **extra)

    def test_the_folders_summarise_each_subject_with_what_is_due_and_pinned(self):
        autre = Subject.objects.create(country=self.subject.country, code="AUTRE", label="Autre matière")
        self._note("a", revision_due=timezone.localdate() - timedelta(days=1), epingle=True)
        self._note("b")
        NoteLibre.objects.create(profil=self.profil, subject=autre, note="c")
        data = self.client.get("/access/etude/carnet/dossiers/").data
        self.assertEqual(data["total"], 3)
        premier = data["dossiers"][0]
        # Le dossier où il y a quelque chose à réviser passe en tête.
        self.assertEqual(premier["matiere_id"], self.subject.pk)
        self.assertEqual((premier["total"], premier["a_reviser"], premier["epingles"]), (2, 1, 1))

    def test_a_folder_is_paged_by_twenty_with_pinned_notes_first(self):
        for i in range(25):
            self._note(f"note {i}")
        epinglee = self._note("la épinglée", epingle=True)
        p1 = self.client.get(f"/access/etude/carnet/page/?matiere={self.subject.pk}").data
        self.assertEqual((p1["count"], len(p1["results"]), p1["page_size"]), (26, 20, 20))
        self.assertEqual(p1["results"][0]["id"], epinglee.pk)
        p2 = self.client.get(f"/access/etude/carnet/page/?matiere={self.subject.pk}&page=2").data
        self.assertEqual(len(p2["results"]), 6)

    def test_the_search_ignores_accents_and_spans_every_subject(self):
        autre = Subject.objects.create(country=self.subject.country, code="AUTRE", label="Autre matière")
        self._note("Théorème de Thalès")
        NoteLibre.objects.create(profil=self.profil, subject=autre, note="thales aussi")
        data = self.client.get("/access/etude/carnet/page/?q=THALÈS").data
        self.assertEqual(data["count"], 2)

    def test_a_bad_page_is_refused_and_someone_elses_notes_stay_hidden(self):
        self.assertEqual(self.client.get("/access/etude/carnet/page/?page=abc").status_code, 400)
        from users.models import User
        intrus = User.objects.create_user(phone_number="677500009", password="x")
        autre = self.client.__class__()
        autre.force_authenticate(user=intrus)
        self._note("privée")
        self.assertEqual(autre.get("/access/etude/carnet/page/").data["count"], 0)
        self.assertEqual(autre.get("/access/etude/carnet/dossiers/").data["dossiers"], [])


class CitationSeuleTests(_Base):
    def test_a_passage_kept_without_text_is_a_note_but_never_a_review_card(self):
        reponse = self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": "", "citation": "Un passage à garder"}, format="json")
        self.assertEqual(reponse.status_code, 201)
        self.assertEqual(self.client.get("/access/etude/carnet/page/?filtre=notes").data["count"], 1)
        self.assertEqual(notes_a_revoir(self.profil)[0], 0)
        dossier = self.client.get("/access/etude/carnet/dossiers/").data["dossiers"][0]
        self.assertEqual((dossier["total"], dossier["avec_note"]), (1, 0))

    def test_without_text_nor_passage_it_is_still_refused_and_editing_may_empty_a_passage_note(self):
        self.assertEqual(self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": " ", "citation": " "}, format="json").status_code, 400)
        note = NoteLibre.objects.create(profil=self.profil, subject=self.subject, note="Un mot", citation="Le passage")
        self.assertEqual(self.client.put(f"/access/etude/notes/{note.pk}/", {"note": ""}, format="json").status_code, 200)
        libre = NoteLibre.objects.create(profil=self.profil, subject=self.subject, note="Sans passage")
        self.assertEqual(self.client.put(f"/access/etude/notes/{libre.pk}/", {"note": ""}, format="json").status_code, 400)


class OrigineTests(_Base):
    def test_a_note_written_from_a_quiz_keeps_its_origin_and_an_unknown_origin_is_ignored(self):
        r = self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": "a", "origine": "quiz"}, format="json")
        self.assertEqual(r.data["origine"], "quiz")
        r = self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": "b", "origine": "autre"}, format="json")
        self.assertEqual(r.data["origine"], "")


def _png(couleur=(200, 30, 30), taille=(40, 30), format="PNG"):
    import io

    from PIL import Image

    tampon = io.BytesIO()
    Image.new("RGB", taille, couleur).save(tampon, format=format)
    tampon.seek(0)
    return tampon


class SourceEtImageTests(_Base):
    def _note(self, **extra):
        return NoteLibre.objects.create(profil=self.profil, subject=self.subject, note="Une note", **extra)

    def test_the_source_is_kept_only_when_it_is_an_internal_address(self):
        bonne = self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": "a", "source": "/cours/x/lire#regle"}, format="json")
        self.assertEqual(bonne.data["source"], "/cours/x/lire#regle")
        for mauvaise in ("https://exemple.org/x", "//exemple.org/x", "javascript:alert(1)", "/a b", "/x" + chr(92) + "y", "/" + "a" * 400):
            r = self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": "b", "source": mauvaise}, format="json")
            self.assertEqual(r.data["source"], "", mauvaise)

    def test_an_image_is_checked_shrunk_and_only_served_to_its_owner(self):
        note = self._note()
        r = self.client.post(f"/access/etude/notes/{note.pk}/image/", {"image": _png(taille=(3000, 2000))}, format="multipart")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["a_image"])
        corps = b"".join(self.client.get(f"/access/etude/notes/{note.pk}/image/").streaming_content)
        from PIL import Image
        import io
        self.assertEqual(max(Image.open(io.BytesIO(corps)).size), 1600)
        from users.models import User
        intrus = User.objects.create_user(phone_number="677500010", password="x")
        autre = self.client.__class__()
        autre.force_authenticate(user=intrus)
        self.assertEqual(autre.get(f"/access/etude/notes/{note.pk}/image/").status_code, 404)
        self.assertEqual(autre.delete(f"/access/etude/notes/{note.pk}/image/").status_code, 404)

    def test_a_file_that_is_not_an_image_is_refused(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        note = self._note()
        faux = SimpleUploadedFile("a.png", b"<html>pas une image</html>", content_type="image/png")
        self.assertEqual(self.client.post(f"/access/etude/notes/{note.pk}/image/", {"image": faux}, format="multipart").status_code, 400)
        gif = _png(format="GIF")
        self.assertEqual(self.client.post(f"/access/etude/notes/{note.pk}/image/", {"image": gif}, format="multipart").status_code, 400)

    def test_removing_the_image_or_the_note_deletes_the_file(self):
        note = self._note()
        self.client.post(f"/access/etude/notes/{note.pk}/image/", {"image": _png()}, format="multipart")
        note.refresh_from_db()
        nom = note.image.name
        stockage = note.image.storage
        self.assertTrue(stockage.exists(nom))
        self.assertFalse(self.client.delete(f"/access/etude/notes/{note.pk}/image/").data["a_image"])
        self.assertFalse(stockage.exists(nom))
        self.client.post(f"/access/etude/notes/{note.pk}/image/", {"image": _png()}, format="multipart")
        note.refresh_from_db()
        nom = note.image.name
        self.client.delete(f"/access/etude/notes/{note.pk}/")
        self.assertFalse(stockage.exists(nom))

    def test_a_note_may_be_only_a_photo(self):
        self.assertEqual(self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": ""}, format="json").status_code, 400)
        r = self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": "", "avec_image": True}, format="json")
        self.assertEqual(r.status_code, 201)


class ThemeDesNotesTests(_Base):
    def _tag(self, nom="trigonométrie"):
        from catalog.models import Tag

        return Tag.objects.create(name=nom)

    def test_a_note_keeps_its_theme_and_comes_back_by_theme_first_pinned(self):
        tag = self._tag()
        a = self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": "Règle", "theme": tag.pk}, format="json")
        self.assertEqual(a.data["theme_id"], tag.pk)
        NoteLibre.objects.create(profil=self.profil, subject=self.subject, note="Épinglée", theme=tag, epingle=True)
        NoteLibre.objects.create(profil=self.profil, subject=self.subject, note="Autre thème", theme=self._tag("autre"))
        data = self.client.get(f"/access/etude/notes/par-theme/?theme={tag.pk}").data
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["notes"][0]["note"], "Épinglée")

    def test_an_unknown_theme_is_ignored_and_other_students_notes_never_show(self):
        r = self.client.post("/access/etude/notes/", {"subject": self.subject.pk, "note": "x", "theme": 999999}, format="json")
        self.assertIsNone(r.data["theme_id"])
        tag = self._tag()
        NoteLibre.objects.create(profil=self.profil, subject=self.subject, note="Privée", theme=tag)
        from users.models import User
        intrus = User.objects.create_user(phone_number="677500011", password="x")
        autre = self.client.__class__()
        autre.force_authenticate(user=intrus)
        self.assertEqual(autre.get(f"/access/etude/notes/par-theme/?theme={tag.pk}").data["total"], 0)
        self.assertEqual(self.client.get("/access/etude/notes/par-theme/?theme=abc").data["total"], 0)
