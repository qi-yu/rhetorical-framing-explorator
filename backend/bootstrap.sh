#!/bin/bash
export PYTHONPATH="./src:$PYTHONPATH"
export FLASK_APP=./src/main.py
source $(pipenv --venv)/bin/activate
python -u ./src/main.py
flask run -h 0.0.0.0