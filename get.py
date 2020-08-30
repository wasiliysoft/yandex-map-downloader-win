#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Yandex Maps downloader, copyright Andrey Zhidenkov (c) 2012-2020

Формат запроса:
http://sat01.maps.yandex.net/tiles?l=sat&v=1.33.0&x=79228&y=41070&z=17&lang=ru-RU
"""

import sys
from ymaps.downloader import YMapDownloader


def main():
    """
    Entry point
    """
    ymap = YMapDownloader()
    ymap.Start()


if __name__ == "__main__":
    sys.exit(main())
