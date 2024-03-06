"""Convert jsonb to geom and index

Revision ID: 4e708c5b002a
Revises: 71f1c8ead2c8
Create Date: 2019-10-09 14:51:06.609997

"""

# revision identifiers, used by Alembic.
revision = '4e708c5b002a'
down_revision = '71f1c8ead2c8'

import json

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import shape, types
from shapely.geometry import shape as shapely_shape
from shapely.geometry.collection import GeometryCollection
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('free_search', sa.Column(
        'search_geom', types.Geometry(srid=27700), autoincrement=False, nullable=True))
    op.create_index('idx_search_geom_free_search', 'free_search', ['search_geom'], postgresql_using='gist')
    query = "SELECT _id, search_extent FROM free_search WHERE search_extent IS NOT NULL;"
    conn = op.get_bind()
    result = conn.execute(query).fetchall()
    for search in result:
        search_id = search[0]
        search_extent = search[1]
        geometries = []
        for feature in search_extent.get("features"):
            if feature.get("geometry").get("type") == "GeometryCollection":
                for geo in feature.get("geometry").get("geometries"):
                    geometries.append(shapely_shape(geo))
            else:
                geometries.append(shapely_shape(feature.get("geometry")))
        update_query = "UPDATE free_search SET search_geom = ST_GeomFromWKB(decode('{}', 'hex'), 27700) WHERE _id = {}".format(
                shape.from_shape(GeometryCollection(geometries), srid=27700), search_id)
        op.execute(update_query)
    op.alter_column('free_search', 'search_geom', nullable=False)
    op.drop_column('free_search', 'search_extent')


def downgrade():
    op.drop_index('idx_search_geom_free_search')
    op.add_column('free_search', sa.Column('search_extent', postgresql.JSONB(), nullable=True))
    query = "SELECT _id, ST_AsGeoJson(search_geom) FROM free_search WHERE search_geom IS NOT NULL;"
    conn = op.get_bind()
    result = conn.execute(query).fetchall()
    for search in result:
        search_id = search[0]
        search_json = json.loads(search[1])
        features = []
        if search_json.get('type') == 'GeometryCollection':
            for geo in search_json.get('geometries'):
                features.append({"type": "Feature", "properties": {}, "geometry": geo})
        else:
            features.append({"type": "Feature", "properties": {}, "geometry": search_json})
        feature_collection = {"type": "FeatureCollection", "features": features}
        update_query = "UPDATE free_search SET search_extent = '{}' WHERE _id = {}".format(
            json.dumps(feature_collection), search_id)
        op.execute(update_query)
    op.drop_column('free_search', 'search_geom')
    op.alter_column('free_search', 'search_extent', nullable=False)