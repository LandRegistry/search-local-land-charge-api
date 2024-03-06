# Import every blueprint file
from search_local_land_charge_api.general import general_bp
from search_local_land_charge_api.resources.free_searches import \
    free_searches_bp
from search_local_land_charge_api.resources.paid_searches import \
    paid_searches_bp
from search_local_land_charge_api.resources.search_service_users import \
    search_service_users_bp
from search_local_land_charge_api.resources.search_status_searches import \
    search_status_searches_bp
from search_local_land_charge_api.resources.service_messages import \
    service_messages_bp


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(paid_searches_bp)
    app.register_blueprint(free_searches_bp)
    app.register_blueprint(search_service_users_bp)
    app.register_blueprint(service_messages_bp)
    app.register_blueprint(general_bp)
    app.register_blueprint(search_status_searches_bp)

    # All done!
    app.logger.info("Blueprints registered")
