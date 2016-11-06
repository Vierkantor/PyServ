#!/bin/bash

# Execute the run script as the correct user
if [ $USER != "py" ]; then
	sudo -u py $0
fi
source venv/bin/activate
python3 run.py
