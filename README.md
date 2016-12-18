# PyServ

A small web server that I use to host my personal website.

## Installation

* Make a user `py`.
* Give them access to a PostgreSQL database (e.g. `py_databrowse`).
* Give them rights to access and execute, but not write(!) to this directory and its subdirectories.
* Copy pyserv/config.py.example to pyserv/config.py and tweak until it's correct.
* Install a virtual environment in the dir `venv`: `python3 -m virtualenv venv`.
* Activate the environment: `source venv/bin/activate`.
* Install all required packages: `pip3 install -r requirements.txt`

## Running
To run, you can simply execute `./run.sh`. This will make sure the right user
and virtual environments are selected.
