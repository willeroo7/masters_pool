#!/bin/bash
# Install dependencies
pip install -r requirements.txt
# Install gunicorn globally
pip install gunicorn
# Make sure it's in the path
export PATH=$PATH:$HOME/.local/bin 