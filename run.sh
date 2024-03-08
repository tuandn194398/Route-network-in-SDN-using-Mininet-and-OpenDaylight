#!/bin/bash
PWD=`pwd`
source "$PWD/server/venv/Scripts/activate" && PYTHONPATH="$PWD" python server/app.py
