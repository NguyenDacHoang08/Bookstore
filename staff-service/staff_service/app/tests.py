from django.test import TestCase
from .models import Staff

class StaffModelTest(TestCase):
    def test_staff_creation(self):
        staff = Staff.objects.create(
            name='Test Staff',
            email='staff@example.com',
            password='password123',
            role='staff'
        )
        self.assertEqual(staff.name, 'Test Staff')
        self.assertEqual(staff.email, 'staff@example.com')