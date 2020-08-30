#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Сборка карты
"""

import sys
from ymaps.builder import YMapBuilder

import logging


def main(argv):
    """
    Entry point
    """
    logging.basicConfig(filename='./makemap.log', level=logging.DEBUG)

    builder = YMapBuilder()
    builder.Prepare()
    builder.Process()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
