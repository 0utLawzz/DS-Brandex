from django.urls import path
from . import views

app_name = "cases"

urlpatterns = [
    # ── Core ──
    path("",                          views.dashboard,               name="dashboard"),
    path("cases/",                    views.application_list,        name="application_list"),
    path("cases/new/",                views.application_create,      name="application_create"),
    path("cases/<int:pk>/",           views.application_detail,      name="application_detail"),
    path("cases/<int:pk>/edit/",      views.application_edit,        name="application_edit"),
    path("cases/<int:pk>/delete/",    views.application_delete,      name="application_delete"),

    # ── Events & Assignments ──
    path("cases/<int:pk>/event/",       views.add_event,             name="add_event"),
    path("cases/<int:pk>/assign/",      views.add_assignment,        name="add_assignment"),
    path("assignments/",                views.assignments_view,       name="assignments"),
    path("assignments/<int:pk>/complete/", views.complete_assignment, name="complete_assignment"),

    # ── Stage actions ──
    path("cases/<int:pk>/proceed/",           views.proceed_to_stage2,          name="proceed_to_stage2"),
    path("cases/<int:pk>/stop/",              views.stop_case,                   name="stop_case"),
    path("cases/<int:pk>/dispatch/print/",    views.dispatch_print_certificate,  name="dispatch_print_certificate"),
    path("cases/<int:pk>/dispatch/dispatch/", views.dispatch_certificate_dispatch, name="dispatch_certificate_dispatch"),

    # ── PDF & Export ──
    path("cases/<int:pk>/pdf/",       views.export_application_pdf,  name="export_application_pdf"),
    path("export/csv/",               views.export_applications_csv, name="export_applications_csv"),
    path("import/csv/",               views.import_applications_csv, name="import_applications_csv"),

    # ── Search & Utilities ──
    path("search/tm/",                views.search_by_tm,            name="search_tm"),
    path("my-tasks/",                 views.my_tasks,                name="my_tasks"),
    path("api/check-tm/",             views.check_tm_duplicate,      name="check_tm_duplicate"),
]
