# Department-Based Access Control for Teachers

## Overview

Implemented department-based access control where teachers are assigned to a specific department during registration and can only view/edit data (students, subjects, attendance) for their assigned department.

## Backend Changes

### 1. Teacher Model (`backend/students/models.py`)

```python
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200)
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Features:**

- Links to Django's User model (one-to-one)
- Stores teacher's department assignment
- Optional employee ID for official identification

### 2. Teacher API (`backend/students/views.py`)

#### TeacherViewSet

- **POST `/api/teachers/`** - Teacher registration (no authentication required)
- **GET `/api/teachers/me/`** - Get current teacher's profile (authentication required)

**Registration Fields:**

- username (required)
- password (required)
- email (optional)
- full_name (required)
- department (required) - **Locked for life**
- employee_id (optional)

### 3. Department Filtering

All ViewSets now filter data by teacher's department:

#### StudentViewSet

```python
def get_queryset(self):
    queryset = Student.objects.all()
    if self.request.user.is_authenticated:
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            queryset = queryset.filter(department=teacher.department)
        except Teacher.DoesNotExist:
            if not self.request.user.is_superuser:
                queryset = queryset.none()
    return queryset
```

#### SubjectViewSet

- Filters subjects by teacher's department
- Additional filtering by query parameters (department, class_year)

#### AttendanceSessionViewSet

- Shows only attendance sessions for teacher's department

### 4. Auth Endpoint Update (`backend/attendance_system/views_auth.py`)

**GET `/api/auth/me`** now returns:

```json
{
  "id": 1,
  "username": "teacher1",
  "email": "teacher1@example.com",
  "is_staff": false,
  "is_superuser": false,
  "teacher": {
    "id": 1,
    "full_name": "John Doe",
    "department": "CSE",
    "employee_id": "T12345"
  }
}
```

### 5. Database Migration

**Migration:** `students/migrations/0003_teacher.py`

- Created Teacher table
- Adds relationship to auth_user

**Apply migration:**

```bash
cd backend
python manage.py migrate
```

## Frontend Changes

### 1. Teacher Registration Page (`frontend/src/pages/TeacherRegistration.jsx`)

**Route:** `/teacher-register`

**Form Fields:**

- **Account Information:**

  - Username (required)
  - Email (optional)
  - Password (required, min 6 characters)
  - Confirm Password (required)

- **Personal Information:**

  - Full Name (required)
  - Employee ID (optional)

- **Department Assignment:**
  - Department (required) - **⚠️ This assignment is permanent**

**Features:**

- Form validation
- Password matching check
- Success screen with auto-redirect to login
- Link back to login page

### 2. Updated Login Page (`frontend/src/pages/Login.jsx`)

**Added:**

- "New teacher? Register here" link to `/teacher-register`

### 3. Student Registration (`frontend/src/pages/Registration.jsx`)

**Changes:**

- Fetches teacher's department on page load
- Pre-fills and locks department field
- Shows 🔒 icon with hint: "Department is locked to your assigned department"
- Teachers can only register students in their own department

### 4. Subjects Management (`frontend/src/pages/SubjectsManagement.jsx`)

**Changes:**

- Fetches teacher's department on page load
- Pre-fills department filter with teacher's department
- Locks department filter (read-only)
- New subjects automatically use teacher's department
- Department field in add/edit modal is locked
- Shows 🔒 icon with hints

### 5. Attendance Page (`frontend/src/pages/Attendance.jsx`)

**Changes:**

- Fetches teacher's department on page load
- Pre-fills and locks department dropdown
- Teachers can only create sessions for their department
- Subject dropdown automatically filters by teacher's department
- Shows 🔒 icon with hint

## User Workflow

### Teacher Registration Flow

1. Navigate to `/teacher-register` or click "New teacher? Register here" from login
2. Fill in account information (username, password, email)
3. Fill in personal information (full name, employee ID)
4. **Select department** - This is a critical decision as it cannot be changed later
5. Click "Register"
6. Success! Redirected to login page

### Teacher Login & Usage Flow

1. Login with username and password
2. Navigate to any page (Register, Students, Subjects, Attendance)
3. Department is automatically pre-filled and locked 🔒
4. Can only view/edit data for assigned department
5. Cannot access or modify data from other departments

### Registering Students

1. Go to Registration page
2. Department field is pre-filled with your department (locked)
3. Select class/year
4. Enter student details
5. Capture face
6. Student is registered to your department

### Managing Subjects

1. Go to Subjects page
2. Department filter is set to your department (locked)
3. Click "Add Subject"
4. Department is pre-filled (locked)
5. Select year and enter subject details
6. Subject is added to your department only

### Taking Attendance

1. Go to Attendance page
2. Department is pre-filled (locked)
3. Select class/year
4. Subject dropdown shows only subjects from your department
5. Create session and mark attendance

## Security Features

### 1. Department Isolation

- Teachers cannot view students from other departments
- Teachers cannot view subjects from other departments
- Teachers cannot view attendance sessions from other departments
- API-level filtering ensures data security

### 2. Superuser Override

- Superusers (admins) can see all data across all departments
- Useful for system administration and reporting

### 3. No Teacher Profile = No Access

- Users without a teacher profile get empty querysets
- Only superusers can access data without a teacher profile

## API Examples

### Register a New Teacher

```bash
curl -X POST "http://localhost:8000/api/teachers/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepass123",
    "email": "john@example.com",
    "full_name": "John Doe",
    "department": "CSE",
    "employee_id": "T12345"
  }'
```

### Get Current Teacher Profile

```bash
curl "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <your_token>"
```

### List Students (Filtered by Teacher's Department)

```bash
curl "http://localhost:8000/api/students/" \
  -H "Authorization: Bearer <your_token>"
# Returns only students from teacher's department
```

### List Subjects (Filtered by Teacher's Department)

```bash
curl "http://localhost:8000/api/subjects/?class_year=First%20Year" \
  -H "Authorization: Bearer <your_token>"
# Returns only subjects from teacher's department
```

## Testing Checklist

- [ ] Register a new teacher with department "CSE"
- [ ] Login with the new teacher account
- [ ] Verify department is locked in all pages
- [ ] Register a student - verify department is CSE and locked
- [ ] Go to Students page - verify only CSE students appear
- [ ] Create a subject for CSE - verify it's created
- [ ] Go to Subjects page - verify only CSE subjects appear
- [ ] Create an attendance session - verify department is CSE
- [ ] Try to access data from another department - verify it's not accessible

## Admin Tasks

### View All Teachers

```bash
cd backend
python manage.py shell
```

```python
from students.models import Teacher
for t in Teacher.objects.all():
    print(f"{t.full_name} ({t.department}) - {t.user.username}")
```

### Change a Teacher's Department (Emergency Only)

```python
from students.models import Teacher
teacher = Teacher.objects.get(user__username='john_doe')
teacher.department = 'ECE'
teacher.save()
```

⚠️ **Warning:** Changing a teacher's department should be done carefully as it affects all their existing data relationships.

### Create Superuser (Can Access All Departments)

```bash
python manage.py createsuperuser
```

## Benefits

1. **Data Isolation**: Each department's data is completely isolated
2. **Simplified UI**: Teachers don't see irrelevant data from other departments
3. **Security**: Teachers cannot accidentally modify data from other departments
4. **Accountability**: Clear assignment of teachers to departments
5. **Scalability**: Easy to add more departments without affecting existing ones

## Future Enhancements

1. **Multi-Department Teachers**: Allow teachers to be assigned to multiple departments
2. **Department Transfer**: Admin interface to transfer teachers between departments
3. **Department Head Role**: Special role with additional permissions
4. **Cross-Department Reporting**: Allow viewing reports across departments for admin users
5. **Department Hierarchy**: Support for sub-departments (e.g., CSE-AI, CSE-Cybersecurity)

## Files Modified

### Backend

- `backend/students/models.py` - Added Teacher model
- `backend/students/serializers.py` - Added TeacherSerializer
- `backend/students/views.py` - Added TeacherViewSet, updated filtering
- `backend/students/urls.py` - Registered TeacherViewSet
- `backend/attendance/views.py` - Added department filtering
- `backend/attendance_system/views_auth.py` - Updated /api/auth/me endpoint
- `backend/students/migrations/0003_teacher.py` - Database migration

### Frontend

- `frontend/src/pages/TeacherRegistration.jsx` - New registration page
- `frontend/src/pages/Login.jsx` - Added registration link
- `frontend/src/pages/Registration.jsx` - Added department locking
- `frontend/src/pages/SubjectsManagement.jsx` - Added department locking
- `frontend/src/pages/Attendance.jsx` - Added department locking
- `frontend/src/App.jsx` - Added teacher registration route

## Status

✅ **COMPLETE AND READY FOR TESTING**
