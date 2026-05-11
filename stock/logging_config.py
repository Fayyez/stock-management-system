from pathlib import Path


def get_logging_config(base_dir: Path):
    """Return Django LOGGING dict with rotating file and console handlers."""
    log_file = str(base_dir / 'stock.log')
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': log_file,
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'stock': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
