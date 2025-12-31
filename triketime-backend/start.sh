#!/bin/sh
set -e

exec gunicorn --bind ":${PORT}" app.main:app