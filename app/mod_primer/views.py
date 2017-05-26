from flask import Blueprint
from flask import render_template, request, url_for, redirect, send_file, session
from flask.ext.login import login_required, current_user
from app.views import admin_required
from forms import Primer, Receive, Search, BulkPrimer, Comment
from app.models import Primers, Users, Boxes, Aliquots, Applications, SavedCarts, Pairs, Comments
from app.primers import s
from sqlalchemy.orm import noload
from Bio.SeqUtils import MeltingTemp as mt
from Bio.SeqUtils import GC
from Bio.Seq import Seq
import json
import time
import itertools
from app.mod_box.views import box_layout_calculator
import csv

primer = Blueprint('primer', __name__, template_folder='templates')
from sqlalchemy.sql import func, or_
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import os
import random


def get_user_by_username(s, username):
    user = s.query(Users).filter_by(username=username)
    for i in user:
        return i.id


@primer.context_processor
def utility_processor():
    def get_glyphicon(value):
        if value is not None and value != "":
            return '<span class="label label-success"><i class="glyphicon glyphicon-ok" aria-hidden="true"></i> YES</span>'
        else:
            return '<span class="label label-default"><i class="glyphicon glyphicon-remove" aria-hidden="true"></i> NO</span>'

    return dict(get_glyphicon=get_glyphicon)


@primer.context_processor
def utility_processor():
    def convert_orient(value):
        if value == 0:
            return 'F'
        if value == 1:
            return 'R'

    return dict(convert_orient=convert_orient)


def get_comments(primer_id=None, pair_id=None):
    comments = s.query(Comments).filter_by(primer_id=primer_id).filter_by(pair_id=None).all()
    return comments


@primer.route('/view', methods=['GET', 'POST'])
@login_required
@admin_required
def view_primers(message=None, modifier=None, ids=None):
    # primers = Primers.query.filter_by(current=1).all()
    primers = s.query(Primers, func.count(Aliquots.id)).outerjoin(Aliquots).filter(Primers.current == 1).group_by(
        Primers).all()
    return render_template('view_primers.html', primers=primers, message=message, modifier=modifier)


@primer.route('/view/pairs', methods=['GET', 'POST'])
@login_required
@admin_required
def view_pairs(message=None, modifier=None, ids=None):
    # pairs= s.query(Primers).with_entities(Primers.id,Primers.alias,Primers.sequence,Primers.box_id,Primers.row,Primers.column,Primers.pair_id).group_by(Primers.pair_id).all()
    pairs = s.query(Pairs).all()

    return render_template('view_pairs.html', pairs=pairs, message=message, modifier=modifier)


@primer.route('/detail/<int:primer_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def view_primer_detail(primer_id, message=None, modifier=None):
    # primer = s.query(Primers).join(Users).filter(Primers.id==primer_id).first()
    primer = Primers.query.filter_by(id=primer_id).first()
    # primer = Primers.query.join(Users).filter_by(id=primer_id).first()

    pairs = Pairs.query.filter(or_(Pairs.forward == primer_id, Pairs.reverse == primer_id)).first()

    if pairs:
        if pairs.forward == primer_id:
            primer_pair = Primers.query.filter_by(id=pairs.reverse).first()
        else:
            primer_pair = Primers.query.filter_by(id=pairs.forward).first()
    else:
        primer_pair = None

    seq = Seq(primer.sequence)
    gc = '%0.2f' % GC(seq)
    mt_wallace = '%0.2f' % mt.Tm_Wallace(seq)
    mt_gc = '%0.2f' % mt.Tm_GC(seq)
    mt_nn = '%0.2f' % mt.Tm_NN(seq)

    archive = s.query(Primers).filter_by(alias=primer.alias).filter_by(current=0).filter(Primers.id != primer_id).all()
    aliquots = s.query(Aliquots).filter_by(primer_id=primer_id).all()

    comment_form = Comment()
    comment_form.object_id.data = primer_id
    comments = get_comments(primer_id=primer_id)

    return render_template('view_primer_detail.html', primer_pair=primer_pair, pairs=pairs, archive=archive,
                           aliquots=aliquots, primer=primer, message=message, modifier=modifier, mt_wallace=mt_wallace,
                           mt_gc=mt_gc, mt_nn=mt_nn, gc=gc, comments=comments, comment_form=comment_form)


@primer.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_primer():
    form = Primer()
    if request.method == 'POST':
        if 'm13' in request.form:
            if request.form['orientation'] == "F":
                tag = 'CACGACGTTGTAAAACGAC'
            else:
                tag = 'CAGGAAACAGCTATGACC'
            sequence = tag + request.form['sequence']
        else:
            sequence = request.form['sequence']

        p = Primers()
        p.alias = request.form['alias']
        p.sequence = sequence
        p.orientation = request.form['orientation']
        p.application = request.form['application']
        p.date_designed = request.form['dt']
        p.scale = request.form['scale']
        p.service = request.form['service']
        p.mod_5 = request.form['mod_5']
        p.mod_3 = request.form['mod_3']

        p.user_designed = get_user_by_username(s, current_user.id)
        p.current = 1

        s.add(p)
        s.commit()

        if request.form["pair_id"]:
            a = Pairs()
            if request.form['orientation'] == "F":
                a.forward = p.id
                a.reverse = request.form['pair_id']
            else:
                a.forward = request.form['pair_id']
                a.reverse = p.id

            s.add(a)
            s.commit()

            update = {}
            update["pair_id"] = a.id
            s.query(Primers).filter_by(id=p.id).update(update)
            s.query(Primers).filter_by(id=request.form['pair_id']).update(update)
            s.commit()

        return redirect(url_for('primer.view_primer_detail', primer_id=p.id))
    else:
        if "pair_id" in request.args:
            form.orientation.default = 1
            form.process()
            form.pair_id.data = request.args["pair_id"]

            # need to disable orientation radio here - or just hide it?

        applications = [(row.id, row.name) for row in Applications.query.all()]
        form.application.choices = applications

        return render_template('add_primer.html', form=form)


@primer.route('/bulk_add', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_add():
    if request.method == 'POST':

        print request.form["data"]
        data = request.form["data"].rstrip().split("\n")
        primers = []
        for d in data:
            if d is not None:
                disease, name, empty0, sequence, empty1, empty2, empty3, empty4, comment, user, empty5, chrom, start, end, alias = d.split(
                    "\t")

                p = Primers()

                p.alias = alias.rstrip().strip()
                p.chrom = chrom
                p.position = start
                p.sequence = sequence.replace(" ", "")
                p.date_designed = time.strftime("%Y-%m-%d")
                p.user_designed = get_user_by_username(s, current_user.id)
                p.current = 1

                s.add(p)
                s.commit()
                primers.append(p.id)

        primers_info = s.query(Primers).filter(Primers.id.in_(primers))

        return render_template('bulk_process.html', primers_info=primers_info)


    else:
        form = BulkPrimer()
        return render_template('bulk_add.html', form=form)


@primer.route('/bulk_process', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_process():
    ids = request.form.getlist("id")
    pairs = request.form.getlist("pair")
    orients = request.form.getlist("orientation")

    for id, pair, orient in itertools.izip(ids, pairs, orients):

        update = {"orientation": int(orient)}
        s.query(Primers).filter_by(id=int(id)).update(update)

        # deal with pairs then update everything else
        pids = [int(id), int(pair)]
        count = s.query(Pairs).filter(Pairs.forward.in_(pids)).filter(Pairs.reverse.in_(pids)).count()
        if count == 0:
            p = Pairs()
            if orient == 0:
                p.forward = int(id)
                p.reverse = int(pair)
            else:
                p.reverse = int(pair)
                p.forward = int(id)

            s.add(p)
            s.commit()

            pair_id = p.id
            update = {"pair_id": pair_id}
            s.query(Primers).filter_by(id=int(id)).update(update)
            s.query(Primers).filter_by(id=int(pair)).update(update)
            s.commit()


@primer.route('/receive', methods=['GET', 'POST'])
@login_required
@admin_required
def receive_primer():
    form = Receive()
    primers_awaiting_receipt = [(row.id, row.alias) for row in Primers.query.filter_by(date_received=None).all()]
    form.primer.choices = primers_awaiting_receipt
    if request.method == 'POST':

        primer_id = request.form['primer']

        update = {}
        update["lot_no"] = request.form['lot_no']
        update["date_received"] = request.form['dt_received']
        update["user_received"] = get_user_by_username(s, current_user.id)
        print update
        print s.query(Primers).filter_by(id=primer_id).update(update)
        s.commit()
        return redirect(url_for('primer.receive_primer', message="Primer marked as received", modifier='success'))

    else:
        if len(primers_awaiting_receipt) > 0:
            if 'message' in request.args:
                return render_template('receive_primer.html', form=form, message=request.args['message'],
                                       modifier=request.args['modifier'])
            else:
                return render_template('receive_primer.html', form=form)
        else:
            return view_primers(message="All primers marked as received", modifier="success")


@primer.route('/reorder/<int:primer_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reorder_primer(primer_id):
    update = {"current": 0}
    s.query(Primers).filter_by(id=primer_id).update(update)
    s.commit()

    to_copy = s.query(Primers).filter_by(id=primer_id).first()
    dict_data = to_copy.to_dict()
    to_delete = ["worklist", "user_received", "date_received", "user_ordered", "date_ordered", "user_acceptance",
                 "date_acceptance", "user_reconstituted", "date_reconstituted", "lot_no", "concentration", "id", "row",
                 "column"]

    dict_data["lot_no"] = None
    dict_data["current"] = 1

    for i in dict_data:
        if "rel" in i:
            to_delete.append(i)

    for i in to_delete:
        # dict_data.pop(i, None)
        del dict_data[i]

    print json.dumps(dict_data, indent=4)

    p = Primers(**dict_data)
    s.add(p)
    s.commit()

    if dict_data["orientation"] == 0:
        pair_update = {"forward": p.id}
    else:
        pair_update = {"reverse": p.id}

    s.query(Pairs).filter_by(id=dict_data["pair_id"]).update(pair_update)
    s.commit()

    return redirect(url_for('primer.view_primer_detail', primer_id=p.id))


@primer.route('/bulk_check', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_check():
    if request.method == 'POST':
        for id in request.form:
            s.query(Primers).filter_by(id=int(id)).update(
                {"user_checked": get_user_by_username(s, current_user.id), "date_checked": time.strftime("%Y-%m-%d")})

        s.commit()
        return view_primers(message="Primers Marked as Checked", modifier="success")
    else:
        ids = request.args['ids'].split(",")
        primers = s.query(Primers).filter(Primers.id.in_(ids)).filter_by(user_checked=None).filter_by(current=1).all()
        if len(primers) == 0:
            return view_primers(message="No Eligable Primers Selected For Checking", modifier="danger")
        else:
            return render_template('bulk_check.html', primers=primers)


@primer.route('/bulk_receive', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_receive():
    if request.method == 'POST':
        ids = request.form.getlist("id")
        lot_nos = request.form.getlist("lot_no")
        date_receiveds = request.form.getlist("date_received")
        for id, lot_no, date_received in itertools.izip(ids, lot_nos, date_receiveds):
            s.query(Primers).filter_by(id=int(id)).update(
                {"lot_no": lot_no, "user_received": get_user_by_username(s, current_user.id),
                 "date_received": date_received})
        s.commit()
        return view_primers(message="Primers Marked as Received", modifier="success")
    else:
        ids = request.args['ids'].split(",")
        primers = s.query(Primers).filter(Primers.id.in_(ids)).filter(Primers.user_ordered != None).filter_by(
            user_received=None).filter_by(current=1).all()
        if len(primers) == 0:
            return view_primers(message="No Eligable Primers Selected For Receipt", modifier="danger")
        else:
            return render_template('bulk_receive.html', primers=primers, today=time.strftime("%Y-%m-%d"))


@primer.route('/bulk_reconstitute', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_reconstitute():
    if request.method == 'POST':
        ids = request.form.getlist("id")
        concs = request.form.getlist("conc")
        locs = request.form.getlist("box")
        date_recons = request.form.getlist("date_reconstituted")
        print ids
        print concs
        print locs
        print date_recons
        for id, conc, loc, date_recon in itertools.izip(ids, concs, locs, date_recons):
            box_name, row, column = loc.split("|")
            id_query = s.query(Boxes).filter_by(name=box_name).first()

            print id

            s.query(Primers).filter_by(id=int(id)).update({"box_id": id_query.id, "row": row, "column": column,
                                                           "user_reconstituted": get_user_by_username(s,
                                                                                                      current_user.id),
                                                           "date_reconstituted": date_recon})
        s.commit()
        return view_primers(message="Primers Marked as Reconstituted", modifier="success")
    else:

        ids = request.args['ids'].split(",")
        primers = s.query(Primers).filter(Primers.id.in_(ids)).filter(Primers.user_received != None).filter_by(
            user_reconstituted=None).filter_by(current=1).all()
        if len(primers) == 0:
            return view_primers(message="No Eligable Primers Selected For Reconstitution", modifier="danger")
        else:

            boxes = s.query(Boxes).all()

            empty = []

            for i in boxes:
                box = box_layout_calculator(i)
                if box["percent_full"] != 100:
                    for row in box["box_layout"]:
                        for column in box["box_layout"][row]:
                            if column != 0 and row != 0 and box["box_layout"][row][column] == "Empty":
                                empty.append(i.name + "|" + str(row) + "|" + str(column))

            return render_template('bulk_reconstitute.html', primers=primers, today=time.strftime("%Y-%m-%d"),
                                   boxes=empty)


@primer.route('/bulk_at', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_at():
    if request.method == 'POST':
        ids = request.form.getlist("id")
        worklists = request.form.getlist("worklist")
        date_ats = request.form.getlist("date_at")
        for id, worklist, date_at in itertools.izip(ids, worklists, date_ats):
            s.query(Primers).filter_by(id=int(id)).update(
                {"worklist": worklist, "user_acceptance": get_user_by_username(s, current_user.id),
                 "date_acceptance": date_at})
        s.commit()
        return view_primers(message="Primers Marked as Acceptance Tested", modifier="success")
    else:
        ids = request.args['ids'].split(",")
        primers = s.query(Primers).filter(Primers.id.in_(ids)).filter(Primers.user_reconstituted != None).filter_by(
            user_acceptance=None).filter_by(current=1).all()
        if len(primers) == 0:
            return view_primers(message="No Eligable Primers Selected For Acceptance Testing", modifier="danger")
        else:
            return render_template('bulk_at.html', primers=primers, today=time.strftime("%Y-%m-%d"))


@primer.route('/bluk_aliquot', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_aliquot():
    if request.method == 'POST':
        ids = request.form.getlist("id")
        aliquot_counts = request.form.getlist("aliquots")
        date_aliquoteds = request.form.getlist("date_aliquoted")
        aliquot_ids = []
        for id, aliquot_count, date_aliquoted in itertools.izip(ids, aliquot_counts, date_aliquoteds):
            for i in range(0, int(aliquot_count)):
                a = Aliquots()
                a.primer_id = id
                a.date_aliquoted = date_aliquoted
                a.user_aliquoted = get_user_by_username(s, current_user.id)
                s.add(a)
                s.commit()
                aliquot_ids.append(a.id)

        print aliquot_ids
        aliquots = s.query(Aliquots).filter(Aliquots.id.in_(aliquot_ids)).all()

        boxes = s.query(Boxes).all()

        empty = []

        for i in boxes:
            box = box_layout_calculator(i)
            if box["percent_full"] != 100:
                for row in box["box_layout"]:
                    for column in box["box_layout"][row]:
                        if column != 0 and row != 0 and box["box_layout"][row][column] == "Empty":
                            empty.append(i.name + "|" + str(row) + "|" + str(column))

        return render_template('place_aliquots.html', aliquots=aliquots, boxes=empty)
        # return view_primers(message="Primers Marked as Aliquoted",modifier="success")
    else:
        ids = request.args['ids'].split(",")
        primers = s.query(Primers).filter(Primers.id.in_(ids)).filter(Primers.user_acceptance != None).filter_by(
            current=1).all()
        if len(primers) == 0:
            return view_primers(message="No Eligable Primers Selected For Aliquoting", modifier="danger")
        else:
            return render_template('bulk_aliquot.html', primers=primers, today=time.strftime("%Y-%m-%d"))


@primer.route('/place_aliquot', methods=['GET', 'POST'])
@login_required
@admin_required
def place_aliquot():
    if request.method == 'POST':
        ids = request.form.getlist("id")
        boxes = request.form.getlist("box")
        for id, loc in itertools.izip(ids, boxes):
            box_name, row, column = loc.split("|")
            id_query = s.query(Boxes).filter_by(name=box_name).first()
            s.query(Aliquots).filter_by(id=int(id)).update({"box_id": id_query.id, "row": row, "column": column})
        s.commit()
        return view_primers(message="Aliquots Created and Stored!", modifier="success")


@primer.route('/order', methods=['GET', 'POST'])
@login_required
@admin_required
def order():
    if 'ids' in request.args:
        ids = request.args['ids'].split(",")
        primers = s.query(Primers).filter(Primers.id.in_(ids)).filter_by(current=1).all()

        output = []

        for primer in primers:
            p = primer.to_dict()
            line = []
            line.append(p["alias"])
            line.append(p["mod_5"])
            line.append(p["sequence"])
            line.append(p["mod_3"])
            line.append(p["scale"])
            line.append(p["purification"])
            line.append(p["service"])

            output.append(line)

        filename = time.strftime("%Y-%m-%d") + "_primer_order_" + current_user.id + ".csv"

        with open("/tmp/" + filename, "wb") as f:
            writer = csv.writer(f)
            writer.writerows(output)

        f.close()

        for id in ids:
            s.query(Primers).filter_by(id=int(id)).update(
                {"user_ordered": get_user_by_username(s, current_user.id), "date_ordered": time.strftime("%Y-%m-%d")})
        s.commit()

        return send_file('/tmp/' + filename, as_attachment=True)


    else:
        primers = Primers.query.filter_by(current=1).filter(Primers.user_checked != None).filter(
            Primers.user_ordered == None).all()
        return render_template('order_primers.html', primers=primers, message='', modifier='')


@primer.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    form = Search()
    if request.method == 'POST':
        if request.form["barcode"] != "":
            raw = request.form["barcode"]
            print raw
            search = int(raw[:-1])
            results = s.query(Primers).filter_by(id=search).all()
        if request.form["term"] != "":
            search = request.form["term"]
            results = Primers.query.whoosh_search(search).filter_by(current=1).group_by(Primers).all()

        return render_template('search_primers.html', form=form, primers=results, request=request, term=search)

    else:
        return render_template('search_primers.html', form=form, request=request)


@primer.route("/cart", methods=['GET', 'POST'])
@login_required
def cart():
    if 'ids' in request.args:
        ids = request.args['ids'].split(",")
        print session
        for id in ids:
            if 'cart' in session:
                # If the product is not in the cart, then add it.
                if not any(id in d for d in session['cart']):
                    session['cart'].append(id)
                else:
                    return view_primers(message="Primer Already in Cart!", modifier="warning")
            else:
                # In this block, the user has not started a cart, so we start it for them and add the product.
                session['cart'] = [id]

        return view_primers(message=str(len(ids)) + " Primer(s) Added to Cart!", modifier="success")

    else:
        ids = session['cart']
        return view_cart(ids=ids)

    primer.route("/cart", methods=['GET', 'POST'])


@primer.route("/cart/clear", methods=['GET', 'POST'])
@login_required
def clear_cart():
    session['cart'] = []
    return redirect(url_for('primer.view_cart'))


@primer.route("/cart/remove", methods=['GET', 'POST'])
@login_required
def remove_from_cart():
    new_cart = []
    if 'ids' in request.args:
        ids = request.args['ids'].split(",")
        for id in session["cart"]:
            if id not in ids:
                new_cart.append(id)
        session["cart"] = new_cart

    return redirect(url_for('primer.view_cart'))


@primer.route('/cart/view', methods=['GET', 'POST'])
@login_required
@admin_required
def view_cart(message=None, modifier=None, ids=None):
    if "cart" in session:
        if len(session["cart"]) > 0:
            primers = s.query(Primers, func.count(Aliquots.id)).outerjoin(Aliquots).filter(
                Primers.id.in_(session["cart"])).filter(
                Primers.current == 1).group_by(
                Primers).all()
        else:
            primers = []
    else:
        primers = []

    return render_template('view_cart.html', primers=primers, message=message, modifier=modifier)


@primer.route('/cart/view_saved', methods=['GET', 'POST'])
@login_required
@admin_required
def view_saved_cart(message=None, modifier=None, name=None):
    primers = s.query(Primers, func.count(Aliquots.id)).outerjoin(Aliquots).filter(
        Primers.id.in_(request.args['ids'])).filter(
        Primers.current == 1).group_by(
        Primers).all()

    return render_template('view_saved_cart.html', primers=primers, message=message, modifier=modifier,
                           name=request.args['name'])


@primer.route('/cart/deleted_saved_cart', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_saved_cart(message=None, modifier=None, name=None):
    SavedCarts.query.filter_by(name=request.form['name']).delete()
    s.commit()

    return redirect(url_for('index'))


@primer.route('/cart/save', methods=['GET', 'POST'])
@login_required
@admin_required
def save_cart(message=None, modifier=None, ids=None):
    if request.method == 'POST':
        if "cart" in session:
            if len(session["cart"]) > 0:
                c = SavedCarts()
                c.name = request.form["name"]
                c.date = time.strftime("%Y-%m-%d")
                c.user = get_user_by_username(s, current_user.id)
                c.ids = session["cart"]
                s.add(c)
                s.commit()
                return view_cart(message='Cart "' + c.name + '" Saved!', modifier='success')
            else:
                return view_cart()
        else:
            return view_cart()


@primer.route('/picklist', methods=['GET', 'POST'])
@login_required
@admin_required
def print_pick_list(ids=None):
    location = os.path.dirname(os.path.dirname(__file__))
    if 'ids' in request.args:
        ids = request.args['ids'].split(",")
    elif ids is not None:
        ids = ids
    primers = s.query(Primers, func.count(Aliquots.id)).outerjoin(Aliquots).filter(
        Primers.id.in_(ids)).filter(
        Primers.current == 1).group_by(
        Primers).all()

    iw = ImageWriter()
    for i in primers:
        print i[0].id

        ean = barcode.codex.Code39(str(i[0].id), add_checksum=True, writer=iw)
        ean.default_writer_options['module_height'] = 2.0
        ean.default_writer_options['module_width'] = 0
        ean.default_writer_options['text_distance'] = 3
        ean.default_writer_options['font_size'] = 0
        file = ean.save(location + '/static/tmp/' + str(i[0].id))
        # im = Image.open(file)
        # im.resize((150,120)).save(location+'/static/tmp/'+str(i[0].id)+"_resized.png")
        # print file

    return render_template('pick_list_print.html', user=current_user.id, date=time.strftime("%Y-%m-%d"),
                           time=time.strftime("%H:%M"), primers=primers, location=location)


@primer.route('/mark_as_pair', methods=['GET', 'POST'])
@login_required
@admin_required
def mark_as_pair():
    if 'ids' in request.args:
        ids = request.args['ids'].split(",")
        if len(ids) < 3 and len(ids) > 1:
            print ids
            # todo make this make the primers a pair

            # 1st find out which is F and which is R

            primer = s.query(Primers).filter(Primers.id == ids[0]).first()
            p = Pairs()
            if primer.orientation == 0:
                p.forward = int(ids[0])
                p.reverse = int(ids[1])
            else:
                p.reverse = int(ids[0])
                p.forward = int(ids[1])

            s.add(p)

            try:
                s.commit()
                pair_id = p.id
                update = {"pair_id": pair_id}
                for id in ids:
                    s.query(Primers).filter_by(id=int(id)).update(update)
                    s.commit()
                return view_primers(message="Primers Marked as Pair", modifier="success")
            except:
                s.rollback()
                return view_primers(message="<strong>Warning!</strong> Are the primers already part of a pair?",
                                    modifier="danger")

        else:
            return view_primers(message="<strong>Warning!</strong> You need to select 2 primers to make a pair!",
                                modifier="danger")


@primer.route('/audit', methods=['GET', 'POST'])
@login_required
@admin_required
def audit():
    primers = s.query(Primers).filter_by(current=1).all()

    ids = []
    for i in primers:
        ids.append(i.id)
    random.shuffle(ids)

    return print_pick_list(ids=ids[0:20])


@primer.route('/add_comment', methods=['GET', 'POST'])
@login_required
@admin_required
def add_comment():
    c = Comments()
    c.comment = request.form["comment"]
    c.primer_id = int(request.form["object_id"])
    c.date = time.strftime("%Y-%m-%d %H:%M")
    c.user_id = get_user_by_username(s, current_user.id)
    s.add(c)
    s.commit()

    return redirect(request.referrer)
