from datetime import datetime
from time import perf_counter
from uuid import uuid4

import PIL
from flask import Flask, request
from flask.json import jsonify
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from coffeegame import CoffeeGame

import matplotlib
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
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:299792458@localhost:5432/coffee_game"

cors = CORS(app)
# metrics = PrometheusMetrics(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# url = "http://localhost:5000"
url = 'coffee-game.ai'
app.config['CORS_HEADERS'] = 'Content-Type'


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary key
    players = db.Column(db.JSON, nullable=False)
    uuid = db.Column(db.String, nullable=False, unique=True)
    pdf = db.Column(db.String, nullable=False, unique=True)
    random_state = db.Column(db.Integer, nullable=False, default=42)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    orientation = db.Column(db.String, nullable=False, default='pointy')
    grid_size = db.Column(db.Float, nullable=False, default=5)

    images = db.relationship("Image", backref='game', lazy=True)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary key
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    image = db.Column(db.String)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    config = db.Column(db.JSON)


@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route("/create_game", methods=['POST'])
@cross_origin()
def create_game():
    request_json = request.get_json()
    players = request_json.get("players")
    random_state = request_json.get('random_state', 42)
    orientation = request_json.get('orientation', 'pointy')
    grid_size = request_json.get('grid_size', 5)

    uuid = uuid4().hex
    cg = CoffeeGame(
        players=players,
        random_state=random_state,
        orientation=orientation,
        grid_size=grid_size,
        uuid=uuid,
        url=url
    )
    cg.generate_game_field(f"static/pdf/{uuid}.pdf")

    game = Game(
        players=players,
        random_state=random_state,
        orientation=orientation,
        grid_size=grid_size,
        uuid=uuid,
        pdf=f"{uuid}.pdf"
    )

    db.session.add(game)
    db.session.commit()

    return jsonify({
        "id": game.id,
        "url": f"{url}/static/pdf/{game.pdf}",
        "date": game.date
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
        })

    try:
        cg = CoffeeGame()
        with catchtime('Image processing'):
            detection_stages = cg.proceed_image(file.stream)
    except Exception as e:
        print(str(e))
        return jsonify({
            "error": "true",
            "message": str(e)
        })

    uuid = cg.uuid

    # try:
    #     game = Game.query.filter_by(uuid=uuid).first()
    # except Exception as e:
    #     return jsonify({
    #         "error": "true",
    #         "message": "Game not found"
    #     })

    stats = cg.get_number_of_cups()
    state_path = f"static/tmp/states/{uuid4().hex}.jpg"
    overlay_path = f"static/tmp/states/{uuid4().hex}_overlay.jpg"
    image_path = f"static/images/{uuid4().hex}.jpg"

    with catchtime('Saving current state'):
        cg.draw_current_state(save=state_path)
    with catchtime('Ploting overlay'):
        fig_overlay = detection_stages.plot_image_overlay()
    with catchtime('Saving overlay'):
        fig_overlay.savefig(overlay_path, bbox_inches='tight', pad_inches=0.0, dpi=100)
    with catchtime('Saving initial image'):
        PIL.Image.open(file.stream).save(image_path)

    # image_entry = Image(
    #     game=game,
    #     image=image_path.split("/")[-1],
    #     config=cg.config
    # )

    # db.session.add(image_entry)
    # db.session.commit()

    return jsonify({
        "statistics": stats,
        "state_image": f"{url}/{state_path}",
        "overlay_image": f"{url}/{overlay_path}"
    })
