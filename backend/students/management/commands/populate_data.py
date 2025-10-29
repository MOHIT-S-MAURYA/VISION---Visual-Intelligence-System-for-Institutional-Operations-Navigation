"""
Management command to populate the database with realistic Indian university data.
Usage: python manage.py populate_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import Department, Teacher, Subject, Student, TeacherSubjectAssignment
from django.db import transaction


class Command(BaseCommand):
    help = 'Populates the database with realistic Indian university data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting database population...'))
        
        with transaction.atomic():
            # Clear existing data
            self.stdout.write('Clearing existing data...')
            TeacherSubjectAssignment.objects.all().delete()
            Student.objects.all().delete()
            Subject.objects.all().delete()
            Teacher.objects.all().delete()
            Department.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            
            # Create admin user
            self.stdout.write('Creating admin user...')
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@university.edu.in',
                    'first_name': 'System',
                    'last_name': 'Administrator',
                    'is_superuser': True,
                    'is_staff': True
                }
            )
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Admin created: username=admin, password=admin123'))
            else:
                admin_user.set_password('admin123')
                admin_user.is_superuser = True
                admin_user.is_staff = True
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Admin password reset: username=admin, password=admin123'))
            
            # Create Departments
            self.stdout.write('Creating departments...')
            departments_data = [
                # UG Programs (4 years)
                ('CSE', 'Computer Science and Engineering', 'UG', 4),
                ('ECE', 'Electronics and Communication Engineering', 'UG', 4),
                ('ME', 'Mechanical Engineering', 'UG', 4),
                ('CE', 'Civil Engineering', 'UG', 4),
                ('EE', 'Electrical Engineering', 'UG', 4),
                ('IT', 'Information Technology', 'UG', 4),
                # PG Programs (2 years)
                ('MCA', 'Master of Computer Applications', 'PG', 2),
                ('MTech-CSE', 'M.Tech Computer Science', 'PG', 2),
                ('MBA', 'Master of Business Administration', 'PG', 2),
            ]
            
            departments = {}
            for code, name, degree_type, duration in departments_data:
                dept = Department.objects.create(
                    code=code,
                    name=name,
                    degree_type=degree_type,
                    duration_years=duration
                )
                departments[code] = dept
                self.stdout.write(f'  ✓ {code} - {name}')
            
            # Create Teachers
            self.stdout.write('Creating teachers...')
            teachers_data = [
                # CSE Faculty
                ('dr.sharma', 'Dr. Rajesh Sharma', 'T001', 'rajesh.sharma@university.edu.in', '+91 98765 43210'),
                ('prof.gupta', 'Prof. Priya Gupta', 'T002', 'priya.gupta@university.edu.in', '+91 98765 43211'),
                ('dr.kumar', 'Dr. Amit Kumar', 'T003', 'amit.kumar@university.edu.in', '+91 98765 43212'),
                # ECE Faculty
                ('dr.patel', 'Dr. Suresh Patel', 'T004', 'suresh.patel@university.edu.in', '+91 98765 43213'),
                ('prof.reddy', 'Prof. Lakshmi Reddy', 'T005', 'lakshmi.reddy@university.edu.in', '+91 98765 43214'),
                # ME Faculty
                ('dr.singh', 'Dr. Vikram Singh', 'T006', 'vikram.singh@university.edu.in', '+91 98765 43215'),
                ('prof.verma', 'Prof. Anita Verma', 'T007', 'anita.verma@university.edu.in', '+91 98765 43216'),
                # General Faculty
                ('dr.mehta', 'Dr. Kavita Mehta', 'T008', 'kavita.mehta@university.edu.in', '+91 98765 43217'),
                ('prof.joshi', 'Prof. Rahul Joshi', 'T009', 'rahul.joshi@university.edu.in', '+91 98765 43218'),
            ]
            
            teachers = {}
            for username, full_name, emp_id, email, phone in teachers_data:
                # Create user account
                user = User.objects.create_user(
                    username=username,
                    password='teacher123',  # Default password for all teachers
                    email=email,
                    first_name=full_name.split()[1],
                    last_name=full_name.split()[-1]
                )
                
                # Create teacher profile
                teacher = Teacher.objects.create(
                    user=user,
                    full_name=full_name,
                    employee_id=emp_id,
                    email=email,
                    phone=phone
                )
                teachers[username] = teacher
                self.stdout.write(f'  ✓ {full_name} ({username})')
            
            self.stdout.write(self.style.SUCCESS('All teachers password: teacher123'))
            
            # Create Subjects
            self.stdout.write('Creating subjects...')
            subjects_data = [
                # CSE - First Year
                ('CSE', 'First Year', 'Programming in C', 'CS101', 4),
                ('CSE', 'First Year', 'Mathematics-I', 'MA101', 4),
                ('CSE', 'First Year', 'Physics', 'PH101', 3),
                ('CSE', 'First Year', 'Engineering Graphics', 'EG101', 3),
                
                # CSE - Second Year
                ('CSE', 'Second Year', 'Data Structures', 'CS201', 4),
                ('CSE', 'Second Year', 'Database Management Systems', 'CS202', 4),
                ('CSE', 'Second Year', 'Computer Organization', 'CS203', 3),
                ('CSE', 'Second Year', 'Mathematics-II', 'MA201', 4),
                
                # CSE - Third Year
                ('CSE', 'Third Year', 'Operating Systems', 'CS301', 4),
                ('CSE', 'Third Year', 'Computer Networks', 'CS302', 4),
                ('CSE', 'Third Year', 'Software Engineering', 'CS303', 3),
                ('CSE', 'Third Year', 'Web Technologies', 'CS304', 3),
                
                # CSE - Fourth Year
                ('CSE', 'Fourth Year', 'Machine Learning', 'CS401', 4),
                ('CSE', 'Fourth Year', 'Cloud Computing', 'CS402', 3),
                ('CSE', 'Fourth Year', 'Cyber Security', 'CS403', 3),
                
                # ECE - First Year
                ('ECE', 'First Year', 'Basic Electrical Engineering', 'EE101', 4),
                ('ECE', 'First Year', 'Mathematics-I', 'MA101', 4),
                ('ECE', 'First Year', 'Physics', 'PH101', 3),
                
                # ECE - Second Year
                ('ECE', 'Second Year', 'Analog Electronics', 'EC201', 4),
                ('ECE', 'Second Year', 'Digital Electronics', 'EC202', 4),
                ('ECE', 'Second Year', 'Signals and Systems', 'EC203', 4),
                
                # ME - First Year
                ('ME', 'First Year', 'Engineering Mechanics', 'ME101', 4),
                ('ME', 'First Year', 'Mathematics-I', 'MA101', 4),
                ('ME', 'First Year', 'Workshop Practice', 'ME102', 3),
                
                # ME - Second Year
                ('ME', 'Second Year', 'Thermodynamics', 'ME201', 4),
                ('ME', 'Second Year', 'Fluid Mechanics', 'ME202', 4),
                ('ME', 'Second Year', 'Manufacturing Processes', 'ME203', 3),
                
                # IT - First Year
                ('IT', 'First Year', 'Programming in Python', 'IT101', 4),
                ('IT', 'First Year', 'Mathematics-I', 'MA101', 4),
                ('IT', 'First Year', 'Digital Logic', 'IT102', 3),
                
                # IT - Second Year
                ('IT', 'Second Year', 'Data Structures', 'IT201', 4),
                ('IT', 'Second Year', 'Database Systems', 'IT202', 4),
                ('IT', 'Second Year', 'Computer Networks', 'IT203', 4),
                
                # MCA - First Year
                ('MCA', 'First Year', 'Advanced Java Programming', 'MCA101', 4),
                ('MCA', 'First Year', 'Software Engineering', 'MCA102', 4),
                ('MCA', 'First Year', 'Data Analytics', 'MCA103', 3),
                
                # MCA - Second Year
                ('MCA', 'Second Year', 'Cloud Computing', 'MCA201', 4),
                ('MCA', 'Second Year', 'Mobile Application Development', 'MCA202', 3),
                ('MCA', 'Second Year', 'Machine Learning', 'MCA203', 4),
            ]
            
            subjects = []
            for dept_code, year, name, code, credits in subjects_data:
                subject = Subject.objects.create(
                    department=departments[dept_code],
                    class_year=year,
                    subject_name=name,
                    subject_code=code,
                    credits=credits
                )
                subjects.append(subject)
                self.stdout.write(f'  ✓ {dept_code} - {year} - {name}')
            
            # Assign Teachers to Subjects
            self.stdout.write('Creating teacher-subject assignments...')
            assignments_data = [
                # Dr. Sharma - CSE subjects
                ('dr.sharma', 'CSE', 'First Year', 'Programming in C'),
                ('dr.sharma', 'CSE', 'Second Year', 'Data Structures'),
                ('dr.sharma', 'CSE', 'Third Year', 'Operating Systems'),
                
                # Prof. Gupta - CSE subjects
                ('prof.gupta', 'CSE', 'Second Year', 'Database Management Systems'),
                ('prof.gupta', 'CSE', 'Third Year', 'Software Engineering'),
                ('prof.gupta', 'CSE', 'Fourth Year', 'Machine Learning'),
                
                # Dr. Kumar - CSE/IT subjects
                ('dr.kumar', 'CSE', 'Third Year', 'Computer Networks'),
                ('dr.kumar', 'CSE', 'Third Year', 'Web Technologies'),
                ('dr.kumar', 'IT', 'Second Year', 'Computer Networks'),
                
                # Dr. Patel - ECE subjects
                ('dr.patel', 'ECE', 'First Year', 'Basic Electrical Engineering'),
                ('dr.patel', 'ECE', 'Second Year', 'Analog Electronics'),
                
                # Prof. Reddy - ECE subjects
                ('prof.reddy', 'ECE', 'Second Year', 'Digital Electronics'),
                ('prof.reddy', 'ECE', 'Second Year', 'Signals and Systems'),
                
                # Dr. Singh - ME subjects
                ('dr.singh', 'ME', 'First Year', 'Engineering Mechanics'),
                ('dr.singh', 'ME', 'Second Year', 'Thermodynamics'),
                
                # Prof. Verma - ME subjects
                ('prof.verma', 'ME', 'Second Year', 'Fluid Mechanics'),
                ('prof.verma', 'ME', 'Second Year', 'Manufacturing Processes'),
                
                # Dr. Mehta - Mathematics (cross-departmental)
                ('dr.mehta', 'CSE', 'First Year', 'Mathematics-I'),
                ('dr.mehta', 'ECE', 'First Year', 'Mathematics-I'),
                ('dr.mehta', 'ME', 'First Year', 'Mathematics-I'),
                ('dr.mehta', 'IT', 'First Year', 'Mathematics-I'),
                
                # Prof. Joshi - MCA subjects
                ('prof.joshi', 'MCA', 'First Year', 'Advanced Java Programming'),
                ('prof.joshi', 'MCA', 'First Year', 'Software Engineering'),
                ('prof.joshi', 'MCA', 'Second Year', 'Cloud Computing'),
            ]
            
            for teacher_username, dept_code, year, subject_name in assignments_data:
                teacher = teachers[teacher_username]
                subject = Subject.objects.get(
                    department=departments[dept_code],
                    class_year=year,
                    subject_name=subject_name
                )
                
                assignment = TeacherSubjectAssignment.objects.create(
                    teacher=teacher,
                    subject=subject,
                    academic_year='2024-25',
                    notes=f'Assigned for Academic Year 2024-25'
                )
                self.stdout.write(f'  ✓ {teacher.full_name} → {subject_name}')
            
            # Create Sample Students
            self.stdout.write('Creating sample students...')
            students_data = [
                # CSE Students
                ('2024CSE001', 'Rahul Sharma', 'CSE', 'First Year', 'rahul.sharma@student.edu.in', '+91 90001 11001'),
                ('2024CSE002', 'Priya Patel', 'CSE', 'First Year', 'priya.patel@student.edu.in', '+91 90001 11002'),
                ('2024CSE003', 'Amit Singh', 'CSE', 'First Year', 'amit.singh@student.edu.in', '+91 90001 11003'),
                ('2023CSE001', 'Sneha Reddy', 'CSE', 'Second Year', 'sneha.reddy@student.edu.in', '+91 90001 11004'),
                ('2023CSE002', 'Vijay Kumar', 'CSE', 'Second Year', 'vijay.kumar@student.edu.in', '+91 90001 11005'),
                ('2022CSE001', 'Anjali Gupta', 'CSE', 'Third Year', 'anjali.gupta@student.edu.in', '+91 90001 11006'),
                ('2022CSE002', 'Rohit Verma', 'CSE', 'Third Year', 'rohit.verma@student.edu.in', '+91 90001 11007'),
                
                # ECE Students
                ('2024ECE001', 'Kavita Joshi', 'ECE', 'First Year', 'kavita.joshi@student.edu.in', '+91 90001 11008'),
                ('2024ECE002', 'Arun Mehta', 'ECE', 'First Year', 'arun.mehta@student.edu.in', '+91 90001 11009'),
                ('2023ECE001', 'Deepa Nair', 'ECE', 'Second Year', 'deepa.nair@student.edu.in', '+91 90001 11010'),
                ('2023ECE002', 'Suresh Iyer', 'ECE', 'Second Year', 'suresh.iyer@student.edu.in', '+91 90001 11011'),
                
                # ME Students
                ('2024ME001', 'Vikram Choudhary', 'ME', 'First Year', 'vikram.c@student.edu.in', '+91 90001 11012'),
                ('2024ME002', 'Pooja Desai', 'ME', 'First Year', 'pooja.desai@student.edu.in', '+91 90001 11013'),
                ('2023ME001', 'Ravi Kulkarni', 'ME', 'Second Year', 'ravi.kulkarni@student.edu.in', '+91 90001 11014'),
                
                # IT Students
                ('2024IT001', 'Neha Agarwal', 'IT', 'First Year', 'neha.agarwal@student.edu.in', '+91 90001 11015'),
                ('2024IT002', 'Karan Malhotra', 'IT', 'First Year', 'karan.malhotra@student.edu.in', '+91 90001 11016'),
                ('2023IT001', 'Swati Bansal', 'IT', 'Second Year', 'swati.bansal@student.edu.in', '+91 90001 11017'),
                
                # MCA Students
                ('2024MCA001', 'Rajat Saxena', 'MCA', 'First Year', 'rajat.saxena@student.edu.in', '+91 90001 11018'),
                ('2024MCA002', 'Divya Rao', 'MCA', 'First Year', 'divya.rao@student.edu.in', '+91 90001 11019'),
                ('2023MCA001', 'Ankit Pandey', 'MCA', 'Second Year', 'ankit.pandey@student.edu.in', '+91 90001 11020'),
            ]
            
            for roll, name, dept_code, year, email, phone in students_data:
                student = Student.objects.create(
                    roll_number=roll,
                    full_name=name,
                    department=departments[dept_code],
                    class_year=year,
                    email=email,
                    phone=phone
                )
                self.stdout.write(f'  ✓ {roll} - {name}')
            
            self.stdout.write(self.style.SUCCESS('\n' + '='*70))
            self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(self.style.SUCCESS('\nLogin Credentials:'))
            self.stdout.write(self.style.SUCCESS('-' * 70))
            self.stdout.write(self.style.SUCCESS('Admin Account:'))
            self.stdout.write(self.style.SUCCESS('  Username: admin'))
            self.stdout.write(self.style.SUCCESS('  Password: admin123'))
            self.stdout.write(self.style.SUCCESS('\nTeacher Accounts (all have same password):'))
            self.stdout.write(self.style.SUCCESS('  Usernames: dr.sharma, prof.gupta, dr.kumar, dr.patel, etc.'))
            self.stdout.write(self.style.SUCCESS('  Password: teacher123'))
            self.stdout.write(self.style.SUCCESS('\nExample Teacher Logins:'))
            self.stdout.write(self.style.SUCCESS('  dr.sharma / teacher123 (CSE Faculty)'))
            self.stdout.write(self.style.SUCCESS('  prof.gupta / teacher123 (CSE Faculty)'))
            self.stdout.write(self.style.SUCCESS('  dr.patel / teacher123 (ECE Faculty)'))
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(self.style.SUCCESS(f'\nSummary:'))
            self.stdout.write(self.style.SUCCESS(f'  • {Department.objects.count()} Departments'))
            self.stdout.write(self.style.SUCCESS(f'  • {Teacher.objects.count()} Teachers'))
            self.stdout.write(self.style.SUCCESS(f'  • {Subject.objects.count()} Subjects'))
            self.stdout.write(self.style.SUCCESS(f'  • {TeacherSubjectAssignment.objects.count()} Teacher Assignments'))
            self.stdout.write(self.style.SUCCESS(f'  • {Student.objects.count()} Students'))
            self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
