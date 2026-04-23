from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from django.contrib.auth import get_user_model

from .models import Application, Assignment, DocumentLink, Event, EventType, Stage, SubStage


@login_required
def application_list(request: HttpRequest):
    q = (request.GET.get("q") or "").strip()

    applications = Application.objects.all()
    if q:
        applications = applications.filter(
            models.Q(folder_number__icontains=q)
            | models.Q(application_name__icontains=q)
            | models.Q(application_number__icontains=q)
            | models.Q(applicant_name__icontains=q)
        )

    context = {
        "applications": applications[:500],
        "q": q,
    }
    return render(request, "cases/application_list.html", context)


@login_required
def application_detail(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)

    today = timezone.localdate()
    users = get_user_model().objects.all().order_by("username")

    assignment_cards = []
    for a in application.assignments.all()[:200]:
        urgency = "normal"
        if a.due_date:
            if a.due_date < today and a.status != "completed":
                urgency = "overdue"
            elif (a.due_date - today).days <= 3 and a.status != "completed":
                urgency = "soon"

        assignment_cards.append((a, urgency))

    context = {
        "application": application,
        "events": application.events.all()[:200],
        "assignments": assignment_cards,
        "documents": application.documents.all()[:200],
        "audit_logs": application.audit_logs.all()[:200],
        "event_type_choices": EventType.choices,
        "stage_choices": Stage.choices,
        "sub_stage_choices": SubStage.choices,
        "users": users,
        "today": today,
    }
    return render(request, "cases/application_detail.html", context)


@login_required
def add_event(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    if request.method == "POST":
        event_type = (request.POST.get("event_type") or "").strip()
        notes = (request.POST.get("notes") or "").strip()
        document_link = (request.POST.get("document_link") or "").strip()
        deadline_date = request.POST.get("deadline_date") or None
        stage = request.POST.get("stage") or None
        sub_stage = (request.POST.get("sub_stage") or "").strip()

        Event.objects.create(
            application=application,
            event_type=event_type,
            notes=notes,
            document_link=document_link,
            deadline_date=deadline_date,
            stage=stage or None,
            sub_stage=sub_stage,
        )
        return redirect("cases:application_detail", pk=application.pk)

    return redirect("cases:application_detail", pk=application.pk)


@login_required
def add_assignment(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    if request.method == "POST":
        assigned_to_id = request.POST.get("assigned_to") or None
        due_date = request.POST.get("due_date") or None
        status = (request.POST.get("status") or "pending").strip()
        notes = (request.POST.get("notes") or "").strip()

        Assignment.objects.create(
            application=application,
            assigned_to_id=assigned_to_id,
            due_date=due_date,
            status=status,
            notes=notes,
        )
        return redirect("cases:application_detail", pk=application.pk)

    return redirect("cases:application_detail", pk=application.pk)


@login_required
def add_document(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    if request.method == "POST":
        file_type = (request.POST.get("file_type") or "other").strip()
        file_path = (request.POST.get("file_path") or "").strip()
        preview_enabled = request.POST.get("preview_enabled") == "on"

        if file_path:
            DocumentLink.objects.create(
                application=application,
                file_type=file_type,
                file_path=file_path,
                preview_enabled=preview_enabled,
            )

        return redirect("cases:application_detail", pk=application.pk)

    return redirect("cases:application_detail", pk=application.pk)
