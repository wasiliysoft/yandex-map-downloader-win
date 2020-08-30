#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Get current Yandex Maps verions
"""

import re
import sys
import argparse
import datetime as dt

import psycopg2
import requests

PARAMS = {
    'load': 'theme.islands.control.layout.ScaleLine,data.Manager,event.Manager,option.Manager,'
            'Map,mapType.storage,projection.wgs84Mercator,util.bounds,util.pixelBounds,'
            'GeoObjectCollection,yandex.layer.poi,LayerCollection,domEvent.Touch,getZoomRange,'
            'behavior.Ruler,templateLayoutFactory,GeoObject,coordSystem.geo,'
            'multiRouter.MultiRouteModel,multiRouter.ViaPointModel,multiRouter.MultiRoute,'
            'Placemark,multiRouter.editor.addon,Polyline,geoObject.addon.editor,'
            'shape.Rectangle,geometry.pixel.Rectangle,Monitor,overlay.html.Placemark,'
            'Layer,Rectangle,geometry.pixel.LineString,geocode,hotspot.Layer,'
            'hotspot.ObjectSource,yandex.dataProvider,option.presetStorage,'
            'theme.islets.traffic.layout.control.PanelContent,traffic.provider.storage,'
            'control.optionMapper,traffic.provider.Actual,traffic.provider.Archive,'
            'traffic.provider.Forecast,layout.Base,shape.Circle,geometry.pixel.Circle,'
            'shape.Polygon,geometry.pixel.Polygon',
    'lang': 'ru_RU',
    'coordorder': 'longlat',
    'mode': 'release'
}

PROJECT_SEARCH_EXPRESSION = '''"([^"]+)":{"version":"([^"]+)"'''
API_VERSION = '2.1.31'

class App():
    """
    Main application class
    """
    conn = None
    args = None

    @staticmethod
    def get_version(layer):
        """
        Returns version
        """
        response = requests.get('https://api-maps.yandex.ru/%s/' % API_VERSION, params=PARAMS)
        if response.status_code != 200:
            print('Invalid response code: %s' % response.status_code)
            sys.exit(1)
        project_data = response.text

        for match in re.findall(PROJECT_SEARCH_EXPRESSION, project_data):
            if match[0] == layer:
                return match[1]
        return None

    def save(self, layer, version):
        """
        Saves result into database
        """
        self.conn = psycopg2.connect(self.args.connection)
        cursor = self.conn.cursor()
        day = dt.date.today()
        cursor.execute('update yandex_map_version set version = %s where day = %s and layer = %s '
                       'returning day', [version, day, layer])
        result = cursor.fetchone()
        if result is None:
            cursor.execute('insert into yandex_map_version(day, layer, version) '
                           'values (%s, %s, %s)', [day, layer, version])
        cursor.close()
        self.conn.commit()
        self.conn.close()

    def run(self):
        """
        Entrypoint
        """
        parser = argparse.ArgumentParser(description='Generate SQL statemets to create '
                                                     'attribute tables.')
        parser.add_argument('--connection', type=str, help='Database connection', required=False)
        self.args = parser.parse_args()

        for layer in ['sat', 'map', 'skl', 'stv']:
            version = self.get_version(layer)
            if version is not None:
                if self.args.connection is not None:
                    self.save(layer, version)

                print('%s: %s' % (layer, version))
        return 0


if __name__ == "__main__":
    app = App()
    sys.exit(app.run())
