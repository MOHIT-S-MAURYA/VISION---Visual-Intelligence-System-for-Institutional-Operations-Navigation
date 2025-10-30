# Database Population & Admin Access

## ✅ Database Populated Successfully!

The database has been populated with realistic Indian university data.

### 📊 Database Summary
- **9 Departments** (CSE, ECE, ME, CE, EE, IT, MCA, MTech-CSE, MBA)
- **9 Teachers** (Faculty across different departments)
- **39 Subjects** (Spanning all departments and years)
- **24 Teacher-Subject Assignments** (Teachers assigned to their subjects)
- **20 Students** (Sample students across departments)

---

## 🔑 Login Credentials

### Admin Account
```
Username: admin
Password: admin123
```
**Access:** Full admin panel access via Django Admin

### Teacher Accounts
All teachers have the same password for testing:
```
Password: teacher123
```

**Example Teacher Logins:**
```
dr.sharma   / teacher123  (CSE Faculty - Programming, Data Structures, OS)
prof.gupta  / teacher123  (CSE Faculty - DBMS, Software Engineering, ML)
dr.kumar    / teacher123  (CSE/IT Faculty - Networks, Web Tech)
dr.patel    / teacher123  (ECE Faculty - Electrical, Analog Electronics)
prof.reddy  / teacher123  (ECE Faculty - Digital Electronics, Signals)
dr.singh    / teacher123  (ME Faculty - Mechanics, Thermodynamics)
prof.verma  / teacher123  (ME Faculty - Fluid Mechanics, Manufacturing)
dr.mehta    / teacher123  (Mathematics - Cross-departmental)
prof.joshi  / teacher123  (MCA Faculty - Java, Cloud Computing)
```

---

## 🎓 Sample Data Structure

### Departments
| Code | Name | Type | Duration |
|------|------|------|----------|
| CSE | Computer Science and Engineering | UG | 4 years |
| ECE | Electronics and Communication | UG | 4 years |
| ME | Mechanical Engineering | UG | 4 years |
| IT | Information Technology | UG | 4 years |
| MCA | Master of Computer Applications | PG | 2 years |

### Sample Students
| Roll Number | Name | Department | Year |
|-------------|------|------------|------|
| 2024CSE001 | Rahul Sharma | CSE | First Year |
| 2024CSE002 | Priya Patel | CSE | First Year |
| 2023CSE001 | Sneha Reddy | CSE | Second Year |
| 2024ECE001 | Kavita Joshi | ECE | First Year |
| 2024MCA001 | Rajat Saxena | MCA | First Year |

### Sample Subjects (CSE)
| Year | Subject | Code | Credits |
|------|---------|------|---------|
| First Year | Programming in C | CS101 | 4 |
| Second Year | Data Structures | CS201 | 4 |
| Second Year | DBMS | CS202 | 4 |
| Third Year | Operating Systems | CS301 | 4 |
| Third Year | Computer Networks | CS302 | 4 |
| Fourth Year | Machine Learning | CS401 | 4 |

---

## 🔄 Single Sign-On (SSO) Enabled

### How It Works
When logged in as admin via the React frontend, clicking **"Admin Panel ↗"** will:
1. Automatically pass your JWT token to Django
2. Log you into Django Admin without re-entering credentials
3. Open Django Admin in a new tab

**No need to login again!** Your JWT authentication is automatically transferred.

---

## 🛠️ Re-populate Database

To clear and re-populate the database at any time:

```bash
cd backend
python manage.py populate_data
```

This will:
- Clear all existing data
- Create fresh departments, teachers, subjects, students
- Create teacher-subject assignments
- Reset admin password to `admin123`
- Reset all teacher passwords to `teacher123`

---

## 📝 Django Admin Access

### Via React Frontend (Recommended)
1. Login to React frontend as admin (`admin / admin123`)
2. Click **"Admin Panel ↗"** in navigation (yellow link)
3. Opens Django Admin automatically authenticated ✅

### Direct Access
1. Go to `http://localhost:8000/admin/`
2. Login with `admin / admin123`

---

## 🎯 What Can Teachers Do?

Teachers can only see and manage data for subjects assigned to them:

### Dr. Sharma (dr.sharma / teacher123)
Can access:
- CSE First Year - Programming in C
- CSE Second Year - Data Structures
- CSE Third Year - Operating Systems

### Prof. Gupta (prof.gupta / teacher123)
Can access:
- CSE Second Year - DBMS
- CSE Third Year - Software Engineering
- CSE Fourth Year - Machine Learning

### Dr. Mehta (dr.mehta / teacher123)
Can access:
- Mathematics-I across CSE, ECE, ME, IT departments (Cross-departmental faculty)

---

## 🔒 Security Notes

**⚠️ These are development credentials!**

For production:
- Change all default passwords
- Use strong, unique passwords
- Enable 2FA for admin accounts
- Rotate JWT secrets regularly
- Use environment variables for sensitive data

---

## 📱 Testing the System

### Complete Test Flow:
1. **Login as Admin** (`admin / admin123`)
2. **Open Django Admin** (click "Admin Panel ↗")
3. **Create/verify teachers, departments, subjects**
4. **Assign teachers to subjects**
5. **Logout and login as teacher** (`dr.sharma / teacher123`)
6. **Register students** (only for assigned subjects)
7. **Start attendance session** (only for assigned subjects)
8. **Mark attendance** using face recognition
9. **View reports** (filtered by assignments)

---

## 🎉 Ready to Use!

Your attendance system is now fully populated with realistic data and ready for testing!
