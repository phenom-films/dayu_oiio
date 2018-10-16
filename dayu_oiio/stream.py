#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import re
import sys

from base import *
from config import OIIO_EXEC

printf_regex = re.compile(r'.*(\%(\d+)d).*')


class OIIO(GlobalStream):
    _name = 'oiiotools'
    _input_count = 0

    def __init__(self):
        super(OIIO, self).__init__()

    def combine(self):
        self._value = OIIO_EXEC[sys.platform] + ' -v '


class Input(InputStream):
    _name = 'input'

    def __init__(self, filename, start, end, step=1):
        super(Input, self).__init__()
        self.filename = filename
        self.start = start
        self.end = end
        self.step = step

    def combine(self):
        match = printf_regex.match(self.filename)
        if match:
            left = self.filename[:match.start(1)]
            right = self.filename[match.start(1):]

            self._value += '{left}{start}-{end}x{step}{right} '.format(start=self.start,
                                                                       end=self.end,
                                                                       step=self.step,
                                                                       left=left,
                                                                       right=right)
        else:
            self._value += self.filename


class Blank(InputStream):
    _name = 'blank'

    def __init__(self, width, height, x=0, y=0, channels=3):
        super(Blank, self).__init__()
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.channels = channels

    def combine(self):
        self._value += '--create {width}x{height}+{x}+{y} {channels} '.format(width=self.width,
                                                                              height=self.height,
                                                                              x=self.x,
                                                                              y=self.y,
                                                                              channels=self.channels)


class Output(OutputStream):
    _name = 'output'

    def __init__(self, filename, start=None, end=None):
        super(Output, self).__init__()
        self.filename = filename
        self.start = start
        self.end = end

    def combine(self):
        match = printf_regex.match(self.filename)
        if match:
            left = self.filename[:match.start(1)]
            right = self.filename[match.start(1):]

            self._value += '-o {left}{start}-{end}{right} '.format(start=self.start,
                                                                   end=self.end,
                                                                   left=left,
                                                                   right=right)
        else:
            self._value += '-o {filename} '.format(filename=self.filename)


class Resize(UnaryFilterStream):
    _name = 'resize'

    def __init__(self, width=None, height=None, scale_x=None, scale_y=None):
        super(Resize, self).__init__()
        self.width = width
        self.height = height
        self.scale_x = scale_x
        self.scale_y = scale_y
        assert self.width or self.height or self.scale_x or self.scale_y

    def combine(self):
        if self.width or self.height:
            self._value += '--{param} {width}x{height} '.format(param=self._name,
                                                                width=0 if self.width is None else self.width,
                                                                height=0 if self.height is None else self.height)
        else:
            if self.scale_x and self.scale_y:
                self._value += '--{param} {width:.0%}x{height:.0%} '.format(param=self._name,
                                                                            width=self.scale_x,
                                                                            height=self.scale_y)
            else:
                self._value += '--{param} {scale:.0%} '.format(param=self._name,
                                                               scale=self.scale_x or self.scale_y)


class Over(BinaryFilterStream):
    _name = 'over'

    def __init__(self, bg_stream):
        super(Over, self).__init__()
        self.bg_stream = bg_stream
        self.set_input(bg_stream, 1)

    def combine(self):
        self._value += '--over '


class BitDepth(CodecStream):
    _name = 'depth'

    def __init__(self, depth, channel=None):
        super(BitDepth, self).__init__()
        self.depth = depth
        self.channel = channel

    def combine(self):
        if self.channel:
            self._value += '-d {channel}={depth} '.format(channel=self.channel,
                                                          depth=self.depth)
        else:
            self._value += '-d {depth} '.format(depth=self.depth)


class Compression(CodecStream):
    _name = 'compression'

    def __init__(self, algorithm):
        super(Compression, self).__init__()
        self.algorithm = algorithm

    def combine(self):
        self._value += '--compression {algorithm} '.format(algorithm=self.algorithm)


class Quality(CodecStream):
    _name = 'quality'

    def __init__(self, quality):
        super(Quality, self).__init__()
        self.quality = quality

    def combine(self):
        self._value += '--quality {quality} '.format(quality=self.quality)


class Tile(CodecStream):
    _name = 'tile'

    def __init__(self, tile_width, tile_height):
        super(Tile, self).__init__()
        self.tile_width = tile_width
        self.tile_height = tile_height

    def combine(self):
        self._value += '--tile {tile_width} {tile_height} '.format(tile_width=self.tile_width,
                                                                   tile_height=self.tile_height)


class Scanline(CodecStream):
    _name = 'scanline'

    def combine(self):
        self._value += '--scanline '


class Crop(UnaryFilterStream):
    _name = 'crop'

    def __init__(self, width=None, height=None, x=None, y=None):
        super(Crop, self).__init__()
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        assert all(map(lambda x: x is not None, (self.width, self.height, self.x, self.y)))

    def combine(self):
        if self.width or self.height:
            self._value += '--crop {width:.0f}x{height:.0f}+{x:.0f}+{y:.0f} '.format(width=self.width,
                                                                                     height=self.height,
                                                                                     x=self.x,
                                                                                     y=self.y)


class Cut(UnaryFilterStream):
    _name = 'cut'

    def __init__(self, width=None, height=None, x=None, y=None):
        super(Cut, self).__init__()
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        assert all(map(lambda x: x is not None, (self.width, self.height, self.x, self.y)))

    def combine(self):
        if self.width or self.height:
            self._value += '--cut {width:.0f}x{height:.0f}+{x:.0f}+{y:.0f} '.format(width=self.width,
                                                                                    height=self.height,
                                                                                    x=self.x,
                                                                                    y=self.y)


class ColorConvert(UnaryFilterStream):
    _name = 'colorconvert'

    def __init__(self, from_colorspace, to_colorspace, ocio=None):
        super(ColorConvert, self).__init__()
        self.from_colorspace = from_colorspace
        self.to_colorspace = to_colorspace
        self.ocio = ocio

    def combine(self):
        if self.ocio:
            self._value += '--colorconfig \"{ocio}\" ' \
                           '--colorconvert \"{from_color}\" \"{to_color}\" '.format(ocio=self.ocio,
                                                                                    from_color=self.from_colorspace,
                                                                                    to_color=self.to_colorspace)
        else:
            self._value += '--colorconvert \"{from_color}\" \"{to_color}\" '.format(from_color=self.from_colorspace,
                                                                                    to_color=self.to_colorspace)


class Mosaic(MultipleFilterStream):
    _name = 'mosaic'

    def __init__(self, list_of_row, row, col, pad=0):
        super(Mosaic, self).__init__(list_of_row)
        self.row = row
        self.col = col
        self.pad = pad

    def combine(self):
        self._value += '--masaic:pad={pad} {col}x{row} '.format(pad=self.pad,
                                                                col=self.col,
                                                                row=self.row)


class Box(UnaryFilterStream):
    _name = 'box'

    def __init__(self, x1, y1, x2, y2, color=(0, 0, 0, 0), fill=True):
        super(Box, self).__init__()
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.color = color
        self.fill = fill

    def combine(self):
        self._value += '--box:color={color}:fill={fill} {pos} '.format(color=','.join(map(str, self.color)),
                                                                       fill=1 if self.fill else 0,
                                                                       pos=','.join(map(str, (self.x1, self.y1,
                                                                                              self.x2, self.y2))))


class Text(UnaryFilterStream):
    _name = 'text'

    def __init__(self, text, x, y, size=32, font=None, color=(1, 1, 1, 1), xalign='left', yalign='base', shadow=1):
        super(Text, self).__init__()
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.font = font
        self.color = color
        self.xalign = xalign
        self.yalign = yalign
        self.shadow = shadow

    def combine(self):
        temp = '--text:x={x}:y={y}:size={size}:color={color}:' \
               'xalign={xalign}:yalign={yalign}:shadow={shadow} '.format(x=self.x,
                                                                         y=self.y,
                                                                         size=self.size,
                                                                         color=','.join(map(str, self.color)),
                                                                         xalign=self.xalign,
                                                                         yalign=self.yalign,
                                                                         shadow=self.shadow)
        if self.font:
            temp += ':font=\"{font}\" '.format(font=self.font)

        temp += '\"{text}\" '.format(text=self.text)
        self._value += temp
