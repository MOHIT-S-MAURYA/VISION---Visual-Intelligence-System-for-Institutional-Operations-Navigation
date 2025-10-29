from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from .models import Student, Teacher, Department, Subject, TeacherSubjectAssignment


class TeacherAdminForm(forms.ModelForm):
    """Custom form for Teacher admin with password field and auto employee_id"""
    
    username = forms.CharField(
        max_length=150,
        help_text="Username for login (will be created if new teacher)"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Set initial password for the teacher",
        required=True
    )
    
    class Meta:
        model = Teacher
        fields = ['username', 'password', 'full_name', 'email', 'phone', 'employee_id']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing teacher, populate username from user
        if self.instance.pk and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['password'].required = False
            self.fields['password'].help_text = "Leave blank to keep current password, or enter new password to change"
        
        # Make employee_id read-only and auto-generate
        self.fields['employee_id'].required = False
        self.fields['employee_id'].widget.attrs['readonly'] = True
        self.fields['employee_id'].help_text = "Auto-generated (T001, T002, etc.)"
        
        # If new teacher, generate employee_id
        if not self.instance.pk:
            self.fields['employee_id'].initial = self._generate_employee_id()
    
    def _generate_employee_id(self):
        """Generate next available employee ID"""
        last_teacher = Teacher.objects.filter(
            employee_id__startswith='T'
        ).order_by('-employee_id').first()
        
        if last_teacher and last_teacher.employee_id:
            try:
                last_num = int(last_teacher.employee_id[1:])
                next_num = last_num + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1
        
        return f"T{next_num:03d}"  # Format: T001, T002, etc.
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        username = self.cleaned_data['username']
        password = self.cleaned_data.get('password')
        
        # Auto-generate employee_id if not set
        if not teacher.employee_id:
            teacher.employee_id = self._generate_employee_id()
        
        # Create or update user
        if teacher.user_id:
            # Existing teacher - update user
            user = teacher.user
            user.username = username
            if password:  # Only update password if provided
                user.set_password(password)
            user.save()
        else:
            # New teacher - create user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': teacher.email or '',
                    'first_name': teacher.full_name.split()[0] if teacher.full_name else '',
                    'last_name': ' '.join(teacher.full_name.split()[1:]) if teacher.full_name and len(teacher.full_name.split()) > 1 else '',
                }
            )
            if not created and password:
                # User exists, update password
                user.set_password(password)
                user.save()
            elif created and password:
                # New user, set password
                user.set_password(password)
                user.save()
            
            teacher.user = user
        
        if commit:
            teacher.save()
        
        return teacher


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "degree_type", "duration_years", "is_active")
    search_fields = ("code", "name")
    list_filter = ("degree_type", "is_active")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    form = TeacherAdminForm
    list_display = ("employee_id", "full_name", "username_display", "email", "phone", "is_active")
    search_fields = ("full_name", "employee_id", "email", "user__username")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ('Account Information', {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('full_name', 'employee_id', 'email', 'phone')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def username_display(self, obj):
        """Display username in list view"""
        return obj.user.username if obj.user else '-'
    username_display.short_description = 'Username'
    
    def save_model(self, request, obj, form, change):
        """Override save to show success message with credentials"""
        super().save_model(request, obj, form, change)
        
        if not change:  # New teacher
            password = form.cleaned_data.get('password')
            self.message_user(
                request,
                f"Teacher created successfully! "
                f"Login credentials: Username/Employee ID: {obj.user.username} or {obj.employee_id}, "
                f"Password: (as set). Please share these credentials securely with the teacher.",
                level='success'
            )


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
