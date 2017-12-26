import random
import requests
import string
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from fernet import app, db, bcrypt


class UserTag(db.Model):
    """Many to many relation between User and Tag.

    Uses the 'association object pattern' to be able to save extra data
    in the associations.
    """
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

    user = db.relationship('User', back_populates='tags')
    tag = db.relationship('Tag', back_populates='users')

    start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end = db.Column(db.DateTime)

    @hybrid_property
    def is_active(self):
        now = datetime.utcnow()

        has_started = (self.start <= now)
        not_ended = self.end.is_(None) | (now < self.end)

        return has_started & not_ended

    def end_association(self):
        self.end = datetime.utcnow()

    def __str__(self):
        return "UserTag({}/{})".format(self.user, self.tag)


class User(UserMixin, db.Model):
    """A representation of a user.

    An email address cannot be longer than 254 characters:
    http://www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))

    # Do not change the following directly, use User.password
    _password = db.Column(db.String(128))
    _password_timestamp = db.Column(db.DateTime)

    tags = db.relationship('UserTag',
                           cascade="all,delete",
                           back_populates='user')

    def __init__(self, *args, **kwargs):
        if 'password' not in kwargs:
            password = ''.join(random.choice(string.ascii_letters +
                                             string.digits) for _ in range(30))
            kwargs['password'] = password

        super().__init__(*args, **kwargs)

    @hybrid_property
    def password(self):
        """Return password hash."""
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        """Generate and save password hash, update password timestamp."""
        self._password = bcrypt.generate_password_hash(plaintext)

        # Save in UTC, password resets compare this to UTC time!
        self._password_timestamp = datetime.utcnow()

    def verify_password(self, plaintext):
        """Return True if plaintext matches password, else return False."""
        return bcrypt.check_password_hash(self._password, plaintext)

    @property
    def active_tags(self):
        return [user_tag.tag
                for user_tag
                in UserTag.query.filter(UserTag.user == self,
                                        UserTag.is_active == True
                                        )]

    @hybrid_method
    def has_tag(self, *tags, active=True):
        """Return True if User instance has at least one of tags."""
        has_tag = UserTag.query.filter(
            UserTag.user == self,
            UserTag.tag.has(Tag.name.in_(tags)),
            UserTag.is_active == active
            ).scalar()

        return has_tag

    @has_tag.expression
    def has_tag(self, *tags, active=True):
        """Return an Exists with all Users that has at least one of tags."""
        return self.tags.any(UserTag.tag.has(Tag.name.in_(tags)),
                             is_active=active)

    @staticmethod
    def authenticate(email, password):
        """Check email and password and return user if matching.

        It might be tempting to return the user that mathes the email
        and a boolean representing if the password was correct, but
        please don't. The email alone does not identify a user, only
        the email toghether with a matching password is enough to
        identify which user we want! No matching email and password ->
        no user.
        """
        user = User.query.filter_by(email=email).first()

        if user and user.verify_password(password):
            return user

        return None

    def __str__(self):
        """String representation of the user."""
        return "{} {}".format(self.first_name, self.last_name)


class Tag(db.Model):
    """Representation of a tag."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)

    users = db.relationship('UserTag', back_populates='tag')

    def __str__(self):
        """String representation of the tag."""
        return self.name
