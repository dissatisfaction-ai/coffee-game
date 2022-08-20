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


def gen_hexs(p1, p2, layout=flat):
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
                bad_hexs.append(Hex(q, r, -q - r))

    return hexs


def gen_polygons(p1, p2, layout=flat):
    hexs = gen_hexs(p1, p2, layout=layout)

    polygons = [[[p.x, p.y] for p in polygon_corners(layout, h)] for h in hexs]
    polygons = [p + [p[0]] for p in polygons]
    polygons = np.array(polygons)

    # plt.fill(polygons[:, :, 0].T, polygons[:, :, 1].T)
    # plt.axis('equal')

    return polygons


def gen_centers(p1, p2, layout=flat):
    hexs = gen_hexs(p1, p2, layout=layout)

    centers = [hex_to_pixel(layout, h) for h in hexs]
    centers = [[p.x, p.y] for p in centers]
    centers = np.array(centers)

    # plt.scatter(centers[:, 0].T, centers[:, 1].T)
    # plt.axis('equal')

    return centers
