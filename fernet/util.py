import ssl
import smtplib
import threading
from email.message import EmailMessage
from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import flash, url_for, request, redirect
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer
from werkzeug.routing import BaseConverter
from fernet import app


ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])


class ListConverter(BaseConverter):
    """A converter that takes an arbitrary amount of arguments.

    Can be used in routes to take an arbitrary amount of arguments by
    separating them with '+', e.g. http://<...>/arg1+arg2+arg3
    """
    def to_python(self, value):
        return value.split('+')

    def to_url(self, values):
        return '+'.join(BaseConverter.to_url(self, value) for value in values)


def paginate(content, page, page_size):
    """Return a page of content.

    Calculates which posts to have on a specific page based on which
    page they're on and how many objects there are per page.
    """
    start_index = (page-1) * page_size
    end_index = start_index + page_size
    pagination = content[start_index:end_index]
    return pagination


def send_email(toaddr, subject, body):
    """Send an email with SMTP & STARTTLS.

    Uses the best security defaults according to the python documentation at
    the time of writing:
    https://docs.python.org/3/library/ssl.html#ssl-security

    "[ssl.create_default_context()] will load the system’s trusted CA
    certificates, enable certificate validation and hostname checking, and try
    to choose reasonably secure protocol and cipher settings."
    """

    msg = EmailMessage()
    msg.set_content(body)

    msg['Subject'] = subject
    msg['From'] = app.config['SMTP_SENDADDR']
    msg['To'] = toaddr

    def thread_func():
        if app.debug:
            print(msg)
            return

        with smtplib.SMTP(app.config['SMTP_MAILSERVER'],
                          port=app.config['SMTP_STARTTLS_PORT']) as smtp:
            context = ssl.create_default_context()
            smtp.starttls(context=context)
            smtp.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
            smtp.send_message(msg)

    thread = threading.Thread(target=thread_func)
    thread.start()


def url_for_other_page(page):
    """Return url for a page number."""
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


def is_safe_url(target):
    """Tests if the url is a safe target for redirection.

    Does so by checking that the url is still using http or https and
    and that the url is still our site.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        test_url.netloc == ref_url.netloc


def get_redirect_target():
    """Get where we want to redirect to.

    Checks the 'next' argument in the request and if nothing there, use
    the http referrer. Also checks whether the target is safe to
    redirect to (no 'open redirects').
    """
    for target in (request.values.get('next'), request.referrer):
        if not target:
            continue
        if target == request.url:
            continue
        if is_safe_url(target):
            return target


def tag_required(*tags):
    """Decorator to requiring the user to have at least one of the tags.

    To require multiple tags ('and' instead of 'or'), use multiple
    decorators.

    E.g., user is Tenor 1 or Tenor 2, and in Sånggrupp 2:
    ```
    @app.route('/my-route')
    @tag_required('Tenor 1', 'Tenor 2')
    @tag_required('Sånggrupp 2')
    def my_view():
        ...
    ```
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if current_user.has_tag(*tags):
                return func(*args, **kwargs)
            flash("You do not have permission to access that.", 'error')
            return redirect(request.referrer or url_for('.index'))
        return decorated_function
    return decorator
