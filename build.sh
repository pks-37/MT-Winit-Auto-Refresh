#!/bin/bash

pip install -r requirements.txt

PLAYWRIGHT_BROWSERS_PATH=./.playwright python -m playwright install chromium