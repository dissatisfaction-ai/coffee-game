import cv2
from hexagons import HexagonsGrid
import detection
import numpy as np
from page_layout_render import render_page
import matplotlib.pyplot as plt
from typing import Union
from pathlib import Path


class CoffeeGame:
    def __init__(self, players=(), orientation='pointy', grid_size=5, url='', random_state=42):

        self.hex_grid = self.create_grid(orientation=orientation, grid_size=grid_size)
        self.random_state = random_state

        # TODO add random_state to generation
        coords = [[i.q, i.r] for i in self.generate_arrangement(len(players))]
        # TODO add assert that there is no neighbors
        self.config = {
            "orientation": "pointy",  # flat
            "grid_size": grid_size,  # size of hex in mm
            "players": [{
                "name": name,
                "coords": coord,
                "components": [coord]
            } for name, coord in zip(players, coords)]
        }
        self.url = url

    def __len__(self):
        return len(self.hex_grid)

    def generate_arrangement(self, n, threshold=4, border_dist=2):
        r = np.random.RandomState(self.random_state)
        while True:
            hexs = r.choice([h for h in self.hex_grid.hexs if h.border_dist >= border_dist], n, replace=False).tolist()
            if n <= 1:
                break

            min_dist = len(hexs[0] - hexs[1])
            for i in range(len(hexs)):
                for j in range(len(hexs)):
                    if i != j:
                        min_dist = min(len(hexs[i] - hexs[j]), min_dist)

            if min_dist > threshold:
                break

        return hexs

    def load_config(self, config):
        self.hex_grid = self.create_grid(orientation=config['orientation'], grid_size=config['grid_size'])
        self.config = config

        return self

    def export_config(self):  # not clean function
        return self.config

    def proceed_image(self, image_path: Union[str, Path]):
        image = plt.imread(image_path)

        # recreate whole grid
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(image)
        config = self.decode_string(value)
        self.load_config(config)

        # recognition
        image = detection.gamma_correction(image, gamma=0.5)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        pts_origin = np.array([[5, 60], [205, 60], [5, 292], [205, 292]]) * 10
        crop, coord = detection.apply_perspective(gray, pts_origin, [0, 1, 2, 3])

        p = np.array(self.hex_grid.get_centers()) / 10 - coord

        corrected, illumination_mask = detection.threshold_makrers_illumanation(crop)

        points = p.astype(int).tolist()
        hexes = detection.check_grid(corrected, grid=points, r=42)

        hexs = [self.hex_grid.get_hexagon_by_coord(*((p + coord) * 10)) for h, p in zip(hexes, np.array(points)) if h]
        for h in hexs:
            h.flag = 1

        for h in self.hex_grid.hexs:
            h.color = 0

        components = []

        colors = {}
        for index, player in enumerate(self.config['players']):
            q, r = player['coords']
            components.append(self.hex_grid.bfs(self.hex_grid[q, r]))
            for h in components[-1]:
                colors[h] = len(components)
                self.config['players'][index]['components'].append([h.q, h.r])

        hexes = [colors.get(self.hex_grid.get_hexagon_by_coord(*((p + coord) * 10)), 0) for h, p in zip(hexes, np.array(points))]

        arucos = detection.detect_aruco(gray)
        return detection.DetectionStages(
            image=image, arucos=arucos,
            pts_origin=pts_origin, crop=crop, corrected=corrected,
            illumination_mask=illumination_mask, hexes=hexes,
            r=50, points=points, orientation='pointy'
        )

    def generate_game_field(self, path):
        render_page(self.config, self.encode_string(self.config, self.url), output_name=path)

    def rename_players(self, players: dict):
        for player in self.config['players']:
            player['name'] = players.get(player['name'], player['name'])

    def draw_current_state(self):
        plt.figure(figsize=(10, 10))
        self.hex_grid.draw(color='black', alpha=0.1)
        for index, player in enumerate(self.config['players']):
            c = [self.hex_grid[q, r] for q, r in player['components']]
            self.hex_grid.draw_hexs(c, color=f'C{index}')
            self.hex_grid.draw_crosses(c, color='black', alpha=0.4)

            x, y = c[0].get_center()
            plt.text(x, y, player['name'], ha='center', va='center')

        plt.axis('equal')
        plt.axis('off')
        plt.gca().invert_yaxis()

    def get_number_of_cups(self):
        return [{
            "name": player["name"],
            "cups": len(player['components']) - 1
        } for player in self.config["players"]]

    @staticmethod
    def encode_string(data: dict, url) -> str:
        s = ""
        if data['orientation'] == "pointy":
            s += 'p'
        else:
            s += 'f'

        s += '='
        s += str(data['grid_size'])
        for player in data['players']:
            s += f"&{player['name']}={player['coords'][0]},{player['coords'][1]}"

        return f"{url}?{s}"

    @staticmethod
    def decode_string(s: str) -> dict:
        s = s.split("?")[-1]
        s.split("&")
        data = {
            "orientation": 'pointy' if s[0] == 'p' else 'flat',
            "grid_size": int(s.split("&")[0][2:]),
            "players": [{
                "name": i,
                "coords": [int(j.split(",")[0]), int(j.split(",")[1])],
                "components": []
            } for i, j in [p.split("=") for p in s.split("&")[1:]]]
        }
        return data

    @staticmethod
    def create_grid(orientation='pointy', grid_size=5):
        h = 297  # height in mm
        w = 210  # width in mm
        pf = 100  # pixel factor (how many pixels in one mm)
        pd = 5  # padding in mm
        header_size = 55  # height fo the header in mm
        corner_aruco_size = 8  # size of the corner aruco markers in mm

        return HexagonsGrid(
            orientation=orientation,
            size=grid_size * pf,
            start_pos=((pd + 10) * pf, (header_size + pd + 15) * pf),
            corners=(((pd + 10) * pf, (header_size + pd + 15) * pf), ((w - pd - 10) * pf, (h - pd - 15) * pf))
        )
