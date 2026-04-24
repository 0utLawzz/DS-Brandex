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
            models.Q(case_number__icontains=q)
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
        logo = request.FILES.get("logo")
        files = request.FILES.getlist("files")

        errors = []
        # Case number is optional now - will be auto-generated if not provided
        # If case_number is provided, it must be unique
        if case_number and Application.objects.filter(case_number=case_number).exists():
            errors.append("Case number already exists")
        # If case_number is not provided, client_id is required for auto-generation
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
                "values": request.POST,
                "site_settings": site_settings,
            }
            return render(request, "cases/application_create.html", context)

        app = Application(
            case_number=case_number,
            client_type=client_type,
            client_id=client_id,
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
def application_edit(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    if request.method == "POST":
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
                "application": application,
                "site_settings": site_settings,
            }
            return render(request, "cases/application_edit.html", context)

        application.case_number = case_number
        application.client_type = client_type
        application.client_id = client_id
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

        # Convert due_date string to date object if provided
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
    application = get_object_or_404(Application, pk=pk)
    from xhtml2pdf import pisa
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    import datetime

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    html_string = render_to_string('cases/application_pdf.html', {
        'application': application,
        'events': application.events.all(),
        'assignments': application.assignments.all(),
        'documents': application.documents.all(),
        'today': datetime.date.today(),
        'site_settings': site_settings,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{application.case_number}_application.pdf"'
    
    pisa.CreatePDF(html_string, dest=response)
    return response


@login_required
def dashboard(request: HttpRequest):
    today = timezone.localdate()

    # Get overdue assignments
    overdue_assignments = Assignment.objects.filter(
        due_date__lt=today,
        status__in=["pending", "overdue"]
    ).select_related('application', 'assigned_to').order_by('due_date')[:50]

    # Get assignments due soon (within 3 days)
    soon_due_date = today + timezone.timedelta(days=3)
    soon_assignments = Assignment.objects.filter(
        due_date__range=[today, soon_due_date],
        status="pending"
    ).select_related('application', 'assigned_to').order_by('due_date')[:50]

    # Get events with deadlines
    overdue_events = Event.objects.filter(
        deadline_date__lt=today
    ).select_related('application').order_by('deadline_date')[:50]

    soon_events = Event.objects.filter(
        deadline_date__range=[today, soon_due_date]
    ).select_related('application').order_by('deadline_date')[:50]

    # Get applications by stage summary
    stage_summary = {}
    for stage_choice in Stage.choices:
        stage_summary[stage_choice[1]] = Application.objects.filter(current_stage=stage_choice[0]).count()

    # Recent applications
    recent_applications = Application.objects.order_by('-created_at')[:10]

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    context = {
        "overdue_assignments": overdue_assignments,
        "soon_assignments": soon_assignments,
        "overdue_events": overdue_events,
        "soon_events": soon_events,
        "stage_summary": stage_summary,
        "recent_applications": recent_applications,
        "today": today,
        "site_settings": site_settings,
    }
    return render(request, "cases/dashboard.html", context)


@login_required
def my_tasks(request: HttpRequest):
    today = timezone.localdate()
    current_user = request.user

    # Get assignments for current user
    my_assignments = Assignment.objects.filter(
        assigned_to=current_user
    ).select_related('application').order_by('due_date', '-assigned_date')

    # Separate by status
    pending_assignments = my_assignments.filter(status="pending")
    overdue_assignments = my_assignments.filter(status="overdue")
    completed_assignments = my_assignments.filter(status="completed")

    # Get events with deadlines for applications assigned to user
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
    """Mark certificate as received in dispatch workflow"""
    application = get_object_or_404(Application, pk=pk)
    application.current_sub_stage = SubStage.CERTIFICATE_RECEIVED
    application.dispatch_status = "Certificate Received"
    application.save()

    Event.objects.create(
        application=application,
        event_type=EventType.CERTIFICATE,
        notes="Certificate marked as received (dispatch workflow)",
        sub_stage=SubStage.CERTIFICATE_RECEIVED,
        stage=Stage.STAGE_4,
    )

    return redirect("cases:application_detail", pk=pk)


@login_required
def dispatch_certificate_print(request: HttpRequest, pk: int):
    """Mark certificate as printed in dispatch workflow"""
    application = get_object_or_404(Application, pk=pk)
    application.current_sub_stage = SubStage.CERTIFICATE_PRINT
    application.dispatch_status = "Certificate Printed"
    application.save()

    Event.objects.create(
        application=application,
        event_type=EventType.CERTIFICATE,
        notes="Certificate marked as printed (dispatch workflow)",
        sub_stage=SubStage.CERTIFICATE_PRINT,
        stage=Stage.STAGE_4,
    )

    return redirect("cases:application_detail", pk=pk)


@login_required
def dispatch_certificate_dispatch(request: HttpRequest, pk: int):
    """Mark certificate as dispatched in dispatch workflow"""
    application = get_object_or_404(Application, pk=pk)
    application.current_sub_stage = SubStage.CERTIFICATE_DISPATCH
    application.dispatch_status = "Certificate Dispatched"
    application.save()

    Event.objects.create(
        application=application,
        event_type=EventType.CERTIFICATE,
        notes="Certificate marked as dispatched (dispatch workflow)",
        sub_stage=SubStage.CERTIFICATE_DISPATCH,
        stage=Stage.STAGE_4,
    )

    return redirect("cases:application_detail", pk=pk)


@login_required
def search_by_tm(request: HttpRequest):
    """Search applications by Trademark Number"""
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

    context = {
        "page_obj": page_obj,
        "q": q,
        "site_settings": site_settings,
    }
    return render(request, "cases/search_tm.html", context)
