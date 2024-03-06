from geoalchemy2 import shape
from shapely.geometry import shape as shapely_shape
from shapely.geometry.collection import GeometryCollection


def process_geometry(extent):
    geometries = []
    if extent.get('type') == 'FeatureCollection':
        for feature in extent.get("features"):
            geometry = feature.get("geometry")
            if geometry.get("type") == "GeometryCollection":
                for geo in geometry.get("geometries"):
                    geometries.append(shapely_shape(geo))
            else:
                geometries.append(shapely_shape(feature.get("geometry")))
        return shape.from_shape(GeometryCollection(geometries), srid=27700)
    elif extent.get('type') == 'Feature':
        return shape.from_shape(shapely_shape(extent.get("geometry")), srid=27700)
    else:
        return shape.from_shape(shapely_shape(extent), srid=27700)
