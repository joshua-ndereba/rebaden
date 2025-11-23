# Quick Reference: User Registration

## URLs
- **Registration**: http://localhost:8000/register/
- **Login**: http://localhost:8000/accounts/login/
- **Dashboard**: http://localhost:8000/dashboard/

## Registration Requirements
- Username: min 3 chars, unique
- Email: valid format, unique
- Password: min 8 chars, must match confirmation

## Test User Created ✅
- Username: `testuser123`
- Email: `testuser@example.com`
- Password: `SecurePass123!`

## Create User via Django Shell
```bash
cd /home/josh/mine/hackathon/web-app/my-django-project/backend
python manage.py shell
```

```python
from django.contrib.auth.models import User

User.objects.create_user(
    username='newuser',
    email='user@example.com',
    password='YourPassword123!',
    first_name='First',
    last_name='Last'
)
```

## Create Superuser
```bash
python manage.py createsuperuser
```

## Key Files Modified
1. `apps/core/views.py` - Added register() view
2. `apps/core/urls.py` - Added /register/ route
3. `templates/registration/register.html` - New registration form
4. `templates/registration/base_auth.html` - New auth base template
5. `templates/registration/login.html` - Updated with registration link

## Features
✅ Beautiful animated UI
✅ Form validation
✅ Automatic login after registration
✅ Audit logging
✅ Error handling
✅ Responsive design
✅ Security (CSRF, password hashing)
