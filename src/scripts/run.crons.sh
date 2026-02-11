#!/usr/bin/sh

cd src/internal/bg

PYTHONPATH=.. celery -A tasks worker -B -l DEBUG

