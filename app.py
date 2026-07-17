import os
from time import perf_counter
from uuid import uuid4

import PIL
from flask import Flask, request
from flask.json import jsonify
from flask_cors import CORS, cross_origin

from coffeegame import CoffeeGame
from exceptions import PlayerArrangementException

import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('Agg')



class catchtime:
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.time = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.time = perf_counter() - self.time
        self.readout = f"{self.time:.2f}s - {self.name}"
        print(self.readout)


app = Flask(__name__, static_folder='static', static_url_path='/')

cors = CORS(app)
# metrics = PrometheusMetrics(app)
url = os.environ.get('COFFEE_GAME_URL', 'http://localhost:5000')
app.config['CORS_HEADERS'] = 'Content-Type'

for directory in ('static/pdf', 'static/tmp/states', 'static/images'):
    os.makedirs(directory, exist_ok=True)


@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route("/create_game", methods=['POST'])
@cross_origin()
def create_game():
    request_json = request.get_json()
    players = request_json.get("players")
    random_state = request_json.get('random_state')
    orientation = request_json.get('orientation', 'pointy')
    grid_size = request_json.get('grid_size', 5)

    if not players or not all(isinstance(p, str) and p.strip() for p in players):
        return jsonify({
            "error": "true",
            "message": "Please provide a non-empty name for every player"
        }), 400

    players = [p.strip() for p in players]

    # names travel inside the QR string, so its delimiters are forbidden
    forbidden = set('?&=,')
    if any(forbidden & set(p) for p in players):
        return jsonify({
            "error": "true",
            "message": "Player names must not contain '?', '&', '=' or ','"
        }), 400

    if len(set(players)) != len(players):
        return jsonify({
            "error": "true",
            "message": "Player names must be unique"
        }), 400

    uuid = uuid4().hex
    try:
        cg = CoffeeGame(
            players=players,
            random_state=random_state,
            orientation=orientation,
            grid_size=grid_size,
            uuid=uuid,
            url=url
        )
    except PlayerArrangementException as e:
        return jsonify({
            "error": "true",
            "message": str(e)
        }), 422

    cg.generate_game_field(f"static/pdf/{uuid}.pdf")

    return jsonify({
        "uuid": uuid,
        "url": f"/static/pdf/{uuid}.pdf"
    })


@app.route("/upload_image", methods=['POST'])
@cross_origin()
def upload_image():
    file = None
    for f in request.files:
        file = request.files[f]

    if file is None:
        return jsonify({
            "error": "true",
            "message": "file not attached"
        }), 400

    try:
        cg = CoffeeGame()
        with catchtime('Image processing'):
            detection_stages = cg.proceed_image(file.stream)
    except Exception as e:
        print(str(e))
        return jsonify({
            "error": "true",
            "message": str(e)
        }), 422

    stats = cg.get_number_of_cups()
    overlay_path = f"static/tmp/states/{uuid4().hex}_overlay.jpg"
    image_path = f"static/images/{uuid4().hex}.jpg"

    with catchtime('Ploting overlay'):
        fig_overlay = detection_stages.plot_image_overlay()
    with catchtime('Saving overlay'):
        fig_overlay.savefig(overlay_path, bbox_inches='tight', pad_inches=0.0, dpi=100)

        fig_overlay.clf()
        plt.close()
        del fig_overlay
        import gc
        gc.collect()

    with catchtime('Saving initial image'):
        PIL.Image.open(file.stream).save(image_path)

    return jsonify({
        "statistics": stats,
        "overlay_image": f"{overlay_path[6:]}"
    })
