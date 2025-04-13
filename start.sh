#!/bin/bash
# Make sure gunicorn is in the path
export PATH=$PATH:$HOME/.local/bin
# Run the application
python -m gunicorn app_team_details:app 