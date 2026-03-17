import logging
import json

# Initialize the root logger and set the default log level to INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_info(message, **kwargs):
    """Log structured informational messages (useful for CloudWatch and log parsing)."""

    log_data = {"message": message, **kwargs}

    logger.info(json.dumps(log_data))

def log_error(message, error, **kwargs):
    """Log structured error messages with additional context and error details."""

    # Include error message and type along with any extra context
    log_data = {
        "message": message,
        "error": str(error),
        "error_type": type(error).__name__,
        **kwargs
    }

    logger.error(json.dumps(log_data))