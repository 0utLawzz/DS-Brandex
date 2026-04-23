from django.contrib import admin

from .models import Application, Assignment, AuditLog, DocumentLink, Event


class EventInline(admin.TabularInline):
    model = Event
    extra = 0
    fields = ("event_type", "event_datetime", "stage", "sub_stage", "deadline_date", "document_link", "notes")
    readonly_fields = ("created_by", "created_at")


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ("assigned_to", "due_date", "status", "notes")
    readonly_fields = ("created_by", "created_at", "assigned_date")


class DocumentInline(admin.TabularInline):
    model = DocumentLink
    extra = 0
    fields = ("file_type", "file_path", "preview_enabled")
    readonly_fields = ("uploaded_by", "uploaded_date")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "folder_number",
        "client_type",
        "client_id",
        "sequence",
        "application_name",
        "application_type",
        "trademark_no",
        "application_number",
        "applicant_name",
        "city",
        "jurisdiction",
        "current_stage",
        "current_sub_stage",
        "current_status",
        "updated_at",
    )
    search_fields = ("folder_number", "application_name", "application_number", "trademark_no", "applicant_name")
    list_filter = (
        "client_type",
        "application_type",
        "current_stage",
        "current_sub_stage",
        "current_status",
        "jurisdiction",
        "city",
    )
    readonly_fields = ("created_at", "updated_at")
    inlines = (EventInline, AssignmentInline, DocumentInline)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("application", "event_type", "event_datetime", "deadline_date", "stage", "sub_stage", "created_by")
    search_fields = ("application__folder_number", "application__application_name", "notes")
    list_filter = ("event_type", "stage", "sub_stage")
    readonly_fields = ("created_by", "created_at")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("application", "assigned_to", "due_date", "status", "created_by", "assigned_date")
    search_fields = ("application__folder_number", "application__application_name")
    list_filter = ("status",)
    readonly_fields = ("created_by", "created_at", "assigned_date")


@admin.register(DocumentLink)
class DocumentLinkAdmin(admin.ModelAdmin):
    list_display = ("application", "file_type", "file_path", "preview_enabled", "uploaded_by", "uploaded_date")
    search_fields = ("application__folder_number", "application__application_name", "file_path")
    list_filter = ("file_type", "preview_enabled")
    readonly_fields = ("uploaded_by", "uploaded_date")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("application", "action_type", "field_changed", "changed_by", "timestamp")
    search_fields = ("application__folder_number", "application__application_name", "field_changed", "old_value", "new_value")
    list_filter = ("action_type", "field_changed")
    readonly_fields = (
        "application",
        "action_type",
        "field_changed",
        "old_value",
        "new_value",
        "changed_by",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
