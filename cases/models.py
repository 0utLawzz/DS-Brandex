from django.conf import settings
from django.db import models
from django.utils import timezone

from .current_user import get_current_user


class ApplicantType(models.TextChoices):
    SOLE_PROPRIETOR = "sole_proprietor", "Sole Proprietor"
    PARTNER = "partner", "Partner"
    CEO = "ceo", "CEO"
    COMPANY = "company", "Company"


class ClientType(models.TextChoices):
    CONSULTANT = "A", "A (consultant)"
    DIRECT = "X", "X (CLIENTS)"
    NORMAL = "N", "N (NOOR BAAF)"


class ApplicationType(models.TextChoices):
    TRADEMARK = "trademark", "Trademark"
    COPYRIGHT = "copyright", "Copyright"
    NTN = "ntn", "NTN"
    COMPANY = "company", "Company"


class Stage(models.IntegerChoices):
    STAGE_1 = 1, "Stage 1: Filing"
    STAGE_2 = 2, "Stage 2: Examination"
    STAGE_3 = 3, "Stage 3: Financial / Legal"
    STAGE_4 = 4, "Stage 4: Completion"


class SubStage(models.TextChoices):
    FILED = "filed", "FILED"
    ACKNOWLEDGMENT_RECEIVED = "ack_received", "ACKNOWLEDGMENT RECEIVED"

    EXAMINATION_DONE = "examination_done", "EXAMINATION DONE"
    ACCEPTANCE_DONE = "acceptance_done", "ACCEPTANCE DONE"
    HEARING = "hearing", "HEARING"

    DEMAND_NOTE_RECEIVED = "demand_note_received", "DEMAND NOTE RECEIVED"
    DEMAND_NOTE_SUBMITTED = "demand_note_submitted", "DEMAND NOTE SUBMITTED"

    PUBLISHED = "published", "PUBLISHED"
    CERTIFICATE_RECEIVED = "certificate_received", "CERTIFICATE RECEIVED"
    CERTIFICATE_PRINT = "certificate_print", "CERTIFICATE PRINT"
    CERTIFICATE_DISPATCH = "certificate_dispatch", "CERTIFICATE DISPATCH"

    OPPOSITION_FILED = "opposition_filed", "OPPOSITION FILED"
    OPPOSITION_RECEIVED = "opposition_received", "OPPOSITION RECEIVED"
    OPPOSITION_WITHDRAWN = "opposition_withdrawn", "OPPOSITION WITHDRAWN"
    OPPOSITION_ABANDONED = "opposition_abandoned", "OPPOSITION ABANDONED"

    REACTIVATION_FILED = "reactivation_filed", "REACTIVATION FILED"
    IMPORTED_DATA = "imported_data", "IMPORTED DATA"
    CLOSED = "closed", "CLOSED / ABD / STOP"


class EventType(models.TextChoices):
    FILING = "filing", "Filing"
    OBJECTION = "objection", "Objection"
    PUBLICATION = "publication", "Publication"
    DEMAND = "demand", "Demand"
    CERTIFICATE = "certificate", "Certificate"
    OTHER = "other", "Other"


SUB_STAGE_TO_STAGE = {
    SubStage.FILED: Stage.STAGE_1,
    SubStage.ACKNOWLEDGMENT_RECEIVED: Stage.STAGE_1,

    SubStage.EXAMINATION_DONE: Stage.STAGE_2,
    SubStage.ACCEPTANCE_DONE: Stage.STAGE_2,
    SubStage.HEARING: Stage.STAGE_2,

    SubStage.DEMAND_NOTE_RECEIVED: Stage.STAGE_3,
    SubStage.DEMAND_NOTE_SUBMITTED: Stage.STAGE_3,

    SubStage.PUBLISHED: Stage.STAGE_4,
    SubStage.CERTIFICATE_RECEIVED: Stage.STAGE_4,
    SubStage.CERTIFICATE_PRINT: Stage.STAGE_4,
    SubStage.CERTIFICATE_DISPATCH: Stage.STAGE_4,
}


class AssignmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    OVERDUE = "overdue", "Overdue"


class AgentChoice(models.TextChoices):
    FASIAL = "Fasial", "Fasial"
    RASHID = "Rashid", "Rashid"
    UZMA = "Uzma", "Uzma"
    SULMAN = "Sulman", "Sulman"


class AuditActionType(models.TextChoices):
    CREATED = "created", "Created"
    UPDATED = "updated", "Updated"
    STATUS_CHANGED = "status_changed", "Status Changed"
    ASSIGNMENT_ADDED = "assignment_added", "Assignment Added"
    EVENT_ADDED = "event_added", "Event Added"


class Application(models.Model):
    case_number = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Case #")
    client_type = models.CharField(max_length=1, choices=ClientType.choices, default=ClientType.DIRECT)
    client_id = models.PositiveIntegerField(null=True, blank=True)
    sequence = models.PositiveIntegerField(null=True, blank=True)

    folder_number = models.CharField(max_length=100, blank=True, verbose_name="Folder No")
    application_name = models.CharField(max_length=255)
    application_type = models.CharField(max_length=30, choices=ApplicationType.choices, default=ApplicationType.TRADEMARK)
    trademark_no = models.CharField(max_length=100, blank=True)

    class_numbers = models.CharField(max_length=255, blank=True)
    application_year = models.PositiveIntegerField(null=True, blank=True)
    filing_date = models.DateField(null=True, blank=True)

    case_no = models.CharField(max_length=100, blank=True, verbose_name="Case No (Official)")
    applicant_name = models.CharField(max_length=255)
    trading_as = models.CharField(max_length=255, blank=True)
    applicant_type = models.CharField(max_length=20, choices=ApplicantType.choices, default=ApplicantType.COMPANY)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True, choices=[("Lahore", "Lahore"), ("Karachi", "Karachi"), ("Islamabad", "Islamabad"), ("Peshawar", "Peshawar")])

    agent_name = models.CharField(max_length=50, blank=True, choices=AgentChoice.choices)
    agent_address = models.TextField(blank=True)

    jurisdiction = models.CharField(max_length=100, blank=True)
    dispatch_status = models.CharField(max_length=100, blank=True)

    logo = models.ImageField(upload_to="logos/", null=True, blank=True)

    current_stage = models.IntegerField(choices=Stage.choices, default=Stage.STAGE_1)
    current_sub_stage = models.CharField(max_length=50, choices=SubStage.choices, blank=True)
    current_status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.case_number} - {self.application_name}"

    def generate_case_number(self) -> str:
        """Generate case number in format: [ClientType]-[ClientID]-[Sequence]"""
        if not self.client_id:
            raise ValueError("client_id is required for auto-generation")

        # Get the next sequence number for this client_type + client_id combination
        last_app = Application.objects.filter(
            client_type=self.client_type,
            client_id=self.client_id
        ).order_by('-sequence').first()

        next_sequence = (last_app.sequence + 1) if last_app else 1
        self.sequence = next_sequence

        return f"{self.client_type}-{self.client_id}-{next_sequence:03d}"

    def get_stage3_deadline(self):
        """Calculate Stage 3 deadline (4 months 15 days = 135 days) from filing date"""
        from datetime import timedelta
        if self.filing_date:
            return self.filing_date + timedelta(days=135)
        return None

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        old = None
        if not is_create:
            old = Application.objects.filter(pk=self.pk).first()

        # Auto-generate case number if not provided
        if not self.case_number and self.client_id:
            self.case_number = self.generate_case_number()

        super().save(*args, **kwargs)

        if is_create:
            AuditLog.log(
                application=self,
                action_type=AuditActionType.CREATED,
                field_changed="application",
                old_value="",
                new_value=f"created case_number={self.case_number}",
            )
            return

        if not old:
            return

        tracked_fields = [
            "case_number",
            "client_type",
            "client_id",
            "sequence",
            "application_name",
            "application_type",
            "trademark_no",
            "class_numbers",
            "application_year",
            "filing_date",
            "case_no",
            "applicant_name",
            "trading_as",
            "applicant_type",
            "address",
            "city",
            "agent_name",
            "agent_address",
            "jurisdiction",
            "dispatch_status",
            "logo",
            "current_stage",
            "current_sub_stage",
            "current_status",
        ]

        for field in tracked_fields:
            old_value = getattr(old, field)
            new_value = getattr(self, field)
            if old_value != new_value:
                action = AuditActionType.UPDATED
                if field in {"current_stage", "current_sub_stage", "current_status"}:
                    action = AuditActionType.STATUS_CHANGED
                AuditLog.log(
                    application=self,
                    action_type=action,
                    field_changed=field,
                    old_value=old_value,
                    new_value=new_value,
                )


class Event(models.Model):
    application = models.ForeignKey(Application, on_delete=models.PROTECT, related_name="events")
    event_type = models.CharField(max_length=50, choices=EventType.choices)
    event_datetime = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    document_link = models.CharField(max_length=500, blank=True)
    file = models.FileField(upload_to='event_documents/%Y/%m/', null=True, blank=True)
    deadline_date = models.DateField(null=True, blank=True)
    stage = models.IntegerField(choices=Stage.choices, null=True, blank=True)
    sub_stage = models.CharField(max_length=50, choices=SubStage.choices, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event_datetime", "-id"]

    def __str__(self) -> str:
        return f"{self.application.folder_number}: {self.get_event_type_display()}"

    def save(self, *args, **kwargs):
        if not self.created_by:
            user = get_current_user()
            if user and getattr(user, "is_authenticated", False):
                self.created_by = user

        is_create = self.pk is None
        super().save(*args, **kwargs)

        if is_create:
            updated_fields = []
            stage_value = self.stage
            sub_stage_value = self.sub_stage

            if sub_stage_value and sub_stage_value in SUB_STAGE_TO_STAGE:
                stage_value = SUB_STAGE_TO_STAGE[sub_stage_value]

            if stage_value:
                self.application.current_stage = int(stage_value)
                updated_fields.append("current_stage")

            if sub_stage_value:
                self.application.current_sub_stage = sub_stage_value
                updated_fields.append("current_sub_stage")

            self.application.current_status = self.event_type
            updated_fields.append("current_status")

            if updated_fields:
                self.application.save(update_fields=updated_fields + ["updated_at"])

            AuditLog.log(
                application=self.application,
                action_type=AuditActionType.EVENT_ADDED,
                field_changed="event",
                old_value="",
                new_value=f"{self.event_type} @ {self.event_datetime.isoformat()}",
            )


class Assignment(models.Model):
    application = models.ForeignKey(Application, on_delete=models.PROTECT, related_name="assignments")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.PENDING)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assignments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-assigned_date", "-id"]

    def __str__(self) -> str:
        return f"{self.application.case_number} assignment"

    def save(self, *args, **kwargs):
        if not self.created_by:
            user = get_current_user()
            if user and getattr(user, "is_authenticated", False):
                self.created_by = user

        # Auto-update status to overdue if due date has passed
        if self.due_date and self.status != "completed":
            today = timezone.localdate()
            if self.due_date < today and self.status != "overdue":
                self.status = "overdue"

        is_create = self.pk is None
        super().save(*args, **kwargs)

        if is_create:
            AuditLog.log(
                application=self.application,
                action_type=AuditActionType.ASSIGNMENT_ADDED,
                field_changed="assignment",
                old_value="",
                new_value=f"assigned_to={self.assigned_to_id} due={self.due_date or ''}",
            )


class DocumentLink(models.Model):
    class FileType(models.TextChoices):
        LOGO = "logo", "Logo"
        CERTIFICATE = "certificate", "Certificate"
        NOTICE = "notice", "Notice"
        OTHER = "other", "Other"

    application = models.ForeignKey(Application, on_delete=models.PROTECT, related_name="documents")
    file_type = models.CharField(max_length=20, choices=FileType.choices, default=FileType.OTHER)
    file_path = models.CharField(max_length=500, blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/', null=True, blank=True)
    preview_enabled = models.BooleanField(default=True)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
    )

    class Meta:
        ordering = ["-uploaded_date", "-id"]

    def __str__(self) -> str:
        return f"{self.application.folder_number} document"

    def save(self, *args, **kwargs):
        if not self.uploaded_by:
            user = get_current_user()
            if user and getattr(user, "is_authenticated", False):
                self.uploaded_by = user
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    application = models.ForeignKey(Application, on_delete=models.PROTECT, related_name="audit_logs")
    action_type = models.CharField(max_length=30, choices=AuditActionType.choices)
    field_changed = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp", "-id"]

    def __str__(self) -> str:
        return f"{self.application.folder_number} {self.action_type} {self.field_changed}"

    @classmethod
    def log(
        cls,
        *,
        application: Application,
        action_type: str,
        field_changed: str,
        old_value: str,
        new_value: str,
        changed_by=None,
    ):
        if changed_by is None:
            changed_by = get_current_user()
            if changed_by is not None and not getattr(changed_by, "is_authenticated", False):
                changed_by = None

        cls.objects.create(
            application=application,
            action_type=action_type,
            field_changed=field_changed,
            old_value=str(old_value),
            new_value=str(new_value),
            changed_by=changed_by,
        )


class SiteSettings(models.Model):
    company_name = models.CharField(max_length=255, default="IP Case Platform")
    company_logo = models.ImageField(upload_to="company_logo/", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self) -> str:
        return self.company_name


class Agent(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class FileUpload(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="file_uploads")
    file = models.FileField(upload_to="case_files/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="file_uploads",
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.application.folder_number} - {self.file.name}"


# Create your models here.
