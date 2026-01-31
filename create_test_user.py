"""Create test user for E2E testing"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser

# Test user credentials
test_email = "test-user-32633@example.com"
test_password = "Test@123456"

# Check if user exists
if CustomUser.objects.filter(email=test_email).exists():
    print(f"Test user {test_email} already exists")
else:
    # Create user
    user = CustomUser.objects.create_user(
        email=test_email,
        password=test_password
    )
    print(f"Test user {test_email} created successfully")
