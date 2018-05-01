from flask import render_template, request, url_for, jsonify, redirect, session, current_app
from flask_login import login_required, login_user, logout_user, LoginManager, UserMixin, \
    current_user
from app.activedirectory import UserAuthentication
from app.primers import s
from forms import *
from models import *
from flask_principal import Principal, Identity, AnonymousIdentity, \
    identity_changed, Permission, RoleNeed, UserNeed,identity_loaded

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

principals = Principal(app)

user_permission = Permission(RoleNeed('USER'))
admin_permission = Permission(RoleNeed('ADMIN'))
primer_admin_permission = Permission(RoleNeed('PRIMER_ADMIN'))

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

class User(UserMixin):
    def __init__(self, id, password=None):
        """
        user class to login the user and store useful information. Access attributes of this class with
        "current_user"

        :param id: user id
        :param password: password
        """
        self.id = id
        self.database_id = self.get_database_id()
        self.password = password
        self.roles = self.get_user_roles()
        self.full_name = self.get_full_name()

    def get_database_id(self):
        """
        gets the id of the row in the database for the user.
        :return: database id
        """
        query= s.query(Users).filter_by(login=self.id).first()
        if query:
            database_id = query.id
        else:
            database_id = None
        return database_id

    def get_user_roles(self):
        """
        gets the roles assigned to this user from the database i.e ADMIN, USER etc
        :return: list of user roles
        """
        result = []
        roles = s.query(UserRolesRef).join(UserRoleRelationship).join(Users).filter(Users.login == self.id).all()
        for role in roles:
            result.append(role.role)
        return result

    def get_full_name(self):
        """
        gets user full name given username, helpful for putting name on welcome pages etc
        :return: full name
        """
        user = s.query(Users).filter_by(login=self.id).first()
        full_name = user.first_name + " " + user.last_name
        return full_name


    def is_authenticated(self, id, password):
        """
        checks if user can authenticate with given user id and password. A user can authenticate if two conditions are met
         1. user is in the stardb database
         2. user credentils authenticate with active directory

        :param id: username
        :param password: password
        :return: True/False user is authenticated
        """
        user = s.query(Users).filter_by(login=id).all()
        if len(list(user)) == 0:
            return False
        else:
            check_activdir = UserAuthentication().authenticate(id, password)

        self.roles = []
        if check_activdir != "False":
            roles = s.query(UserRolesRef).join(UserRoleRelationship).join(Users).filter(Users.login == id).all()
            for role in roles:
                self.roles.append(role.role)
            print self.roles
            return True


        else:
            return False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            #identity.provides.add(RoleNeed(role.name))
            identity.provides.add(RoleNeed(role))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(401)
def custom_401(e):
    """
    handles 403 errors (no permission i.e. if not admin)
    :param e:
    :return: template login.html
    """
    session['redirected_from'] = request.url
    return render_template('403.html'), 403


@app.context_processor
def get_cart_count():
    print session
    if 'cart' in session:
        if session["cart"] is not None:
            return dict(cart_count=len(session["cart"]))
        else:
            dict(cart_count=0)
    else:
        return dict(cart_count=0)


@app.route('/')
def index():
    browser = request.user_agent.browser
    print browser
    designed = s.query(Primers).filter(Primers.date_designed != None).filter_by(current=1).count()
    unchecked = s.query(Primers).filter(Primers.user_checked == None).filter_by(current=1).count()
    ordering = s.query(Primers).filter(Primers.user_checked != None).filter_by(current=1).filter(Primers.user_ordered == None).count()
    on_order = s.query(Primers).filter(Primers.user_ordered != None).filter_by(current=1).filter(Primers.user_checked != None).filter(Primers.user_received == None).count()
    reconstitution = s.query(Primers).filter(Primers.user_received != None).filter_by(current=1).filter(Primers.user_reconstituted == None).count()
    at = s.query(Primers).filter(Primers.user_reconstituted != None).filter_by(current=1).filter(Primers.date_acceptance == None).count()
    try:
        carts = s.query(SavedCarts).filter(SavedCarts.user == current_user.database_id).all()
    except:
        carts = None


    return render_template('home.html',browser=browser,carts=carts,designed=designed,unchecked=unchecked,ordering=ordering,on_order=on_order,reconstitution=reconstitution,at=at)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    method to login user
    :return: either login.html or if successful the page the user was trying to access
    """
    form = Login(next=request.args.get('next'))
    if request.method == 'GET':
        return render_template("login.html", form=form)
    elif request.method == 'POST':
        user = User(form.data["username"], password=form.data["password"])
        result = user.is_authenticated(id=form.data["username"], password=form.data["password"])
        if result:
            login_user(user)
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.id))

            if form.data["next"] != "":
                return redirect(form.data["next"])
            else:
                return redirect(url_for('index'))
        else:
            return render_template("login.html", form=form, modifier="Oh Snap!", message="Wrong username or password")

@app.route('/logout')
@login_required
def logout():
    """
    method to logout the user
    :return: the login page
    """
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(request.args.get('next') or '/')

@app.route("/faq")
def faq():
    # todo unlock all users locked
    return render_template("faq.html")

