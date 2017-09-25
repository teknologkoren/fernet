from flask import (Blueprint, request, redirect, render_template, url_for,
                   abort, flash)
from flask_login import current_user, login_user, logout_user
from itsdangerous import SignatureExpired
from fernet import db, login_manager, forms
from fernet.models import User
from fernet.util import send_email, ts


mod = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(userid):
    """Tell flask-login how to get logged in user."""
    return User.query.get(userid)


@mod.route('/login/', methods=['GET', 'POST'])
def login():
    """Show login page and form.

    Not showing which field was wrong if any is intentional. Usernames
    and passwords only represent anything when used in combination
    (http://ux.stackexchange.com/a/13523).
    """
    form = forms.LoginForm(request.form)

    if current_user.is_authenticated:
        return form.redirect('intranet.index')

    if form.validate_on_submit():
        user = form.user
        login_user(user, remember=form.remember.data)
        return form.redirect('intranet.index')
    elif form.is_submitted():
        flash("Sorry, your email address or password was incorrect.", 'error')

    return render_template('auth/login.html', form=form)


@mod.route('/logout/')
def logout():
    """Logout user (if logged in) and redirect to main page."""
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('blog.index'))


def verify_email(user, email):
    """Create an email verification email.

    The user id and the requested email address is hashed and included as a
    token in a link referring to the verification page. The link is sent to the
    requested email address.

    The token is timestamped, when verifying we can check the age.
    """
    token = ts.dumps([user.id, email], 'verify-email')

    verify_link = url_for('auth.verify_token', token=token, _external=True)

    email_body = render_template('auth/email_verification.jinja2',
                                 link=verify_link)

    subject = "Verify your email at teknologkoren.se"

    send_email(email, subject, email_body)


@mod.route('/verify/<token>/')
def verify_token(token):
    """Verify email reset token.

    Loads the user id and the requested email and simultaneously checks
    token age. If not too old, get user with id and set email.
    """
    try:
        user_id, email = ts.loads(token, salt='verify-email', max_age=900)
    except SignatureExpired:
        flash("Sorry, the link has expired. Please try again.", 'error')
        return redirect(url_for('blog.index'))
    except:
        abort(404)

    user = User.query.get_or_404(user_id)
    user.email = email
    db.session.commit()

    flash("{} is now verified!".format(email), 'success')
    return redirect(url_for('blog.index'))


@mod.route('/reset/', methods=['GET', 'POST'])
def reset():
    """View for requesting password reset.

    If a non-registred email address is entered, do nothing but tell
    user that an email has been sent. This way we do not expose what
    email addresses are registred.

    If a registred email address is entered, get the id of the user the
    email address is registred to and create a timestamped token with
    the id. The token is sent as a part of a link to the email of that
    user.

    The view which the link leads to checks that the token is intact and
    has not been tampered with, checks its age, and checks if the
    password has been changed after the token was created. This means:
    * Tokens are time limited.
    * Multiple tokens can be valid at the same time, which prevents
        confusion for the user.
    * If the password is changed, using a token or in some other way,
        all tokens generated before that change become invalid.
    * Tokens are therefore single use.
    * Tokens are not stored anywhere other than in the email sent to
        user.
    """
    reset_flash = ("If {} exists in our system, we've sent a password reset "
                   "link to it.")

    form = forms.ExistingEmailForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = ts.dumps(user.id, salt='recover-key')

        recover_url = url_for('.reset_token', token=token, _external=True)

        email_body = render_template(
            'auth/password_reset_email.jinja2',
            name=user.first_name,
            link=recover_url)

        subject = "Reset your password at teknologkoren.se"

        send_email(user.email, subject, email_body)

        flash(reset_flash.format(form.email.data), 'info')
        return redirect(url_for('.login'))

    elif form.email.data:
        flash(reset_flash.format(form.email.data), 'info')
        return redirect(url_for('.login'))

    elif form.errors:
        flash("Please enter your email.", 'error')

    return render_template('auth/reset.html', form=form)


@mod.route('/reset/<token>/', methods=['GET', 'POST'])
def reset_token(token):
    """Verify a password reset token.

    Checks if the token is intact and has not been tampered with,
    checks its age, and checks if the password has been changed after
    the token was created.

    If the token is valid, allow user to enter a new password.

    Note: itsdangerous saves the timestamp in tokens in UTC!
    """
    expired = "Sorry, the link has expired. Please try again."
    invalid = "Sorry, the link appears to be broken. Please try again."

    try:
        data, timestamp = ts.loads(token, salt='recover-key', max_age=3600,
                                   return_timestamp=True)
        user = User.query.get(data)
    except SignatureExpired:
        flash(expired, 'error')
        return redirect(url_for('.login'))
    except:
        flash(invalid, 'error')
        return redirect(url_for('.login'))

    if timestamp < user._password_timestamp:
        flash(expired, 'error')
        return redirect(url_for('.login'))

    form = forms.NewPasswordForm()

    if form.validate_on_submit():
        user.password = form.new_password.data
        db.session.commit()
        flash("Your password has been reset!", 'success')
        return redirect(url_for('.login'))
    else:
        forms.flash_errors(form)

    return render_template('auth/reset_token.html', form=form)
