# Backend Model Restructuring Summary

## Overview

Completely restructured the backend database from a simple department-based system to a normalized, assignment-based system that supports flexible teacher-subject assignments across multiple departments and classes.

## Key Changes

### 1. New Database Schema

#### Models Created/Updated:

**Department Model** (NEW)

- `code`: Unique department code (e.g., 'CSE', 'MCA')
- `name`: Full department name
- `degree_type`: UG (Undergraduate) or PG (Postgraduate)
- `duration_years`: Program duration (4 for UG, 2 for PG)
- `is_active`: Boolean flag
- Purpose: Centralized department management with proper normalization

**Teacher Model** (UPDATED)

- Removed: `department` CharField (was permanent assignment)
- Added: `email`, `phone`, `is_active` fields
- Kept: `user` (OneToOne to User), `full_name`, `employee_id`
- Purpose: Teacher profile without permanent department binding

**Subject Model** (UPDATED)

- Changed: `department` from CharField to ForeignKey(Department)
- Added: `credits`, `is_active` fields
- Kept: `class_year`, `subject_name`, `subject_code`
- Purpose: Subjects now properly linked to Department objects

**TeacherSubjectAssignment Model** (NEW)

- `teacher`: ForeignKey to Teacher
- `subject`: ForeignKey to Subject
- `academic_year`: Optional academic year
- `is_active`: Boolean flag
- `assigned_date`: Auto timestamp
- `notes`: Optional text field
- Unique constraint: (teacher, subject, academic_year)
- Purpose: Junction table for many-to-many teacher-subject relationships

**Student Model** (UPDATED)

- Changed: `department` from CharField to ForeignKey(Department)
- Added: `email`, `phone`, `is_active` fields
- Removed: `created_at`, `updated_at` (can add back if needed)
- Kept: `roll_number`, `full_name`, `class_year`, `face_embedding_id`, `face_image`
- Purpose: Students linked to departments via FK

### 2. API Changes

#### New Endpoints:

- `/api/departments/` - CRUD for departments (supports `degree_type` filter)
- `/api/teacher-assignments/` - CRUD for teacher-subject assignments

#### Updated Endpoints:

- `/api/teachers/me/` - Now returns teacher profile + all subject assignments
- `/api/students/` - Filters by teacher's assigned class combinations (department + class_year)
- `/api/subjects/` - Filters by teacher's assigned subject IDs
- `/api/attendance/sessions/` - Filters by teacher's assigned subject-class combinations

#### Filtering Logic:

Teachers now see data based on their `TeacherSubjectAssignment` records:

- Students: Filtered by matching (department, class_year) from assigned subjects
- Subjects: Filtered by assigned subject IDs
- Attendance: Filtered by (department, class_year, subject) combinations

### 3. Serializer Updates

**DepartmentSerializer** (NEW)

- All department fields
- Used for department CRUD operations

**TeacherSerializer** (UPDATED)

- Removed `department` field
- Creates both User and Teacher profile
- Password handling for registration

**SubjectSerializer** (UPDATED)

- `department`: Now expects department ID (integer)
- Added read-only fields: `department_code`, `department_name`
- Proper FK relationship handling

**TeacherSubjectAssignmentSerializer** (NEW)

- Nested read-only fields for teacher and subject details
- Used for managing teacher assignments

**StudentSerializer** (UPDATED)

- `department`: Now expects department ID (integer)
- Added read-only fields: `department_code`, `department_name`
- Proper FK relationship handling

### 4. Migration Strategy

Successfully executed 6 migrations:

1. **0004**: Created Department model, removed teacher.department, added new fields, added temporary fields
2. **0005**: Data migration - copied old department strings to temporary fields, created Department objects, linked to FKs
3. **0006**: Removed temporary fields, finalized FK constraints

### 5. Data Seeding

**seed_departments Management Command**

- Seeds 26 departments (20 UG + 6 PG)
- Includes all major engineering disciplines and postgraduate programs
- Idempotent (can run multiple times safely)

Usage: `python manage.py seed_departments`

### 6. Admin Interface

Updated Django admin for all models:

- DepartmentAdmin: List/filter/search departments
- TeacherAdmin: Manage teacher profiles
- SubjectAdmin: Manage subjects with department filtering
- TeacherSubjectAssignmentAdmin: Manage assignments
- StudentAdmin: Updated for new schema

## Breaking Changes

### Frontend Implications:

1. **Department Selection**: Must now use department IDs (integers) instead of codes (strings)
2. **Teacher Registration**: No longer requires department selection
3. **Subject Management**: Department field now expects ID
4. **Student Registration**: Department field now expects ID
5. **Filtering**: All department-based filtering needs update

### API Contract Changes:

- POST `/api/students/`: `department` must be integer (department ID)
- POST `/api/subjects/`: `department` must be integer (department ID)
- POST `/api/teachers/`: `department` field removed
- GET responses: Department info now includes nested `department_code` and `department_name`

## Next Steps

### Immediate (Required for functionality):

1. ✅ Update attendance views (DONE)
2. ⏳ Update auth endpoint to return teacher assignments
3. ⏳ Create UI for managing teacher assignments (admin or teacher self-service)
4. ⏳ Update all frontend pages:
   - Registration pages (teacher, student, subject)
   - Dashboard/listing pages
   - Attendance pages
   - Filter components

### Future Enhancements:

1. Add assignment approval workflow (admin approves teacher assignments)
2. Add historical tracking (assignment start/end dates)
3. Add workload management (track teaching hours per teacher)
4. Add conflict detection (same teacher, same time slot)
5. Add bulk assignment import (CSV upload)

## Testing Checklist

- [ ] Teacher registration (without department)
- [ ] Create department via admin/API
- [ ] Create subjects with department FK
- [ ] Assign subjects to teacher
- [ ] Register student with department FK
- [ ] Teacher login - verify sees only assigned data
- [ ] Create attendance session (verify assignment validation)
- [ ] Test all filtering (students, subjects, attendance)
- [ ] Test admin interface for all models

## Database Reset (Development Only)

If you need to start fresh:

```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_departments
```

## Migration Files

- `0001_initial.py` - Initial Student model
- `0002_subject.py` - Added Subject model
- `0003_teacher.py` - Added Teacher model (with old department field)
- `0004_department_*.py` - Major restructuring
- `0005_migrate_to_department_fk.py` - Data migration
- `0006_remove_student_department_old_*.py` - Cleanup

## Performance Considerations

Added `select_related()` in ViewSets for:

- StudentViewSet: `select_related('department')`
- SubjectViewSet: `select_related('department')`
- TeacherSubjectAssignmentViewSet: `select_related('teacher', 'subject', 'subject__department')`

This prevents N+1 query problems when fetching related data.
