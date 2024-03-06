import json
from datetime import date
from operator import or_

from flask import Blueprint, Response, current_app, request
from marshmallow import ValidationError
from search_local_land_charge_api.exceptions import ApplicationError
from search_local_land_charge_api.extensions import db
from search_local_land_charge_api.models import ServiceMessage
from search_local_land_charge_api.schema.service_message_schema import \
    ServiceMessageSchema

service_messages_bp = Blueprint('service_messages', __name__, url_prefix='/service-messages')


@service_messages_bp.route('', methods=['GET'])
def get_service_messages():
    """Get service messages

    Returns the list of service messages
    """
    active_messages = ServiceMessage.query \
        .filter(or_(ServiceMessage.message_expiry_date.is_(None),
                    ServiceMessage.message_expiry_date >= date.today())) \
        .order_by(ServiceMessage.id.desc()) \
        .all()

    expired_messages = ServiceMessage.query \
        .filter(ServiceMessage.message_expiry_date < date.today()) \
        .order_by(ServiceMessage.id.desc()) \
        .all()

    if not active_messages and not expired_messages:
        return "No service messages found", 404

    active_messages_list = ServiceMessageSchema().dump(active_messages, many=True) or []
    expired_messages_list = ServiceMessageSchema().dump(expired_messages, many=True) or []
    response_json = {
        "messages": active_messages_list,
        "expired-messages": expired_messages_list
    }

    return Response(json.dumps(response_json), 200, mimetype='application/json')


@service_messages_bp.route('', methods=['POST'])
def post_service_message():
    """Post service message

    Adds a service message to the database
    """

    service_message_json = request.get_json()

    if not service_message_json:
        raise ApplicationError("Service message must be provided in json format", "SM001", 400)

    schema = ServiceMessageSchema()

    try:
        service_message = schema.load(service_message_json)
    except ValidationError as exc:
        current_app.logger.error("Failed to save service message item: {}".format(exc.normalized_messages()))
        raise ApplicationError(exc.normalized_messages(), "SM002", 400)

    if isinstance(service_message, ServiceMessage):
        db.session.add(service_message)
        db.session.commit()
        return Response(schema.dumps(service_message), 201, mimetype='application/json')


@service_messages_bp.route('/<service_message_id>', methods=['DELETE'])
def delete_service_message(service_message_id):
    """Delete service message

    Removes a service message from the database by ID
    """

    service_message = db.session.query(ServiceMessage).get(service_message_id)

    if not service_message:
        raise ApplicationError("Service message '{}' not found".format(service_message_id), "SM404", 404)

    db.session.delete(service_message)
    db.session.commit()

    return "Service message '{}' deleted".format(service_message_id), 204
