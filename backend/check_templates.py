import os
import sys

# Mock missing ml modules before django setup
from unittest.mock import MagicMock
sys.modules['numpy'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.ensemble'] = MagicMock()
sys.modules['sklearn.preprocessing'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.stats'] = MagicMock()
sys.modules['pandas'] = MagicMock()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()

from django.template.loader import get_template
from django.template import TemplateSyntaxError
from pathlib import Path

templates_dir = Path('/home/josh/projects/rebaden/backend/templates/siem/')
errors = []

for html_file in templates_dir.glob('**/*.html'):
    rel_path = f"siem/{html_file.name}"
    try:
        # get_template will compile the template and check for syntax errors
        get_template(rel_path)
    except TemplateSyntaxError as e:
        errors.append((rel_path, str(e)))
    except Exception as e:
        errors.append((rel_path, type(e).__name__ + ": " + str(e)))

if errors:
    print("Found template syntax errors:")
    for path, err in errors:
        print(f"{path}: {err}")
else:
    print("No template syntax errors found.")
