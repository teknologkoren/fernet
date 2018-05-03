import datetime
import pytz
import requests
from flask import flash
from fernet import app

API_URL = app.config['TEKNOLOGKORENSE_API_URL']
AUTH = requests.auth.HTTPBasicAuth(
        app.config['TEKNOLOGKORENSE_API_USERNAME'],
        app.config['TEKNOLOGKORENSE_API_PASSWORD']
        )


def make_request(requests_func, url, data=None, files=None):
    """Wrap a requests function.

    Returns response if connection was successful and response is ok, flashes
    an error and returns None otherwise.
    """
    try:
        r = requests_func(url, json=data, files=files, auth=AUTH)
    except requests.exceptions.ConnectionError:
        flash('Failed to connect to teknologkoren.se.', 'error')
        return None
    except requests.exceptions.Timeout:
        flash('Connection to teknologkoren.se timed out.', 'error')
        return None

    if not r.ok:
        if r.status_code == 404:
            flash('Whatever you were trying access does not exist.', 'error')
            return None

        else:
            flash('Something went wrong, try again or ask webmaster for help.',
                  'error')

            # log error
            print(('API error: request = {}, url = {}, data = {}, files = {}'
                   ', status_code = {}, response = {}'
                   ).format(requests_func, url, data, files, r.status_code,
                            r.json()))

            return None

    return r


def make_get(url):
    r = make_request(requests.get, url)

    return r


def make_post(url, data=None, files=None):
    return make_request(requests.post, url, data, files)


def make_put(url, data=None, files=None):
    return make_request(requests.put, url, data, files)


def make_delete(url):
    return make_request(requests.delete, url)


def get_all_posts():
    return make_get("{}/posts".format(API_URL))


def get_post(post_id):
    return make_get("{}/posts/{}".format(API_URL, post_id))


def new_post(title, content_sv, content_en, readmore_sv, readmore_en,
             published, image=None):
    """Upload a new post.

    `image` is not the actual image, it is the filename returned by an
    upload via `/api/images`.
    """
    data = {
        'title': title,
        'content_sv': content_sv,
        'content_en': content_en or None,
        'readmore_sv': readmore_sv or None,
        'readmore_en': readmore_en or None,
        'published': published,
        'image': image,
    }
    return make_post("{}/posts".format(API_URL), data)


def update_post(post_id, title, content_sv, content_en, readmore_sv,
                readmore_en, published, image=None):
    """Update a post.

    `image` is not the actual image, it is the filename returned by an
    upload via `/api/images`.
    """
    data = {
        'title': title,
        'content_sv': content_sv,
        'content_en': content_en or None,
        'readmore_sv': readmore_sv or None,
        'readmore_en': readmore_en or None,
        'published': published,
        'image': image,
    }
    return make_put("{}/posts/{}".format(API_URL, post_id), data)


def delete_post(post_id):
    return make_delete("{}/posts/{}".format(API_URL, post_id))


def get_all_events():
    return make_get("{}/events".format(API_URL))


def get_event(event_id):
    """Get an event.

    Returns modified response, converting iso-format date string to
    datetime.
    """
    r = make_get("{}/events/{}".format(API_URL, event_id))

    if not r:
        return r

    d = r.json()

    tz = pytz.timezone('Europe/Stockholm')
    utc_start_time = datetime.datetime.strptime(d['start_time'],
                                                '%Y-%m-%dT%H:%M')
    local_time = pytz.utc.localize(utc_start_time, is_dst=None).astimezone(tz)

    d['start_time'] = local_time

    return d


def new_event(title, content_sv, content_en, readmore_sv, readmore_en,
              published, start_time, location, image=None):
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
        'content_en': content_en or None,
        'readmore_sv': readmore_sv or None,
        'readmore_en': readmore_en or None,
        'published': published,
        'start_time': utc_start_time_str,
        'location': location,
        'image': image,
    }
    return make_post("{}/events".format(API_URL), data)


def update_event(event_id, title, content_sv, content_en, readmore_sv,
                 readmore_en, published, start_time, location, image=None):
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
        'content_en': content_en or None,
        'readmore_sv': readmore_sv or None,
        'readmore_en': readmore_en or None,
        'published': published,
        'start_time': utc_start_time_str,
        'location': location,
        'image': image,
    }
    return make_put("{}/events/{}".format(API_URL, event_id), data)


def delete_event(event_id):
    return make_delete("{}/events/{}".format(API_URL, event_id))


def upload_image(image):
    files = {'image': (image.filename, image.read())}
    return make_post("{}/images".format(API_URL), files=files)


def get_all_contacts():
    return make_get("{}/contact".format(API_URL))


def get_contact(contact_id):
    return make_get("{}/contact/{}".format(API_URL))


def new_contact(title, first_name, last_name, email, phone, weight):
    data = {
        'title': title,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone': phone,
        'weight': weight,
    }
    return make_post("{}/contact".format(API_URL), data)


def delete_contact(contact_id):
    return make_delete("{}/contact/{}".format(API_URL, contact_id))
