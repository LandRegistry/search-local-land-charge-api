from datetime import datetime

from dateutil.relativedelta import relativedelta
from geoalchemy2 import Geometry, shape
from search_local_land_charge_api.extensions import db
from shapely.geometry import mapping
from shapely.geometry import shape as shapely_shape
from shapely.geometry.collection import GeometryCollection
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property


class PaidSearch(db.Model):
    __tablename__ = 'search_history'

    search_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.String, nullable=True)
    payment_id = db.Column(db.String, nullable=False)
    charges = db.Column(JSONB)
    search_extent = db.Column(JSONB, nullable=False)
    search_area_description = db.Column(db.String, nullable=True)
    search_date = db.Column(db.DateTime, nullable=False)
    document_url = db.Column(db.String, nullable=False)
    payment_provider = db.Column(db.String, nullable=True)
    card_brand = db.Column(db.String, nullable=True)
    amount = db.Column(db.Integer, nullable=True)
    reference = db.Column(db.String, nullable=True)
    parent_search_id = db.Column(db.BigInteger, db.ForeignKey('search_history.search_id'))

    def __init__(self, search_id, user_id, payment_id, charges, search_extent, search_date, search_area_description,
                 document_url, payment_provider, card_brand, amount, reference,
                 parent_search_id=None):
        self.search_id = search_id
        self.user_id = user_id
        self.payment_id = payment_id
        self.charges = charges
        self.search_extent = search_extent
        self.search_area_description = search_area_description
        self.search_date = search_date
        self.document_url = document_url
        self.payment_provider = payment_provider
        self.card_brand = card_brand
        self.amount = amount
        self.reference = reference
        self.parent_search_id = parent_search_id

    @hybrid_property
    def lapsed_date(self):
        # remove the timezone from the search date in case it has come from the acceptance tests, in which Ruby
        # forces a timezone into its datetime objects which makes the comparison break. Thanks Ruby.
        lapsed_date = self.search_date.replace(tzinfo=None) + relativedelta(months=+6)
        if lapsed_date > datetime.now():
            # if the lapsed date is in the future, do not return one as the logic later in the code assumes that if
            # a lapsed date is present then the search has lapsed
            lapsed_date = None

        return lapsed_date


class FreeSearch(db.Model):
    __tablename__ = 'free_search'

    _id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    charge_ids = db.Column(JSONB, nullable=False)
    search_geom = db.Column(Geometry(srid=27700))
    search_date = db.Column(db.DateTime, nullable=False)
    address = db.Column(db.String, nullable=True)

    def __init__(self, user_id, charge_ids, search_extent, search_date, address):
        self.user_id = user_id
        self.charge_ids = charge_ids
        self.search_extent = search_extent
        self.search_date = search_date
        self.address = address

    # Convert geom column to geojson
    @hybrid_property
    def search_extent(self):
        if self.search_geom is None:
            return None
        extents = mapping(shape.to_shape(self.search_geom))
        features = []
        if extents.get('type') == 'GeometryCollection':
            for geo in extents.get('geometries'):
                features.append({"type": "Feature", "properties": {}, "geometry": geo})
        else:
            features.append({"type": "Feature", "properties": {}, "geometry": extents})
        return {"type": "FeatureCollection", "features": features}

    # Convert geojson to geom column
    @search_extent.setter
    def search_extent(self, extents):
        if extents is None:
            return None
        geometries = []
        for feature in extents.get("features"):
            geometry = feature.get("geometry")
            if geometry.get("type") == "GeometryCollection":
                for geo in geometry.get("geometries"):
                    geometries.append(shapely_shape(geo))
            else:
                geometries.append(shapely_shape(geometry))
        self.search_geom = shape.from_shape(GeometryCollection(geometries), srid=27700)


class ServiceMessage(db.Model):
    __tablename__ = 'service_messages'

    id = db.Column(db.BigInteger, primary_key=True)
    message_name = db.Column(db.String, nullable=False)
    message_en = db.Column(db.String, nullable=False)
    message_cy = db.Column(db.String, nullable=False)
    hyperlink_message_en = db.Column(db.String, nullable=True)
    hyperlink_message_cy = db.Column(db.String, nullable=True)
    hyperlink_link_en = db.Column(db.String, nullable=True)
    hyperlink_link_cy = db.Column(db.String, nullable=True)
    message_expiry_date = db.Column(db.Date, nullable=True)

    def __init__(self, message_name, message_en, message_cy, hyperlink_message_en=None, hyperlink_message_cy=None,
                 hyperlink_link_en=None, hyperlink_link_cy=None, message_expiry_date=None):
        self.message_name = message_name
        self.message_en = message_en
        self.message_cy = message_cy
        self.hyperlink_message_en = hyperlink_message_en
        self.hyperlink_message_cy = hyperlink_message_cy
        self.hyperlink_link_en = hyperlink_link_en
        self.hyperlink_link_cy = hyperlink_link_cy
        self.message_expiry_date = message_expiry_date


class SearchStatusSearch(db.Model):
    __tablename__ = 'search_status_search'

    _id = db.Column(db.BigInteger, primary_key=True)
    search_date = db.Column(db.DateTime, nullable=False)
    organisation = db.Column(db.String, nullable=False)
    display_name = db.Column(db.String, nullable=False)
    charge_ids = db.Column(JSONB, nullable=False)
    search_geom = db.Column(Geometry(srid=27700))

    def __init__(self, search_date, organisation, display_name, charge_ids, search_extent):
        self.search_date = search_date
        self.organisation = organisation
        self.display_name = display_name
        self.charge_ids = charge_ids
        self.search_extent = search_extent

    # Convert geom column to geojson
    @hybrid_property
    def search_extent(self):
        if self.search_geom is None:
            return None
        extents = mapping(shape.to_shape(self.search_geom))
        features = []
        if extents.get('type') == 'GeometryCollection':
            for geo in extents.get('geometries'):
                features.append({"type": "Feature", "properties": {}, "geometry": geo})
        else:
            features.append({"type": "Feature", "properties": {}, "geometry": extents})
        return {"type": "FeatureCollection", "features": features}

    # Convert geojson to geom column
    @search_extent.setter
    def search_extent(self, extents):
        if extents is None:
            return None
        geometries = []
        if extents.get("type") == "GeometryCollection":
            for geo in extents.get("geometries"):
                geometries.append(shapely_shape(geo))
        elif extents.get("type") != "FeatureCollection":
            geometries.append(shapely_shape(extents))
        else:
            for feature in extents.get("features"):
                geometry = feature.get("geometry")
                if geometry.get("type") == "GeometryCollection":
                    for geo in geometry.get("geometries"):
                        geometries.append(shapely_shape(geo))
                else:
                    geometries.append(shapely_shape(geometry))
        self.search_geom = shape.from_shape(GeometryCollection(geometries), srid=27700)


class SearchQuery(db.Model):
    __tablename__ = 'search_query'

    id = db.Column(db.BigInteger, primary_key=True)
    request_timestamp = db.Column(db.DateTime, nullable=False)
    completion_timestamp = db.Column(db.DateTime, nullable=True)
    userid = db.Column(db.String, nullable=False)
    document = db.Column(db.String, nullable=True)
    external_url = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=False)

    def __init__(self, request_timestamp, completion_timestamp, userid, document, external_url, status):
        self.request_timestamp = request_timestamp
        self.completion_timestamp = completion_timestamp
        self.userid = userid
        self.document = document
        self.external_url = external_url
        self.status = status
