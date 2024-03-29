from collections import deque

import matplotlib.pyplot as plt
import numpy as np

from hexlib import *

size = 15
flat = Layout(layout_flat, Point(size, size), Point(0, 0))


def get_layout(orientation="flat", size=size, start_position=(0, 0)):
    if orientation == "flat":
        orientation = layout_flat

    elif orientation == "pointy":
        orientation = layout_pointy

    else:
        raise Exception("Incorrect orientation")

    return Layout(orientation, Point(size, size), Point(start_position[0], start_position[1]))


class Hexagon:
    def __init__(self, q, r, s, grid=None):
        assert not (round(q + r + s) != 0), "q + r + s must be 0"

        self.q = q
        self.r = r
        self.s = s
        self.grid = grid

    def __add__(self, other):

        q = self.q + other.q
        r = self.r + other.r
        s = self.s + other.s

        if self.grid is not None:
            grid = self.grid

        elif other.grid is not None:
            grid = other.grid

        else:
            grid = None

        if grid is not None:
            if q in grid.hexs_dict and r in grid.hexs_dict[q]:
                return grid[q, r]

        return Hexagon(q, r, s, None)

    def __len__(self):
        return (abs(self.q) + abs(self.r) + abs(self.s)) // 2

    def __sub__(self, other):
        return self + Hexagon(-other.q, -other.r, -other.s, other.grid)

    def __repr__(self):
        return f"Hexagon(q={self.q}, r={self.r}, s={self.s}, grid={self.grid})"

    @property
    def neigs(self):
        hex_directions = [
            Hexagon(1, 0, -1),
            Hexagon(1, -1, 0),
            Hexagon(0, -1, 1),
            Hexagon(-1, 0, 1),
            Hexagon(-1, 1, 0),
            Hexagon(0, 1, -1)
        ]

        return [self + i for i in hex_directions if (self + i).grid]

    @staticmethod
    def dist(a, b):
        return len(a - b)

    def get_polygon(self, loop=False):
        if self.grid is None:
            raise Exception("Can't draw polygon without grid")

        layout = self.grid.layout

        corners = []
        center = hex_to_pixel(layout, Hex(self.q, self.r, self.s))
        for i in range(0, 6):
            offset = hex_corner_offset(layout, i)
            corners.append(Point(center.x + offset.x, center.y + offset.y))

        corners = [[c.x, c.y] for c in corners]
        if loop:
            corners = corners + [corners[0]]

        return corners

    def get_center(self):
        if self.grid is None:
            raise Exception("Can't draw polygon without grid")

        layout = self.grid.layout
        center = hex_to_pixel(layout, Hex(self.q, self.r, self.s))

        return [center.x, center.y]

    def get_cross(self):
        if self.grid is None:
            raise Exception("Can't draw polygon without grid")

        x, y = self.get_center()
        r = self.grid.size
        h = r * 3**0.5 / 2
        f = h / 2
        f = f / 2**0.5

        x_shifts = np.array([0, -1, 0, 1, 0, 1, 0, -1, 0]) * f
        y_shifts = np.array([0, 1, 0, 1, 0, -1, 0, -1, 0]) * f

        return np.array([np.array([x]*9) + x_shifts, np.array([y]*9) + y_shifts]).T.tolist()


class HexagonsGrid:
    def __init__(self, orientation='flat', size=5, start_pos=(0, 0), corners=((0, 0), (210, 297))):

        self.size = size
        self.layout = get_layout(orientation=orientation, size=size, start_position=start_pos)
        self.corners = corners

        self.hexs = [Hexagon(_hex.q, _hex.r, -_hex.q - _hex.r, self) for _hex in self.gen_hexs()]
        self.hexs_dict = {}

        for _hex in self.hexs:
            self.hexs_dict[_hex.q] = {}

        for _hex in self.hexs:
            self.hexs_dict[_hex.q][_hex.r] = _hex
            _hex.flag = 0
            _hex.color = 0

        self.calculate_border_distances()

    def gen_hexs(self):
        layout = self.layout
        p1, p2 = self.corners

        eps = max(layout.size.x, layout.size.y)

        x1, y1 = p1
        x2, y2 = p2

        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        qr = [
            hex_round(pixel_to_hex(layout, Point(x1, y1))),
            hex_round(pixel_to_hex(layout, Point(x2, y1))),
            hex_round(pixel_to_hex(layout, Point(x1, y2))),
            hex_round(pixel_to_hex(layout, Point(x2, y2))),
        ]

        q_min, r_min = np.min([[p.q, p.r] for p in qr], axis=0)
        q_max, r_max = np.max([[p.q, p.r] for p in qr], axis=0)

        hexs = []
        bad_hexs = []
        for q in range(q_min - 1, q_max + 1):
            for r in range(r_min - 1, r_max + 1):
                pixel = hex_to_pixel(layout, Hex(q, r, -q - r))
                if x1 - eps < pixel.x < x2 + eps and y1 - eps < pixel.y < y2 + eps:
                    hexs.append(Hex(q, r, -q - r))
                else:
                    bad_hexs.append(Hex(q, r, -q - r))  # deprecated

        return hexs

    def get_polygons(self, loop=False):
        hexs = self.hexs

        polygons = [h.get_polygon(loop=loop) for h in hexs]

        return polygons

    def get_centers(self):
        hexs = self.hexs

        centers = [h.get_center() for h in hexs]

        return centers

    def get_crosses(self):
        hexs = self.hexs

        crosses = [h.get_cross() for h in hexs]

        return crosses

    def __len__(self):
        return len(self.hexs)

    def __getitem__(self, item):
        if len(item) == 2:
            q, r = item

        elif len(item) == 3:
            q, r, s = item

        else:
            raise IndexError("Incorrect Index")

        return self.hexs_dict[q][r]

    def get_hexagon_by_coord(self, x, y):
        h = hex_round(pixel_to_hex(self.layout, Point(x, y)))

        return self.hexs_dict[h.q][h.r]

    def draw(self, color=None, alpha=1):
        coords = np.array(self.get_polygons(loop=True))
        plt.plot(coords[:, :, 0].T, coords[:, :, 1].T, color=color, alpha=alpha)
        plt.axis("equal")

    @staticmethod
    def draw_hexs(hexs, color=None, alpha=1):
        if len(hexs) == 0:
            return
        polygons = np.array([h.get_polygon(loop=True) for h in hexs])
        plt.plot(polygons[:, :, 0].T, polygons[:, :, 1].T, color=color, alpha=alpha)

    @staticmethod
    def draw_crosses(hexs, color=None, alpha=1):
        crosses = np.array([h.get_cross() for h in hexs])
        plt.plot(crosses[:, :, 0].T, crosses[:, :, 1].T, color=color, alpha=alpha)

    def bfs(self, h, clean=False):
        hexs = []
        q = deque()
        h.color = 1
        q.append(h)

        while len(q) != 0:
            h = q.popleft()
            hexs.append(h)
            for neig in h.neigs:
                if neig.color == 0 and neig.flag == 1:
                    neig.color = 1
                    q.append(neig)

        if clean:
            for h in hexs:
                h.color = 0

        return hexs

    def clean(self):
        for _hex in self.hexs:
            _hex.flag = 0
            _hex.color = 0

    def calculate_border_distances(self):
        self.clean()
        q = deque()

        for h in self.hexs:
            if len(h.neigs) < 6:
                h.border_dist = 0
                h.color = 1
                q.append(h)

        while len(q) != 0:
            h = q.popleft()
            for neig in h.neigs:
                if neig.color == 0:
                    neig.color = 1
                    neig.border_dist = h.border_dist + 1
                    q.append(neig)

        self.clean()
