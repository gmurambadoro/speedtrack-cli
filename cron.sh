#!/usr/bin/env bash

cd /home/gavin/PycharmProjects/speedtrack-cli || exit

source ./venv/bin/activate
python3 --version
python3 main.py
deactivate
