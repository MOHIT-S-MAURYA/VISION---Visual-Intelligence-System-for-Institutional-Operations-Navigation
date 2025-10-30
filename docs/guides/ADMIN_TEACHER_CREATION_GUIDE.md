# Admin Guide: Creating Teachers

## How to Create a New Teacher

### Step 1: Access Django Admin

1. Login to Django Admin: `http://localhost:8000/admin/`
2. Navigate to: **Students → Teachers**
3. Click **"ADD TEACHER"** button (top right)

### Step 2: Fill Teacher Information

You'll see a form with the following sections:

#### **Account Information**

- **Username**: Enter login username (e.g., `dr.patel`)
  - Used for login
  - Must be unique
  - No spaces allowed
- **Password**: Enter initial password for teacher
  - Teacher will use this to login
  - Share securely with the teacher
  - Recommend asking teacher to change after first login

#### **Personal Information**

- **Full Name**: Teacher's full name (e.g., `Dr. Suresh Patel`)
- **Employee ID**: ✨ **AUTO-GENERATED** - Don't edit this!
  - System automatically generates: T001, T002, T003, etc.
  - Read-only field (grayed out)
  - Sequential numbering
- **Email**: Teacher's email (optional)
- **Phone**: Teacher's phone number (optional, format: +91 98765 43210)

#### **Status**

- **Is active**: Keep checked (unchecked to disable account)

### Step 3: Save

Click **"SAVE"** button at the bottom.

You'll see a success message:

```
Teacher created successfully!
Login credentials: Username/Employee ID: dr.patel or T010,
Password: (as set). Please share these credentials securely with the teacher.
```

### Step 4: Share Credentials with Teacher

Send teacher their login details via secure channel:

**Template Email:**

```
Dear [Teacher Name],

Your account has been created in the Attendance Management System.

Login Details:
- Website: http://[your-domain]/login
- Username: [username] (e.g., dr.patel)
- Employee ID: [emp_id] (e.g., T010)
- Password: [password-you-set]

You can login using EITHER your username OR employee ID.

Please change your password after your first login for security.

For support, contact: [admin-contact]

Best regards,
Administration
```

## Example: Creating Dr. Suresh Patel

### Form Input:

```
Account Information:
  Username: dr.patel
  Password: Welcome@123

Personal Information:
  Full Name: Dr. Suresh Patel
  Employee ID: T010 (auto-generated, don't touch!)
  Email: suresh.patel@university.edu.in
  Phone: +91 98765 43210

Status:
  ☑ Is active
```

### Result:

- Teacher created with Employee ID: **T010**
- Can login with: `dr.patel` OR `T010`
- Password: `Welcome@123`

## Editing Existing Teachers

### To Update Teacher Info:

1. Go to **Students → Teachers**
2. Click on teacher name
3. Modify fields as needed
4. **Password field**:
   - Leave blank to keep current password
   - Enter new password to change it
5. **Employee ID**: Cannot be changed (read-only)
6. Click **SAVE**

## Assigning Subjects to Teachers

After creating teacher, assign subjects:

1. Go to **Students → Teacher Subject Assignments**
2. Click **"ADD TEACHER SUBJECT ASSIGNMENT"**
3. Select:
   - **Teacher**: Choose from dropdown
   - **Subject**: Choose subject to assign
   - **Academic Year**: e.g., 2024-25
   - **Notes**: Optional notes
4. Click **SAVE**

Teacher will now see this subject when they login!

## Auto-Generated Employee IDs

### How It Works:

- System finds the highest existing employee ID
- Increments the number
- Formats as: T001, T002, T003, ..., T099, T100, etc.

### Examples:

| Order         | Generated ID |
| ------------- | ------------ |
| 1st teacher   | T001         |
| 2nd teacher   | T002         |
| 10th teacher  | T010         |
| 100th teacher | T100         |

### Important Notes:

✅ Employee IDs are **sequential** and **cannot be skipped**
✅ Employee IDs are **read-only** after creation
✅ System ensures **uniqueness** automatically
❌ Don't try to manually edit employee_id in database

## Bulk Teacher Creation

For creating multiple teachers at once:

### Option 1: Django Admin (One by One)

- Best for small numbers (1-10 teachers)
- Use the form as described above

### Option 2: Management Command (Bulk)

- Best for large numbers (10+ teachers)
- Modify `populate_data.py` with your teacher list
- Run: `python manage.py populate_data`

### Option 3: CSV Import (Future Enhancement)

- Not currently implemented
- Can be added if needed

## Common Issues & Solutions

### ❌ "Username already exists"

**Problem**: Username is taken
**Solution**: Choose a different username

### ❌ "User with this username already exists"

**Problem**: A Django user account with that username exists
**Solution**: Use a different username or delete/rename the existing user

### ❌ Employee ID shows as blank

**Problem**: JavaScript disabled or form error
**Solution**: Refresh page, employee ID should auto-populate

### ❌ Teacher can't login

**Check**:

1. Is teacher marked as "Active"?
2. Is password correct?
3. Is username/employee_id typed correctly?
4. Check Django admin → Users → [username] → "Active" is checked

## Security Best Practices

1. ✅ Use **strong passwords** (minimum 8 chars, mix of letters/numbers/symbols)
2. ✅ Share credentials via **secure channels** (not public chat/email groups)
3. ✅ Ask teachers to **change password** after first login
4. ✅ Disable (uncheck "Is active") instead of deleting teachers
5. ✅ Regularly **audit** active teachers
6. ✅ Use **unique usernames** (avoid generic ones like "teacher1")

## Password Guidelines for Teachers

Recommend teachers use passwords with:

- Minimum 8 characters
- Mix of uppercase and lowercase
- At least one number
- At least one special character (@, !, #, etc.)

Example strong passwords:

- `Teach@2024`
- `Welcome#123`
- `MyPass@456`

---

**Need Help?** Contact system administrator or refer to TEACHER_LOGIN_GUIDE.md
