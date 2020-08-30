import math

def to_pixels(coord, zoom):
    l = 2 * math.pi * 6378137.0
    d = l / 2.0
    h = 1.0 / l
    b = math.pow(2, zoom + 8) * h
    return (d - coord) * b

def coordinates_to_tiles(lat, lon, zoom):
    tileSize = 256

    # Ellipsoid, WGS84, f = 298.257...
    a = 6378137.0
    b = 6356752.3142
    f = (a - b) / a
    e = math.sqrt(2*f - f**2) # В combine.js = .0818191908426

    rLat = math.radians(lat)
    rLong = math.radians(lon)

    tx = (lon + 180.0) / 360.0 * (1 << zoom)
    # Google
    # y = (1.0 - math.log(math.tan(rLat) + 1.0 / math.cos(rLat)) / math.pi) / 2.0 * (1 << zoom)
    M = math.tan(math.pi / 4 + rLat / 2) / math.pow(math.tan(math.pi / 4 + math.asin(e * math.sin(rLat)) / 2), e)
    y = a * math.log(M)

    yp = to_pixels(y, zoom)
    # Pixels to tile
    ty = int(math.floor(yp / float(tileSize)))
    return (math.trunc(tx), math.trunc(ty))
