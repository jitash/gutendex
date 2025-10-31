"""
WSGI config for gutendex project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gutendex.settings")

application = get_wsgi_application()

# 注意：定时同步任务通过 start.sh 中的独立进程启动
# 这样可以避免在多个 Gunicorn worker 中重复启动调度器
