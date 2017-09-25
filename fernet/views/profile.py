from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from fernet import app, db, forms
from fernet.views.auth import verify_email
from fernet.models import User

mod = Blueprint('profile', __name__)

app.jinja_env.add_extension('jinja2.ext.do')


@mod.before_request
@login_required
def before_request():
    """Make sure user is logged in before request.

    This function does nothing, but the decorators do.
    """
    pass


@mod.route('/member/<int:id>/')
def member(id):
    """Show member of user with matching id."""
    user = User.query.get_or_404(id)
    tags = user.active_tags

    return render_template('profile/member.html',
                           user=user,
                           tags=tags)


@mod.route('/member/edit/', methods=['GET', 'POST'])
def edit_user():
    """Edit (own) member.

    Redirects to admin-edit if user is webmaster, redirects to viewing
    member if not own member. Allows editing of email, phone number,
    and password. Edit of email has to be confirmed by clicking a link
    sent to the new email address.
    """
    form = forms.EditUserForm(current_user, request.form)

    if form.validate_on_submit():
        if form.email.data != current_user.email:
            verify_email(current_user, form.email.data)
            flash("Please check {} for a verification link."
                  .format(form.email.data), 'info')

        current_user.phone = form.phone.data

        db.session.commit()

        return redirect(url_for('.member', id=current_user.id))
    else:
        forms.flash_errors(form)

    return render_template('profile/edit_user.html',
                           user=current_user,
                           form=form)


@mod.route('/member/edit/password/', methods=['GET', 'POST'])
def change_password():
    """Change current users password."""
    form = forms.ChangePasswordForm(current_user)
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.commit()
        flash('Your password has been changed!', 'success')
        return redirect(url_for('.member', id=current_user.id))
    else:
        forms.flash_errors(form)

    return render_template('profile/change_password.html', form=form)
