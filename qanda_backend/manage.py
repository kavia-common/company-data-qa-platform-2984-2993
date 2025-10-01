#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Load .env as early as possible to ensure any imports that read env see correct values
try:
    from pathlib import Path
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:  # pragma: no cover
        load_dotenv = None  # type: ignore
    if load_dotenv is not None:
        base_dir = Path(__file__).resolve().parent
        # qanda_backend/ is project root for Django container; .env is expected here
        env_path = base_dir / ".env"
        try:
            load_dotenv(dotenv_path=str(env_path))
        except Exception:
            # Do not fail if .env cannot be loaded; rely on system environment
            pass
except Exception:
    # Avoid failing this script on dotenv issues
    pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
