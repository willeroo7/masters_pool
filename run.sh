#!/bin/bash
pip install gunicorn
pip install -r requirements.txt
python -m gunicorn wsgi:app 