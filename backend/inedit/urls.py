from django.urls import path

from . import views

app_name = "inedit"

urlpatterns = [
    path("mes-inscriptions/", views.list_my_inscriptions_inedites, name="mes-inscriptions"),
    path("mes-tentatives/", views.list_my_tentatives_inedites, name="mes-tentatives"),
    path("epreuves/", views.list_epreuves, name="epreuve-list"),
    # <slug:id> (pas <int:id>) : accepte aussi bien le slug ("URL publique", voir
    # EpreuveInedite.slug) que l'id numérique historique - même patron que
    # catalog:lesson-detail (<slug:slug>) + VisibleQuerySet.par_slug_ou_id, résolu
    # côté vue (inedit n'a pas de manager équivalent, voir epreuve_inedite_detail).
    path("epreuves/<slug:id>/", views.epreuve_inedite_detail, name="epreuve-detail"),
    path("tentatives/", views.start_tentative, name="start-tentative"),
    path("tentatives/<int:tentative_id>/", views.tentative_detail, name="tentative-detail"),
    path("tentatives/<int:tentative_id>/mode-examen/", views.start_exam_mode, name="start-exam-mode"),
    path(
        "tentatives/<int:tentative_id>/questions/<int:question_id>/corrige/",
        views.reveal_corrige, name="reveal-corrige",
    ),
    path(
        "tentatives/<int:tentative_id>/questions/<int:question_id>/answer/",
        views.answer_question, name="answer-question",
    ),
    path(
        "tentatives/<int:tentative_id>/questions/<int:question_id>/marquer/",
        views.toggle_question_marquee, name="toggle-question-marquee",
    ),
    path("tentatives/<int:tentative_id>/completer/", views.complete_tentative, name="complete-tentative"),
    path("epreuves/<int:epreuve_id>/sujet.pdf", views.download_sujet_pdf, name="download-sujet-pdf"),
]
