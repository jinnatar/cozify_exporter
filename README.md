# cozify_exporter
Pull data from Cozify Hub managed devices and export it in a Prometheus compatible format.

Authentication and other Cozify details are handled by python-cozify bindings developed separately: [github.com/Artanicus/python-cozify](https://github.com/Artanicus/python-cozify) but this repo acts as an official example of what it can do.

## Installation

If you just want to use it:
```
pip3 install cozify_exporter
cozify_exporter # perform the first time authentication and create a default config in `~/.config/python-cozify` if you don't already have it and start the exporter.
```

If you want to experiment with the code:
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -
git clone https://github.com/Artanicus/cozify_exporter
cd cozify_exporter
poetry install
poetry run cozify_exporter
```

## Docker

The image is published on GitHub at [ghcr.io/artanicus/cozify_exporter](https://ghcr.io/artanicus/cozify_exporter) As with other methods of running, first run the image interactively to authenticate to the hub and persist `/root/.config/python-cozify/python-cozify.cfg` with for example a mounted volume.
```
docker pull ghcr.io/artanicus/cozify_export:latest
docker run -v /path/to/persistent/config:/root/.config/ -it cozify_exporter:latest
docker run -v /path/to/persistent/config:/root/.config/ -p 9841:9841 cozify_exporter:latest
curl localhost:9841/metrics
```
