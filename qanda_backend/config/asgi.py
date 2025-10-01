"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

# Load .env as early as possible for ASGI servers
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

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
