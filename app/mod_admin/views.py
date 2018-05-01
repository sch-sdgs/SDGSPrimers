from collections import OrderedDict

from flask import Blueprint
from flask import render_template, request, url_for, redirect
from flask.ext.login import login_required, current_user

from app.primers import s
from app.views import admin_permission
from flask_table import Table, Col, LinkCol
from forms import *
from app.models import *
from app.activedirectory import UserAuthentication
import time

class ItemTableUsers(Table):
    username = Col('User')
    admin = Col('Admin')
    toggle_admin = LinkCol('Toggle Admin', 'admin.toggle_admin', url_kwargs=dict(id='id'))

class ItemTableApplications(Table):
    name = Col('Name')
    paired = Col('Paired')
    #toggle_admin = LinkCol('Toggle Admin', 'admin.toggle_admin', url_kwargs=dict(id='id'))



class ItemTableLocked(Table):
    name = Col('Panel')
    username = Col('Locked By')
    toggle_lock = LinkCol('Toggle Lock', 'admin.toggle_locked', url_kwargs=dict(id='id'))


admin = Blueprint('admin', __name__, template_folder='templates')


def convertTimestampToSQLDateTime(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))


# ajax methods
@admin.route('/get_user_details', methods=['GET', 'POST'])
@admin_permission.require(http_exception=401)
def get_user_details():
    """
    gets user details form active directory based on the username
    :return: json of the results
    """
    username = request.args["username"]
    u = UserAuthentication().get_user_detail_from_username(username)
    return jsonify(u);


@admin.route('/')
@admin_permission.require(http_exception=401)
def index():
    """
    shows the admin homepage
    :return: template admin.html
    """
    return render_template("admin.html")


@admin.route('/users/view', methods=['GET', 'POST'])
@admin_permission.require(http_exception=401)
def users_view():
    """
    view all users in the database - roles control how much info you can see
    :return: template users_view.html
    """
    users = s.query(Users).all()
    data = []
    for user in users:
        roles = s.query(UserRoleRelationship).join(UserRolesRef).filter(UserRoleRelationship.user_id == user.id).all()
        user_dict = dict(user)
        user_dict["staff_no"] = user.staff_no

        user_dict["roles"] = []
        for i in roles:
            user_dict["roles"].append(i.userrole_id_rel.role)

        data.append(user_dict)

    return render_template("users_view.html", data=data)


@admin.route('/users/toggle_active/<id>', methods=['GET', 'POST'])
@admin_permission.require(http_exception=401)
def users_toggle_active(id=None):
    """
    toggles user active or not in database

    :param id: database user id
    :return: template users_view.html
    """
    user = s.query(Users).filter_by(id=id).first()
    if user.active == True:
        s.query(Users).filter_by(id=id).update({'active': False})
    elif user.active == False:
        s.query(Users).filter_by(id=id).update({'active': True})
    s.commit()
    return redirect(url_for('admin.users_view'))


@admin.route('/users/add', methods=['GET', 'POST'])
@admin_permission.require(http_exception=401)
def users_add():
    """
    adds a user to the database

    :return: either GET: template users_add.html (or) POST: template users_view.html
    """
    form = UserForm()
    if request.method == 'POST':
        now = datetime.datetime.now()



        u = Users(login=request.form["username"],
                  first_name=request.form["firstname"],
                  last_name=request.form["surname"],
                  email=request.form["email"],
                  band=0,
                  staff_no=request.form["staff_no"],
                  active=True)

        print u.date_created

        s.add(u)
        s.commit()
        print request.form.getlist('userrole')
        for role_id in request.form.getlist('userrole'):
            urr = UserRoleRelationship(userrole_id=int(role_id), user_id=u.id)
            s.add(urr)

        s.commit()
        return redirect(url_for('admin.users_view'))

    return render_template("users_add.html", form=form)


@admin.route('/users/edit/<id>', methods=['GET', 'POST'])
@admin_permission.require(http_exception=401)
def users_edit(id=None):
    """
    edit user details

    :param id: user id
    :return: either GET: template users_edit.html (or) POST: template users_view.html
    """
    if request.method == 'GET':
        form = UserEditForm()

        user = s.query(Users).filter_by(id=id).first()
        form.username.data = user.login
        form.firstname.data = user.first_name
        form.surname.data = user.last_name
        form.email.data = user.email
        form.staff_no.data = user.staff_no


        userrole_ids = [name for (name,) in s.query(UserRoleRelationship.userrole_id).filter_by(user_id=id).all()]

        form.userrole.choices = s.query(UserRolesRef.id, UserRolesRef.role).all()
        form.userrole.process_data(userrole_ids)

        return render_template("users_edit.html", id=id, form=form)

    if request.method == 'POST':

        s.query(UserRoleRelationship).filter_by(user_id=id).delete()

        for role_id in request.form.getlist('userrole'):
            urr = UserRoleRelationship(userrole_id=int(role_id), user_id=id)
            s.add(urr)

        s.commit()

        if "staff_no" in request.form:
            staff_no = request.form["staff_no"]
            print "HELLO"
        else:
            staff_no = s.query(Users).filter_by(id=id).first().staff_no

        data = {
            'login': request.form["username"],
            'first_name': request.form["firstname"],
            'last_name': request.form["surname"],
            'email': request.form["email"],
            'staff_no': staff_no
        }

        s.query(Users).filter_by(id=id).update(data)

        s.commit()

        return redirect(url_for('admin.users_view'))


@admin.route('/userroles', methods=['GET', 'POST'])
@admin_permission.require(http_exception=401)
def userroles():
    """
    administer user roles - these are the role of the user on stardb e.g. "ADMIN", "USER" etc
    you can only add or change these with overall code changes
    :return:
    """
    form = UserRoleForm()

    if request.method == 'POST':
        u = UserRolesRef(role=request.form["role"])
        s.add(u)
        s.commit()

    user_roles = s.query(UserRolesRef).all()

    return render_template("userroles.html", form=form, data=user_roles)


@admin.route('/userroles/edit/<id>', methods=['GET', 'POST'])
@admin_permission.require(http_exception=401)
def userroles_edit(id=None):
    form = UserRoleForm()
    user_role = s.query(UserRolesRef).filter_by(id=id).first()
    form.role.data = user_role.role

    if request.method == 'POST':
        s.query(UserRolesRef).filter_by(id=id).update({'role': request.form["role"]})
        s.commit()
        return redirect(url_for('admin.userroles'))

    return render_template("userroles_edit.html", form=form, id=id)


@admin.route('/userroles/delete/<id>', methods=['GET', 'POST'])
@admin_permission.require(http_exception=401)
def deleterole(id=None):
    s.query(UserRolesRef).filter_by(id=id).delete()

    s.commit()

    return redirect(url_for('admin.userroles'))






@admin.route('/logs', methods=['GET', 'POST'])
@login_required
def view_logs():
    """
    view admin logs so that you can see what users have been doing

    :return: render hmtl template
    """
    if request.args.get('file'):
        log = request.args.get('file')
    else:
        log = 'PanelPal.log'

    import glob
    files = []
    listing = glob.glob('*log*')
    for filename in listing:
        files.append(filename)

    result = []
    with open(log) as f:
        for line in f:
            result.append(line.rstrip())

    return render_template('logs.html', log=result, files=files)


@admin.route('/application', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=401)
def application_admin():
    """
    view to allow users to be added and admin rights toggled

    :return: render html template
    """
    form = ApplicationsForm()
    message = None
    if request.method == 'POST':
        name = request.form["name"]

        a = Applications()
        a.name = name
        if "paired" in request.form:
            a.paired = 1
        else:
            a.paired = 0
        s.add(a)
        s.commit()
        message = "Added Application: " + name
        
    applications = s.query(Applications).all()
    result = []
    for i in applications:
        result.append(i.to_dict())
    table = ItemTableApplications(result, classes=['table', 'table-striped'])
    return render_template('applications.html', form=form, table=table, message=message)
