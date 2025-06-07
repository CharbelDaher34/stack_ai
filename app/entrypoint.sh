#!/usr/bin/env bash
set -e           # exit immediately if any command fails

# 1) Initialize the database
uv run initialize_db.py

# 2) Start the main application
exec uv run main.py
