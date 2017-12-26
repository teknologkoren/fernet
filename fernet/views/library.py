from flask import Blueprint, flash, redirect, render_template, request, url_for
from fernet import db, forms
from fernet.models import Score


mod = Blueprint('library', __name__, url_prefix='/library')


@mod.route('/')
def index():
    scores = Score.query.all()
    return render_template('library/index.html', scores=scores)


@mod.route('/add/', methods=['GET', 'POST'])
def add_score():
    form = forms.EditScoreForm(request.form)

    if form.validate_on_submit():
        score = Score()
        form.populate_obj(score)
        db.session.add(score)
        db.session.commit()

        flash("{} added!".format(score.name), 'success')

        return redirect(url_for('.add_score'))

    else:
        forms.flash_errors(form)

    return render_template('library/edit_score.html', form=form, score=None)


@mod.route('/edit/<int:score_id>/', methods=['GET', 'POST'])
def edit_score(score_id):
    score = Score.query.get_or_404(score_id)
    form = forms.EditScoreForm(request.form, obj=score)

    if form.validate_on_submit():
        form.populate_obj(score)
        db.session.commit()
        flash("{} edited!".format(score.name), 'success')

    else:
        forms.flash_errors(form)

    return render_template('library/edit_score.html', form=form, score=score)
