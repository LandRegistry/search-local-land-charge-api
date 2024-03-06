import os
from urllib.parse import quote_plus

# RULES OF CONFIG:
# 1. No region specific code. Regions are defined by setting the OS environment variables appropriately to build up the
# desired behaviour.
# 2. No use of defaults when getting OS environment variables. They must all be set to the required values prior to the
# app starting.
# 3. This is the only file in the app where os.environ should be used.

# For logging
LOG_LEVEL = os.environ['LOG_LEVEL']

# For health route
COMMIT = os.environ['COMMIT']
DEFAULT_TIMEOUT = int(os.environ['DEFAULT_TIMEOUT'])

# This APP_NAME variable is to allow changing the app name when the app is running in a cluster. So that
# each app in the cluster will have a unique name.
APP_NAME = os.environ['APP_NAME']

# --- Database variables start
# These must all be set in the OS environment.
# The password must be the correct one for either the app user or alembic user,
# depending on which will be used (which is controlled by the SQL_USE_ALEMBIC_USER variable)
SQL_HOST = os.environ['SQL_HOST']
SQL_DATABASE = os.environ['SQL_DATABASE']
SQL_PASSWORD = os.environ['SQL_PASSWORD']
APP_SQL_USERNAME = os.environ['APP_SQL_USERNAME']
ALEMBIC_SQL_USERNAME = os.environ['ALEMBIC_SQL_USERNAME']
ACCTEST_SQL_USERNAME = os.environ['ACCTEST_SQL_USERNAME']
ACCTEST_SQL_PASSWORD = os.environ['ACCTEST_SQL_PASSWORD']
FINANCE_REPORT_SQL_USERNAME = os.environ['FINANCE_REPORT_SQL_USERNAME']
FINANCE_REPORT_SQL_PASSWORD = os.environ['FINANCE_REPORT_SQL_PASSWORD']

if os.environ['SQL_USE_ALEMBIC_USER'] == 'yes':
    FINAL_SQL_USERNAME = ALEMBIC_SQL_USERNAME
else:
    FINAL_SQL_USERNAME = APP_SQL_USERNAME
SQLALCHEMY_DATABASE_URI_ALEMBIC = 'postgresql://{0}:{1}@{2}/{3}'.format(
    FINAL_SQL_USERNAME, SQL_PASSWORD, SQL_HOST, SQL_DATABASE)

SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}/{3}'.format(
    FINAL_SQL_USERNAME, quote_plus(SQL_PASSWORD), SQL_HOST, SQL_DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Explicitly set this in order to remove warning on run
SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': int(os.environ['SQLALCHEMY_POOL_RECYCLE'])}

AUTHENTICATION_API_URL = os.environ['AUTHENTICATION_API_URL']
AUTHENTICATION_API_ROOT = os.environ['AUTHENTICATION_API_ROOT']
ACCOUNT_API_URL = os.environ['ACCOUNT_API_URL']

REPORT_API_BASE_URL = os.environ['REPORT_API_BASE_URL']

MAX_HEALTH_CASCADE = os.environ['MAX_HEALTH_CASCADE']

STORAGE_API = os.environ['STORAGE_API']
SEARCH_QUERY_TIMEOUT = int(os.environ['SEARCH_QUERY_TIMEOUT'])
SEARCH_QUERY_BUCKET = os.environ['SEARCH_QUERY_BUCKET']

DEPENDENCIES = {
    "postgres": SQLALCHEMY_DATABASE_URI,
    "authentication-api": AUTHENTICATION_API_ROOT,
    "storage-api": STORAGE_API
}

LOGCONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            '()': 'search_local_land_charge_api.extensions.JsonFormatter'
        },
        'audit': {
            '()': 'search_local_land_charge_api.extensions.JsonAuditFormatter'
        }
    },
    'filters': {
        'contextual': {
            '()': 'search_local_land_charge_api.extensions.ContextualFilter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['contextual'],
            'stream': 'ext://sys.stdout'
        },
        'audit_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'audit',
            'filters': ['contextual'],
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'search_local_land_charge_api': {
            'handlers': ['console'],
            'level': LOG_LEVEL
        },
        'audit': {
            'handlers': ['audit_console'],
            'level': 'INFO'
        }
    }
}
