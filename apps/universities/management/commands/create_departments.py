from django.core.management.base import BaseCommand
from apps.universities.models import Department, University

department_code_mapping = {
    'c': {'full_name': 'Computer Science And Engineering (CSE)', 'short_name': 'CSE'},
    'p': {'full_name': 'Pharmacy', 'short_name': 'Pharmacy'},
    'ce': {'full_name': 'Civil Engineering (CE)', 'short_name': 'CE'},
    'd': {'full_name': 'Da’wah & Islamic Studies (DIS)', 'short_name': 'DIS'},
    'b': {'full_name': 'Business Administration', 'short_name': 'BBA'},
    't': {'full_name': 'Electronic And Telecommunication Engineering (ETE)', 'short_name': 'ETE'},
    'et': {'full_name': 'Electrical And Electronic Engineering (EEE)', 'short_name': 'EEE'},
    'e': {'full_name': 'English Language and Literature (ELL)', 'short_name': 'ELL'},
    'q': {'full_name': 'Qur’anic Sciences and Islamic Studies (QSIS)', 'short_name': 'QSIS'},
    's': {'full_name': 'Science of Hadith and Islamic Studies (SHIS)', 'short_name': 'SHIS'},
    'l': {'full_name': 'Department of Law', 'short_name': 'Law'},
    'ec': {'full_name': 'Economics & Banking', 'short_name': 'Eco'},
    'a': {'full_name': 'Arabic Language and Literature (ALL)', 'short_name': 'ALL'},
}


class Command(BaseCommand):
    help = 'Create department and university data from department_code_mapping'

    def handle(self, *args, **kwargs):
        # Create the university if it doesn't exist
        university, created = University.objects.get_or_create(
            name='International Islamic University Chittagong', 
            domain='ugrad.iiuc.ac.bd'
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"University {university.name} created successfully."))
        else:
            self.stdout.write(self.style.SUCCESS(f"University {university.name} already exists."))
        
        # Create departments
        for code, department in department_code_mapping.items():
            # Ensure the department is created if it doesn't exist
            department_obj, created = Department.objects.get_or_create(
                code=code, 
                university=university,
                defaults={'full_name': department['full_name'], 'short_name': department['short_name']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Department {department['full_name']} created successfully."))
            else:
                self.stdout.write(self.style.SUCCESS(f"Department {department['full_name']} already exists."))

        self.stdout.write(self.style.SUCCESS("All departments and university have been processed."))
