#!/bin/bash

# Activate the virtual environment
source /PATH TO YOUR VIRTUAL ENVIRONMENT/activate

LOG_FILE="/PATH TO YOUR LOG"

echo "Script started at $(date)" >> $LOG_FILE


# Run the Python script with arguments
/PATH TO PYTHON /PATH TO BOOKING SCRIPT "8:00 PM" "9" >> $LOG_FILE 2>&1

echo "Script finished at $(date)" >> $LOG_FILE


