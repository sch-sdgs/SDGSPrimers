from flask import Blueprint
from flask import render_template, request, url_for, redirect, jsonify
from flask.ext.login import login_required, current_user
from forms import Box, Fill
from app.models import Primers, Users, Boxes, Freezers, Aliquots
from app.primers import s
import json


box = Blueprint('box', __name__, template_folder='templates')

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
    a = Aliquots.query.filter_by(box_id=box.id).all()
    print a
    filled={}
    if p:
        for primer in p:

            if primer.row not in filled:
                filled[primer.row]={}
            if primer.column not in filled[primer.row]:
                filled[primer.row][primer.column]={}
                filled[primer.row][primer.column]["primer"]=primer
                filled[primer.row][primer.column]["aliquot"] =False

    if a:
        for aliquot in a:

            if aliquot.row not in filled:
                filled[aliquot.row] = {}
            if aliquot.column not in filled[aliquot.row]:
                filled[aliquot.row][aliquot.column] = {}
                filled[aliquot.row][aliquot.column]["primer"] = s.query(Primers).filter_by(id=aliquot.primer_id).first()
                filled[aliquot.row][aliquot.column]["aliquot"] = True

    for row in range(1, box.rows + 1):
        box_layout[row] = {}
        for column in range(0, box.columns + 1):
            if column == 0:
                box_layout[row][0] = row
            else:
                if row in filled:
                    if column in filled[row]:
                        box_layout[row][column]={}
                        box_layout[row][column]["primer"] = filled[row][column]["primer"]
                        box_layout[row][column]["aliquot"] = filled[row][column]["aliquot"]
                        total_primers += 1
                    else:
                        box_layout[row][column] = {}
                        box_layout[row][column]["primer"] = "Empty"
                else:
                    box_layout[row][column] = {}
                    box_layout[row][column]["primer"] = "Empty"

    total_spaces = box.rows * box.columns
    percent_full = (total_primers / float(total_spaces)) * 100
    print box_layout
    return {"box_layout":box_layout,"percent_full":percent_full}

@box.route('/view', methods=['GET', 'POST'])
@login_required
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
def view_box_detail(box_id,message=None,modifier=None):
    box = Boxes.query.filter_by(id=box_id).first()

    calculator = box_layout_calculator(box)

    box_layout=calculator["box_layout"]
    percent_full = calculator["percent_full"]

    return render_template('view_box_detail.html',box=box,percent_full='%0.1f' % percent_full,message=message,modifier=modifier,box_layout=box_layout)


@box.route('/add', methods=['GET', 'POST'])
@login_required
def add_box():
    form = Box()
    if request.method == 'POST':

        b = Boxes()
        b.name = request.form['alias']
        b.columns = request.form['columns']
        b.rows = request.form['rows']
        b.user = current_user.database_id
        b.freezer_id = request.form['freezer']
        b.aliquots = request.form['aliquots']
        s.add(b)
        s.commit()

        return redirect(url_for('box.view_box_detail',box_id=b.id))
    else:

        freezers = [(r.id, r.name) for r in Freezers.query.all()]
        form.freezer.choices = freezers

        return render_template('add_box.html',form=form)

@box.route('/autocomplete', methods=['GET'])
@login_required
def autocomplete():
    search = request.args.get('q')
    query = s.query(Primers.alias).filter(Primers.alias.like('%' + str(search) + '%'))
    results = [mv[0] for mv in query.all()]
    print results
    return jsonify(matching_results=results)


@box.route('/fill/<int:box_id>/<int:row>/<int:column>', methods=['GET', 'POST'])
@login_required
def fill_box(box_id,row,column):
    form = Fill()

    if request.method == 'POST':

        update = {}
        update['row'] = row
        update['column'] = column
        update['box_id'] = box_id
        alias = request.form['primer']

        s.query(Primers).filter_by(alias=alias).update(update)
        s.commit()
        return redirect(url_for('box.view_box_detail', box_id=box_id))

    else:

        primers_awaiting_reconstitution = [(r.id, r.alias) for r in Primers.query.filter(Primers.user_reconstituted!=None).all()]
        form.primer.choices = primers_awaiting_reconstitution
        print row
        print column
        print box_id
        return render_template('fill_box.html', form=form, box_id=box_id, column=column, row=row)



