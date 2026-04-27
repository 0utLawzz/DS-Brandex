from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
import csv
import io

from django.contrib.auth import get_user_model

from .models import Application, Assignment, DocumentLink, Event, EventType, Stage, SubStage, FileUpload, SiteSettings, AgentChoice


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
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib import colors
    from django.http import HttpResponse
    import datetime

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{application.case_number}_application.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#722F37'),
        spaceAfter=12
    )
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2E5339'),
        spaceAfter=6
    )

    elements = []

    # Header with company name
    if site_settings.company_logo and site_settings.company_logo.path:
        try:
            img = Image(site_settings.company_logo.path, width=2*inch, height=1*inch)
            elements.append(img)
        except:
            pass
    
    elements.append(Paragraph(site_settings.company_name or "Office IP Case Platform", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Case Information
    elements.append(Paragraph("Case Information", header_style))
    case_data = [
        ["Case #", application.case_number],
        ["Client Type", application.get_client_type_display()],
        ["Application Type", application.get_application_type_display()],
        ["Application Name", application.application_name],
        ["Trademark No", application.trademark_no],
        ["Case No (Official)", application.case_no or "-"],
        ["Class", application.class_numbers],
        ["Filing Date", application.filing_date.strftime("%d-%b-%Y") if application.filing_date else ""],
        ["Applicant", application.applicant_name],
        ["Trading As", application.trading_as],
        ["City", application.city],
        ["Agent", application.agent_name],
        ["Dispatch Status", application.dispatch_status],
    ]
    case_table = Table(case_data, colWidths=[2*inch, 4*inch])
    case_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(case_table)
    elements.append(Spacer(1, 0.2*inch))

    # Status
    elements.append(Paragraph("Status", header_style))
    status_data = [
        ["Stage", application.get_current_stage_display()],
        ["Sub-Status", application.get_current_sub_stage_display()],
        ["Status", application.current_status],
    ]
    status_table = Table(status_data, colWidths=[2*inch, 4*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 0.2*inch))

    # Timeline
    elements.append(Paragraph("Timeline", header_style))
    timeline_data = [["Date/Time", "Event Type", "Notes", "Deadline"]]
    for e in application.events.all():
        timeline_data.append([
            e.event_datetime.strftime("%d-%b-%Y %H:%M"),
            f"{e.get_event_type_display()} - {e.get_sub_stage_display()}" if e.sub_stage else e.get_event_type_display(),
            e.notes,
            e.deadline_date.strftime("%d-%b-%Y") if e.deadline_date else ""
        ])
    timeline_table = Table(timeline_data, colWidths=[1.2*inch, 1.5*inch, 2*inch, 1.3*inch])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    elements.append(timeline_table)
    elements.append(Spacer(1, 0.2*inch))

    # Assignments
    elements.append(Paragraph("Assignments (CASES)", header_style))
    assignment_data = [["Assigned To", "Due Date", "Status", "Notes"]]
    for a in application.assignments.all():
        assignment_data.append([
            a.assigned_to.username if a.assigned_to else "(Unassigned)",
            a.due_date.strftime("%d-%b-%Y") if a.due_date else "",
            a.get_status_display(),
            a.notes
        ])
    assignment_table = Table(assignment_data, colWidths=[1.2*inch, 1*inch, 1*inch, 2.8*inch])
    assignment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    elements.append(assignment_table)
    elements.append(Spacer(1, 0.2*inch))

    # Documents
    elements.append(Paragraph("Documents", header_style))
    doc_data = [["Type", "Link"]]
    for d in application.documents.all():
        doc_data.append([d.get_file_type_display(), d.file_path])
    doc_table = Table(doc_data, colWidths=[1.5*inch, 4.5*inch])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    elements.append(doc_table)

    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        f"{site_settings.company_name or 'Office IP Case Platform'} | Generated: {datetime.datetime.now().strftime('%d-%b-%Y %H:%M')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    ))

    doc.build(elements)
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
    return render(request, "cases/application_list.html", context)


@login_required
def export_applications_csv(request: HttpRequest):
    """Export all applications to CSV file"""
    applications = Application.objects.all().order_by('-created_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="applications_export.csv"'

    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Case Number', 'Client Type', 'Client ID', 'Sequence',
        'Folder Number', 'Application Name', 'Application Type',
        'Trademark No', 'Case No', 'Class Numbers', 'Filing Date',
        'Application Year', 'Applicant Name', 'Trading As',
        'Applicant Type', 'Address', 'City', 'Agent Name',
        'Agent Address', 'Jurisdiction', 'Dispatch Status',
        'Demand Note Date', 'Current Stage', 'Current Sub Stage',
        'Current Status', 'Created At', 'Updated At'
    ])

    # Write data rows
    for app in applications:
        writer.writerow([
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
def import_applications_csv(request: HttpRequest):
    """Import applications from CSV file"""
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

        # Read CSV file
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        imported_count = 0
        errors = []

        for row in reader:
            try:
                # Skip if case number already exists
                case_number = row.get('Case Number', '').strip()
                if case_number and Application.objects.filter(case_number=case_number).exists():
                    errors.append(f"Case {case_number} already exists - skipped")
                    continue

                # Create application from CSV row
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
