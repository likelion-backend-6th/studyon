import os
import multiprocessing

import django

ENV = os.getenv("RUN_MODE", "base")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{ENV}")

django.setup()

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1

worker_class = "uvicorn.workers.UvicornWorker"
