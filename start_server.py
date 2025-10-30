import os
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviereviews.settings")  # <-- use your real project name!
    # disable autoreload by adding "--noreload"
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000", "--noreload"])

