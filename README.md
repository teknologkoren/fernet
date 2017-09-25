# FerNET

## Installation in a virtualenv
Clone and change directory to the repo, then run
```
python3 -m venv venv                # Create virtualenv "venv"
. venv/bin/activate                 # Source the virtualenv
pip install -r requirements.txt     # Install python requirements to venv
nodeenv -p -r npm-requirements.txt  # Install node.js requirements
```
You can deactivate the virtualenv by running `deactivate`.

## Create database
Use `manage.py` to create the database. `python3 manage.py full_setup` will
create the database, some useful tags and a user with the Webmaster tag.

## Running
### Flask development server
Set environment variable `FLASK_APP` to `fernet/__init__.py`, then run
`flask run`. To enable debugging, set `FLASK_DEBUG` to `1`.

E.g.,
```
FLASK_APP=fernet/__init__.py FLASK_DEBUG=1 flask run
```

Image paths have the optional /img(400|800|1600)/ which nginx understands but
Flask's developement server does not. Images with the resize path argument will
return 404. Setting `DEBUG = True` in the config will however enable redirection
of those paths to the original image, making it possible to use Flask's server.
