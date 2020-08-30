# yandex-map-downloader

A simple tool that downloads Yandex Map tiles into a directory when coords and layer are provided.

## Configuration

Configuration file example:

```
[MAIN]
VersionVec=20.08.29-1
VersionSat=3.635.0
Language=ru_RU
coords1=55.94,37.29
coords2=55.50,37.92
DirMap=maps/moscow_{layer}_{version}_{date}
Scale=10,11,12,13,14,15,16,17,18

[MAP]
TileWidth=256
TileHeight=256
Empty=empty.jpg
Scale=14
```

Use `get-coords.html` to get `coords1` and `coords2` for your area.

## Usage

```bash
./get.py --conf conf/moscow.conf --layer vec
```

## Making a map

Once tiles are downloaded you can use `makemap.py` script to merge the tiles into one image. This requires ImageMagick installed on your machine.