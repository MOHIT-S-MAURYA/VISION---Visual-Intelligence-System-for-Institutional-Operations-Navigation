# Technical Specification Document

**Project:** Smart Attendance System with Face Recognition  
**Version:** 1.0  
**Date:** October 31, 2025

---

## 1. System Overview

### 1.1 Purpose

This document provides detailed technical specifications for the Smart Attendance System, including system architecture, component interactions, data models, API contracts, and implementation details.

### 1.2 Scope

The system encompasses three main components:

- Django Backend (RESTful API)
- FastAPI AI Service (Face Recognition)
- React Frontend (User Interface)

### 1.3 Technologies Used

#### Backend Stack

- **Language:** Python 3.11+
- **Framework:** Django 4.2.7
- **REST Framework:** Django REST Framework 3.14.0
- **Authentication:** SimpleJWT 5.3.1
- **Database:** SQLite (dev), PostgreSQL (prod)
- **ORM:** Django ORM

#### AI/ML Stack

- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn 0.24.0
- **Face Detection:** SCRFD (buffalo_sc)
- **Face Recognition:** ArcFace (w600k_r50)
- **Vector DB:** FAISS 1.7.4
- **Inference:** ONNX Runtime 1.17.0
- **Image Processing:** OpenCV 4.8.1

#### Frontend Stack

- **Library:** React 18.x
- **Routing:** React Router DOM 6.x
- **HTTP Client:** Axios 1.x
- **Styling:** TailwindCSS 3.x
- **Build Tool:** Vite

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Browser    │  │    Mobile    │  │    Tablet    │     │
│  │  (Desktop)   │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/WSS
┌────────────────────────▼────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              React Frontend (Port 3000)              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │  Student   │  │  Teacher   │  │   Admin    │    │  │
│  │  │    UI      │  │     UI     │  │     UI     │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (JSON)
┌────────────────────────▼────────────────────────────────────┐
│                      Business Layer                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Django Backend (Port 8000)                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │ Students   │  │ Attendance │  │    Auth    │    │  │
│  │  │  Service   │  │   Service  │  │  Service   │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │Department  │  │  Reports   │  │   Users    │    │  │
│  │  │  Service   │  │  Service   │  │  Service   │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        │ (Internal API) │   (Database)   │
        │                │                │
┌───────▼─────────┐  ┌──▼──────────┐  ┌─▼──────────────────┐
│   AI Service    │  │  Data Layer │  │   File Storage     │
│  (Port 8001)    │  │   SQLite/   │  │  /media/           │
│                 │  │  PostgreSQL │  │  /static/          │
│  ┌───────────┐  │  │             │  │                    │
│  │   SCRFD   │  │  └─────────────┘  └────────────────────┘
│  │ Detection │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │  ArcFace  │  │
│  │Embeddings │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │   FAISS   │  │
│  │  Search   │  │
│  └───────────┘  │
└─────────────────┘
```

### 2.2 Component Interactions

#### Student Registration Flow

```
User → Frontend → Backend → AI Service → FAISS Index
  ↓        ↓         ↓           ↓            ↓
Upload   Validate  Create    Extract     Store
Photo    Data      Student   Embedding   Vector
  ↓        ↓         ↓           ↓            ↓
         Success ← Response ← Success ← Updated
```

#### Attendance Marking Flow

```
User → Frontend → Backend → AI Service → FAISS Search
  ↓        ↓         ↓           ↓            ↓
Capture  Send     Validate   Detect      Match
Photo    Image    Session    Faces       Faces
  ↓        ↓         ↓           ↓            ↓
         Display ← Create ← Results ← Matches
                   Records
```

### 2.3 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    Student Registration                   │
└──────────────────────────────────────────────────────────┘
         │
         ▼
    [User Input]
    - Name
    - Email
    - Phone
    - Department
    - Photo
         │
         ▼
    [Frontend Validation]
    - Required fields
    - Email format
    - Phone format
    - Image size/type
         │
         ▼
    [Backend Processing]
    - Generate roll number
    - Save student data
    - Store photo file
         │
         ▼
    [AI Processing]
    - Detect face
    - Extract embedding
    - Quality check
         │
         ▼
    [FAISS Storage]
    - Add vector
    - Update index
    - Map student ID
         │
         ▼
    [Response]
    - Success/Error
    - Student details
    - Roll number

┌──────────────────────────────────────────────────────────┐
│                   Attendance Marking                      │
└──────────────────────────────────────────────────────────┘
         │
         ▼
    [Session Info]
    - Session ID
    - Department
    - Subject
         │
         ▼
    [Capture Image]
    - Webcam feed
    - Photo capture
    - Quality check
         │
         ▼
    [Face Detection]
    - Detect faces
    - Extract features
    - Quality gating
         │
         ▼
    [Face Recognition]
    - Search FAISS
    - Match faces
    - Calculate confidence
         │
         ▼
    [Attendance Record]
    - Create records
    - Update session
    - Calculate stats
         │
         ▼
    [Response]
    - Marked students
    - Unrecognized faces
    - Statistics
```

---

## 3. Database Schema

### 3.1 Entity Relationship Diagram (ERD)

```sql
-- Core Entities and Relationships

Department 1───N Student
     │
     └───N AttendanceSession
              │
              └───N AttendanceRecord ───N Student
                       │
                       └───1 User (marked_by)

User 1───N AttendanceSession (created_by)
```

### 3.2 Table Specifications

#### Department Table

```sql
CREATE TABLE departments_department (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_department_code ON departments_department(code);
CREATE INDEX idx_department_name ON departments_department(name);
```

**Constraints:**

- `name`: Unique, max 100 characters
- `code`: Unique, max 10 characters, alphanumeric
- `description`: Optional text field

**Business Rules:**

- Code must be uppercase
- Cannot delete department with existing students
- Cannot delete department with attendance sessions

#### Student Table

```sql
CREATE TABLE students_student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    photo VARCHAR(200),
    department_id INTEGER NOT NULL,
    face_encoding TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments_department(id) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX idx_student_roll_no ON students_student(roll_no);
CREATE INDEX idx_student_email ON students_student(email);
CREATE INDEX idx_student_department ON students_student(department_id);
CREATE INDEX idx_student_active ON students_student(is_active);
```

**Constraints:**

- `roll_no`: Unique, format: {DEPT_CODE}-{YEAR}-{SEQ}
- `email`: Unique, valid email format
- `phone`: Optional, 10-15 digits
- `photo`: Path to uploaded image
- `face_encoding`: JSON string of embedding (optional storage)

**Business Rules:**

- Roll number auto-generated on creation
- Cannot delete student with attendance records
- Email must be verified before activation
- Photo required for face registration

#### User Table (Django Auth)

```sql
CREATE TABLE auth_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Custom fields via profile extension
CREATE TABLE users_userprofile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    role VARCHAR(20) DEFAULT 'student',
    phone VARCHAR(15),
    department_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments_department(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_user_username ON auth_user(username);
CREATE INDEX idx_user_email ON auth_user(email);
CREATE INDEX idx_userprofile_role ON users_userprofile(role);
```

**Roles:**

- `student`: Regular student access
- `teacher`: Faculty access
- `admin`: Full system access

**Business Rules:**

- Username must be unique
- Password must meet complexity requirements
- Email must be verified for active accounts
- Cannot delete user with associated records

#### AttendanceSession Table

```sql
CREATE TABLE attendance_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    subject VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    created_by_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments_department(id) ON DELETE RESTRICT,
    FOREIGN KEY (created_by_id) REFERENCES auth_user(id) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX idx_session_department ON attendance_session(department_id);
CREATE INDEX idx_session_date ON attendance_session(date);
CREATE INDEX idx_session_status ON attendance_session(status);
CREATE INDEX idx_session_created_by ON attendance_session(created_by_id);
```

**Status Values:**

- `active`: Session in progress
- `completed`: Session ended
- `cancelled`: Session cancelled

**Business Rules:**

- Only teachers and admins can create sessions
- End time must be after start time
- Cannot modify completed sessions
- Automatically set status to completed after end_time

#### AttendanceRecord Table

```sql
CREATE TABLE attendance_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'present',
    confidence FLOAT,
    marked_by_id INTEGER,
    manual_override BOOLEAN DEFAULT FALSE,
    notes TEXT,
    FOREIGN KEY (session_id) REFERENCES attendance_session(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students_student(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    UNIQUE (session_id, student_id)
);

-- Indexes
CREATE INDEX idx_record_session ON attendance_record(session_id);
CREATE INDEX idx_record_student ON attendance_record(student_id);
CREATE INDEX idx_record_status ON attendance_record(status);
CREATE INDEX idx_record_timestamp ON attendance_record(timestamp);
```

**Status Values:**

- `present`: Student attended
- `absent`: Student did not attend
- `late`: Student arrived late
- `excused`: Excused absence

**Business Rules:**

- One record per student per session (UNIQUE constraint)
- Confidence stored from face recognition (0-1)
- Manual override flag for teacher corrections
- Cannot delete records after session completion

### 3.3 Data Validation Rules

#### Student Validation

```python
class StudentValidator:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone):
        """Validate phone number (10-15 digits)"""
        pattern = r'^\d{10,15}$'
        return re.match(pattern, phone) is not None

    @staticmethod
    def validate_photo(file):
        """Validate photo file"""
        valid_extensions = ['.jpg', '.jpeg', '.png']
        max_size = 5 * 1024 * 1024  # 5MB

        if file.size > max_size:
            raise ValidationError("File size exceeds 5MB")

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError("Invalid file format")

        return True
```

#### Session Validation

```python
class SessionValidator:
    @staticmethod
    def validate_time_range(start_time, end_time):
        """Validate session time range"""
        if end_time and end_time <= start_time:
            raise ValidationError("End time must be after start time")

        duration = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)
        if duration.total_seconds() > 4 * 3600:  # Max 4 hours
            raise ValidationError("Session duration exceeds maximum (4 hours)")

        return True

    @staticmethod
    def validate_date(date_value):
        """Validate session date"""
        today = date.today()
        if date_value < today:
            raise ValidationError("Cannot create session for past date")

        if date_value > today + timedelta(days=30):
            raise ValidationError("Cannot create session more than 30 days in advance")

        return True
```

---

## 4. API Specifications

### 4.1 Authentication APIs

#### POST /api/auth/register/

**Description:** Register a new user account

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "username": "string (required, 3-150 chars, alphanumeric)",
  "email": "string (required, valid email)",
  "password": "string (required, min 8 chars, must contain uppercase, lowercase, digit)",
  "first_name": "string (optional, max 150 chars)",
  "last_name": "string (optional, max 150 chars)",
  "role": "string (optional, one of: student, teacher, admin, default: student)",
  "phone": "string (optional, 10-15 digits)",
  "department": "integer (optional, valid department ID)"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "message": "User registered successfully. Please verify your email."
}
```

**Response (400 Bad Request):**

```json
{
  "error": "validation_error",
  "details": {
    "username": ["This field is required."],
    "email": ["Enter a valid email address."],
    "password": ["Password must contain at least one uppercase letter."]
  }
}
```

**Validation Rules:**

- Username: 3-150 characters, alphanumeric + underscore
- Email: Valid email format, unique
- Password: Min 8 chars, uppercase + lowercase + digit + special char
- Role: One of predefined roles
- Phone: 10-15 digits (if provided)

#### POST /api/auth/login/

**Description:** Authenticate user and receive JWT tokens

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response (200 OK):**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "student",
    "department": {
      "id": 1,
      "name": "Computer Science"
    }
  }
}
```

**Response (401 Unauthorized):**

```json
{
  "error": "invalid_credentials",
  "message": "Invalid username or password"
}
```

**Token Details:**

- Access Token: Valid for 24 hours
- Refresh Token: Valid for 7 days
- Algorithm: HS256
- Issuer: attendance-system

#### POST /api/auth/refresh/

**Description:** Refresh access token using refresh token

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "refresh": "string (required, valid refresh token)"
}
```

**Response (200 OK):**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access_expiry": "2025-11-01T10:00:00Z"
}
```

**Response (401 Unauthorized):**

```json
{
  "error": "token_expired",
  "message": "Refresh token has expired. Please login again."
}
```

### 4.2 Student APIs

#### POST /api/students/register/

**Description:** Register a new student with photo

**Request Headers:**

```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (Form Data):**

```
name: string (required, max 100 chars)
email: string (required, valid email)
phone: string (optional, 10-15 digits)
department: integer (required, valid department ID)
photo: file (required, jpg/jpeg/png, max 5MB)
```

**Response (201 Created):**

```json
{
  "id": 1,
  "roll_no": "CS-2025-001",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "department": {
    "id": 1,
    "name": "Computer Science",
    "code": "CS"
  },
  "photo": "/media/student_faces/john_doe_1730332800.jpg",
  "face_registered": true,
  "face_quality": "good",
  "created_at": "2025-10-31T10:00:00Z"
}
```

**Response (400 Bad Request):**

```json
{
  "error": "validation_error",
  "details": {
    "photo": ["No face detected in the uploaded image"],
    "email": ["Student with this email already exists"]
  }
}
```

**Response (422 Unprocessable Entity):**

```json
{
  "error": "face_quality_error",
  "message": "Face quality too low. Please upload a clearer photo.",
  "details": {
    "blur_score": 0.3,
    "face_size": 45,
    "requirements": {
      "min_blur_score": 0.5,
      "min_face_size": 80
    }
  }
}
```

**Processing Steps:**

1. Validate input data
2. Generate roll number
3. Save photo to media folder
4. Send photo to AI service for face detection
5. Extract face embedding
6. Store embedding in FAISS index
7. Create student record
8. Return success response

#### GET /api/students/

**Description:** List all students with pagination and filtering

**Request Headers:**

```
Authorization: Bearer {access_token}
```

**Query Parameters:**

```
page: integer (default: 1)
page_size: integer (default: 20, max: 100)
department: integer (optional, filter by department ID)
search: string (optional, search by name or roll number)
is_active: boolean (optional, filter by active status)
ordering: string (optional, one of: name, roll_no, created_at, -name, -roll_no, -created_at)
```

**Example Request:**

```
GET /api/students/?page=1&page_size=10&department=1&search=john&ordering=-created_at
```

**Response (200 OK):**

```json
{
  "count": 50,
  "next": "http://localhost:8000/api/students/?page=2&page_size=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "roll_no": "CS-2025-001",
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "1234567890",
      "department": {
        "id": 1,
        "name": "Computer Science",
        "code": "CS"
      },
      "photo": "/media/student_faces/john_doe.jpg",
      "is_active": true,
      "created_at": "2025-10-31T10:00:00Z"
    }
  ],
  "facets": {
    "total_students": 50,
    "active_students": 48,
    "inactive_students": 2,
    "by_department": {
      "Computer Science": 30,
      "Electronics": 20
    }
  }
}
```

#### GET /api/students/{id}/

**Description:** Get detailed information about a specific student

**Request Headers:**

```
Authorization: Bearer {access_token}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "roll_no": "CS-2025-001",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "department": {
    "id": 1,
    "name": "Computer Science",
    "code": "CS",
    "description": "Department of Computer Science and Engineering"
  },
  "photo": "/media/student_faces/john_doe.jpg",
  "is_active": true,
  "created_at": "2025-10-31T10:00:00Z",
  "updated_at": "2025-10-31T10:00:00Z",
  "attendance_stats": {
    "total_sessions": 10,
    "present": 9,
    "absent": 1,
    "late": 0,
    "attendance_percentage": 90.0
  },
  "recent_attendance": [
    {
      "session_id": 5,
      "subject": "Machine Learning",
      "date": "2025-10-30",
      "status": "present",
      "timestamp": "2025-10-30T10:05:00Z"
    }
  ]
}
```

**Response (404 Not Found):**

```json
{
  "error": "not_found",
  "message": "Student with id 999 does not exist"
}
```

#### PUT /api/students/{id}/

**Description:** Update student information

**Request Headers:**

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**

```json
{
  "name": "string (optional)",
  "email": "string (optional)",
  "phone": "string (optional)",
  "department": "integer (optional)",
  "is_active": "boolean (optional)"
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "roll_no": "CS-2025-001",
  "name": "John Updated",
  "email": "john_new@example.com",
  "phone": "9876543210",
  "department": {
    "id": 1,
    "name": "Computer Science"
  },
  "is_active": true,
  "updated_at": "2025-10-31T11:00:00Z"
}
```

**Note:** Roll number and photo cannot be updated via this endpoint.

#### DELETE /api/students/{id}/

**Description:** Delete a student record

**Request Headers:**

```
Authorization: Bearer {access_token}
```

**Response (204 No Content):**

```
(Empty response body)
```

**Response (400 Bad Request):**

```json
{
  "error": "deletion_error",
  "message": "Cannot delete student with existing attendance records",
  "details": {
    "attendance_records": 15,
    "suggestion": "Mark student as inactive instead"
  }
}
```

**Business Logic:**

- Soft delete: Set `is_active = False`
- Hard delete: Only if no attendance records exist
- Remove face embedding from FAISS index
- Delete photo file from media folder

### 4.3 Attendance APIs

#### POST /api/attendance/sessions/

**Description:** Create a new attendance session

**Request Headers:**

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**

```json
{
  "department": "integer (required, valid department ID)",
  "subject": "string (required, max 100 chars)",
  "date": "string (required, format: YYYY-MM-DD)",
  "start_time": "string (required, format: HH:MM:SS)",
  "end_time": "string (optional, format: HH:MM:SS)",
  "notes": "string (optional)"
}
```

**Example:**

```json
{
  "department": 1,
  "subject": "Machine Learning",
  "date": "2025-10-31",
  "start_time": "10:00:00",
  "end_time": "11:00:00",
  "notes": "Midterm exam attendance"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "department": {
    "id": 1,
    "name": "Computer Science",
    "code": "CS"
  },
  "subject": "Machine Learning",
  "date": "2025-10-31",
  "start_time": "10:00:00",
  "end_time": "11:00:00",
  "status": "active",
  "created_by": {
    "id": 5,
    "username": "teacher_john",
    "name": "John Teacher"
  },
  "total_students": 30,
  "present_count": 0,
  "absent_count": 0,
  "attendance_percentage": 0.0,
  "created_at": "2025-10-31T09:55:00Z"
}
```

**Permissions:**

- Only teachers and admins can create sessions
- Teachers can only create sessions for their assigned departments

#### POST /api/attendance/mark/

**Description:** Mark attendance using face recognition

**Request Headers:**

```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (Form Data):**

```
session: integer (required, valid session ID)
image: file (required, jpg/jpeg/png, max 10MB)
manual: boolean (optional, default: false)
```

**Response (200 OK):**

```json
{
  "session_id": 1,
  "session_info": {
    "subject": "Machine Learning",
    "date": "2025-10-31",
    "department": "Computer Science"
  },
  "processing_time_ms": 65,
  "faces_detected": 3,
  "faces_recognized": 2,
  "attendance_marked": [
    {
      "student": {
        "id": 1,
        "roll_no": "CS-2025-001",
        "name": "John Doe"
      },
      "status": "present",
      "confidence": 0.95,
      "timestamp": "2025-10-31T10:05:30Z",
      "already_marked": false,
      "bbox": [100, 150, 250, 300]
    },
    {
      "student": {
        "id": 2,
        "roll_no": "CS-2025-002",
        "name": "Jane Smith"
      },
      "status": "present",
      "confidence": 0.92,
      "timestamp": "2025-10-31T10:05:30Z",
      "already_marked": false,
      "bbox": [350, 150, 500, 300]
    }
  ],
  "unrecognized": [
    {
      "bbox": [600, 150, 750, 300],
      "reason": "No match found (confidence below threshold)"
    }
  ],
  "summary": {
    "total_marked": 2,
    "new_marks": 2,
    "duplicate_attempts": 0,
    "session_attendance": {
      "total": 30,
      "present": 2,
      "percentage": 6.67
    }
  }
}
```

**Response (400 Bad Request):**

```json
{
  "error": "session_error",
  "message": "Session has ended or is inactive",
  "details": {
    "session_id": 1,
    "status": "completed",
    "end_time": "2025-10-31T11:00:00Z"
  }
}
```

**Processing Logic:**

1. Validate session is active
2. Send image to AI service
3. Detect and recognize faces
4. Filter by confidence threshold (>= 0.8)
5. Create attendance records
6. Update session statistics
7. Return detailed results

#### GET /api/attendance/sessions/

**Description:** List attendance sessions with filters

**Request Headers:**

```
Authorization: Bearer {access_token}
```

**Query Parameters:**

```
page: integer (default: 1)
page_size: integer (default: 20)
department: integer (optional)
date: string (optional, format: YYYY-MM-DD)
date_from: string (optional, format: YYYY-MM-DD)
date_to: string (optional, format: YYYY-MM-DD)
status: string (optional, one of: active, completed, cancelled)
subject: string (optional, partial match)
created_by: integer (optional, user ID)
ordering: string (optional)
```

**Response (200 OK):**

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/attendance/sessions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "department": {
        "id": 1,
        "name": "Computer Science"
      },
      "subject": "Machine Learning",
      "date": "2025-10-31",
      "start_time": "10:00:00",
      "end_time": "11:00:00",
      "status": "completed",
      "created_by": "John Teacher",
      "statistics": {
        "total": 30,
        "present": 27,
        "absent": 3,
        "percentage": 90.0
      }
    }
  ]
}
```

#### GET /api/attendance/records/

**Description:** Get attendance records with filtering

**Request Headers:**

```
Authorization: Bearer {access_token}
```

**Query Parameters:**

```
session: integer (optional, filter by session)
student: integer (optional, filter by student)
date: string (optional)
date_from: string (optional)
date_to: string (optional)
status: string (optional)
department: integer (optional)
```

**Response (200 OK):**

```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "session": {
        "id": 1,
        "subject": "Machine Learning",
        "date": "2025-10-31",
        "department": "Computer Science"
      },
      "student": {
        "id": 1,
        "roll_no": "CS-2025-001",
        "name": "John Doe"
      },
      "status": "present",
      "confidence": 0.95,
      "timestamp": "2025-10-31T10:05:30Z",
      "marked_by": "Auto (Face Recognition)",
      "manual_override": false
    }
  ]
}
```

#### GET /api/attendance/statistics/

**Description:** Get attendance statistics and analytics

**Request Headers:**

```
Authorization: Bearer {access_token}
```

**Query Parameters:**

```
student: integer (optional)
department: integer (optional)
date_from: string (required, format: YYYY-MM-DD)
date_to: string (required, format: YYYY-MM-DD)
group_by: string (optional, one of: day, week, month, student, subject)
```

**Response (200 OK):**

```json
{
  "period": {
    "from": "2025-10-01",
    "to": "2025-10-31"
  },
  "overall": {
    "total_sessions": 50,
    "total_records": 1500,
    "present": 1350,
    "absent": 120,
    "late": 30,
    "attendance_percentage": 90.0
  },
  "by_department": [
    {
      "department": "Computer Science",
      "total_sessions": 30,
      "attendance_percentage": 92.0
    }
  ],
  "by_student": [
    {
      "student": {
        "roll_no": "CS-2025-001",
        "name": "John Doe"
      },
      "total_sessions": 25,
      "present": 23,
      "absent": 2,
      "percentage": 92.0
    }
  ],
  "trends": {
    "daily": [
      {
        "date": "2025-10-01",
        "sessions": 2,
        "percentage": 88.0
      }
    ]
  }
}
```

### 4.4 AI Service APIs

#### POST /api/ai/detect/

**Description:** Detect faces in an image

**Request Headers:**

```
Content-Type: multipart/form-data
```

**Request Body (Form Data):**

```
file: image file (jpg/jpeg/png, max 10MB)
min_confidence: float (optional, default: 0.5, range: 0.0-1.0)
```

**Response (200 OK):**

```json
{
  "success": true,
  "processing_time_ms": 35,
  "image_size": {
    "width": 1920,
    "height": 1080
  },
  "faces_detected": 2,
  "faces": [
    {
      "bbox": [100, 150, 250, 300],
      "confidence": 0.99,
      "landmarks": {
        "left_eye": [120, 180],
        "right_eye": [180, 180],
        "nose": [150, 220],
        "left_mouth": [130, 250],
        "right_mouth": [170, 250]
      },
      "quality_metrics": {
        "blur_score": 0.85,
        "brightness": 0.65,
        "face_size": 150,
        "angle": 5.2,
        "quality": "good"
      }
    }
  ]
}
```

**Response (400 Bad Request):**

```json
{
  "error": "no_faces_detected",
  "message": "No faces detected in the image",
  "suggestions": [
    "Ensure face is clearly visible",
    "Check lighting conditions",
    "Face should be at least 80x80 pixels"
  ]
}
```

#### POST /api/ai/register/

**Description:** Register a face encoding for a student

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "student_id": "integer (required)",
  "image_path": "string (required, path to student photo)"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "student_id": 1,
  "embedding_generated": true,
  "embedding_size": 512,
  "quality_check": {
    "blur_score": 0.85,
    "face_size": 150,
    "passed": true
  },
  "faiss_index": {
    "total_vectors": 150,
    "index_updated": true
  },
  "processing_time_ms": 48
}
```

**Response (422 Unprocessable Entity):**

```json
{
  "error": "quality_check_failed",
  "message": "Face quality insufficient for registration",
  "details": {
    "blur_score": 0.3,
    "required_blur_score": 0.5,
    "face_size": 45,
    "required_face_size": 80
  }
}
```

#### POST /api/ai/recognize/

**Description:** Recognize faces in an image against registered students

**Request Headers:**

```
Content-Type: multipart/form-data
```

**Request Body (Form Data):**

```
file: image file (jpg/jpeg/png, max 10MB)
confidence_threshold: float (optional, default: 0.35, range: 0.0-1.0)
top_k: integer (optional, default: 1, range: 1-5)
```

**Response (200 OK):**

```json
{
  "success": true,
  "processing_time_ms": 67,
  "faces_detected": 3,
  "faces_recognized": 2,
  "faces": [
    {
      "bbox": [100, 150, 250, 300],
      "recognized": true,
      "student_id": 1,
      "distance": 0.15,
      "confidence": 0.95,
      "match_quality": "excellent",
      "top_matches": [
        {
          "student_id": 1,
          "distance": 0.15,
          "confidence": 0.95
        }
      ]
    },
    {
      "bbox": [350, 150, 500, 300],
      "recognized": true,
      "student_id": 2,
      "distance": 0.25,
      "confidence": 0.88,
      "match_quality": "good"
    },
    {
      "bbox": [600, 150, 750, 300],
      "recognized": false,
      "distance": 0.52,
      "confidence": 0.32,
      "reason": "Distance exceeds threshold",
      "closest_match": {
        "student_id": 5,
        "distance": 0.52,
        "confidence": 0.32
      }
    }
  ],
  "summary": {
    "total_faces": 3,
    "recognized": 2,
    "unrecognized": 1,
    "recognition_rate": 66.67
  }
}
```

**Confidence Calculation:**

```python
# Cosine similarity distance (0 = identical, 2 = opposite)
distance = faiss_search_result

# Convert to confidence score (0-1)
confidence = max(0.0, 1.0 - (distance / 2.0))

# Match quality categories
if distance < 0.25:
    quality = "excellent"  # Very confident match
elif distance < 0.35:
    quality = "good"       # Confident match (threshold)
elif distance < 0.45:
    quality = "fair"       # Uncertain match
else:
    quality = "poor"       # Not a match
```

#### GET /api/ai/health/

**Description:** Check AI service health and model status

**Response (200 OK):**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-31T10:00:00Z",
  "models": {
    "face_detection": {
      "name": "SCRFD (buffalo_sc)",
      "loaded": true,
      "model_size_mb": 2.5,
      "input_size": [640, 640],
      "backend": "onnxruntime"
    },
    "face_recognition": {
      "name": "ArcFace (w600k_r50)",
      "loaded": true,
      "embedding_size": 512,
      "backend": "onnxruntime"
    }
  },
  "faiss_index": {
    "loaded": true,
    "total_vectors": 150,
    "dimension": 512,
    "index_type": "IndexFlatL2",
    "size_mb": 0.3
  },
  "performance": {
    "avg_detection_time_ms": 35,
    "avg_recognition_time_ms": 15,
    "total_requests": 1523,
    "uptime_hours": 24.5
  },
  "system": {
    "cpu_usage_percent": 15.3,
    "memory_usage_mb": 450,
    "gpu_available": false
  }
}
```

---

## 5. Security Specifications

### 5.1 Authentication Flow

```
┌─────────┐                                           ┌─────────┐
│ Client  │                                           │ Server  │
└────┬────┘                                           └────┬────┘
     │                                                      │
     │  1. POST /api/auth/login/                           │
     │     {username, password}                            │
     ├────────────────────────────────────────────────────►│
     │                                                      │
     │                                        2. Validate  │
     │                                           credentials│
     │                                                      │
     │  3. 200 OK                                          │
     │     {access, refresh, user}                         │
     │◄────────────────────────────────────────────────────┤
     │                                                      │
     │  4. Store tokens                                    │
     │     localStorage/sessionStorage                     │
     │                                                      │
     │  5. API Request                                     │
     │     Authorization: Bearer {access_token}            │
     ├────────────────────────────────────────────────────►│
     │                                                      │
     │                                        6. Verify    │
     │                                           token     │
     │                                                      │
     │  7. 200 OK {data}                                   │
     │◄────────────────────────────────────────────────────┤
     │                                                      │
     │  ... token expires after 24h ...                    │
     │                                                      │
     │  8. API Request (expired token)                     │
     ├────────────────────────────────────────────────────►│
     │                                                      │
     │  9. 401 Unauthorized                                │
     │     {error: "token_expired"}                        │
     │◄────────────────────────────────────────────────────┤
     │                                                      │
     │  10. POST /api/auth/refresh/                        │
     │      {refresh}                                      │
     ├────────────────────────────────────────────────────►│
     │                                                      │
     │  11. 200 OK                                         │
     │      {access}                                       │
     │◄────────────────────────────────────────────────────┤
     │                                                      │
     │  12. Retry API Request                              │
     │      Authorization: Bearer {new_access_token}       │
     ├────────────────────────────────────────────────────►│
     │                                                      │
     │  13. 200 OK {data}                                  │
     │◄────────────────────────────────────────────────────┤
     │                                                      │
```

### 5.2 Authorization Matrix

| Role    | Student CRUD | Session Create | Attendance Mark | Reports View | User Manage |
| ------- | ------------ | -------------- | --------------- | ------------ | ----------- |
| Student | Read (Self)  | ❌             | ❌              | Read (Self)  | ❌          |
| Teacher | Read All     | ✅             | ✅              | Read All     | ❌          |
| Admin   | Full CRUD    | ✅             | ✅              | Full Access  | ✅          |

### 5.3 Data Encryption

**Password Hashing:**

```python
# Django PBKDF2 with SHA256
algorithm: PBKDF2
hash_function: SHA256
iterations: 320000
salt: random per password (32 bytes)

Example:
pbkdf2_sha256$320000$randomsalt$hashed_password
```

**JWT Token Structure:**

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": 1,
    "username": "john_doe",
    "role": "student",
    "exp": 1730419200,
    "iat": 1730332800,
    "token_type": "access"
  },
  "signature": "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), secret)"
}
```

**File Storage Security:**

```python
# Secure filename generation
import hashlib
import time

def generate_secure_filename(original_filename):
    timestamp = str(time.time())
    hash_input = f"{original_filename}{timestamp}".encode()
    hash_value = hashlib.sha256(hash_input).hexdigest()[:16]
    ext = os.path.splitext(original_filename)[1]
    return f"student_{hash_value}{ext}"

# Result: student_a3f5e9b2c1d4f876.jpg
```

---

## 6. Performance Specifications

### 6.1 Response Time Requirements

| Endpoint Type     | Target Response Time | Maximum Acceptable |
| ----------------- | -------------------- | ------------------ |
| Authentication    | < 200ms              | 500ms              |
| CRUD Operations   | < 100ms              | 300ms              |
| Face Detection    | < 50ms               | 100ms              |
| Face Recognition  | < 70ms               | 150ms              |
| Report Generation | < 500ms              | 2000ms             |

### 6.2 Throughput Requirements

| Service     | Requests/Second | Concurrent Users |
| ----------- | --------------- | ---------------- |
| Backend API | 100+            | 50+              |
| AI Service  | 20-30           | 10-15            |
| Database    | 1000+ queries   | N/A              |

### 6.3 Resource Usage

**Backend (Django):**

- CPU: < 50% (4 cores)
- Memory: < 512MB (idle), < 1GB (active)
- Disk I/O: < 10MB/s

**AI Service (FastAPI):**

- CPU: < 80% (4 cores)
- Memory: < 2GB (models loaded)
- GPU: Optional (10x speed improvement)

**Database:**

- Storage: ~10MB per 1000 students
- Memory: < 256MB
- Connections: 20 concurrent max

### 6.4 Scalability Metrics

**Current Capacity:**

- Students: Up to 10,000
- Concurrent sessions: 50
- Daily attendance marks: 50,000
- Face recognition speed: 28 faces/second

**Scaling Strategy:**

- Horizontal scaling: Add more AI service instances
- Database: Migrate to PostgreSQL for > 5000 students
- Caching: Implement Redis for frequent queries
- Load balancing: Nginx for multiple backend instances

---

## 7. Error Handling

### 7.1 Error Response Format

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional context",
    "timestamp": "2025-10-31T10:00:00Z"
  },
  "trace_id": "abc123def456"
}
```

### 7.2 HTTP Status Codes

| Code | Meaning               | Usage                                |
| ---- | --------------------- | ------------------------------------ |
| 200  | OK                    | Successful GET, PUT, PATCH           |
| 201  | Created               | Successful POST                      |
| 204  | No Content            | Successful DELETE                    |
| 400  | Bad Request           | Validation errors, malformed request |
| 401  | Unauthorized          | Missing/invalid token                |
| 403  | Forbidden             | Insufficient permissions             |
| 404  | Not Found             | Resource doesn't exist               |
| 422  | Unprocessable Entity  | Business logic error                 |
| 429  | Too Many Requests     | Rate limit exceeded                  |
| 500  | Internal Server Error | Unexpected server error              |
| 503  | Service Unavailable   | Maintenance, overload                |

### 7.3 Common Error Codes

**Authentication Errors:**

- `invalid_credentials`: Wrong username/password
- `token_expired`: Access token expired
- `token_invalid`: Malformed or tampered token
- `refresh_token_expired`: Refresh token expired

**Validation Errors:**

- `validation_error`: Input validation failed
- `missing_required_field`: Required field not provided
- `invalid_format`: Field format incorrect
- `value_out_of_range`: Value exceeds limits

**Business Logic Errors:**

- `duplicate_entry`: Resource already exists
- `resource_not_found`: Resource doesn't exist
- `insufficient_permissions`: User lacks required permissions
- `session_inactive`: Session is not active
- `face_not_detected`: No face in image
- `face_quality_low`: Face quality insufficient

**AI Service Errors:**

- `model_load_error`: Failed to load ML model
- `inference_error`: Error during model inference
- `faiss_index_error`: FAISS index operation failed
- `embedding_generation_error`: Failed to generate embedding

---

## 8. Testing Specifications

### 8.1 Unit Test Coverage

**Backend Tests:**

```python
# tests/test_students.py
class StudentTestCase(TestCase):
    def test_roll_number_generation(self):
        """Test roll number is correctly generated"""
        dept = Department.objects.create(name="CS", code="CS")
        student = Student.objects.create(
            name="John",
            email="john@test.com",
            department=dept
        )
        self.assertRegex(student.roll_no, r'^CS-\d{4}-\d{3}$')

    def test_duplicate_email_raises_error(self):
        """Test duplicate email raises validation error"""
        dept = Department.objects.create(name="CS", code="CS")
        Student.objects.create(
            name="John",
            email="john@test.com",
            department=dept
        )
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                name="Jane",
                email="john@test.com",
                department=dept
            )
```

**AI Service Tests:**

```python
# tests/test_ai_service.py
import pytest
from fastapi.testclient import TestClient

def test_face_detection():
    """Test face detection endpoint"""
    with open("test_images/face.jpg", "rb") as f:
        response = client.post(
            "/api/ai/detect/",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["faces_detected"] > 0
    assert "bbox" in data["faces"][0]

def test_face_recognition_accuracy():
    """Test face recognition accuracy on known faces"""
    # Test with known student photo
    with open("test_images/student_001.jpg", "rb") as f:
        response = client.post(
            "/api/ai/recognize/",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    data = response.json()
    assert data["faces"][0]["recognized"] == True
    assert data["faces"][0]["student_id"] == 1
    assert data["faces"][0]["confidence"] > 0.9
```

### 8.2 Integration Tests

**End-to-End Workflow:**

```python
def test_complete_attendance_workflow():
    """Test complete attendance marking workflow"""
    # 1. Create session
    session = create_attendance_session(department=1, subject="ML")

    # 2. Register student with photo
    student = register_student(
        name="Test Student",
        email="test@example.com",
        photo="test_photo.jpg"
    )

    # 3. Mark attendance with face recognition
    result = mark_attendance(
        session_id=session.id,
        image="group_photo.jpg"
    )

    # 4. Verify attendance recorded
    assert result["attendance_marked"][0]["student"]["id"] == student.id
    assert result["attendance_marked"][0]["status"] == "present"

    # 5. Check attendance record created
    record = AttendanceRecord.objects.get(
        session=session,
        student=student
    )
    assert record.status == "present"
```

### 8.3 Performance Tests

**Load Testing:**

```python
from locust import HttpUser, task, between

class AttendanceUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def list_students(self):
        self.client.get("/api/students/")

    @task(2)
    def view_sessions(self):
        self.client.get("/api/attendance/sessions/")

    @task(1)
    def mark_attendance(self):
        with open("test_photo.jpg", "rb") as f:
            self.client.post(
                "/api/attendance/mark/",
                data={"session": 1},
                files={"image": f}
            )

# Run: locust -f locustfile.py --users 50 --spawn-rate 10
```

---

## Appendices

### A. Glossary

- **SCRFD**: Sample and Computation Redistribution for Efficient Face Detection
- **ArcFace**: Additive Angular Margin Loss for Deep Face Recognition
- **FAISS**: Facebook AI Similarity Search - vector database
- **ONNX**: Open Neural Network Exchange - model format
- **JWT**: JSON Web Token - authentication token format
- **CORS**: Cross-Origin Resource Sharing
- **ORM**: Object-Relational Mapping

### B. References

- InsightFace: https://github.com/deepinsight/insightface
- FAISS Documentation: https://faiss.ai/
- Django Documentation: https://docs.djangoproject.com/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- ONNX Runtime: https://onnxruntime.ai/

### C. Change Log

| Version | Date       | Changes                         |
| ------- | ---------- | ------------------------------- |
| 1.0     | 2025-10-31 | Initial technical specification |

---

**Document Status:** Approved  
**Last Reviewed:** October 31, 2025  
**Next Review:** January 31, 2026
