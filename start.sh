#!/bin/bash

while true; do
    # start the venv first
    source .venv/bin/activate
    # Start the Python script in the background and save its process ID
    python3 ./salesforce_events/app/SalesforceListener.py &
    pid=$!

    # Wait for the Python script to finish (i.e., exit) or be killed
    wait $pid
    sleep 1

    # Print a message indicating that the Python script has stopped
    echo "Python script stopped with exit code $?. Restarting..."
done


