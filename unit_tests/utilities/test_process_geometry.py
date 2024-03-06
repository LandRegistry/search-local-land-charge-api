import json

from flask_testing import TestCase
from geoalchemy2 import shape
from search_local_land_charge_api import main
from search_local_land_charge_api.resources.free_searches import \
    process_geometry
from shapely.geometry import mapping

POLYGON_FC = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry":
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            0.0,
                            0.0
                        ],
                        [
                            1.0,
                            0.0
                        ],
                        [
                            1.0,
                            1.0
                        ],
                        [
                            0.0,
                            1.0
                        ],
                        [
                            0.0,
                            0.0
                        ]
                    ]
                ]
            }
        }
    ]
}

POLYGON_FC_GC = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "GeometryCollection",
                "geometries": [
                    {
                        "type": "Polygon",
                        "coordinates": [
                                [
                                    [
                                        0.0,
                                        0.0
                                    ],
                                    [
                                        1.0,
                                        0.0
                                    ],
                                    [
                                        1.0,
                                        1.0
                                    ],
                                    [
                                        0.0,
                                        1.0
                                    ],
                                    [
                                        0.0,
                                        0.0
                                    ]
                                ]
                        ]
                    }
                ]
            }
        }
    ]
}


class TestProcessGeometry(TestCase):

    def create_app(self):
        main.app.testing = True
        return main.app

    def test_process_geometry_fc(self):
        result = process_geometry(POLYGON_FC)
        mapping(shape.to_shape(result))
        self.assertEqual(json.dumps(mapping(shape.to_shape(result))['geometries'][0]),
                         json.dumps(POLYGON_FC['features'][0]['geometry']))

    def test_process_geometry_feature(self):
        result = process_geometry(POLYGON_FC["features"][0])
        mapping(shape.to_shape(result))
        self.assertEqual(json.dumps(mapping(shape.to_shape(result))),
                         json.dumps(POLYGON_FC['features'][0]['geometry']))

    def test_process_geometry_gc(self):
        result = process_geometry(POLYGON_FC_GC)
        mapping(shape.to_shape(result))
        self.assertEqual(json.dumps(mapping(shape.to_shape(result))),
                         json.dumps(POLYGON_FC_GC['features'][0]['geometry']))

    def test_process_geometry_geom(self):
        result = process_geometry(POLYGON_FC["features"][0]['geometry'])
        mapping(shape.to_shape(result))
        self.assertEqual(json.dumps(mapping(shape.to_shape(result))),
                         json.dumps(POLYGON_FC['features'][0]['geometry']))
