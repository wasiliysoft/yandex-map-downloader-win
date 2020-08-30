#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Map build
"""

import sys
import logging

from ymaps.builder import YMapBuilder

def main():
    """
    Entry point
    """
    logging.basicConfig(filename='./makemap.log', level=logging.DEBUG)

    builder = YMapBuilder()
    builder.Prepare()
    builder.Process()


if __name__ == "__main__":
    sys.exit(main())
