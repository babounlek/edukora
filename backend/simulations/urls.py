from django.urls import path

from . import views

app_name = "simulations"

urlpatterns = [
    path("", views.start_simulation, name="start"),
    path("mes-simulations/", views.mes_simulations, name="mes-simulations"),
    path("<int:simulation_id>/", views.simulation_detail, name="detail"),
    path("<int:simulation_id>/mode-examen/", views.start_exam_mode, name="mode-examen"),
    path("<int:simulation_id>/exercices/<int:exercice_id>/noter/", views.noter_exercice, name="noter"),
    path("<int:simulation_id>/exercices/<int:exercice_id>/marquer/", views.toggle_marque, name="marquer"),
    path("<int:simulation_id>/completer/", views.complete_simulation, name="completer"),
]
