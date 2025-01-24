#!/usr/bin/python3
# -*- coding: utf8

import os
import sys
import argparse
import logging
import configparser
import math
import subprocess
import datetime as dt


class YMapBuilder(object):
    """Yandex Maps stitcher algorithm"""

    def __init__(self):
        parser = argparse.ArgumentParser(description='Yandex Map downloader.')
        parser.add_argument('--dir', type=str, help='Map dir', required=True)
        parser.add_argument('--conf', type=str, help='Configuration file', required=True)
        parser.add_argument('--out', type=str, help='Output filename', required=True)
        self.args = parser.parse_args()

        self.ReadConfig(self.args.conf)
        self.CheckMap()
        self.CalcDimensions()
        self.PrintInfo()
        logging.debug("YMapBuilder initialization completed. Path = '{path}'.".format(path=self.DirMap))
        print("YMapBuilder initialization completed. Path = '{path}'.".format(path=self.DirMap))

    def CheckMap(self):
        if not os.path.isdir(self.DirMap):
            raise RuntimeError("Map dir '{dir}' was not found.".format(dir=self.DirMap))
        if not os.path.isdir(self.TilesDir):
            raise RuntimeError("Tiles dir '{dir}' was not found.".format(dir=self.TilesDir))
        if not os.path.isfile(self.EmptyJPG):
            raise RuntimeError("File not found: {f}".format(f=self.EmptyJPG))

    def CalcDimensions(self):
        """
        Вычиление размеров
        """
        tiles = os.listdir(self.TilesDir)
        coords = [[int(t.split('_')[0]), int(t.split('_')[1].split('.')[0])] for t in tiles]
        self.MinX = min(c[0] for c in coords)
        self.MinY = min(c[1] for c in coords)
        self.MaxX = max(c[0] for c in coords)
        self.MaxY = max(c[1] for c in coords)
        # Количество файлов
        self.TilesCount = len(tiles)
        self.TilesW = (self.MaxX - self.MinX + 1)
        self.TilesH = (self.MaxY - self.MinY + 1)
        print("TilesW = {tw}".format(tw=self.TilesW))
        print("TilesH = {th}".format(th=self.TilesH))
        # Количество требуемых элементов для склейки карты
        self.TilesNeeded = self.TilesW * self.TilesH

    def PrintInfo(self):
        """
        Вывод отладочной информации
        """
        print("min_x = {min_x}, min_y = {min_y}, max_x = {max_x}, "
              "max_y = {max_y}".format(min_x=self.MinX, min_y=self.MinY,
                                       max_x=self.MaxX, max_y=self.MaxY))
        print("Tiles count: {c}".format(c=self.TilesCount))
        print("Tiles needed: {c}".format(c=self.TilesNeeded))
        print("Tile size: {x}x{y}.".format(x=self.TileWidth, y=self.TileHeight))

    def PutVariables(self, s):
        return s.replace('{date}', dt.datetime.now().strftime('%Y%m%d'))

    def ReadConfig(self, ConfFile):
        """
        Чтение конфигурации
        """
        config = configparser.ConfigParser()
        config.read(ConfFile)
        self.DirMap = self.args.dir
        self.TileWidth = int(config.get('MAP', 'TileWidth'))
        self.TileHeight = int(config.get('MAP', 'TileHeight'))
        self.PrepareDir = os.path.join(self.DirMap, 'prepare')
        self.EmptyJPG = config.get('MAP', 'Empty')
        self.Scale = config.get('MAP', 'Scale')
        self.TilesDir = os.path.join(self.DirMap, 'tiles', self.Scale)
        self.Result = self.PutVariables(self.args.out)

    def Process(self):
        """
        Склеивание целиковой карты из подготовленных кусков 10x10
        """
        tiles = os.listdir(self.PrepareDir)
        width = max([int(i.split('_')[0]) for i in tiles]) + 1
        height = max([int(i.replace('.jpg', '').split('_')[1]) for i in tiles]) + 1
        print('Width: %s, height: %s' % (width, height))
        files = []
        for y in range(0, height):
            for x in range(0, width):
                files.append(os.path.join(self.PrepareDir, '%s_%s.jpg' % (x, y)))
        FileList = ' '.join(files)
        execute = "magick.exe montage %s -quality 100%% -mode " \
                  "Concatenate -tile %sx%s %s" % (FileList, width, height, self.Result)
        print(execute)
        subprocess.check_output(execute, shell=True)

    def TryFiles(self, fname, *args):
        # print(fname)
        for ext in args:
            filename = os.path.join(self.TilesDir, '%s.%s' % (fname, ext))
            if os.path.exists(filename):
                return filename
        return None

    def Prepare(self):
        """
        Подготовка карты заключается в генерировании склеенных кусков 10x10,
        которые размещаются затем в директории 'prepare'
        """
        if not os.path.isdir(self.PrepareDir):
            os.makedirs(self.PrepareDir)
        # Посчитаем количество тайлов, которые будут получены в результате склейки
        # исходных тайлов в куски 10x10
        Tiles10W = int(self.TilesW / 10) if self.TilesW % 10 == 0 \
            else int(math.floor(self.TilesW / 10)) + 1
        Tiles10H = int(self.TilesH / 10) if self.TilesH % 10 == 0 \
            else int(math.floor(self.TilesH / 10)) + 1
        self.Tiles10Count = Tiles10W * Tiles10H
        print("Tiles10 width: {c}".format(c=Tiles10W))
        print("Tiles10 height: {c}".format(c=Tiles10H))
        for y in range(0, Tiles10H):
            for x in range(0, Tiles10W):
                FileList = ''
                for ty in range(0, 10):
                    for tx in range(0, 10):
                        y_ = self.MinY + y * 10 + ty
                        x_ = self.MinX + x * 10 + tx
                        f = {'x': x_, 'y': y_, 's': self.Scale}
                        FileName = self.TryFiles("{x}_{y}_{s}".format(**f), 'png', 'jpg')
                        if FileName is not None:
                            FileList = FileList + ' ' + FileName
                        else:
                            FileList = FileList + ' ' + self.EmptyJPG
                # Склеиваем
                OutFileName = os.path.join(self.PrepareDir, "{x}_{y}.jpg".format(x=x, y=y))
                execute = "magick.exe montage %s -quality 100%% -mode " \
                          "Concatenate -tile 10x10 %s" % (FileList, OutFileName)
                sys.stdout.write("Concatenating %s..." % OutFileName)
                subprocess.check_output(execute, shell=True)
                sys.stdout.write(" OK\n")
                sys.stdout.flush()
        return

    def Scale(self, width, height):
        """
        Основная процедура - склеивание и масштабирование карты
        """
        # Правила склеивания:
        # После каждой итерации размер склеиваемого изображения не должен
        # превышать заданные размеры
        return
