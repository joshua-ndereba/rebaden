import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from apps.core.views import dashboard
from django.test import RequestFactory
from django.contrib.auth.models import User

user, _ = User.objects.get_or_create(username='testadmin', is_staff=True, is_superuser=True)
request = RequestFactory().get('/dashboard/')
request.user = user

try:
    response = dashboard(request)
    print("Success! Status code:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
