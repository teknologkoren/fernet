from functools import partialmethod
from flask import flash, url_for, redirect
from wtforms import fields, validators
import wtforms.fields.html5 as html5_fields
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from fernet import db, images
from fernet.models import User, UserTag
from fernet.util import get_redirect_target, is_safe_url


def flash_errors(form):
    """Flash all errors in a form."""
    for field in form:
        for error in field.errors:
            flash(("Error in {} field: {}"
                   .format(field.label.text, error)),
                  'error')


class TagForm:
    """Namespace for tag forms.

    Do not use this as an object, it is only the methods that are
    interesting.

    WTForms does not allow adding fields after initialization, so we
    use a method to extend a form with a FormField that contains the
    tag fields, checked and ready to go.

    We make sure not to setattr the base as this will modify it
    process wide, instead we let a new class inherit from the base.
    """
    @classmethod
    def extend_form(cls, base, tags, user=None):
        """Return an extended form with tag fields and user modifying method.

        Arguments:
            base: the form to extend
            tags: the tags to extend the form with
            user: a user to check tags against (optional)

        If a user is passed, check the fields of the tags that the user
        has, and set set_user_tags as a method with arguments attached.
        Also set user as an attribute of the extended form.
        """
        class ExtendedBase(base):
            pass

        Tags = cls.tag_form(tags, user)
        ExtendedBase.tags = fields.FormField(Tags)

        if user:
            ExtendedBase.user = user
            # Add TagForm.set_user_tags to Tags together with arguments.
            ExtendedBase.set_user_tags = partialmethod(cls.set_user_tags, user)

        return ExtendedBase

    @classmethod
    def tag_form(cls, tags, user=None):
        class Tags(FlaskForm):
            pass

        for tag in tags:
            # If user has this tag, set its value to checked
            if user and user.has_tag(tag.name):
                field = fields.BooleanField(tag.name, default=True)
            else:
                field = fields.BooleanField(tag.name)

            # Add the field to this class with the name of the tag
            setattr(Tags, tag.name, field)

        Tags.tags = tags
        Tags.checked_tags = partialmethod(cls.checked_tags)

        return Tags

    def checked_tags(self):
        """Get list of checked tags."""
        tags = self.tags
        checked = []
        for tag in tags:
            tag_field = getattr(self, tag.name)

            if tag_field.data:
                checked.append(tag.name)

        return checked

    @staticmethod
    def set_user_tags(form, user):
        """Update user with new and removed tags."""
        tag_form = form.tags
        for tag in tag_form.tags:
            tag_field = getattr(tag_form, tag.name)

            # If tag field is checked and the user did not already
            # have that tag, give user tag
            if tag_field.data and not user.has_tag(tag.name):
                user_tag = UserTag()
                user_tag.tag = tag
                user.tags.append(user_tag)

            # If tag field isn't checked but the user has that tag,
            # remove it.
            elif not tag_field.data and user.has_tag(tag.name):
                user_tag = UserTag.query.filter(UserTag.user == user,
                                                UserTag.tag == tag,
                                                UserTag.is_active == True
                                                ).one()
                user_tag.end_association()

        db.session.commit()


class LowercaseEmailField(html5_fields.EmailField):
    """Custom field that lowercases input."""
    def process_formdata(self, valuelist):
        valuelist[0] = valuelist[0].lower()
        super().process_formdata(valuelist)


class Unique:
    """Validate that field is unique in model."""
    def __init__(self, model, field, message='This element already exists.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        if (db.session.query(self.model)
                .filter(self.field == field.data).scalar()):
            raise validators.ValidationError(self.message)


class Exists:
    """Validate that field is unique in model."""
    def __init__(self, model, field, message='This element does not exist.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        if not (db.session.query(self.model)
                .filter(self.field == field.data).scalar()):
            raise validators.ValidationError(self.message)


class RedirectForm(FlaskForm):
    next = fields.HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if self.next.data and is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class EmailForm(FlaskForm):
    email = LowercaseEmailField('Email', validators=[
        validators.InputRequired(),
        validators.Email()
        ])


class ExistingEmailForm(FlaskForm):
    email = LowercaseEmailField('Email', validators=[
        validators.InputRequired(),
        validators.Email(),
        Exists(
            User,
            User.email,
            message='Unknown email')
        ])


class PasswordForm(FlaskForm):
    password = fields.PasswordField(
        'Password',
        validators=[validators.InputRequired()],
        description="Required, your current password"
        )


class NewPasswordForm(FlaskForm):
    new_password = fields.PasswordField(
        'New password',
        validators=[validators.InputRequired(), validators.Length(min=8)],
        description="Required, your new password. At least 8 characters long."
        )


class ChangePasswordForm(PasswordForm, NewPasswordForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        if not self.user.verify_password(self.password.data):
            self.password.errors.append("Wrong password.")
            return False

        return True


class LoginForm(RedirectForm, EmailForm, PasswordForm):
    """Get login details."""
    remember = fields.BooleanField('Remember me')

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        user = User.authenticate(self.email.data, self.password.data)
        if not user:
            return False

        self.user = user
        return True


class AddUserForm(FlaskForm):
    first_name = fields.StringField('First Name', validators=[
        validators.InputRequired()
        ])

    last_name = fields.StringField('Last Name', validators=[
        validators.InputRequired()
        ])

    email = LowercaseEmailField('Email', validators=[
        validators.InputRequired(),
        validators.Email(),
        Unique(
            User,
            User.email,
            message="This email is already in use")
        ])

    phone = html5_fields.TelField('Phone', validators=[
        validators.Regexp(r'^\+?[0-9]*$')
        ])


class EditUserForm(FlaskForm):
    email = LowercaseEmailField(
        'Email',
        validators=[
            validators.InputRequired(),
            validators.Email()
        ],
        description="Required, a valid email address"
        )

    phone = html5_fields.TelField(
        'Phone',
        validators=[
            validators.InputRequired(),
            validators.Regexp(r'^\+?[0-9]*$')
        ],
        description="Required, a phone number like 0701234567"
        )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(obj=user, *args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        if db.session.query(User.id).filter_by(email=self.email.data).scalar():
            if self.email.data != self.user.email:
                self.email.errors.append("This email is already in use")
                return False

        return True


class FullEditUserForm(EditUserForm):
    first_name = fields.StringField(
        'First Name',
        validators=[validators.InputRequired()],
        description="Required, user's first name"
        )

    last_name = fields.StringField(
        'Last Name',
        validators=[validators.InputRequired()],
        description="Required, user's last/family name"
        )


class UploadForm(FlaskForm):
    upload = fields.FileField('Image', validators=[
        FileAllowed(images, 'Images only!')
        ])


class EditPostForm(UploadForm):
    content_sv = fields.TextAreaField(validators=[
        validators.InputRequired()
        ])

    content_en = fields.TextAreaField()

    title = fields.StringField('Title', validators=[
        validators.InputRequired()
        ])

    published = fields.BooleanField('Publish')


class EditEventForm(EditPostForm):
    start_time = fields.DateTimeField(format='%Y-%m-%d %H:%M', validators=[
        validators.InputRequired()
        ])
    location = fields.StringField('Location', validators=[
        validators.InputRequired()
        ])


class UpdateContactsForm(FlaskForm):
    pass
