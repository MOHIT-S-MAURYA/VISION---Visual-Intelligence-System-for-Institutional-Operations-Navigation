# Teacher Login & Credentials Management

## How Teachers Receive Their Credentials

### 1. **Admin Creates Teacher Account**

Admins use the Django Admin Panel to create teacher accounts:

- Navigate to: `http://localhost:8000/admin/`
- Login with admin credentials
- Go to **Students → Teachers** → **Add Teacher**
- Fill in:
  - Username (e.g., `dr.sharma`)
  - Employee ID (e.g., `T001`)
  - Full Name
  - Email & Phone
  - Password

### 2. **Automated Credentials File**

When running `python manage.py populate_data`, a file is automatically generated:

- **Location**: `backend/TEACHER_CREDENTIALS.txt`
- **Contains**: All teacher login details with their assigned subjects
- **Format**: Easy to print/share with individual teachers

### 3. **Manual Credential Sharing**

Admin should:

1. Open `TEACHER_CREDENTIALS.txt`
2. Find the specific teacher's section
3. Share credentials securely (email/printed letter/in person)
4. Remind teacher to change password after first login

## Teacher Login Options

Teachers have **TWO ways** to login:

### Option 1: Username

```
Username: dr.sharma
Password: teacher123
```

### Option 2: Employee ID

```
Username: T001
Password: teacher123
```

Both work identically!

## How It Works Technically

### Backend (Django)

- **Custom Authentication** (`attendance_system/custom_auth.py`):
  - Tries to authenticate with username first
  - If username not found, looks up by employee_id in Teacher model
  - Returns JWT token on successful authentication

### Frontend (React)

- **Login Page** (`frontend/src/pages/Login.jsx`):
  - Single input field accepts both username and employee ID
  - Placeholder shows both options: `e.g., dr.sharma or T001`
  - Help text: "You can use either your username or employee ID"

## Sample Teacher Accounts

After running `populate_data`, you get 9 teachers:

| Name                | Employee ID | Username   | Password   | Department |
| ------------------- | ----------- | ---------- | ---------- | ---------- |
| Dr. Rajesh Sharma   | T001        | dr.sharma  | teacher123 | CSE        |
| Prof. Priya Gupta   | T002        | prof.gupta | teacher123 | CSE        |
| Dr. Amit Kumar      | T003        | dr.kumar   | teacher123 | CSE/IT     |
| Dr. Suresh Patel    | T004        | dr.patel   | teacher123 | ECE        |
| Prof. Lakshmi Reddy | T005        | prof.reddy | teacher123 | ECE        |
| Dr. Vikram Singh    | T006        | dr.singh   | teacher123 | ME         |
| Prof. Anita Verma   | T007        | prof.verma | teacher123 | ME         |
| Dr. Kavita Mehta    | T008        | dr.mehta   | teacher123 | Math (All) |
| Prof. Rahul Joshi   | T009        | prof.joshi | teacher123 | MCA        |

## Testing Login

### Test with Username:

```bash
# Frontend login page
Username: dr.sharma
Password: teacher123
```

### Test with Employee ID:

```bash
# Frontend login page
Username: T001
Password: teacher123
```

Both should successfully login the same teacher!

## Creating New Teachers (Admin Guide)

### Via Django Admin Panel:

1. **Login to Admin Panel**: `http://localhost:8000/admin/`
2. **Navigate to**: Students → Teachers → Add Teacher
3. **Create User First**:
   - Click the "+" next to User field
   - Enter username, email, password
   - Mark as "Staff status" if admin
4. **Fill Teacher Info**:
   - Select the created user
   - Enter Employee ID (must be unique, e.g., T010)
   - Enter Full Name, Email, Phone
5. **Assign Subjects**:
   - Go to Students → Teacher Subject Assignments
   - Create assignment linking teacher to subject
6. **Share Credentials**:
   - Send teacher their username/employee_id and temporary password
   - Ask them to change password on first login

### Credentials Template for New Teachers:

```
Dear [Teacher Name],

Your account has been created in the Attendance Management System.

Login Details:
- Website: http://your-domain.com
- Username: [username]
- Employee ID: [emp_id] (you can use this to login too)
- Temporary Password: [password]

Please change your password after your first login.

You have been assigned the following subjects:
- [Subject 1] ([Department] - [Year])
- [Subject 2] ([Department] - [Year])

For any issues, contact the system administrator.

Best regards,
Admin Team
```

## Security Notes

1. ✅ **Default passwords** should be changed after first login
2. ✅ **Employee IDs** must be unique
3. ✅ **Credentials file** (`TEACHER_CREDENTIALS.txt`) should be kept secure
4. ✅ **Share credentials** through secure channels (not public/group messages)
5. ✅ **JWT tokens** used for API authentication (secure)

## Password Change Process

Teachers can change their password via:

1. Django Admin Panel (if they have staff access)
2. Custom password change endpoint (to be implemented if needed)
3. Admin can reset password via Django Admin Panel

---

**Note**: The `TEACHER_CREDENTIALS.txt` file is regenerated every time you run `python manage.py populate_data`. Keep a backup if you've made manual changes!
