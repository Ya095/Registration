#!/bin/bash

poetry run alembic upgrade head
poetry run python registration_app/run_main.py