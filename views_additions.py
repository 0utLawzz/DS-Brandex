# ═══════════════════════════════════════════════════════════════
# ADDITIONAL VIEWS — append these to the existing views.py
# OR replace the dashboard() function with the one below
# ═══════════════════════════════════════════════════════════════

# Add these imports at the top of views.py:
# from django.db.models import Count
# from django.http import JsonResponse

# ─────────────────────────────────────────────────────────────
# DASHBOARD (replace existing dashboard view)
# ─────────────────────────────────────────────────────────────
@login_required
def dashboard(request: HttpRequest):
    from django.db.models import Count

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    # Stage counts
    total_count   = Application.objects.count()
    stage1_count  = Application.objects.filter(current_stage=1).count()
    stage2_count  = Application.objects.filter(current_stage=2).count()
    stage3_count  = Application.objects.filter(current_stage=3).count()
    stage4_count  = Application.objects.filter(current_stage=4).count()
    stopped_count = Application.objects.exclude(stop_status="").count()

    # Assignment counts
    pending_assignments = Assignment.objects.filter(status="pending").count()
    overdue_assignments  = Assignment.objects.filter(status="overdue").count()

    # Recent cases (last 15 updated)
    recent_cases = Application.objects.order_by("-updated_at")[:15]

    # Overdue assignment list
    overdue_list = Assignment.objects.filter(status="overdue").select_related(
        "application", "assigned_to"
    ).order_by("due_date")[:10]

    # Agent stats
    agent_stats_qs = (
        Application.objects
        .exclude(agent_name="")
        .values("agent_name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    agent_stats = [{"agent_name": r["agent_name"], "count": r["count"]} for r in agent_stats_qs]

    # Client type stats with percentage
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

    # Sub-stage stats
    SUBSTAGE_STAGE_MAP = {
        "filed": (1, "Filed"),
        "ack_received": (1, "Acknowledgement Received"),
        "examination_done": (1, "Examination"),
        "acceptance_done": (2, "Acceptance Done"),
        "hearing": (2, "Hearing"),
        "published": (2, "Published"),
        "demand_note_issue": (3, "Demand Note Issue"),
        "demand_note_received": (3, "Demand Note Received"),
        "demand_note_submitted": (3, "Demand Note Submitted"),
        "certificate_issued": (3, "Certificate Issued"),
        "certificate_received": (3, "Certificate Received"),
        "certificate_print": (3, "Certificate Print"),
        "certificate_dispatch": (3, "Certificate Dispatch"),
        "opposition_received": (4, "Opposition Received"),
        "opposition_withdrawn": (4, "Opposition Withdrawn"),
        "opposition_filed": (4, "Opposition Filed"),
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
        substage_stats.append({
            "key": r["current_sub_stage"],
            "label": label,
            "stage": stage_num,
            "count": r["count"],
        })

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
    }
    return render(request, "cases/dashboard.html", context)


# ─────────────────────────────────────────────────────────────
# APPLICATION LIST (replace existing — adds filter params)
# ─────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────
# ASSIGNMENTS PAGE
# ─────────────────────────────────────────────────────────────
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

    # Agent summary cards
    AGENTS = [
        {"name": "Fasial",  "city": "LHR"},
        {"name": "Rashid",  "city": "ISB"},
        {"name": "Uzma",    "city": "KRI"},
        {"name": "Sulman",  "city": "LHR"},
    ]

    agent_summary = []
    for ag in AGENTS:
        qs = Assignment.objects.filter(
            application__agent_name=ag["name"]
        )
        agent_summary.append({
            "name": ag["name"],
            "city": ag["city"],
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


# ─────────────────────────────────────────────────────────────
# COMPLETE ASSIGNMENT
# ─────────────────────────────────────────────────────────────
@login_required
def complete_assignment(request: HttpRequest, pk: int):
    if request.method == "POST":
        assignment = get_object_or_404(Assignment, pk=pk)
        assignment.status = "completed"
        assignment.save()
        messages.success(request, "Assignment marked as completed.")
    return redirect("cases:assignments")


# ─────────────────────────────────────────────────────────────
# TM DUPLICATE CHECK (AJAX)
# ─────────────────────────────────────────────────────────────
@login_required
def check_tm_duplicate(request: HttpRequest):
    """AJAX endpoint: returns JSON {exists: bool, case_number, application_name}"""
    from django.http import JsonResponse
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


# ─────────────────────────────────────────────────────────────
# APPLICATION DELETE (staff only)
# ─────────────────────────────────────────────────────────────
@login_required
def application_delete(request: HttpRequest, pk: int):
    if not request.user.is_staff:
        messages.error(request, "Only admin users can delete cases.")
        return redirect("cases:application_detail", pk=pk)

    application = get_object_or_404(Application, pk=pk)

    if request.method == "POST":
        case_num = application.case_number
        # Log deletion in audit before deleting
        from .models import AuditLog, AuditActionType
        # Note: since the app is being deleted, log to system or skip
        application.delete()
        messages.success(request, f"Case {case_num} deleted.")
        return redirect("cases:application_list")

    site_settings = SiteSettings.objects.first()
    return render(request, "cases/application_confirm_delete.html", {
        "application": application,
        "site_settings": site_settings,
    })


# ─────────────────────────────────────────────────────────────
# EXPORT PDF (replace existing if exists)
# ─────────────────────────────────────────────────────────────
@login_required
def export_application_pdf(request: HttpRequest, pk: int):
    application = get_object_or_404(Application, pk=pk)
    site_settings = SiteSettings.objects.first()
    if not site_settings:
        site_settings = SiteSettings.objects.create()

    context = {
        "application": application,
        "site_settings": site_settings,
    }
    return render(request, "cases/application_pdf.html", context)
