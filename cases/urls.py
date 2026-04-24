from django.urls import path

from . import views


app_name = "cases"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("applications/", views.application_list, name="application_list"),
    path("applications/new/", views.application_create, name="application_create"),
    path("applications/<int:pk>/", views.application_detail, name="application_detail"),
    path("applications/<int:pk>/add-event/", views.add_event, name="add_event"),
    path("applications/<int:pk>/add-assignment/", views.add_assignment, name="add_assignment"),
    path("applications/<int:pk>/add-document/", views.add_document, name="add_document"),
]
