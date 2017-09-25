from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from wtforms.fields import FormField
from flask_wtf import FlaskForm
from fernet import app, forms
from fernet.models import User, Tag

mod = Blueprint('members', __name__)

app.jinja_env.add_extension('jinja2.ext.do')


@mod.before_request
@login_required
def before_request():
    """Make sure user is logged in before request.

    This function does nothing, but the decorators do.
    """
    pass


@mod.route('/members/all/')
def all_members():
    """Show all registred members."""
    tag_dict = {'All': User.query.order_by(User.first_name)}
    tag_list = ['All']

    return render_template(
        'members/members.html',
        tag_list=tag_list,
        tag_dict=tag_dict)


@mod.route('/members/<list:tag_list>/')
def members_by_tags(tag_list):
    """Show active members sorted by the tags in tag_list."""
    active_users = User.query.filter(User.has_tag('Aktiv'))

    tag_dict = {}
    for tag in tag_list:
        tag_dict[tag] = active_users.filter(User.has_tag(tag)
                                            ).order_by(User.first_name)

    return render_template(
        'members/members.html',
        tag_list=tag_list,
        tag_dict=tag_dict)


@mod.route('/members/<list:columns>/<list:rows>/')
def member_matrix(columns, rows):
    """Show a matrice of members based on their tags."""
    tag_dict = {}
    for column in columns:
        tag_dict[column] = {}
        for row in rows:
            tag_dict[column][row] = User.query.filter(
                    User.has_tag(column),
                    User.has_tag(row))

    return render_template('members/member_matrix.html',
                           columns=columns,
                           rows=rows,
                           tag_dict=tag_dict)


@mod.route('/members/filter/', methods=['GET', 'POST'])
def filter_members():
    class F(FlaskForm):
        pass

    TagColForm = forms.TagForm.tag_form(Tag.query.all())
    TagRowForm = forms.TagForm.tag_form(Tag.query.all())

    F.col_form = FormField(TagColForm)
    F.row_form = FormField(TagRowForm)

    form = F()

    if form.validate_on_submit():
        if form.col_form.checked_tags():

            if form.row_form.checked_tags():
                return redirect(url_for('.member_matrix',
                                        columns=form.col_form.checked_tags(),
                                        rows=form.row_form.checked_tags()))

            return redirect(url_for('.members_by_tags',
                                    tag_list=form.col_form.checked_tags()))
        else:
            flash("Please enter which tags to display (in columns)", 'error')

    return render_template('members/filter_members.html',
                           form=form)


@mod.route('/members/')
def voices():
    """Show members by voice."""
    tag_list = ['Sopran 1', 'Sopran 2', 'Alt 1', 'Alt 2', 'Tenor 1',
                'Tenor 2', 'Bas 1', 'Bas 2']
    return members_by_tags(tag_list)


@mod.route('/members/groups/')
def groups():
    """Show members by group."""
    columns = ['Sånggrupp 1', 'Sånggrupp 2', 'Sånggrupp 3']
    rows = ['Sopran 1', 'Sopran 2', 'Alt 1', 'Alt 2', 'Tenor 1', 'Tenor 2',
            'Bas 1', 'Bas 2']
    return member_matrix(columns, rows)
