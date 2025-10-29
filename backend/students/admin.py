from django.contrib import admin
from .models import Student, Teacher, Department, Subject, TeacherSubjectAssignment


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "degree_type", "duration_years", "is_active")
    search_fields = ("code", "name")
    list_filter = ("degree_type", "is_active")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("full_name", "employee_id", "email", "phone", "is_active")
    search_fields = ("full_name", "employee_id", "email")
    list_filter = ("is_active",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("subject_name", "subject_code", "department", "class_year", "credits", "is_active")
    search_fields = ("subject_name", "subject_code")
    list_filter = ("department", "class_year", "is_active")


@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "subject", "academic_year", "is_active", "assigned_date")
    search_fields = ("teacher__full_name", "subject__subject_name")
    list_filter = ("is_active", "academic_year")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "roll_number",
        "full_name",
        "department",
        "class_year",
        "face_embedding_id",
        "is_active",
    )
    search_fields = ("roll_number", "full_name")
    list_filter = ("department", "class_year", "is_active")
