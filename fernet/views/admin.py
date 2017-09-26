import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict
from fernet import app, db, images, forms, teknologkoren_se
from fernet.views.auth import verify_email
from fernet.models import User, Tag
from fernet.util import tag_required

mod = Blueprint('admin', __name__, url_prefix='/admin')

app.jinja_env.add_extension('jinja2.ext.do')


@mod.before_request
@login_required
def before_request():
    """Make sure user is logged in before request.

    This function does nothing, but the decorators do.
    """
    pass


@mod.route('/')
@tag_required('Webmaster', 'PRoletär')
def admin():
    """Show administration page."""
    return render_template('admin/admin.html')


@mod.route('/edit-user/<int:id>/', methods=['GET', 'POST'])
@tag_required('Webmaster')
def full_edit_user(id):
    """Edit all user attributes.

    Allows for editing of all user attributes, including name and tags.
    Tags are in an encapsulated form generated dynamically in this view.
    """
    user = User.query.get_or_404(id)

    tags = Tag.query.order_by(Tag.name).all()
    form = forms.TagForm.extend_form(forms.FullEditUserForm, tags, user)

    form = form(user)

    if form.validate_on_submit():
        if form.email.data != user.email:
            verify_email(user, form.email.data)
            flash("A verification link has been sent to {}"
                  .format(form.email.data), 'info')

        user.phone = form.phone.data

        user.first_name = form.first_name.data
        user.last_name = form.last_name.data

        form.set_user_tags()

        db.session.commit()

        return redirect(url_for('profile.member', id=id))
    else:
        forms.flash_errors(form)

    return render_template('admin/full_edit_user.html',
                           user=user,
                           form=form)


@mod.route('/adduser/', methods=['GET', 'POST'])
@tag_required('Webmaster')
def adduser():
    """Add a user."""
    tags = Tag.query.order_by(Tag.name).all()
    Form = forms.TagForm.extend_form(forms.AddUserForm, tags)

    form = Form()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    phone=form.phone.data)

        forms.TagForm.set_user_tags(form, user)

        db.session.commit()

        form = forms.AddUserForm()

        flash("User {} added!".format(user.email), 'success')

        return redirect(url_for('.adduser'))

    else:
        if form.errors:
            flash(form.errors, 'error')

    return render_template('admin/adduser.html', form=form)


@mod.route('/view-posts/')
@tag_required('Webmaster', 'PRoletär')
def view_posts():
    """Show links to all post's edit mode."""
    posts = teknologkoren_se.get_all_posts()

    return render_template('admin/view-posts.html', posts=posts)


@mod.route('/view-events/')
@tag_required('Webmaster', 'PRoletär')
def view_events():
    """Show links to all event's edit mode."""
    events = teknologkoren_se.get_all_events()

    return render_template('admin/view-events.html', events=events)


@mod.route('/new-post/', methods=['GET', 'POST'])
@tag_required('Webmaster', 'PRoletär')
def new_post():
    """Create a new post."""
    form = forms.EditPostForm(CombinedMultiDict((request.form, request.files)))

    if form.validate_on_submit():
        if form.upload.data:
            upload = teknologkoren_se.upload_image(form.upload.data)
            image = upload['filename']
        else:
            image = None

        post = teknologkoren_se.new_post(form.title.data,
                                         form.content.data,
                                         form.published.data,
                                         image)

        return redirect(url_for('.edit_post',
                                post_id=post['id'],
                                slug=post['slug']))

    else:
        forms.flash_errors(form)

    return render_template('admin/edit-post.html', form=form)


@mod.route('/edit-post/<int:post_id>/', methods=['GET', 'POST'])
@mod.route('/edit-post/<int:post_id>/<slug>/', methods=['GET', 'POST'])
@tag_required('Webmaster', 'PRoletär')
def edit_post(post_id, slug=None):
    """Edit an existing post."""
    post = teknologkoren_se.get_post(post_id)

    if slug != post['slug']:
        return redirect(url_for('.edit_post',
                                post_id=post['id'],
                                slug=post['slug']))

    form = forms.EditPostForm(CombinedMultiDict((request.form, request.files)),
                              data=post)

    if form.validate_on_submit():
        if form.upload.data:
            upload = teknologkoren_se.upload_image(form.upload.data)
            image = upload['filename']
        else:
            image = post['image']

        teknologkoren_se.update_post(post['id'],
                                     form.title.data,
                                     form.content.data,
                                     form.published.data,
                                     image)

    else:
        forms.flash_errors(form)

    return render_template('admin/edit-post.html', form=form, post=post)


@mod.route('/remove-post/<int:post_id>/')
@mod.route('/remove-post/<int:post_id>/<slug>/')
@tag_required('Webmaster', 'PRoletär')
def remove_post(post_id, slug=None):
    """Remove a post."""
    teknologkoren_se.delete_post(post_id)
    return redirect(url_for('.view_posts'))


@mod.route('/new-event/', methods=['GET', 'POST'])
@tag_required('Webmaster', 'PRoletär')
def new_event():
    """Create a new event."""
    form = forms.EditEventForm(
        CombinedMultiDict((request.form, request.files))
        )

    if form.validate_on_submit():
        if form.upload.data:
            upload = teknologkoren_se.upload_image(form.upload.data)
            image = upload['filename']
        else:
            image = None

        start_time = form.start_time.data.strftime('%Y-%m-%dT%H:%M')

        event = teknologkoren_se.new_event(form.title.data,
                                           form.content.data,
                                           form.published.data,
                                           start_time,
                                           form.location.data,
                                           image)

        return redirect(url_for('.edit_event',
                                event_id=event['id'],
                                slug=event['slug']))

    else:
        forms.flash_errors(form)

    return render_template('admin/edit-event.html', form=form)


@mod.route('/edit-event/<int:event_id>/', methods=['GET', 'POST'])
@mod.route('/edit-event/<int:event_id>/<slug>/', methods=['GET', 'POST'])
@tag_required('Webmaster', 'PRoletär')
def edit_event(event_id, slug=None):
    """Edit an existing post."""
    event = teknologkoren_se.get_event(event_id)

    if slug != event['slug']:
        return redirect(url_for('.edit_post',
                                event_id=event['id'],
                                slug=event['slug']))

    form = forms.EditEventForm(
            CombinedMultiDict((request.form, request.files)),
            data=event)

    if form.validate_on_submit():
        if form.upload.data:
            upload = teknologkoren_se.upload_image(form.upload.data)
            image = upload['filename']
        else:
            image = event['image']

        start_time = form.start_time.data.strftime('%Y-%m-%dT%H:%M')

        teknologkoren_se.update_event(event['id'],
                                      form.title.data,
                                      form.content.data,
                                      form.published.data,
                                      start_time,
                                      form.location.data,
                                      image)

    else:
        forms.flash_errors(form)

    return render_template('admin/edit-event.html', form=form, event=event)


@mod.route('/remove-event/<int:event_id>/')
@mod.route('/remove-event/<int:event_id>/<slug>/')
@tag_required('Webmaster', 'PRoletär')
def remove_event(event_id, slug=None):
    """Remove an event."""
    teknologkoren_se.delete_event(event_id)
    return redirect(url_for('.view_events'))


@mod.route('/update-contacts/', methods=['GET', 'POST'])
@tag_required('Webmaster')
def update_contacts():
    form = forms.UpdateContactsForm(
            CombinedMultiDict((request.form, request.files)))

    if form.validate_on_submit():
        tags = [('Ordförande', 'ordf@teknologkoren.se', 0),
                ('Vice ordförande', 'vice@teknologkoren.se', 1),
                ('Kassör', 'pengar@teknologkoren.se', 2),
                ('Sekreterare', 'sekr@teknologkoren.se', 3),
                ('PRoletär', 'pr@teknologkoren.se', 4),
                ('Notfisqual', 'noter@teknologkoren.se', 5),
                ('Qlubbmästare', 'qm@teknologkoren.se', 6),
                ]

        new_contacts = []
        for tag in tags:
            user = User.query.filter(User.has_tag(tag[0])).first()
            new_contacts.append({
                    'title': tag[0],
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': tag[1],
                    'phone': user.phone if tag[0] == 'Ordförande' else None,
                    'weight': tag[2],
                    })

        remote_contacts = teknologkoren_se.get_all_contacts()

        [teknologkoren_se.delete_contact(contact['id'])
            for contact in remote_contacts]

        [teknologkoren_se.new_contact(**contact)
            for contact in new_contacts]

        flash('Contacts updated!', 'success')

    return render_template('admin/update-contacts.html', form=form)
