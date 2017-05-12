from flask import Blueprint
from flask import render_template, request, url_for, redirect
from flask.ext.login import login_required, current_user
from app.views import admin_required
from forms import Box, Fill
from app.models import Primers, Users, Boxes, Freezers
from app.primers import s



box = Blueprint('box', __name__, template_folder='templates')

def get_user_by_username(s, username):
    user = s.query(Users).filter_by(username=username)
    for i in user:
        return i.id

def box_layout_calculator(box):
    box_layout = {}
    box_layout[0] = {}

    for column in range(0, box.columns + 1):
        if column == 0:
            box_layout[0][column] = ""
        else:
            box_layout[0][column] = column

    total_primers = 0

    p = Primers.query.filter_by(box_id=box.id).filter_by(current=1).all()

    filled={}

    for primer in p:
        print primer
        print primer.row

        if primer.row not in filled:
            filled[primer.row]={}
        if primer.column not in filled[primer.row]:
            filled[primer.row][primer.column]=primer


    for row in range(1, box.rows + 1):
        box_layout[row] = {}
        for column in range(0, box.columns + 1):
            if column == 0:
                box_layout[row][0] = row
            else:
                if row in filled:
                    if column in filled[row]:
                        box_layout[row][column] = filled[row][column]
                        total_primers += 1
                    else:
                        box_layout[row][column] = "Empty"
                else:
                    box_layout[row][column] = "Empty"

    total_spaces = box.rows * box.columns
    percent_full = (total_primers / float(total_spaces)) * 100

    return {"box_layout":box_layout,"percent_full":percent_full}

@box.route('/view', methods=['GET', 'POST'])
@login_required
@admin_required
def view_boxes(message=None,modifier=None):
    boxes_query = Boxes.query.all()
    boxes = []
    for i in boxes_query:
        j = i.to_dict()
        calculator = box_layout_calculator(i)

        j["percent_full"] = calculator["percent_full"]

        boxes.append(j)

    print boxes
    return render_template('view_boxes.html',boxes=boxes,message=message,modifier=modifier)

@box.route('/detail/<int:box_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def view_box_detail(box_id,message=None,modifier=None):
    box = Boxes.query.filter_by(id=box_id).first()

    calculator = box_layout_calculator(box)

    box_layout=calculator["box_layout"]
    percent_full = calculator["percent_full"]

    return render_template('view_box_detail.html',box=box,percent_full='%0.1f' % percent_full,message=message,modifier=modifier,box_layout=box_layout)


@box.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_box():
    form = Box()
    if request.method == 'POST':

        b = Boxes()
        b.name = request.form['alias']
        b.columns = request.form['columns']
        b.rows = request.form['rows']
        b.user = get_user_by_username(s,current_user.id)
        b.freezer_id = request.form['freezer']
        b.aliquots = request.form['aliquots']
        s.add(b)
        s.commit()

        return redirect(url_for('box.view_box_detail',box_id=b.id))
    else:

        freezers = [(r.id, r.name) for r in Freezers.query.all()]
        form.freezer.choices = freezers

        return render_template('add_box.html',form=form)


@box.route('/fill/<int:box_id>/<int:row>/<int:column>', methods=['GET', 'POST'])
@login_required
@admin_required
def fill_box(box_id,row,column):
    form = Fill()

    if request.method == 'POST':

        update = {}
        update['row'] = row
        update['column'] = column
        update['box_id'] = box_id
        primer_id = request.form['primer']

        s.query(Primers).filter_by(id=primer_id).update(update)
        s.commit()
        return redirect(url_for('box.view_box_detail', box_id=box_id))

    else:

        primers_awaiting_reconstitution = [(r.id, r.alias) for r in Primers.query.filter(Primers.user_reconstituted!=None).all()]
        form.primer.choices = primers_awaiting_reconstitution
        print row
        print column
        print box_id
        return render_template('fill_box.html', form=form, box_id=box_id, column=column, row=row)



