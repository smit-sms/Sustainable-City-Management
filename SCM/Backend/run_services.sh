#!/bin/bash

# Start Django App
python manage.py runserver 0.0.0.0:8000 &

# Start ETL Pipeline
etl_pipeline &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
