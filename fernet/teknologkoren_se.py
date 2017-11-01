import datetime
import pytz
import requests
from flask import abort
from fernet import app

API_URL = app.config['TEKNOLOGKORENSE_API_URL']
AUTH = requests.auth.HTTPBasicAuth(
        app.config['TEKNOLOGKORENSE_API_USERNAME'],
        app.config['TEKNOLOGKORENSE_API_PASSWORD']
        )


def get_all_posts():
    r = requests.get("{}/posts".format(API_URL), auth=AUTH)
    return r.json()


def get_post(post_id):
    r = requests.get("{}/posts/{}".format(API_URL, post_id), auth=AUTH)
    return r.json() if r.ok else abort(404)


def new_post(title, content_sv, content_en, published, image=None):
    """Upload a new post.

    `image` is not the actual image, it is the filename returned by an
    upload via `/api/images`.
    """
    data = {
        'title': title,
        'content_sv': content_sv,
        'content_en': content_en,
        'published': published,
        'image': image,
    }
    r = requests.post("{}/posts".format(API_URL), json=data, auth=AUTH)
    return r.json() if r.ok else False


def update_post(post_id, title, content_sv, content_en, published, image=None):
    """Update a post.

    `image` is not the actual image, it is the filename returned by an
    upload via `/api/images`.
    """
    data = {
            'title': title,
            'content_sv': content_sv,
            'content_en': content_en,
            'published': published,
            'image': image,
            }
    r = requests.put("{}/posts/{}".format(API_URL, post_id),
                     json=data,
                     auth=AUTH)
    return r.json()


def delete_post(post_id):
    r = requests.delete("{}/posts/{}".format(API_URL, post_id), auth=AUTH)
    return True if r.ok else False


def get_all_events():
    r = requests.get("{}/events".format(API_URL), auth=AUTH)
    return r.json()


def get_event(event_id):
    """Get an event.

    Returns modified response, converting iso-format date string to
    datetime.
    """
    r = requests.get("{}/events/{}".format(API_URL, event_id), auth=AUTH)
    d = r.json()

    tz = pytz.timezone('Europe/Stockholm')
    utc_start_time = datetime.datetime.strptime(d['start_time'],
                                                '%Y-%m-%dT%H:%M')
    local_time = pytz.utc.localize(utc_start_time, is_dst=None).astimezone(tz)

    d['start_time'] = local_time

    return d


def new_event(title, content_sv, content_en, published, start_time, location, image=None):
    """Upload a new event.

    `image` is not the actual image, it is the filename returned by an
    upload via `/api/images`.
    """
    # User enters local time, convert to utc
    tz = pytz.timezone('Europe/Stockholm')
    utc_start_time = tz.localize(start_time, is_dst=None).astimezone(pytz.utc)
    utc_start_time_str = utc_start_time.strftime('%Y-%m-%dT%H:%M')

    data = {
        'title': title,
        'content_sv': content_sv,
        'content_en': content_en,
        'published': published,
        'start_time': utc_start_time_str,
        'location': location,
        'image': image,
    }
    r = requests.post("{}/events".format(API_URL), json=data, auth=AUTH)
    return r.json() if r.ok else False


def update_event(event_id,
                 title,
                 content_sv,
                 content_en,
                 published,
                 start_time,
                 location,
                 image=None):
    """Update an event.

    `image` is not the actual image, it is the filename returned by an
    upload via `/api/images`.
    """
    # User enters local time, convert to utc
    tz = pytz.timezone('Europe/Stockholm')
    utc_start_time = tz.localize(start_time, is_dst=None).astimezone(pytz.utc)
    utc_start_time_str = utc_start_time.strftime('%Y-%m-%dT%H:%M')

    data = {
        'title': title,
        'content_sv': content_sv,
        'content_en': content_en,
        'published': published,
        'start_time': utc_start_time_str,
        'location': location,
        'image': image,
    }
    r = requests.put("{}/events/{}".format(API_URL, event_id),
                     json=data,
                     auth=AUTH)
    return r.json() if r.ok else False


def delete_event(event_id):
    r = requests.delete("{}/events/{}".format(API_URL, event_id), auth=AUTH)
    return True if r.ok else False


def upload_image(image):
    files = {'image': (image.filename, image.read())}
    r = requests.post("{}/images".format(API_URL), files=files, auth=AUTH)
    return r.json()


def get_all_contacts():
    r = requests.get("{}/contact".format(API_URL), auth=AUTH)
    return r.json()


def get_contact(contact_id):
    r = requests.get("{}/contact/{}".format(API_URL), auth=AUTH)
    return r.json()


def new_contact(title, first_name, last_name, email, phone, weight):
    data = {
        'title': title,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone': phone,
        'weight': weight,
    }
    r = requests.post("{}/contact".format(API_URL), json=data, auth=AUTH)
    return r.json()


def delete_contact(contact_id):
    r = requests.delete("{}/contact/{}".format(API_URL, contact_id), auth=AUTH)
    return True if r.ok else False
