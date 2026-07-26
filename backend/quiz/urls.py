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
]
