#!/bin/bash

set -e

python -m mypy main.py itemize/

python -m flake8 main.py itemize/
