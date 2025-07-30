import os

SENTRY_DSN = os.getenv("OGPU_SERVICE_SENTRY_DSN")

SOURCE_ADDRESS = os.getenv("SOURCE_ADDRESS", "0xundefined")

SERVICE_HOST = "0.0.0.0"
SERVICE_PORT = 5555

CALLBACK_ADDRESS = os.getenv(
    "CALLBACK_ADDRESS", "http://host.docker.internal:20000/task"
)
