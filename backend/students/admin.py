from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = (
		"roll_number",
		"full_name",
		"department",
		"class_year",
		"face_embedding_id",
		"created_at",
	)
	search_fields = ("roll_number", "full_name", "department", "class_year")
	list_filter = ("department", "class_year")
	readonly_fields = ("created_at", "updated_at")
