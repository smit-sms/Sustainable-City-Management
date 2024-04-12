#!/bin/bash

# Function to clean up processes on exit
cleanup() {
    echo "Cleaning up processes..."
    kill $DJANGO_PID $ETL_PID
    wait $DJANGO_PID $ETL_PID
    echo "Processes cleaned up."
}

# Trap SIGINT and SIGTERM signals and call cleanup
trap cleanup SIGINT SIGTERM

# Start Django App
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Start ETL Pipeline
etl_pipeline &
ETL_PID=$!

# Start the script to schedule the process
python ./scripts/dublin_bikes_pipeline.py &

# Wait for any process to exit
wait -n

# Cleanup and exit with the status of the first process to exit
cleanup
exit $?
