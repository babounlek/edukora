from django.urls import path

from . import views

app_name = "quiz"

urlpatterns = [
    path("sessions/", views.start_session, name="start-session"),
    path("sessions/<int:session_id>/", views.session_detail, name="session-detail"),
    path(
        "sessions/<int:session_id>/questions/<int:quiz_question_id>/corrige/",
        views.reveal_corrige, name="reveal-corrige",
    ),
    path("sessions/<int:session_id>/questions/<int:quiz_question_id>/answer/", views.answer_question, name="answer-question"),
    path("sessions/<int:session_id>/completer/", views.complete_session, name="complete-session"),
    path("sessions/<int:session_id>/fiche-pdf/", views.quiz_fiche_pdf, name="quiz-fiche-pdf"),
    path("sessions/<int:session_id>/sujet.pdf", views.download_quiz_sujet_pdf, name="download-quiz-sujet-pdf"),
    path("sessions/<int:session_id>/corrige.pdf", views.download_quiz_corrige_pdf, name="download-quiz-corrige-pdf"),
    path("revisions/", views.list_revisions_dues, name="revisions-dues"),
    path("maitrise/", views.maitrise, name="maitrise"),
    path("subjects/", views.list_quiz_subjects, name="quiz-subjects"),
    path("parcours/", views.parcours, name="parcours"),
    path("parcours/resume/", views.parcours_resume, name="parcours-resume"),
]
