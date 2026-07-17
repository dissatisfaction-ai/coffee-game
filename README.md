# coffee-game

A coffee tracker for the lab fridge. Create a game on the website, print the generated
PDF board, and stick it on the fridge. Every time someone drinks a cup of coffee they
cross a hex tile adjacent to their region. To get the leaderboard, photograph the board
(keep the QR code in the frame) and upload the photo — the app aligns the image using
the corner ArUco markers, detects the crosses, and counts cups per player.

The backend is stateless: the whole game configuration travels inside the QR code
printed on the board, so no database is needed.

## Running it

Requires **Python 3.10** (the pinned OpenCV build has no wheels for newer versions)
and Node.js for building the frontend.

```bash
# backend
conda create -n coffee-game python=3.10 -y        # or pyenv/uv
conda activate coffee-game
pip install -r requirements.txt

# frontend (build once, Flask serves it from static/)
cd front-coffee-game
npm ci
npm run build
cp -r build/* ../static/
cd ..

# run
flask --app app run
```

Open http://localhost:5000.

Set `COFFEE_GAME_URL` if the app is served from a different host — this URL is embedded
in the QR code of newly created boards (default `http://localhost:5000`).

## Frontend development

```bash
cd front-coffee-game
npm start
```

The CRA dev server proxies API calls to the Flask backend on `localhost:5000`
(see `"proxy"` in `package.json`), so run `flask --app app run` alongside it.

## Optional: better QR recognition with ZBar

The app decodes QR codes with OpenCV out of the box. Installing `zbarlight` adds a
second, more robust decoder that is tried first:

On Debian
```bash
apt-get install libzbar0 libzbar-dev
pip install zbarlight
```
On Mac OS X
```bash
brew install zbar
export LDFLAGS="-L$(brew --prefix zbar)/lib"
export CFLAGS="-I$(brew --prefix zbar)/include"
pip install zbarlight
```

## Monitoring (optional)

`docker-compose.yml` starts Prometheus + Grafana. App metrics export is currently
disabled in `app.py` (`PrometheusMetrics` is commented out).
