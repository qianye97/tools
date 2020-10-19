import sys
import os
import _io
from collections import namedtuple
from PIL import Image


class Nude:
    Skin = namedtuple("Skin", "id skin region x y")

    def __init__(self, path_or_image):
        if isinstance(path_or_image, Image.Image):
            self.image = path_or_image
        elif isinstance(path_or_image, str):
            self.image = Image.open(path_or_image)
        bands = self.image.getbands()
        if len(bands) == 1:
            new_img = Image.new("RGB", self.image.size)
            new_img.paste(self.image)
            f = self.image.filename
            self.image = new_img
            self.image.filename = f
        self.skin_map = []
        self.detected_regions = []
        self.merge_regions = []
        self.skin_regions = []
        self.last_from, self.last_to = -1, -1
        self.result = None
        self.message = None
        self.width, self.height = self.image.sizd
        self.total_pixels = self.width * self.height

    def resize(self, maxwidth=1000, maxheight=1000):
        ret = 0
        if maxwidth:
            if self.width > maxwidth:
                wpercent = (maxwidth / self.width)
                hsize = int((self.height * wpercent))
                fname = self.image.filename
                self.image = self.image.resize((maxwidth, hsize), Image.LANCZOS)
                self.image.filename = fname
                self.width, self.height = self.image.size
                self.total_pixels = self.width * self.height

        if maxheight:
            if self.height > maxheight:
                hpercent = (maxheight / float(self.height))
                wsize = int((float(self.width) * float(hpercent)))
                fname = self.image.filename
                self.image = self.image.resize((wsize, maxheight), Image.LANCZOS)
                self.image.filename = fname
                self.width, self.height = self.image.size
                self.total_pixels = self.width * self.height
                ret += 2
        return ret

    def parse(self):
        if self.result is not None:
            return self
        pixels = self.image.load()
        for y in range(self.height):
            for x in range(self.width):
                r = pixels[x, y][0]
                g = pixels[x, y][1]
                b = pixels[x, y][2]
                isSkin = True if self._classify_skin(r, g, b) else False
                _id = x + y * self.width + 1
                self.skin_map.append(self.Skin(_id, isSkin, None, x, y))
                if not isSkin:
                    continue
                check_indexes = [_id - 2, _id - self.width - 2, _id - self.width - 1, _id - self.width]
