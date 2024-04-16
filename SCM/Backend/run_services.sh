#!/bin/bash

# Function to clean up processes on exit
cleanup() {
    echo "Cleaning up processes..."
    kill $DJANGO_PID $ETL_PID
    wait $DJANGO_PID $ETL_PID
    echo "Processes cleaned up."
}

# Trap SIGINT and SIGTERM signals and call cleanup
trap cleanup SIGINT SIGTERM EXIT

# Start Django App
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Wait for django server to startup
sleep 10

# Start ETL Pipeline
etl_pipeline --host "0.0.0.0" --port 8003 &
ETL_PID=$!

# Start and wait for the Python script to complete
python ./scripts/dublin_bikes_pipeline.py
SCRIPT_STATUS=$?

# Check the exit status of the script
if [ $SCRIPT_STATUS -ne 0 ]; then
  echo "Python script exited with error status $SCRIPT_STATUS"
  cleanup
  exit $SCRIPT_STATUS
fi

# Continue running, now only waiting on the server and ETL pipeline
wait
