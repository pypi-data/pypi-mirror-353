"""Fix for the wrong conversion of geometry fields"""


def fix_geojson():
    """Makes a fix for wrongly converted coordinates to geojson"""
    try:
        import json
        from django.contrib.gis.geos import GEOSGeometry
        test = GEOSGeometry('SRID=4326;POINT(2 1)')
        if int(list(json.loads(test.geojson)['coordinates'])[0]) == 1:
            # The fix is required
            GEOSGeometry._json_orig = GEOSGeometry.json.fget
            def geojson_fixed(self):
                return self.from_gml(self.ogr.gml)._json_orig()
            GEOSGeometry.json = property(geojson_fixed)
            GEOSGeometry.geojson = GEOSGeometry.json
    except Exception as ex:
        pass
