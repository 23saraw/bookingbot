#!/bin/bash

# Activate the virtual environment
source /Users/sarawan/myenv/bin/activate

LOG_FILE="/Users/sarawan/booking_bot/booking_bot_log.log"

echo "Script started at $(date)" >> $LOG_FILE


# Run the Python script with arguments
/Users/sarawan/myenv/bin/python /Users/sarawan/booking_bot/booking_bot_script.py "8:00 PM" "9" >> $LOG_FILE 2>&1

echo "Script finished at $(date)" >> $LOG_FILE


