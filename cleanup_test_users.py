"""
Cleanup script to remove test users created during E2E testing
"""

import django
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()

# Find test users (pattern: test-user-*@example.com)
test_users = User.objects.filter(email__startswith='test-user-', email__endswith='@example.com')

print('=' * 80)
print('TEST USER CLEANUP SCRIPT')
print('=' * 80)
print()
print(f'Found {test_users.count()} test user(s) to remove:')
print()

if test_users.count() == 0:
    print('No test users found. Database is clean.')
else:
    for user in test_users:
        print(f'  - {user.email} (ID: {user.id}, Created: {user.date_joined})')

    print()
    response = input('Delete these users? (yes/no): ').strip().lower()

    if response == 'yes':
        count = test_users.count()
        # Profiles will be deleted via CASCADE
        test_users.delete()
        print(f'\n✓ Successfully deleted {count} test user(s) and their profiles.')
    else:
        print('\nCancelled. No users were deleted.')

print()
print('=' * 80)
