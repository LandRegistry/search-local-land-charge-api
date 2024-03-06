# Set the base image to the s2i image
FROM docker-registry/stp/stp-s2i-python-extended:3.9

# Development environment values
# These values are not the same as our production environment
ENV APP_NAME="search-local-land-charge-api" \
    LDAP_HOST="dev-search-llc-ldap" \
    LOG_LEVEL="DEBUG" \
    LDAP_PORT=400 \
    LDAP_USERNAME="cn=Directory\ Manager" \
    LDAP_PASSWORD="password" \
    LAST_LOGIN_MONTHS_EXPIRY=12 \
    SQL_HOST="postgres-13" \
    SQL_DATABASE="search_local_land_charges" \
    SQL_PASSWORD="search_local_land_charges_password" \
    _DEPLOY_SQL_PASSWORD="superroot" \
    APP_SQL_USERNAME="search_local_land_charges_user" \
    AUTHENTICATION_API_URL="http://dev-search-authentication-api:8080/v2.0" \
    AUTHENTICATION_API_ROOT="http://dev-search-authentication-api:8080" \
    ALEMBIC_SQL_USERNAME="root" \
    ALEMBIC_SQL_PASSWORD="superroot" \
    SQL_USE_ALEMBIC_USER="no" \
    MAX_HEALTH_CASCADE=6 \
    ACCTEST_SQL_USERNAME="search_local_land_charge_acceptance_test_user" \
    ACCTEST_SQL_PASSWORD="search_local_land_charge_acceptance_test_password" \
    FINANCE_REPORT_SQL_USERNAME="search_local_land_charge_finance_report_user" \
    FINANCE_REPORT_SQL_PASSWORD="search_local_land_charge_finance_report_password" \
    SQLALCHEMY_POOL_RECYCLE="3300" \
    ACCOUNT_API_URL="http://dev-search-account-api:8080" \
    APP_MODULE='search_local_land_charge_api.main:app' \
    FLASK_APP='search_local_land_charge_api.main' \
    GUNICORN_ARGS='--reload' \
    WEB_CONCURRENCY='2' \
    REPORT_API_BASE_URL="http://report-api:8080" \
    SEARCH_QUERY_BUCKET="llcs-search-query" \
    SEARCH_QUERY_TIMEOUT="900" \
    STORAGE_API="http://storage-api:8080/v1.0/storage" \
    DEFAULT_TIMEOUT="30" \
    PYTHONPATH=/src

# Switch from s2i's non-root user back to root for the following commmands
USER root

# Create a user that matches dev-env runner's host user
# And ensure they have access to the jar folder at runtime
ARG OUTSIDE_UID
ARG OUTSIDE_GID
RUN groupadd --force --gid $OUTSIDE_GID containergroup && \
    useradd --uid $OUTSIDE_UID --gid $OUTSIDE_GID containeruser

ADD requirements_test.txt requirements_test.txt
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && \
    pip3 install -r requirements_test.txt

# Set the user back to a non-root user like the s2i run script expects
# When creating files inside the docker container, this will also prevent the files being owned
# by the root user, which would cause issues if running on a Linux host machine
USER containeruser

CMD ["/usr/libexec/s2i/run"]
