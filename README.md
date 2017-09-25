# FerNET

## Installation with Pipenv
Make sure [Pipenv is installed](https://pipenv.readthedocs.io/en/latest/basics.html#installing-pipenv).
Clone the change directory to the repo, then run
```
pipenv install                      # Create virtualenv and install deps
pipenv shell                        # Spawn a shell with our environment
nodeenv -p -r npm-requirements.txt  # Install node.js requirements
```
You can exit out of the shell with `exit` or `^D`

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
