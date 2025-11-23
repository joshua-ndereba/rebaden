# DERE SIEM - Backend

## Django SIEM Application

This is the backend for the DERE SIEM (Security Information and Event Management) platform.

## Quick Start

```bash
# Start the development server
python manage.py runserver

# Access the application
http://localhost:8000
```

## Default Credentials

Create a superuser:
```bash
python manage.py createsuperuser
```

Or register a new user at: http://localhost:8000/register/

## Documentation

All documentation has been moved to the `documentation/` folder.

**Start here**: [documentation/README.md](documentation/README.md)

## Key Features

- ✅ Log file upload & analysis
- ✅ Automatic threat detection
- ✅ Alert management
- ✅ Investigation workflows
- ✅ Report generation (JSON/CSV/HTML)
- ✅ Advanced search
- ✅ User profile management
- ✅ Data export

## Project Structure

```
backend/
├── apps/core/          # Main SIEM application
├── project/            # Django project settings
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── media/              # Uploaded files
├── documentation/      # All documentation
└── test_sample.log     # Sample log file for testing
```

## Test the Application

Upload the test log file:
1. Go to http://localhost:8000/logs/
2. Upload `test_sample.log`
3. Watch threats get detected automatically!

## Documentation Files

See the `documentation/` folder for:
- Complete implementation guide
- Quick start guide
- Feature documentation
- Sample logs
- User registration guide

## Support

For detailed documentation, see: `documentation/README.md`
