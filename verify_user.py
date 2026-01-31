
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()

email = 'test-user-38531@example.com'
print(f'Checking for user: {email}')

try:
    user = User.objects.get(email=email)
    print(f'✓ User found in database')
    print(f'  ID: {user.id}')
    print(f'  Email: {user.email}')
    print(f'  Active: {user.is_active}')
    print(f'  Created: {user.date_joined}')

    # Check for profile
    try:
        profile = Profile.objects.get(user=user)
        print(f'✓ Profile created')
        print(f'  Profile ID: {profile.id}')
    except Profile.DoesNotExist:
        print(f'✗ Profile not found for user')

except User.DoesNotExist:
    print(f'✗ User not found in database')
