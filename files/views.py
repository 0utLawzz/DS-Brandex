from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
import csv
import io

from django.contrib.auth import get_user_model

from .models import (
    Application,
    AgentChoice,
    Assignment,
    DocumentLink,
    Event,
    EventType,
    FileUpload,
    SiteSettings,
    Stage,
    SubStage,
    SUB_STAGE_TO_STAGE,
)


@login_required
def application_list(request: HttpRequest):
    q             = (request.GET.get("q") or "").strip()
    stage_filter  = (request.GET.get("stage") or "").strip()
    ct_filter     = (request.GET.get("client_type") or "").strip()
    agent_filter  = (request.GET.get("agent") or "").strip()

    applications = Application.objects.all()

    if q:
        applications = applications.filter(
            models.Q(trademark_no__icontains=q)
            | models.Q(case_number__icontains=q)
            | models.Q(application_name__icontains=q)
            | models.Q(applicant_name__icontains=q)
            | models.Q(ref_number__icontains=q)
        )

    if stage_filter:
        try:
            applications = applications.filter(current_stage=int(stage_filter))
        except ValueError:
            pass

    if ct_filter:
        applications = applications.filter(client_type=ct_filter)

    if agent_filter:
        applications = applications.filter(agent_name=agent_filter)

    paginator   = Paginator(applications, 100)
    page_number = request.GET.get("page", 1)
    page_obj    = paginator.get_page(page_number)

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    context = {
        "page_obj": page_obj,
        "q": q,
        "stage_filter": stage_filter,
        "ct_filter": ct_filter,
        "agent_filter": agent_filter,
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
        case_number = (request.POST.get("case_number") or "").strip()
        client_type = (request.POST.get("client_type") or "").strip()
        client_id = request.POST.get("client_id") or None
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
        demand_note_date = request.POST.get("demand_note_date") or None
        logo = request.FILES.get("logo")
        files = request.FILES.getlist("files")

        errors = []
        if case_number and Application.objects.filter(case_number=case_number).exists():
            errors.append("Case number already exists")
        if not case_number and not client_id:
            errors.append("Either case number or client ID is required")
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

        # TM duplicate warning
        tm_duplicate = None
        if trademark_no and Application.objects.filter(trademark_no=trademark_no).exists():
            tm_duplicate = Application.objects.filter(trademark_no=trademark_no).first()
            errors.append(f"WARNING: TM No {trademark_no} already exists in case {tm_duplicate.case_number} ({tm_duplicate.application_name})")

        if errors:
            context = {
                "errors": errors,
                "client_type_choices": Application._meta.get_field("client_type").choices,
                "application_type_choices": Application._meta.get_field("application_type").choices,
                "applicant_type_choices": Application._meta.get_field("applicant_type").choices,
                "city_choices": Application._meta.get_field("city").choices,
                "agent_choices": AgentChoice.choices,
                "values": request.POST,
                "site_settings": site_settings,
            }
            return render(request, "cases/application_create.html", context)

        app = Application(
            case_number=case_number,
            client_type=client_type,
            client_id=client_id,
            folder_number=folder_number,
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
            demand_note_date=demand_note_date,
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
        "agent_choices": AgentChoice.choices,
        "city_choices": Application._meta.get_field("city").choices,
        "values": {},
        "site_settings": site_settings,
    }
    return render(request, "cases/application_create.html", context)


@login_required
def application_edit(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    if request.method == "POST":
        folder_number = (request.POST.get("folder_number") or "").strip()
        case_number = (request.POST.get("case_number") or "").strip()
        client_type = (request.POST.get("client_type") or "").strip()
        client_id = request.POST.get("client_id") or None
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
        demand_note_date = request.POST.get("demand_note_date") or None
        logo = request.FILES.get("logo")
        files = request.FILES.getlist("files")

        errors = []
        if case_number and case_number != application.case_number and Application.objects.filter(case_number=case_number).exists():
            errors.append("Case number already exists")
        if not case_number and not client_id:
            errors.append("Either case number or client ID is required")
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
                "agent_choices": AgentChoice.choices,
                "application": application,
                "site_settings": site_settings,
            }
            return render(request, "cases/application_edit.html", context)

        application.case_number = case_number
        application.client_type = client_type
        application.client_id = client_id
        application.folder_number = folder_number
        application.application_type = application_type
        application.application_name = application_name
        application.trademark_no = trademark_no
        application.case_no = case_no
        application.class_numbers = class_numbers
        application.filing_date = filing_date
        application.application_year = application_year or None
        application.applicant_name = applicant_name
        application.trading_as = trading_as
        application.applicant_type = applicant_type or Application._meta.get_field("applicant_type").default
        application.address = address
        application.city = city
        application.agent_name = agent_name
        application.agent_address = agent_address
        application.jurisdiction = jurisdiction
        application.dispatch_status = dispatch_status
        application.demand_note_date = demand_note_date
        if logo:
            application.logo = logo

        application.save()

        for f in files:
            FileUpload.objects.create(application=application, file=f)

        return redirect("cases:application_detail", pk=application.pk)

    context = {
        "client_type_choices": Application._meta.get_field("client_type").choices,
        "application_type_choices": Application._meta.get_field("application_type").choices,
        "applicant_type_choices": Application._meta.get_field("applicant_type").choices,
        "city_choices": Application._meta.get_field("city").choices,
        "agent_choices": AgentChoice.choices,
        "application": application,
        "site_settings": site_settings,
    }
    return render(request, "cases/application_edit.html", context)


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
        file = request.FILES.get("file")
        deadline_date = request.POST.get("deadline_date") or None
        stage = request.POST.get("stage") or None
        sub_stage = (request.POST.get("sub_stage") or "").strip()

        computed_stage = None
        if sub_stage and sub_stage in SUB_STAGE_TO_STAGE:
            computed_stage = int(SUB_STAGE_TO_STAGE[sub_stage])
        elif stage:
            try:
                computed_stage = int(stage)
            except (TypeError, ValueError):
                computed_stage = None

        if computed_stage and computed_stage >= Stage.STAGE_2 and not application.proceed_to_stage2:
            messages.error(request, "Stage 1 → 2 proceed is required before moving to Stage 2+")
            return redirect("cases:application_detail", pk=application.pk)

        Event.objects.create(
            application=application,
            event_type=event_type,
            notes=notes,
            document_link=document_link,
            file=file,
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
        due_date_str = request.POST.get("due_date") or None
        status = (request.POST.get("status") or "pending").strip()
        notes = (request.POST.get("notes") or "").strip()

        due_date = None
        if due_date_str:
            from datetime import datetime
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

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
        file = request.FILES.get("file")
        preview_enabled = request.POST.get("preview_enabled") == "on"

        if file_path or file:
            DocumentLink.objects.create(
                application=application,
                file_type=file_type,
                file_path=file_path,
                file=file,
                preview_enabled=preview_enabled,
            )

        return redirect("cases:application_detail", pk=application.pk)

    return redirect("cases:application_detail", pk=application.pk)


@login_required
def export_application_pdf(request: HttpRequest, pk: int):
    """Render print-ready HTML PDF view"""
    application = get_object_or_404(Application, pk=pk)
    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    context = {
        "application": application,
        "site_settings": site_settings,
    }
    return render(request, "cases/application_pdf.html", context)


@login_required
def dashboard(request: HttpRequest):
    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    total_count   = Application.objects.count()
    stage1_count  = Application.objects.filter(current_stage=1).count()
    stage2_count  = Application.objects.filter(current_stage=2).count()
    stage3_count  = Application.objects.filter(current_stage=3).count()
    stage4_count  = Application.objects.filter(current_stage=4).count()
    stopped_count = Application.objects.exclude(stop_status="").count()

    pending_assignments = Assignment.objects.filter(status="pending").count()
    overdue_assignments  = Assignment.objects.filter(status="overdue").count()

    recent_cases = Application.objects.order_by("-updated_at")[:15]

    overdue_list = Assignment.objects.filter(status="overdue").select_related(
        "application", "assigned_to"
    ).order_by("due_date")[:10]

    agent_stats_qs = (
        Application.objects
        .exclude(agent_name="")
        .values("agent_name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    agent_stats = [{"agent_name": r["agent_name"], "count": r["count"]} for r in agent_stats_qs]

    ct_labels = {"X": "X — Clients", "A": "A — Consultants", "N": "N — Noor Baaf"}
    ct_qs = (
        Application.objects
        .values("client_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    client_type_stats = []
    for r in ct_qs:
        pct = round((r["count"] / total_count * 100)) if total_count else 0
        client_type_stats.append({
            "client_type": r["client_type"],
            "label": ct_labels.get(r["client_type"], r["client_type"]),
            "count": r["count"],
            "pct": pct,
        })

    SUBSTAGE_STAGE_MAP = {
        "filed": (1, "Filed"), "ack_received": (1, "Acknowledgement Received"),
        "examination_done": (1, "Examination"), "acceptance_done": (2, "Acceptance Done"),
        "hearing": (2, "Hearing"), "published": (2, "Published"),
        "demand_note_issue": (3, "Demand Note Issue"), "demand_note_received": (3, "Demand Note Received"),
        "demand_note_submitted": (3, "Demand Note Submitted"), "certificate_issued": (3, "Certificate Issued"),
        "certificate_received": (3, "Certificate Received"), "certificate_print": (3, "Certificate Print"),
        "certificate_dispatch": (3, "Certificate Dispatch"), "opposition_received": (4, "Opposition Received"),
        "opposition_withdrawn": (4, "Opposition Withdrawn"), "opposition_filed": (4, "Opposition Filed"),
    }

    ss_qs = (
        Application.objects
        .exclude(current_sub_stage="")
        .values("current_sub_stage")
        .annotate(count=Count("id"))
        .order_by("-count")[:15]
    )
    substage_stats = []
    for r in ss_qs:
        stage_num, label = SUBSTAGE_STAGE_MAP.get(r["current_sub_stage"], (0, r["current_sub_stage"]))
        substage_stats.append({"key": r["current_sub_stage"], "label": label, "stage": stage_num, "count": r["count"]})

    context = {
        "site_settings": site_settings,
        "total_count": total_count,
        "stage1_count": stage1_count,
        "stage2_count": stage2_count,
        "stage3_count": stage3_count,
        "stage4_count": stage4_count,
        "stopped_count": stopped_count,
        "pending_assignments": pending_assignments,
        "overdue_assignments": overdue_assignments,
        "recent_cases": recent_cases,
        "overdue_list": overdue_list,
        "agent_stats": agent_stats,
        "client_type_stats": client_type_stats,
        "substage_stats": substage_stats,
        "today": timezone.localdate(),
    }
    return render(request, "cases/dashboard.html", context)


@login_required
def my_tasks(request: HttpRequest):
    today = timezone.localdate()
    current_user = request.user

    my_assignments = Assignment.objects.filter(
        assigned_to=current_user
    ).select_related('application').order_by('due_date', '-assigned_date')

    pending_assignments = my_assignments.filter(status="pending")
    overdue_assignments = my_assignments.filter(status="overdue")
    completed_assignments = my_assignments.filter(status="completed")

    my_application_ids = my_assignments.values_list('application_id', flat=True)
    my_events = Event.objects.filter(
        application_id__in=my_application_ids,
        deadline_date__isnull=False
    ).select_related('application').order_by('deadline_date')

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    context = {
        "pending_assignments": pending_assignments,
        "overdue_assignments": overdue_assignments,
        "completed_assignments": completed_assignments,
        "my_events": my_events,
        "today": today,
        "site_settings": site_settings,
    }
    return render(request, "cases/my_tasks.html", context)


@login_required
def dispatch_certificate_received(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    application.current_sub_stage = SubStage.CERTIFICATE_RECEIVED
    application.dispatch_status = "Certificate Received"
    application.save()
    Event.objects.create(
        application=application, event_type=EventType.CERTIFICATE,
        notes="Certificate marked as received (dispatch workflow)",
        sub_stage=SubStage.CERTIFICATE_RECEIVED, stage=Stage.STAGE_3,
    )
    return redirect("cases:application_detail", pk=pk)


@login_required
def proceed_to_stage2(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    if request.method == "POST":
        application.proceed_to_stage2 = True
        application.proceed_datetime = timezone.now()
        application.save(update_fields=["proceed_to_stage2", "proceed_datetime", "updated_at"])
        messages.success(request, "Proceed set. Stage 2 is now unlocked.")
    return redirect("cases:application_detail", pk=pk)


@login_required
def stop_case(request: HttpRequest, pk: int):
    """Set stop status (Closed / Abandoned / By Client) on a case"""
    application = get_object_or_404(Application, pk=pk)
    if request.method == "POST":
        stop_status = (request.POST.get("stop_status") or "").strip()
        if stop_status:
            application.stop_status = stop_status
            application.save(update_fields=["stop_status", "updated_at"])
            messages.success(request, f"Case marked as: {application.get_stop_status_display()}")
        else:
            # Clear stop status
            application.stop_status = ""
            application.save(update_fields=["stop_status", "updated_at"])
            messages.success(request, "Stop status cleared.")
    return redirect("cases:application_detail", pk=pk)


@login_required
def update_journal(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    if request.method == "POST":
        journal_number = request.POST.get("journal_number") or None
        journal_date = request.POST.get("journal_date") or None
        journal_screenshot = request.FILES.get("journal_screenshot")

        if journal_number is not None:
            try:
                application.journal_number = int(journal_number)
            except (TypeError, ValueError):
                application.journal_number = None
        application.journal_date = journal_date or None
        if journal_screenshot:
            application.journal_screenshot = journal_screenshot

        application.save(update_fields=["journal_number", "journal_date", "journal_screenshot", "updated_at"])
        messages.success(request, "Journal details updated.")
    return redirect("cases:application_detail", pk=pk)


@login_required
def dispatch_certificate_print(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    application.current_sub_stage = SubStage.CERTIFICATE_PRINT
    application.dispatch_status = "Certificate Printed"
    application.save()
    Event.objects.create(
        application=application, event_type=EventType.CERTIFICATE,
        notes="Certificate marked as printed (dispatch workflow)",
        sub_stage=SubStage.CERTIFICATE_PRINT, stage=Stage.STAGE_3,
    )
    return redirect("cases:application_detail", pk=pk)


@login_required
def dispatch_certificate_dispatch(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    application.current_sub_stage = SubStage.CERTIFICATE_DISPATCH
    application.dispatch_status = "Certificate Dispatched"
    application.save()
    Event.objects.create(
        application=application, event_type=EventType.CERTIFICATE,
        notes="Certificate marked as dispatched (dispatch workflow)",
        sub_stage=SubStage.CERTIFICATE_DISPATCH, stage=Stage.STAGE_3,
    )
    return redirect("cases:application_detail", pk=pk)


@login_required
def search_by_tm(request: HttpRequest):
    q = (request.GET.get("q") or "").strip()
    applications = []
    if q:
        applications = Application.objects.filter(trademark_no__icontains=q)

    paginator = Paginator(applications, 100)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    context = {"page_obj": page_obj, "q": q, "site_settings": site_settings}
    return render(request, "cases/application_list.html", context)


@login_required
def export_applications_csv(request: HttpRequest):
    applications = Application.objects.all().order_by('-created_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="applications_export.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Ref #', 'Case Number', 'Client Type', 'Client ID', 'Sequence',
        'Folder Number', 'Application Name', 'Application Type',
        'Trademark No', 'Case No', 'Class Numbers', 'Filing Date',
        'Application Year', 'Applicant Name', 'Trading As',
        'Applicant Type', 'Address', 'City', 'Agent Name',
        'Agent Address', 'Jurisdiction', 'Dispatch Status',
        'Demand Note Date', 'Current Stage', 'Current Sub Stage',
        'Current Status', 'Created At', 'Updated At'
    ])
    for app in applications:
        writer.writerow([
            app.ref_number or '',
            app.case_number or '',
            app.client_type or '',
            app.client_id or '',
            app.sequence or '',
            app.folder_number or '',
            app.application_name or '',
            app.application_type or '',
            app.trademark_no or '',
            app.case_no or '',
            app.class_numbers or '',
            app.filing_date.strftime('%Y-%m-%d') if app.filing_date else '',
            app.application_year or '',
            app.applicant_name or '',
            app.trading_as or '',
            app.applicant_type or '',
            app.address or '',
            app.city or '',
            app.agent_name or '',
            app.agent_address or '',
            app.jurisdiction or '',
            app.dispatch_status or '',
            app.demand_note_date.strftime('%Y-%m-%d') if app.demand_note_date else '',
            app.current_stage or '',
            app.current_sub_stage or '',
            app.current_status or '',
            app.created_at.strftime('%Y-%m-%d %H:%M:%S') if app.created_at else '',
            app.updated_at.strftime('%Y-%m-%d %H:%M:%S') if app.updated_at else ''
        ])
    return response


@login_required
def assignments_view(request: HttpRequest):
    status_filter = (request.GET.get("status") or "all").strip()

    assignments = Assignment.objects.select_related(
        "application", "assigned_to", "created_by"
    ).order_by("due_date", "-assigned_date")

    if status_filter == "pending":
        assignments = assignments.filter(status="pending")
    elif status_filter == "overdue":
        assignments = assignments.filter(status="overdue")
    elif status_filter == "completed":
        assignments = assignments.filter(status="completed")

    AGENTS = [
        {"name": "Fasial", "city": "LHR"},
        {"name": "Rashid", "city": "ISB"},
        {"name": "Uzma",   "city": "KRI"},
        {"name": "Sulman", "city": "LHR"},
    ]

    agent_summary = []
    for ag in AGENTS:
        qs = Assignment.objects.filter(application__agent_name=ag["name"])
        agent_summary.append({
            "name": ag["name"], "city": ag["city"],
            "pending":   qs.filter(status="pending").count(),
            "overdue":   qs.filter(status="overdue").count(),
            "completed": qs.filter(status="completed").count(),
        })

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    context = {
        "assignments": assignments,
        "agent_summary": agent_summary,
        "status_filter": status_filter,
        "site_settings": site_settings,
    }
    return render(request, "cases/assignments.html", context)


@login_required
def complete_assignment(request: HttpRequest, pk: int):
    if request.method == "POST":
        assignment = get_object_or_404(Assignment, pk=pk)
        assignment.status = "completed"
        assignment.save()
        messages.success(request, "Assignment marked as completed.")
    return redirect("cases:assignments")


@login_required
def check_tm_duplicate(request: HttpRequest):
    tm_no = (request.GET.get("tm_no") or "").strip()
    exclude_pk = request.GET.get("exclude_pk")

    if not tm_no:
        return JsonResponse({"exists": False})

    qs = Application.objects.filter(trademark_no=tm_no)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)

    if qs.exists():
        app = qs.first()
        return JsonResponse({
            "exists": True,
            "case_number": app.case_number,
            "application_name": app.application_name,
            "ref_number": app.ref_number or "",
            "stage": app.current_stage,
        })

    return JsonResponse({"exists": False})


@login_required
def application_delete(request: HttpRequest, pk: int):
    if not request.user.is_staff:
        messages.error(request, "Only admin users can delete cases.")
        return redirect("cases:application_detail", pk=pk)

    application = get_object_or_404(Application, pk=pk)

    if request.method == "POST":
        case_num = application.case_number
        application.delete()
        messages.success(request, f"Case {case_num} deleted.")
        return redirect("cases:application_list")

    site_settings = SiteSettings.objects.first()
    return render(request, "cases/application_confirm_delete.html", {
        "application": application,
        "site_settings": site_settings,
    })


@login_required
def import_applications_csv(request: HttpRequest):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            return render(request, 'cases/import_applications.html', {
                'error': 'Please select a CSV file to import.'
            })

        if not csv_file.name.endswith('.csv'):
            return render(request, 'cases/import_applications.html', {
                'error': 'Please upload a CSV file.'
            })

        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        imported_count = 0
        errors = []

        for row in reader:
            try:
                case_number = row.get('Case Number', '').strip()
                if case_number and Application.objects.filter(case_number=case_number).exists():
                    errors.append(f"Case {case_number} already exists - skipped")
                    continue

                app = Application(
                    case_number=case_number or None,
                    client_type=row.get('Client Type', 'X') or 'X',
                    client_id=int(row.get('Client ID', 0)) if row.get('Client ID') else None,
                    sequence=int(row.get('Sequence', 0)) if row.get('Sequence') else None,
                    folder_number=row.get('Folder Number', '').strip() or '',
                    application_name=row.get('Application Name', '').strip(),
                    application_type=row.get('Application Type', 'trademark') or 'trademark',
                    trademark_no=row.get('Trademark No', '').strip() or '',
                    case_no=row.get('Case No', '').strip() or '',
                    class_numbers=row.get('Class Numbers', '').strip() or '',
                    filing_date=row.get('Filing Date', '').strip() or None,
                    application_year=row.get('Application Year', '').strip() or None,
                    applicant_name=row.get('Applicant Name', '').strip(),
                    trading_as=row.get('Trading As', '').strip() or '',
                    applicant_type=row.get('Applicant Type', '').strip() or '',
                    address=row.get('Address', '').strip() or '',
                    city=row.get('City', '').strip() or '',
                    agent_name=row.get('Agent Name', '').strip() or '',
                    agent_address=row.get('Agent Address', '').strip() or '',
                    jurisdiction=row.get('Jurisdiction', '').strip() or '',
                    dispatch_status=row.get('Dispatch Status', '').strip() or '',
                    demand_note_date=row.get('Demand Note Date', '').strip() or None,
                    current_stage=int(row.get('Current Stage', 1)) if row.get('Current Stage') else 1,
                    current_sub_stage=row.get('Current Sub Stage', 'filed') or 'filed',
                    current_status=row.get('Current Status', '').strip() or '',
                )
                app.save()
                imported_count += 1

            except Exception as e:
                errors.append(f"Error importing row: {str(e)}")
                continue

        return render(request, 'cases/import_applications.html', {
            'success': True,
            'imported_count': imported_count,
            'errors': errors
        })

    return render(request, 'cases/import_applications.html')
