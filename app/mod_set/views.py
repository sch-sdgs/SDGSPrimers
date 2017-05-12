from flask import Blueprint
from flask import render_template, request, url_for, redirect
from flask.ext.login import login_required, current_user
from app.views import admin_required
from app.models import Primers, Users, Sets, SetMembers
from app.primers import s
from forms import Add, Choose
import time
from sqlalchemy import func

set = Blueprint('set', __name__, template_folder='templates')

def get_user_by_username(s, username):
    user = s.query(Users).filter_by(username=username)
    for i in user:
        return i.id

@set.route('/view', methods=['GET', 'POST'])
@login_required
@admin_required
def view_sets(message=None,modifier=None):
    #sets = Sets.query.all()

    sets = s.query(Sets, func.count(SetMembers.id)).outerjoin(SetMembers).filter(Sets.current == 1).group_by(Sets).all()
    print sets
    return render_template('view_sets.html',sets=sets,message=message,modifier=modifier)

@set.route('/detail/<int:set_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def view_set_detail(set_id,message=None,modifier=None):
    set = Sets.query.filter_by(id=set_id).first()
    members = SetMembers.query.filter_by(set_id=set_id).all()
    return render_template('view_set_detail.html',set=set,members=members,message=message,modifier=modifier)

@set.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_set(message=None,modifier=None):
    form = Add()
    if request.method == 'POST':

        se = Sets()
        se.name = request.form['name']
        se.date = time.strftime("%Y-%m-%d")
        se.user = get_user_by_username(s, current_user.id)
        se.current = 1

        s.add(se)
        s.commit()
        return redirect(url_for('set.view_set_detail', set_id=se.id))
    else:
        return render_template('add_set.html', form=form)




@set.route('/add_members', methods=['GET', 'POST'])
@login_required
@admin_required
def add_members(message=None,modifier=None):
    form = Choose()
    if request.method == 'POST':
        ids = request.args['ids'].split(",")

        for id in ids:
            if s.query(SetMembers).filter_by(primer_id=id).filter_by(set_id=request.form["set"]).count() == 0:
                sm = SetMembers()
                sm.set_id = request.form["set"]
                sm.primer_id = id
                sm.user = get_user_by_username(s, current_user.id)

                s.add(sm)
        s.commit()
        return redirect(url_for('set.view_set_detail', set_id=request.form["set"]))
    else:
        ids = request.args['ids'].split(",")
        sets = [(row.id, row.name) for row in Sets.query.filter_by(current=1).all()]
        form.set.choices = sets
        return render_template('choose_set.html', form=form, ids=ids)




@set.route('/add_to_cart', methods=['GET', 'POST'])
@login_required
@admin_required
def add_set_to_cart():
    ids = request.args['ids'].split(",")
    primer_ids = []
    for id in ids:
        members=s.query(SetMembers).filter_by(set_id=id).all()
        for primer in members:
            primer_ids.append(str(primer.primer_id))

    print primer_ids

    return redirect(url_for('primer.cart')+"?ids="+",".join(primer_ids))
