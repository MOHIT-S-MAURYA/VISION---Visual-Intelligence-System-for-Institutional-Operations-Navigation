from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"department",
		"class_year",
		"subject",
		"session_date",
		"start_time",
		"end_time",
		"is_active",
	)
	list_filter = ("department", "class_year", "subject", "is_active", "session_date")
	search_fields = ("department", "class_year", "subject")
	readonly_fields = ("start_time",)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"session",
		"student",
		"status",
		"confidence",
		"marked_at",
	)
	list_filter = ("status", "marked_at")
	search_fields = ("student__roll_number", "student__full_name", "session__subject")
	readonly_fields = ("marked_at",)
