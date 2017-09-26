from flask_script import Manager, prompt, prompt_pass

from fernet import app, db
from fernet.models import Tag, User

manager = Manager(app)


@manager.command
def create_db():
    """Create database and all tables."""
    db.create_all()


@manager.command
def create_tags():
    """Create a set of standard tags."""
    tags = ['Webmaster',
            'Aktiv',
            'Sopran 1',
            'Sopran 2',
            'Alt 1',
            'Alt 2',
            'Tenor 1',
            'Tenor 2',
            'Bas 1',
            'Bas 2',
            'Sånggrupp 1',
            'Sånggrupp 2',
            'Sånggrupp 3',
            'Ordförande',
            'Vice ordförande',
            'Sekreterare',
            'PRoletär',
            'Kassör',
            'Qlubbmästare',
            'Notfisqual']

    for tag_name in tags:
        tag = Tag(name=tag_name)
        db.session.add(tag)

    db.session.commit()


@manager.command
def create_webmaster():
    """Create a user with webmaster tag.
    A webmaster tag has had to be created prior to running this
    command, either manually or with create_tags().
    """
    user = User(
        first_name = prompt('First name'),
        last_name = prompt('Last name'),
        email = prompt('Email'),
        password = prompt_pass('Password')
        )


    user.tags.append(Tag.query.filter_by(name='Webmaster').one())

    db.session.add(user)
    db.session.commit()


@manager.command
def full_setup():
    """First time setup of database."""
    print('Creating database...')
    create_db()
    print('Done!')
    print('Creating tags...')
    create_tags()
    print('Done!')
    print('Creating webmaster user...')
    create_webmaster()
    print('Done, setup complete.')


if __name__ == "__main__":
    manager.run()
