# API Testing Commands

Quick reference for testing the Subject Management API endpoints.

## Prerequisites

Make sure your Django server is running:

```bash
cd backend
python manage.py runserver
```

## 1. List All Subjects

```bash
curl "http://localhost:8000/api/subjects/"
```

## 2. Filter Subjects by Department

```bash
curl "http://localhost:8000/api/subjects/?department=CSE"
```

## 3. Filter Subjects by Department and Year

```bash
curl "http://localhost:8000/api/subjects/?department=CSE&class_year=First%20Year"
```

```bash
curl "http://localhost:8000/api/subjects/?department=MCA&class_year=Second%20Year"
```

## 4. Create a New Subject

```bash
curl -X POST "http://localhost:8000/api/subjects/" \
  -H "Content-Type: application/json" \
  -d '{
    "department": "ECE",
    "class_year": "First Year",
    "subject_name": "Network Theory",
    "subject_code": "ECE101"
  }'
```

## 5. Get a Single Subject

```bash
curl "http://localhost:8000/api/subjects/1/"
```

## 6. Update a Subject

```bash
curl -X PUT "http://localhost:8000/api/subjects/1/" \
  -H "Content-Type: application/json" \
  -d '{
    "department": "CSE",
    "class_year": "First Year",
    "subject_name": "Engineering Mathematics-I",
    "subject_code": "MATH101"
  }'
```

## 7. Delete a Subject

```bash
curl -X DELETE "http://localhost:8000/api/subjects/1/"
```

## 8. Bulk Create Subjects

```bash
curl -X POST "http://localhost:8000/api/subjects/bulk_create/" \
  -H "Content-Type: application/json" \
  -d '{
    "subjects": [
      {
        "department": "ECE",
        "class_year": "First Year",
        "subject_name": "Electronic Devices",
        "subject_code": "ECE102"
      },
      {
        "department": "ECE",
        "class_year": "First Year",
        "subject_name": "Signals and Systems",
        "subject_code": "ECE103"
      }
    ]
  }'
```

## 9. Check Current Subject Count

```bash
# For CSE First Year
curl "http://localhost:8000/api/subjects/?department=CSE&class_year=First%20Year" | python -m json.tool | grep -c "\"id\""
```

## 10. Pretty Print JSON Response

```bash
curl "http://localhost:8000/api/subjects/?department=CSE&class_year=First%20Year" | python -m json.tool
```

## Example Response

```json
[
  {
    "id": 1,
    "department": "CSE",
    "class_year": "First Year",
    "subject_name": "Engineering Mathematics-I",
    "subject_code": null,
    "created_at": "2025-10-29T09:13:10.077367+05:30",
    "updated_at": "2025-10-29T09:13:10.077384+05:30"
  },
  {
    "id": 2,
    "department": "CSE",
    "class_year": "First Year",
    "subject_name": "Engineering Physics",
    "subject_code": null,
    "created_at": "2025-10-29T09:13:10.078281+05:30",
    "updated_at": "2025-10-29T09:13:10.078291+05:30"
  }
]
```

## URL Encoding Reference

When using query parameters with spaces, encode them:

- Space → `%20`
- First Year → `First%20Year`
- Second Year → `Second%20Year`
- Third Year → `Third%20Year`
- Fourth Year → `Fourth%20Year`

Or use quotes in zsh/bash:

```bash
curl "http://localhost:8000/api/subjects/?class_year=First Year"
```

## Test the Complete Flow

```bash
# 1. Check existing CSE subjects
curl "http://localhost:8000/api/subjects/?department=CSE&class_year=First%20Year"

# 2. Add a new subject
curl -X POST "http://localhost:8000/api/subjects/" \
  -H "Content-Type: application/json" \
  -d '{
    "department": "CSE",
    "class_year": "First Year",
    "subject_name": "Introduction to AI",
    "subject_code": "CSE109"
  }'

# 3. Verify it was added
curl "http://localhost:8000/api/subjects/?department=CSE&class_year=First%20Year" | grep "Introduction to AI"

# 4. Get the ID from the response, then delete it
curl -X DELETE "http://localhost:8000/api/subjects/49/"

# 5. Verify it was deleted
curl "http://localhost:8000/api/subjects/?department=CSE&class_year=First%20Year" | grep "Introduction to AI"
```

## Authenticated Requests (If using Django Auth)

If your API requires authentication:

```bash
# Login first to get token (if using token auth)
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "teacher1", "password": "password"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['token'])")

# Then use the token in subsequent requests
curl "http://localhost:8000/api/subjects/" \
  -H "Authorization: Token $TOKEN"
```

## Database Query (Alternative)

If you want to query the database directly:

```bash
cd backend
python manage.py shell
```

Then in the Python shell:

```python
from students.models import Subject

# Get all subjects
Subject.objects.all()

# Filter by department
Subject.objects.filter(department='CSE')

# Count subjects
Subject.objects.filter(department='CSE', class_year='First Year').count()

# Get specific subject
Subject.objects.get(id=1)
```
