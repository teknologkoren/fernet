from flask import request, send_from_directory
from fernet import app

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
