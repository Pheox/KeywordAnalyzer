#!/bin/bash

virtualenv flask
source flask/bin/activate

pip install -r reqs.txt

./db_create.py
./run.py
