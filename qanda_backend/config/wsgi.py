"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

# Load .env as early as possible for WSGI servers
try:
    from pathlib import Path
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:  # pragma: no cover
        load_dotenv = None  # type: ignore
    if load_dotenv is not None:
        base_dir = Path(__file__).resolve().parent.parent
        env_path = base_dir / ".env"
        try:
            load_dotenv(dotenv_path=str(env_path))
        except Exception:
            pass
except Exception:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
