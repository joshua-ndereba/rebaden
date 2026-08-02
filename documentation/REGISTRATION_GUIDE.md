# User Registration & Authentication Guide

## Overview
Your Django SIEM application now has a complete user registration system that allows new users to create accounts and automatically log in for the first time.

## What Was Implemented

### 1. **Registration View** (`apps/core/views.py`)
- **Location**: `/register/`
- **Features**:
  - User-friendly registration form
  - Comprehensive validation:
    - Username must be at least 3 characters
    - Email must be unique
    - Password must be at least 8 characters
    - Password confirmation matching
  - Automatic login after successful registration
  - Audit logging for new user registrations
  - Error handling with clear feedback

### 2. **Beautiful UI Templates**

#### Authentication Base Template (`templates/registration/base_auth.html`)
- Stunning gradient background
- Animated floating shapes
- Centered, responsive layout
- Professional branding with DERE logo

#### Registration Page (`templates/registration/register.html`)
- Clean, modern form design
- Two-column layout for name fields
- Real-time field validation indicators
- Password strength requirements
- Link to login page for existing users
- Security badge at bottom

#### Updated Login Page (`templates/registration/login.html`)
- Now uses the same beautiful auth base template
- Link to registration page for new users
- Consistent design with registration page

### 3. **URL Configuration**
- Registration route added: `/register/`
- Integrated with existing authentication URLs

## How to Use

### For End Users - Creating a New Account

1. **Navigate to Registration Page**:
   - Go to: `http://localhost:8000/register/`
   - Or click "Create Account" from the login page

2. **Fill Out the Form**:
   - **First Name** (optional): Your first name
   - **Last Name** (optional): Your last name
   - **Username** (required): At least 3 characters, must be unique
   - **Email** (required): Valid email address, must be unique
   - **Password** (required): At least 8 characters
   - **Confirm Password** (required): Must match password

3. **Submit**:
   - Click "Create Account" button
   - If successful, you'll be automatically logged in and redirected to the dashboard
   - If there are errors, they'll be displayed at the top of the form

### For Administrators - Creating Users Programmatically

#### Method 1: Django Shell
```bash
cd /home/josh/mine/hackathon/web-app/my-django-project/backend
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Create a regular user
user = User.objects.create_user(
    username='analyst1',
    email='analyst1@example.com',
    password='SecurePassword123!',
    first_name='John',
    last_name='Doe'
)
print(f"User created: {user.username}")
```

#### Method 2: Django Admin
1. Go to: `http://localhost:8000/admin/`
2. Navigate to "Users"
3. Click "Add User +"
4. Fill in username and password
5. Save and add additional details

#### Method 3: Management Command (for superusers)
```bash
python manage.py createsuperuser
```

## Validation Rules

### Username
- ✅ Required
- ✅ Minimum 3 characters
- ✅ Must be unique
- ✅ Case-sensitive

### Email
- ✅ Required
- ✅ Must be valid email format
- ✅ Must be unique
- ✅ Case-insensitive

### Password
- ✅ Required
- ✅ Minimum 8 characters
- ✅ Must match confirmation
- ⚠️ Consider adding complexity requirements in production

## Security Features

1. **CSRF Protection**: All forms include CSRF tokens
2. **Password Hashing**: Passwords are automatically hashed using Django's secure hashing
3. **Audit Logging**: All registrations are logged in the AuditLog table
4. **Automatic Login**: Users are logged in immediately after registration
5. **Input Validation**: Server-side validation prevents invalid data

## Testing the Registration

### Test User Created
A test user has been successfully created:
- **Username**: testuser123
- **Email**: testuser@example.com
- **Password**: SecurePass123!
- **Status**: ✅ Successfully registered and logged in

### Manual Testing Steps
1. Visit `http://localhost:8000/register/`
2. Fill out the form with test data
3. Submit and verify redirect to dashboard
4. Log out and try logging in with the new credentials

## Customization Options

### Adding More Fields
Edit `apps/core/views.py` in the `register` function to add more fields:
```python
# Example: Add phone number
phone = request.POST.get('phone', '').strip()
# Add validation
# Save to user profile or custom model
```

### Changing Password Requirements
Modify the validation in `apps/core/views.py`:
```python
if len(password) < 12:  # Change from 8 to 12
    errors.append('Password must be at least 12 characters long.')

# Add complexity check
if not any(char.isdigit() for char in password):
    errors.append('Password must contain at least one number.')
```

### Email Verification
To add email verification:
1. Install `django-allauth` or similar package
2. Configure email backend in `settings.py`
3. Add email verification view and template
4. Update registration flow to send verification email

### User Roles/Permissions
Assign users to groups during registration:
```python
from django.contrib.auth.models import Group

# In the register view after user creation
analyst_group = Group.objects.get(name='Analysts')
user.groups.add(analyst_group)
```

## Troubleshooting

### "Username already exists" Error
- The username is taken
- Try a different username
- Usernames are case-sensitive

### "Email already registered" Error
- An account with this email exists
- Use the login page instead
- Or use password reset if you forgot credentials

### Form Doesn't Submit
- Check browser console for JavaScript errors
- Ensure all required fields are filled
- Verify CSRF token is present

### Redirect Issues
- Check `LOGIN_REDIRECT_URL` in `settings.py`
- Ensure user is authenticated after registration
- Verify `@login_required` decorators on dashboard

## File Structure

```
backend/
├── apps/
│   └── core/
│       ├── views.py          # Registration view logic
│       └── urls.py           # URL routing
├── templates/
│   └── registration/
│       ├── base_auth.html    # Auth pages base template
│       ├── register.html     # Registration form
│       └── login.html        # Login form (updated)
└── project/
    └── urls.py               # Main URL configuration
```

## Next Steps

### Recommended Enhancements
1. **Email Verification**: Verify email addresses before activation
2. **Password Reset**: Add "Forgot Password" functionality
3. **Social Authentication**: Add Google/GitHub login
4. **Two-Factor Authentication**: Add 2FA for enhanced security
5. **User Profiles**: Create extended user profiles with avatars
6. **Rate Limiting**: Prevent brute force registration attempts
7. **CAPTCHA**: Add reCAPTCHA to prevent bot registrations

### Production Considerations
1. Use HTTPS for all authentication pages
2. Implement strong password policies
3. Add account lockout after failed attempts
4. Enable email notifications for new registrations
5. Regular security audits
6. Implement session management
7. Add user activity monitoring

## Support

For issues or questions:
- Check Django documentation: https://docs.djangoproject.com/
- Review the code in `apps/core/views.py`
- Check the browser console for errors
- Review server logs for backend errors

---

**Status**: ✅ Fully Implemented and Tested
**Last Updated**: 2025-11-22
**Version**: 1.0
