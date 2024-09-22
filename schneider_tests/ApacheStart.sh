#!/bin/sh
# This script starts Apache and runs the Python script.

# Give the container time to start.
sleep 10

# Set ServerName to avoid warning message
echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Start Apache
echo "Starting Apache"
service apache2 start

# Run the Python script in a loop
while true
do
    echo "Running Python Script"
    python3 /VolumeData/myScript.py
    echo "Python Script Exited, restarting.."
    sleep 5
done
