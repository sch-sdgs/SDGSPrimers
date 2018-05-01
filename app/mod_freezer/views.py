from flask import Blueprint
from flask import render_template, request, url_for, redirect
from flask.ext.login import login_required, current_user
from forms import Freezer
from app.models import Primers, Users, Boxes, Freezers
from app.primers import s


freezer = Blueprint('freezer', __name__, template_folder='templates')

@freezer.route('/view', methods=['GET', 'POST'])
@login_required
def view_freezers(message=None,modifier=None):
    freezers = Freezers.query.all()
    return render_template('view_freezers.html',freezers=freezers,message=message,modifier=modifier)

@freezer.route('/detail/<int:freezer_id>', methods=['GET', 'POST'])
@login_required
def view_freezer_detail(freezer_id,message=None,modifier=None):
    freezer = Freezers.query.filter_by(id=freezer_id).first()
    boxes = Boxes.query.filter_by(freezer_id=freezer_id).all()
    return render_template('view_freezer_detail.html',freezer=freezer,message=message,modifier=modifier,boxes=boxes)


@freezer.route('/add', methods=['GET', 'POST'])
@login_required
def add_freezer():
    form = Freezer()
    if request.method == 'POST':

        f = Freezers()
        f.name = request.form['name']
        f.location = request.form['location']
        print current_user.database_id
        f.user = current_user.database_id

        s.add(f)
        s.commit()
        return redirect(url_for('freezer.view_freezer_detail',freezer_id=f.id))
    else:
        return render_template('add_freezer.html',form=form)
