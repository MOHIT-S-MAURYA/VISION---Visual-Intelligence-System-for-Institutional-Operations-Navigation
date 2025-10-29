from django.core.management.base import BaseCommand
from students.models import Subject

class Command(BaseCommand):
    help = 'Populate database with initial subjects'

    def handle(self, *args, **kwargs):
        subjects_data = [
            # CSE - First Year
            ("CSE", "First Year", "Engineering Mathematics-I"),
            ("CSE", "First Year", "Engineering Physics"),
            ("CSE", "First Year", "Engineering Chemistry"),
            ("CSE", "First Year", "Basic Electrical Engineering"),
            ("CSE", "First Year", "Engineering Graphics"),
            ("CSE", "First Year", "Programming in C"),
            ("CSE", "First Year", "Environmental Science"),
            ("CSE", "First Year", "Communication Skills"),
            
            # CSE - Second Year
            ("CSE", "Second Year", "Engineering Mathematics-II"),
            ("CSE", "Second Year", "Data Structures"),
            ("CSE", "Second Year", "Digital Logic Design"),
            ("CSE", "Second Year", "Computer Organization"),
            ("CSE", "Second Year", "Object Oriented Programming"),
            ("CSE", "Second Year", "Discrete Mathematics"),
            ("CSE", "Second Year", "Database Management Systems"),
            ("CSE", "Second Year", "Operating Systems"),
            
            # CSE - Third Year
            ("CSE", "Third Year", "Design and Analysis of Algorithms"),
            ("CSE", "Third Year", "Computer Networks"),
            ("CSE", "Third Year", "Software Engineering"),
            ("CSE", "Third Year", "Theory of Computation"),
            ("CSE", "Third Year", "Compiler Design"),
            ("CSE", "Third Year", "Web Technologies"),
            ("CSE", "Third Year", "Machine Learning"),
            ("CSE", "Third Year", "Microprocessors and Microcontrollers"),
            
            # CSE - Fourth Year
            ("CSE", "Fourth Year", "Artificial Intelligence"),
            ("CSE", "Fourth Year", "Cryptography and Network Security"),
            ("CSE", "Fourth Year", "Cloud Computing"),
            ("CSE", "Fourth Year", "Big Data Analytics"),
            ("CSE", "Fourth Year", "Mobile Application Development"),
            ("CSE", "Fourth Year", "Internet of Things"),
            ("CSE", "Fourth Year", "Blockchain Technology"),
            ("CSE", "Fourth Year", "Project Work"),
            
            # MCA - First Year
            ("MCA", "First Year", "Advanced Database Management Systems"),
            ("MCA", "First Year", "Computer Networks"),
            ("MCA", "First Year", "Software Engineering"),
            ("MCA", "First Year", "Design and Analysis of Algorithms"),
            ("MCA", "First Year", "Object Oriented Programming with Java"),
            ("MCA", "First Year", "Web Technologies"),
            ("MCA", "First Year", "Data Structures"),
            ("MCA", "First Year", "Operating Systems"),
            
            # MCA - Second Year
            ("MCA", "Second Year", "Machine Learning"),
            ("MCA", "Second Year", "Cloud Computing"),
            ("MCA", "Second Year", "Mobile Application Development"),
            ("MCA", "Second Year", "Cyber Security"),
            ("MCA", "Second Year", "Big Data Analytics"),
            ("MCA", "Second Year", "Software Testing"),
            ("MCA", "Second Year", "DevOps"),
            ("MCA", "Second Year", "Dissertation"),
        ]
        
        created_count = 0
        skipped_count = 0
        
        for dept, year, subject in subjects_data:
            _, created = Subject.objects.get_or_create(
                department=dept,
                class_year=year,
                subject_name=subject
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {dept} - {year} - {subject}'))
            else:
                skipped_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\nCompleted! Created: {created_count}, Skipped: {skipped_count}'))
