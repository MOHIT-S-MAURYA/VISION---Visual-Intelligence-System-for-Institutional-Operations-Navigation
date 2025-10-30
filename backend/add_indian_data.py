"""
Script to add realistic Indian educational data to the database
Adds: Departments, Teachers, Subjects, and Teacher-Subject Assignments
Does NOT add students (as per requirement)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth.models import User
from students.models import Department, Teacher, Subject, TeacherSubjectAssignment

def add_indian_data():
    print("🇮🇳 Adding realistic Indian educational data...")
    
    # Clear existing data (except students and admin user)
    print("\n📝 Clearing existing data (keeping students and admin)...")
    TeacherSubjectAssignment.objects.all().delete()
    Subject.objects.all().delete()
    Teacher.objects.all().delete()
    User.objects.exclude(username='admin').delete()
    
    # Keep departments but update them
    Department.objects.all().delete()
    
    # 1. Create Indian Departments
    print("\n🏛️  Creating Indian Departments...")
    departments_data = [
        {
            'name': 'Computer Science and Engineering',
            'code': 'CSE',
            'degree_type': 'UG',
            'duration_years': 4
        },
        {
            'name': 'Electronics and Communication Engineering',
            'code': 'ECE',
            'degree_type': 'UG',
            'duration_years': 4
        },
        {
            'name': 'Mechanical Engineering',
            'code': 'ME',
            'degree_type': 'UG',
            'duration_years': 4
        },
        {
            'name': 'Civil Engineering',
            'code': 'CE',
            'degree_type': 'UG',
            'duration_years': 4
        },
        {
            'name': 'Electrical Engineering',
            'code': 'EE',
            'degree_type': 'UG',
            'duration_years': 4
        },
        {
            'name': 'Information Technology',
            'code': 'IT',
            'degree_type': 'UG',
            'duration_years': 4
        },
        {
            'name': 'Master of Computer Applications',
            'code': 'MCA',
            'degree_type': 'PG',
            'duration_years': 3
        },
        {
            'name': 'Master of Business Administration',
            'code': 'MBA',
            'degree_type': 'PG',
            'duration_years': 2
        }
    ]
    
    departments = {}
    for dept_data in departments_data:
        dept = Department.objects.create(**dept_data)
        departments[dept.code] = dept
        print(f"   ✓ Created: {dept.name} ({dept.code})")
    
    # 2. Create Indian Teachers
    print("\n👨‍🏫 Creating Indian Teachers...")
    teachers_data = [
        # CSE Faculty
        {'username': 'dr.sharma', 'email': 'sharma.cse@college.edu.in', 'first_name': 'Rajesh', 'last_name': 'Sharma', 'phone': '+91-9876543210', 'department': 'CSE'},
        {'username': 'dr.verma', 'email': 'verma.cse@college.edu.in', 'first_name': 'Priya', 'last_name': 'Verma', 'phone': '+91-9876543211', 'department': 'CSE'},
        {'username': 'dr.kumar', 'email': 'kumar.cse@college.edu.in', 'first_name': 'Amit', 'last_name': 'Kumar', 'phone': '+91-9876543212', 'department': 'CSE'},
        {'username': 'dr.singh', 'email': 'singh.cse@college.edu.in', 'first_name': 'Neha', 'last_name': 'Singh', 'phone': '+91-9876543213', 'department': 'CSE'},
        
        # ECE Faculty
        {'username': 'dr.patel', 'email': 'patel.ece@college.edu.in', 'first_name': 'Kiran', 'last_name': 'Patel', 'phone': '+91-9876543214', 'department': 'ECE'},
        {'username': 'dr.reddy', 'email': 'reddy.ece@college.edu.in', 'first_name': 'Suresh', 'last_name': 'Reddy', 'phone': '+91-9876543215', 'department': 'ECE'},
        {'username': 'dr.gupta', 'email': 'gupta.ece@college.edu.in', 'first_name': 'Anjali', 'last_name': 'Gupta', 'phone': '+91-9876543216', 'department': 'ECE'},
        
        # ME Faculty
        {'username': 'dr.mehta', 'email': 'mehta.me@college.edu.in', 'first_name': 'Vikram', 'last_name': 'Mehta', 'phone': '+91-9876543217', 'department': 'ME'},
        {'username': 'dr.joshi', 'email': 'joshi.me@college.edu.in', 'first_name': 'Kavita', 'last_name': 'Joshi', 'phone': '+91-9876543218', 'department': 'ME'},
        
        # CE Faculty
        {'username': 'dr.rao', 'email': 'rao.ce@college.edu.in', 'first_name': 'Ramesh', 'last_name': 'Rao', 'phone': '+91-9876543219', 'department': 'CE'},
        {'username': 'dr.desai', 'email': 'desai.ce@college.edu.in', 'first_name': 'Pooja', 'last_name': 'Desai', 'phone': '+91-9876543220', 'department': 'CE'},
        
        # EE Faculty
        {'username': 'dr.nair', 'email': 'nair.ee@college.edu.in', 'first_name': 'Arun', 'last_name': 'Nair', 'phone': '+91-9876543221', 'department': 'EE'},
        {'username': 'dr.pillai', 'email': 'pillai.ee@college.edu.in', 'first_name': 'Lakshmi', 'last_name': 'Pillai', 'phone': '+91-9876543222', 'department': 'EE'},
        
        # IT Faculty
        {'username': 'dr.iyer', 'email': 'iyer.it@college.edu.in', 'first_name': 'Ganesh', 'last_name': 'Iyer', 'phone': '+91-9876543223', 'department': 'IT'},
        {'username': 'dr.menon', 'email': 'menon.it@college.edu.in', 'first_name': 'Divya', 'last_name': 'Menon', 'phone': '+91-9876543224', 'department': 'IT'},
        
        # MCA Faculty
        {'username': 'dr.chawla', 'email': 'chawla.mca@college.edu.in', 'first_name': 'Rohit', 'last_name': 'Chawla', 'phone': '+91-9876543225', 'department': 'MCA'},
        
        # MBA Faculty
        {'username': 'dr.malhotra', 'email': 'malhotra.mba@college.edu.in', 'first_name': 'Simran', 'last_name': 'Malhotra', 'phone': '+91-9876543226', 'department': 'MBA'},
        {'username': 'dr.kapoor', 'email': 'kapoor.mba@college.edu.in', 'first_name': 'Arjun', 'last_name': 'Kapoor', 'phone': '+91-9876543227', 'department': 'MBA'},
    ]
    
    teachers = {}
    for teacher_data in teachers_data:
        dept_code = teacher_data.pop('department')
        phone = teacher_data.pop('phone')
        
        # Create user
        user = User.objects.create_user(
            username=teacher_data['username'],
            email=teacher_data['email'],
            password='teacher123',  # Default password for all teachers
            first_name=teacher_data['first_name'],
            last_name=teacher_data['last_name']
        )
        
        # Create teacher profile
        teacher = Teacher.objects.create(
            user=user,
            full_name=f"{teacher_data['first_name']} {teacher_data['last_name']}",
            employee_id=f"{dept_code}{str(Teacher.objects.count() + 1).zfill(3)}",
            email=teacher_data['email'],
            phone=phone
        )
        teachers[teacher_data['username']] = teacher
        print(f"   ✓ Created: Dr. {teacher_data['first_name']} {teacher_data['last_name']} ({dept_code})")
    
    # 3. Create Indian Subjects
    print("\n📚 Creating Indian Subjects...")
    subjects_data = [
        # CSE Year 1
        {'dept': 'CSE', 'year': 'Year 1', 'name': 'Programming in C', 'code': 'CS101', 'credits': 4},
        {'dept': 'CSE', 'year': 'Year 1', 'name': 'Mathematics I (Calculus)', 'code': 'MA101', 'credits': 4},
        {'dept': 'CSE', 'year': 'Year 1', 'name': 'Engineering Physics', 'code': 'PH101', 'credits': 3},
        {'dept': 'CSE', 'year': 'Year 1', 'name': 'Engineering Chemistry', 'code': 'CH101', 'credits': 3},
        {'dept': 'CSE', 'year': 'Year 1', 'name': 'Engineering Graphics', 'code': 'EG101', 'credits': 2},
        
        # CSE Year 2
        {'dept': 'CSE', 'year': 'Year 2', 'name': 'Data Structures', 'code': 'CS201', 'credits': 4},
        {'dept': 'CSE', 'year': 'Year 2', 'name': 'Object Oriented Programming', 'code': 'CS202', 'credits': 4},
        {'dept': 'CSE', 'year': 'Year 2', 'name': 'Digital Electronics', 'code': 'CS203', 'credits': 3},
        {'dept': 'CSE', 'year': 'Year 2', 'name': 'Discrete Mathematics', 'code': 'MA201', 'credits': 4},
        {'dept': 'CSE', 'year': 'Year 2', 'name': 'Computer Organization', 'code': 'CS204', 'credits': 3},
        
        # CSE Year 3
        {'dept': 'CSE', 'year': 'Year 3', 'name': 'Database Management Systems', 'code': 'CS301', 'credits': 4},
        {'dept': 'CSE', 'year': 'Year 3', 'name': 'Operating Systems', 'code': 'CS302', 'credits': 4},
        {'dept': 'CSE', 'year': 'Year 3', 'name': 'Computer Networks', 'code': 'CS303', 'credits': 4},
        {'dept': 'CSE', 'year': 'Year 3', 'name': 'Software Engineering', 'code': 'CS304', 'credits': 3},
        {'dept': 'CSE', 'year': 'Year 3', 'name': 'Design and Analysis of Algorithms', 'code': 'CS305', 'credits': 4},
        
        # CSE Year 4
        {'dept': 'CSE', 'year': 'Year 4', 'name': 'Machine Learning', 'code': 'CS401', 'credits': 4},
        {'dept': 'CSE', 'year': 'Year 4', 'name': 'Artificial Intelligence', 'code': 'CS402', 'credits': 4},
        {'dept': 'CSE', 'year': 'Year 4', 'name': 'Cloud Computing', 'code': 'CS403', 'credits': 3},
        {'dept': 'CSE', 'year': 'Year 4', 'name': 'Cyber Security', 'code': 'CS404', 'credits': 3},
        {'dept': 'CSE', 'year': 'Year 4', 'name': 'Project Work', 'code': 'CS499', 'credits': 6},
        
        # ECE Subjects
        {'dept': 'ECE', 'year': 'Year 1', 'name': 'Basic Electrical Engineering', 'code': 'EE101', 'credits': 4},
        {'dept': 'ECE', 'year': 'Year 2', 'name': 'Analog Electronics', 'code': 'EC201', 'credits': 4},
        {'dept': 'ECE', 'year': 'Year 2', 'name': 'Signals and Systems', 'code': 'EC202', 'credits': 4},
        {'dept': 'ECE', 'year': 'Year 3', 'name': 'Digital Signal Processing', 'code': 'EC301', 'credits': 4},
        {'dept': 'ECE', 'year': 'Year 3', 'name': 'Microprocessors and Microcontrollers', 'code': 'EC302', 'credits': 4},
        {'dept': 'ECE', 'year': 'Year 3', 'name': 'Communication Systems', 'code': 'EC303', 'credits': 4},
        {'dept': 'ECE', 'year': 'Year 4', 'name': 'Wireless Communications', 'code': 'EC401', 'credits': 4},
        {'dept': 'ECE', 'year': 'Year 4', 'name': 'VLSI Design', 'code': 'EC402', 'credits': 4},
        
        # ME Subjects
        {'dept': 'ME', 'year': 'Year 1', 'name': 'Engineering Mechanics', 'code': 'ME101', 'credits': 4},
        {'dept': 'ME', 'year': 'Year 2', 'name': 'Thermodynamics', 'code': 'ME201', 'credits': 4},
        {'dept': 'ME', 'year': 'Year 2', 'name': 'Fluid Mechanics', 'code': 'ME202', 'credits': 4},
        {'dept': 'ME', 'year': 'Year 3', 'name': 'Machine Design', 'code': 'ME301', 'credits': 4},
        {'dept': 'ME', 'year': 'Year 3', 'name': 'Manufacturing Technology', 'code': 'ME302', 'credits': 4},
        {'dept': 'ME', 'year': 'Year 4', 'name': 'Automobile Engineering', 'code': 'ME401', 'credits': 4},
        {'dept': 'ME', 'year': 'Year 4', 'name': 'Robotics', 'code': 'ME402', 'credits': 3},
        
        # CE Subjects
        {'dept': 'CE', 'year': 'Year 1', 'name': 'Engineering Surveying', 'code': 'CE101', 'credits': 3},
        {'dept': 'CE', 'year': 'Year 2', 'name': 'Strength of Materials', 'code': 'CE201', 'credits': 4},
        {'dept': 'CE', 'year': 'Year 2', 'name': 'Building Materials', 'code': 'CE202', 'credits': 3},
        {'dept': 'CE', 'year': 'Year 3', 'name': 'Structural Analysis', 'code': 'CE301', 'credits': 4},
        {'dept': 'CE', 'year': 'Year 3', 'name': 'Geotechnical Engineering', 'code': 'CE302', 'credits': 4},
        {'dept': 'CE', 'year': 'Year 4', 'name': 'Construction Management', 'code': 'CE401', 'credits': 3},
        
        # EE Subjects
        {'dept': 'EE', 'year': 'Year 2', 'name': 'Electrical Machines I', 'code': 'EE201', 'credits': 4},
        {'dept': 'EE', 'year': 'Year 2', 'name': 'Circuit Theory', 'code': 'EE202', 'credits': 4},
        {'dept': 'EE', 'year': 'Year 3', 'name': 'Power Systems', 'code': 'EE301', 'credits': 4},
        {'dept': 'EE', 'year': 'Year 3', 'name': 'Control Systems', 'code': 'EE302', 'credits': 4},
        {'dept': 'EE', 'year': 'Year 4', 'name': 'Renewable Energy Systems', 'code': 'EE401', 'credits': 3},
        
        # IT Subjects
        {'dept': 'IT', 'year': 'Year 2', 'name': 'Web Technologies', 'code': 'IT201', 'credits': 4},
        {'dept': 'IT', 'year': 'Year 2', 'name': 'Python Programming', 'code': 'IT202', 'credits': 4},
        {'dept': 'IT', 'year': 'Year 3', 'name': 'Mobile Application Development', 'code': 'IT301', 'credits': 4},
        {'dept': 'IT', 'year': 'Year 3', 'name': 'Information Security', 'code': 'IT302', 'credits': 3},
        {'dept': 'IT', 'year': 'Year 4', 'name': 'Big Data Analytics', 'code': 'IT401', 'credits': 4},
        
        # MCA Subjects
        {'dept': 'MCA', 'year': 'Year 1', 'name': 'Advanced Java Programming', 'code': 'MCA101', 'credits': 4},
        {'dept': 'MCA', 'year': 'Year 1', 'name': 'Data Structures and Algorithms', 'code': 'MCA102', 'credits': 4},
        {'dept': 'MCA', 'year': 'Year 2', 'name': 'Web Development', 'code': 'MCA201', 'credits': 4},
        {'dept': 'MCA', 'year': 'Year 2', 'name': 'Software Project Management', 'code': 'MCA202', 'credits': 3},
        {'dept': 'MCA', 'year': 'Year 3', 'name': 'Dissertation', 'code': 'MCA399', 'credits': 8},
        
        # MBA Subjects
        {'dept': 'MBA', 'year': 'Year 1', 'name': 'Principles of Management', 'code': 'MBA101', 'credits': 3},
        {'dept': 'MBA', 'year': 'Year 1', 'name': 'Financial Accounting', 'code': 'MBA102', 'credits': 3},
        {'dept': 'MBA', 'year': 'Year 1', 'name': 'Marketing Management', 'code': 'MBA103', 'credits': 3},
        {'dept': 'MBA', 'year': 'Year 1', 'name': 'Human Resource Management', 'code': 'MBA104', 'credits': 3},
        {'dept': 'MBA', 'year': 'Year 2', 'name': 'Business Strategy', 'code': 'MBA201', 'credits': 3},
        {'dept': 'MBA', 'year': 'Year 2', 'name': 'Entrepreneurship Development', 'code': 'MBA202', 'credits': 3},
    ]
    
    subjects = {}
    for subj_data in subjects_data:
        dept_code = subj_data.pop('dept')
        year = subj_data.pop('year')
        
        subject = Subject.objects.create(
            department=departments[dept_code],
            class_year=year,
            subject_name=subj_data['name'],
            subject_code=subj_data['code'],
            credits=subj_data['credits']
        )
        subjects[subj_data['code']] = subject
        print(f"   ✓ Created: {subj_data['name']} ({subj_data['code']}) - {dept_code} {year}")
    
    # 4. Create Teacher-Subject Assignments
    print("\n👨‍🏫 Assigning Subjects to Teachers...")
    assignments_data = [
        # CSE Assignments
        {'teacher': 'dr.sharma', 'subjects': ['CS101', 'CS201', 'CS301']},
        {'teacher': 'dr.verma', 'subjects': ['CS202', 'CS302', 'CS401']},
        {'teacher': 'dr.kumar', 'subjects': ['CS203', 'CS303', 'CS402']},
        {'teacher': 'dr.singh', 'subjects': ['CS204', 'CS304', 'CS305', 'CS403']},
        
        # ECE Assignments
        {'teacher': 'dr.patel', 'subjects': ['EE101', 'EC201', 'EC301']},
        {'teacher': 'dr.reddy', 'subjects': ['EC202', 'EC302', 'EC401']},
        {'teacher': 'dr.gupta', 'subjects': ['EC303', 'EC402']},
        
        # ME Assignments
        {'teacher': 'dr.mehta', 'subjects': ['ME101', 'ME201', 'ME301']},
        {'teacher': 'dr.joshi', 'subjects': ['ME202', 'ME302', 'ME401', 'ME402']},
        
        # CE Assignments
        {'teacher': 'dr.rao', 'subjects': ['CE101', 'CE201', 'CE301']},
        {'teacher': 'dr.desai', 'subjects': ['CE202', 'CE302', 'CE401']},
        
        # EE Assignments
        {'teacher': 'dr.nair', 'subjects': ['EE201', 'EE301']},
        {'teacher': 'dr.pillai', 'subjects': ['EE202', 'EE302', 'EE401']},
        
        # IT Assignments
        {'teacher': 'dr.iyer', 'subjects': ['IT201', 'IT301', 'IT401']},
        {'teacher': 'dr.menon', 'subjects': ['IT202', 'IT302']},
        
        # MCA Assignments
        {'teacher': 'dr.chawla', 'subjects': ['MCA101', 'MCA102', 'MCA201', 'MCA202']},
        
        # MBA Assignments
        {'teacher': 'dr.malhotra', 'subjects': ['MBA101', 'MBA102', 'MBA201']},
        {'teacher': 'dr.kapoor', 'subjects': ['MBA103', 'MBA104', 'MBA202']},
    ]
    
    for assignment in assignments_data:
        teacher = teachers[assignment['teacher']]
        for subj_code in assignment['subjects']:
            subject = subjects[subj_code]
            TeacherSubjectAssignment.objects.create(
                teacher=teacher,
                subject=subject
            )
            print(f"   ✓ Assigned: {subject.subject_name} → {teacher.user.get_full_name()}")
    
    print("\n" + "="*60)
    print("✅ Indian educational data added successfully!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   • Departments: {Department.objects.count()}")
    print(f"   • Teachers: {Teacher.objects.count()}")
    print(f"   • Subjects: {Subject.objects.count()}")
    print(f"   • Assignments: {TeacherSubjectAssignment.objects.count()}")
    print(f"\n🔑 All teachers can login with:")
    print(f"   Username: (see above)")
    print(f"   Password: teacher123")
    print(f"\n👨‍💼 Admin credentials:")
    print(f"   Username: admin")
    print(f"   Password: (your existing admin password)")
    print("\n" + "="*60)

if __name__ == '__main__':
    add_indian_data()
