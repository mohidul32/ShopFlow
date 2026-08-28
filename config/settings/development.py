from dotenv import load_dotenv

load_dotenv()

from .base import *  # noqa: E402, F403

DEBUG = True
ALLOWED_HOSTS = ALLOWED_HOSTS or ["localhost", "127.0.0.1"]  # noqa: F405

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append("rest_framework.renderers.BrowsableAPIRenderer")  # noqa: F405
