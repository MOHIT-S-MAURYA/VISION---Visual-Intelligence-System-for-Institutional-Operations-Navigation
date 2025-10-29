from django.core.management.base import BaseCommand
from students.models import Department


class Command(BaseCommand):
    help = 'Seed departments with standard academic departments'

    def handle(self, *args, **options):
        departments_data = [
            # Undergraduate Programs (4 years)
            {'code': 'CSE', 'name': 'Computer Science and Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'ECE', 'name': 'Electronics and Communication Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'EEE', 'name': 'Electrical and Electronics Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'ME', 'name': 'Mechanical Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'CE', 'name': 'Civil Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'IT', 'name': 'Information Technology', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'CHE', 'name': 'Chemical Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'BME', 'name': 'Biomedical Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'AE', 'name': 'Aeronautical Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'AUTO', 'name': 'Automobile Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'MECH', 'name': 'Mechatronics Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'PE', 'name': 'Production Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'IE', 'name': 'Industrial Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'AGRI', 'name': 'Agricultural Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'ENVIR', 'name': 'Environmental Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'BT', 'name': 'Biotechnology', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'FT', 'name': 'Food Technology', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'TEXT', 'name': 'Textile Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'MIN', 'name': 'Mining Engineering', 'degree_type': 'UG', 'duration_years': 4},
            {'code': 'PETRO', 'name': 'Petroleum Engineering', 'degree_type': 'UG', 'duration_years': 4},
            
            # Postgraduate Programs (2 years)
            {'code': 'MCA', 'name': 'Master of Computer Applications', 'degree_type': 'PG', 'duration_years': 2},
            {'code': 'MBA', 'name': 'Master of Business Administration', 'degree_type': 'PG', 'duration_years': 2},
            {'code': 'MTECH', 'name': 'Master of Technology', 'degree_type': 'PG', 'duration_years': 2},
            {'code': 'MSC', 'name': 'Master of Science', 'degree_type': 'PG', 'duration_years': 2},
            {'code': 'MPHARM', 'name': 'Master of Pharmacy', 'degree_type': 'PG', 'duration_years': 2},
            {'code': 'MARCH', 'name': 'Master of Architecture', 'degree_type': 'PG', 'duration_years': 2},
        ]

        created = 0
        existing = 0
        
        for dept_data in departments_data:
            dept, created_flag = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            if created_flag:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {dept.code} - {dept.name}')
                )
            else:
                existing += 1

        self.stdout.write(
            self.style.SUCCESS(f'\nSummary: {created} created, {existing} already existed')
        )
