from cv2 import aruco
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from scipy import ndimage
from typing import Union
from dataclasses import dataclass


def detect_aruco(image: np.ndarray):
    """
    Parameters
    ----------
    image : np.ndarray
        Grayscale image

    Returns
    -------
    Dictionary {aruco_id: corner_coodrinates}
    """
    aruco_dict = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)
    parameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(image, aruco_dict, parameters=parameters)
    aruco_found = {int(id): corner[0] for id, corner in zip(ids, corners)}
    return aruco_found


def show_aruco(image: np.ndarray, aruco_found: dict, ax=None):
    if ax is None:
        plt.figure(figsize=(10, 10))
        ax = plt.gca()

    ax.imshow(image)
    for id, corner in aruco_found.items():
        ax.plot([corner[0, 0]], [corner[0, 1]], "o", label=f"{id}")
    ax.legend()


def apply_perspective(image: np.ndarray, points_origin: Union[list, np.ndarray], ids: list):
    aruco_found = detect_aruco(image)

    points_image = np.stack([aruco_found[ids[0]][0],
                             aruco_found[ids[1]][1],
                             aruco_found[ids[2]][3],
                             aruco_found[ids[3]][2]]).astype(np.float32)

    points_origin = np.array(points_origin).astype(np.float32)
    min_coord = points_origin.min(axis=0).astype(int)
    points_origin -= min_coord
    image_orig_size = points_origin.max(axis=0).astype(int)

    M = cv2.getPerspectiveTransform(points_image, points_origin)
    dst = cv2.warpPerspective(image, M, image_orig_size)

    return dst, min_coord


def threshold_markers_CLAHE(image: np.ndarray):
    assert len(image.shape) == 2

    clahe = cv2.createCLAHE(clipLimit=0.5, tileGridSize=(8, 8))
    equ = clahe.apply(image)
    equ = cv2.equalizeHist(equ)
    return equ


def threshold_makrers_illumanation(image: np.ndarray):
    image = cv2.GaussianBlur(image, (11, 11), 0)
    image_mini = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    mask = ndimage.percentile_filter(image_mini, 99, size=5)
    mask = cv2.medianBlur(mask, 13)
    mask_large = cv2.resize(mask, image.shape[::-1])
    corrected = image + (250 - mask_large)
    clip_value = np.quantile(corrected, 0.0005)
    corrected[corrected < clip_value] = clip_value
    corrected = cv2.normalize(corrected, corrected, 0, 255, cv2.NORM_MINMAX)
    return corrected, mask_large


def create_circular_mask(h, w, center=None, radius=None):
    if center is None:  # use the middle of the image
        center = (int(w / 2), int(h / 2))
    if radius is None:  # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w - center[0], h - center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)

    mask = dist_from_center <= radius
    return mask


def adaptive_threshold(image: np.ndarray):
    image = cv2.medianBlur(image, 7)
    image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 131, 4)
    image = image.astype(np.uint8)
    return image


def gamma_correction(image, gamma=0.5):
    lookUpTable = np.empty((1, 256), np.uint8)
    for i in range(256):
        lookUpTable[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    image = cv2.LUT(image, lookUpTable)
    return image


def create_points_grid(x, y, n_rows, n_cols, r, h):
    """       ____
             /    \r
            /      \
            \  h|  /
             \__|_/"""

    points = []

    for col_num in range(n_cols):
        for row_num in range(n_rows):
            x_cur = x + r * 1.5 * col_num
            y_cur = y + row_num * h * 2 - (col_num % 2) * h
            x_cur, y_cur = int(x_cur), int(y_cur)
            points.append((x_cur, y_cur))

    return points


def check_grid(image, grid, r):
    mask_size = r * 2
    mask = create_circular_mask(mask_size, mask_size, radius=r)

    hexs = []
    image = image > 185  # TODO
    for x, y in grid:
        mini_image = image[y - r:y + r, x - r:x + r]

        if min(mini_image.shape) < mask_size:  # TODO logging
            hexs.append(False)
            continue
        # image[y - r: y + r, x - r: x + r] = image[y - r: y + r, x - r: x + r] * mask
        if mini_image[mask].mean() < 0.97:  # TODO
            hexs.append(True)
        else:
            hexs.append(False)
    # plt.imshow(image)
    return hexs


def plot_hexes_by_class(image, grid, hex_classes, r, orientation='flat', ax=None,
                        skip_empty=False, alpha=0.25):
    if ax is None:
        ax = plt.gca()

    if orientation == 'flat':
        orientation = np.pi / 2
    elif orientation == 'pointy':
        orientation = 0

    color_classes = ['blue', 'red', 'yellowgreen', 'purple', 'forestgreen',
                     'darkorange', 'peru', 'gold', 'aqua', 'springgreen', 'firebrick']

    for h, (x, y) in zip(hex_classes, grid):
        if skip_empty and h == 0:
            continue
        hexagon = RegularPolygon((x, y), numVertices=6,
                                 radius=r, alpha=alpha,
                                 edgecolor=color_classes[h],
                                 orientation=orientation,
                                 facecolor=color_classes[h])
        ax.add_patch(hexagon)

    if image is not None:
        image = adaptive_threshold(image)
        ax.imshow(image, cmap='Greys_r')
    else:
        ax.set_xlim(0, 2000)
        ax.set_ylim(0, 2400)
        ax.set_aspect('equal')


@dataclass(init=True)
class DetectionStages:
    image: np.ndarray
    arucos: dict
    pts_origin: np.array
    crop: np.ndarray
    corrected: np.ndarray
    illumination_mask: np.ndarray
    hexes: list
    r: float
    points: list
    orientation: str

    def plot_decoding_debug(self):
        fig, axs = plt.subplots(1, 5, figsize=(20, 4))
        axs = axs.flatten()
        show_aruco(self.image, self.arucos, ax=axs[0])
        axs[1].imshow(self.crop)
        axs[2].imshow(self.corrected)
        axs[3].imshow(self.illumination_mask)
        plot_hexes_by_class(self.corrected, self.points, self.hexes, r=self.r, ax=axs[4], orientation=self.orientation)
        plt.show()

    def plot_result(self, skip_empty=False, binary=True):
        hexes = self.hexes
        if binary:
            hexes = [bool(i) for i in hexes]
        plot_hexes_by_class(self.corrected, self.points, hexes, r=self.r,
                            orientation=self.orientation, skip_empty=skip_empty)
        plt.show()
