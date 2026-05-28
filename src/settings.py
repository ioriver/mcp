import os
import logging.config
from log_formatter import JSONFormatter


MCP_CONFIG_LOG_LEVEL = os.environ.get('MCP_CONFIG_LOG_LEVEL', 'INFO')
MCP_CONFIG_PORT = os.environ.get('MCP_CONFIG_PORT', "80")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        }
    },
    'loggers': {
        '': {
            'level': MCP_CONFIG_LOG_LEVEL,
            'handlers': ['console'],
        },
        'uvicorn': {
            'level': MCP_CONFIG_LOG_LEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
        'uvicorn.error': {
            'level': MCP_CONFIG_LOG_LEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
        'uvicorn.access': {
            'level': MCP_CONFIG_LOG_LEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
    },
    'formatters': {
        'verbose': {
            'format': '[{asctime} ({levelname}) - {name}:{lineno} - {funcName}()] {message}',
            'style': '{',  # str.format()
        },
        "json": {
            "()": JSONFormatter,
        },
    }
}

logging.config.dictConfig(LOGGING)
