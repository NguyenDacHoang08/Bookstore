from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_default_staff(apps, schema_editor):
    Staff = apps.get_model("app", "Staff")
    email = "staff@example.com"
    if not Staff.objects.filter(email=email).exists():
        Staff.objects.create(
            name="Default Staff",
            email=email,
            password=make_password("staff123"),
            role="staff",
        )


def reverse_func(apps, schema_editor):
    Staff = apps.get_model("app", "Staff")
    Staff.objects.filter(email="staff@example.com").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_staff, reverse_func),
    ]
