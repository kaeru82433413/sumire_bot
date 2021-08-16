import os
from os import path
from typing import NamedTuple, Union
import math
import operator
import itertools
import functools
import re
from PIL import Image, ImageDraw, ImageFont


POS_PATTERN = re.compile(r"([a-z])(\d{1,2})")

class Vector(NamedTuple): # 二次元の座標やベクトルを表すクラス
    x: Union[int, float]
    y: Union[int, float]


    def _operator(self, value, func):
        cls = type(self)
        if isinstance(value, (int, float, complex)):
            return cls(*map(func, self, [value]*len(self)))
        elif hasattr(value, "__iter__"):
            return cls(*map(func, self, value))
        else:
            raise NotImplementedError

    def __add__(self, value):
        return self._operator(value, operator.add)
    def __sub__(self, value):
        return self._operator(value, operator.sub)
    def __mul__(self, value):
        return self._operator(value, operator.mul)
    def __truediv__(self, value):
        return self._operator(value, operator.truediv)
    def __floordiv__(self, value):
        return self._operator(value, operator.floordiv)
    def __mod__(self, value):
        return self._operator(value, operator.mod)
    
    def _roperator(self, value, func):
        cls = type(self)
        if isinstance(value, (int, float, complex)):
            return cls(*map(func, [value]*len(self), self))
        elif hasattr(value, "__iter__"):
            return cls(*map(func, value, self))
        else:
            raise NotImplementedError

    def __radd__(self, value):
        return self._roperator(value, operator.add)
    def __rsub__(self, value):
        return self._roperator(value, operator.sub)
    def __rmul__(self, value):
        return self._roperator(value, operator.mul)
    def __rtruediv__(self, value):
        return self._roperator(value, operator.truediv)
    def __rfloordiv__(self, value):
        return self._roperator(value, operator.floordiv)
    def __rmod__(self, value):
        return self._roperator(value, operator.mod)

    def __pos__(self):
        return self*+1
    def __neg__(self):
        return self*-1
    def __abs__(self): # 原点からの距離
        return sum(x**2 for x in self)**0.5

    @classmethod
    def from_radian(cls, radian=math.pi/2):
        return cls(math.cos(radian), math.sin(radian))
    
    @classmethod
    def from_str(cls, string):
        match = POS_PATTERN.fullmatch(string)
        
        if match is None:
            return None
        else:
            x, y = match.groups()
            return cls(ord(x)-ord("a"), int(y)-1)
    
    def to_str(self):
        return f'{chr(ord("a")+self.x)}{self.y+1}'
    
    def radian(self):
        return math.atan2(*self[::-1])
    
    def in_range(self, value):
        return 0 <= value.x < self.x and 0 <= value.y < self.y
    
    def __repr__(self):
        return f"{type(self).__name__}{tuple(self)}"
    
    def __str__(self):
        return str(tuple(self))


DIRECTION4 = [Vector(*map(round, Vector.from_radian(math.pi*2/4*i))) for i in range(4)]
DIRECTION8 = [Vector(*map(round, Vector.from_radian(math.pi*2/8*i))) for i in range(8)]

if os.name == "posix": # Herokuだとファイル名だけで開けない
    FONT_PATH = r"/app/.fonts/NotoSansMonoCJKjp-Regular.otf"
else:
    FONT_PATH = r"NotoSansMonoCJKjp-Regular.otf"

@functools.cache
def truetype(font=FONT_PATH, size=32):
    return ImageFont.truetype(font=font, size=size)

FONT = truetype()

class CustomDraw(ImageDraw.ImageDraw):
    def rectangle(self, xy, *args, **kwargs):
        if len(xy) == 2:
            xy = itertools.chain(xy)
        x1, y1, x2, y2 = xy
        super().rectangle((x1, y1, x2-1, y2-1), *args, **kwargs)

    def text(self, text, pos, font=FONT, color=(0, 0, 0)):
        if isinstance(font, int):
            font = truetype(size=font)
        size = Vector(*self.textsize(text, font))
        super().text(pos-size/2, text, color, font)


MODE_LIST = [None, "L", "LA", "RGB", "RGBA"]
def new_image(size, color=(255, 255, 255), mode=None):
    if mode is None: mode = MODE_LIST[len(color)]
    image = Image.new(mode, size, color)
    draw = CustomDraw(image)
    return image, draw

DIRECOTRY = path.dirname(path.abspath(__file__))
def open_image(file):
    if path.isfile(file):
        image = Image.open(file)
    else:
        image = Image.open(path.join(DIRECOTRY, file))

    draw = CustomDraw(image)
    return image, draw


def field_image(field, func=None, background=(255, 255, 255)):
    if not field or not field[0]:
        raise ValueError("argument is empty")
    field = [list(map(func, row)) for row in field]

    width = field[0][0].width
    height = field[0][0].height
    result = new_image((width*len(field[0]), height*len(field)), background)[0]

    for i, row in enumerate(field):
        for j, value in enumerate(row):
            result.paste(value, (width*j, height*i))
    return result

