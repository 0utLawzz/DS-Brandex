from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from django.contrib.auth import get_user_model

from .models import Application, Assignment, DocumentLink, Event, EventType, Stage, SubStage, FileUpload, SiteSettings


@login_required
def application_list(request: HttpRequest):
    q = (request.GET.get("q") or "").strip()

    applications = Application.objects.all()
    if q:
        applications = applications.filter(
            models.Q(folder_number__icontains=q)
            | models.Q(application_name__icontains=q)
            | models.Q(case_no__icontains=q)
            | models.Q(applicant_name__icontains=q)
        )

    paginator = Paginator(applications, 100)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    context = {
        "page_obj": page_obj,
        "q": q,
        "site_settings": site_settings,
    }
    return render(request, "cases/application_list.html", context)


@login_required
def application_create(request: HttpRequest):
    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    if request.method == "POST":
        folder_number = (request.POST.get("folder_number") or "").strip()
        client_type = (request.POST.get("client_type") or "").strip()
        application_type = (request.POST.get("application_type") or "").strip()
        application_name = (request.POST.get("application_name") or "").strip()
        trademark_no = (request.POST.get("trademark_no") or "").strip()
        case_no = (request.POST.get("case_no") or "").strip()
        class_numbers = (request.POST.get("class_numbers") or "").strip()
        filing_date = request.POST.get("filing_date") or None
        application_year = request.POST.get("application_year") or None
        applicant_name = (request.POST.get("applicant_name") or "").strip()
        trading_as = (request.POST.get("trading_as") or "").strip()
        applicant_type = (request.POST.get("applicant_type") or "").strip()
        address = (request.POST.get("address") or "").strip()
        city = (request.POST.get("city") or "").strip()
        agent_name = (request.POST.get("agent_name") or "").strip()
        agent_address = (request.POST.get("agent_address") or "").strip()
        jurisdiction = (request.POST.get("jurisdiction") or "").strip()
        dispatch_status = (request.POST.get("dispatch_status") or "").strip()
        logo = request.FILES.get("logo")
        files = request.FILES.getlist("files")

        errors = []
        if not folder_number:
            errors.append("Folder number is required")
        if not application_name:
            errors.append("Application name is required")
        if not applicant_name:
            errors.append("Applicant name is required")
        if client_type not in {c[0] for c in Application._meta.get_field("client_type").choices}:
            errors.append("Invalid client type")
        if application_type not in {c[0] for c in Application._meta.get_field("application_type").choices}:
            errors.append("Invalid application type")
        if applicant_type and applicant_type not in {c[0] for c in Application._meta.get_field("applicant_type").choices}:
            errors.append("Invalid applicant type")

        if errors:
            context = {
                "errors": errors,
                "client_type_choices": Application._meta.get_field("client_type").choices,
                "application_type_choices": Application._meta.get_field("application_type").choices,
                "applicant_type_choices": Application._meta.get_field("applicant_type").choices,
                "city_choices": Application._meta.get_field("city").choices,
                "values": request.POST,
                "site_settings": site_settings,
            }
            return render(request, "cases/application_create.html", context)

        app = Application(
            folder_number=folder_number,
            client_type=client_type,
            application_type=application_type,
            application_name=application_name,
            trademark_no=trademark_no,
            case_no=case_no,
            class_numbers=class_numbers,
            filing_date=filing_date,
            application_year=application_year or None,
            applicant_name=applicant_name,
            trading_as=trading_as,
            applicant_type=applicant_type or Application._meta.get_field("applicant_type").default,
            address=address,
            city=city,
            agent_name=agent_name,
            agent_address=agent_address,
            jurisdiction=jurisdiction,
            dispatch_status=dispatch_status,
            current_stage=Stage.STAGE_1,
            current_sub_stage=SubStage.FILED,
            current_status="",
        )
        if logo:
            app.logo = logo

        app.save()

        for f in files:
            FileUpload.objects.create(application=app, file=f)

        return redirect("cases:application_detail", pk=app.pk)

    context = {
        "client_type_choices": Application._meta.get_field("client_type").choices,
        "application_type_choices": Application._meta.get_field("application_type").choices,
        "applicant_type_choices": Application._meta.get_field("applicant_type").choices,
        "city_choices": Application._meta.get_field("city").choices,
        "values": {},
        "site_settings": site_settings,
    }
    return render(request, "cases/application_create.html", context)


@login_required
def application_detail(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)

    today = timezone.localdate()
    users = get_user_model().objects.all().order_by("username")

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

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
        "site_settings": site_settings,
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
