#!/bin/bash

# Execute the run script as the correct user
if [ $USER != "py" ]; then
	sudo -u py $0
	exit $?
fi
# Activate the virtual env if it exists
if [ -d venv ]; then
	source venv/bin/activate
else
	echo "Warning: you should install a virtual env in the venv directory"
	echo "Hopefully, you're running in a VM with nothing else..."
fi
python3 run.py
