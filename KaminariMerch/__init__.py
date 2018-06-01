from os import path

from flask import Flask, render_template, redirect, session, request, jsonify, abort, url_for
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_qrcode import QRcode
from flask_htmlmin import HTMLMIN
from flask_socketio import SocketIO, join_room

from flask_security.utils import hash_password, verify_password
from flask_security import Security, SQLAlchemyUserDatastore, url_for_security, LoginForm, login_required, current_user

from KaminariMerch.models import User, Role, db, Post, Comment
from KaminariMerch.forms import DeleteAccountForm, PasswordResetForm
from KaminariMerch.views import PostView, CommentView

appdir = path.abspath(path.dirname(__file__))
imagedir = path.join(appdir, 'static/images')


def create_app(environment=None):

    app = Flask(__name__)
    app.config.from_object('config')
    app.config['ENVIRONMENT'] = environment

    # Wraps app in useful helpers.
    QRcode(app)
    HTMLMIN(app)

    # Initialize's database and user datastores.
    db.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore)

    # Sets up administration page.
    admin = Admin(
        app,
        'The Local Theatre Admin',
        index_view=PostView(Post, db.session, url='/admin'),
        template_mode='bootstrap3'
    )


    # Registers pages to the administration page.
    admin.add_link(MenuLink(name='Home', endpoint='store_page'))
    admin.add_view(CommentView(session=db.session, name='Comments', endpoint='comments', model=Comment))
    # admin.add_view(UserView(session=db.session, name='Users', endpoint='users', model=User))

    # Passes the login form to templates.
    @app.context_processor
    def login_context():
        return {
            'url_for_security': url_for_security,
            'login_user_form': LoginForm(),
        }

    @app.route('/')
    @app.route('/index')
    def store_page():

        """
        The main store page that includes all the active products for purchase.
        This is where users add items to their cart.
        """

        posts = Post.query.all()

        return render_template('index.html')

    @app.route('/post/<post_id>')
    def post(post_id):
        post = Post.query.filter_by(id=post_id).first_or_404()
        comments = Comment.query.filter_by(post_id=post_id).all()
        return render_template('post.html', post=post, comments=comments)

    @app.route('/post/<post_id>/post_comment', methods=['POST'])
    @login_required
    def post_comment(post_id):

        text = request.form['comment'] or ''
        if text:

            comment = Comment(body=text, post_id=post_id, user_id=current_user.id, user_email=current_user.email)
            db.session.add(comment)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return abort(500)



    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def user_settings():

        """
        User settings page where users manage their information as well as
        delete their account.
        """

        password_form = PasswordResetForm()
        delete_account_form = DeleteAccountForm()


        # Verifys that the password was correct and changes it to a new one.
        if password_form.submit_password.data and password_form.validate():
            if verify_password(password_form.old_password.data, current_user.password):
                current_user.password = hash_password(password_form.new_password.data)
                db.session.commit()
                return redirect(url_for('store_page'))

        # Verifies that the password was correct and then deletes the account.
        if delete_account_form.submit_delete_account.data and delete_account_form.validate():
            if verify_password(delete_account_form.password.data, current_user.password):
                db.session.delete(current_user)
                db.session.commit()
                return redirect(url_for('store_page'))

        return render_template(
            'user_settings.html',
            password_form=password_form,
            delete_account_form=delete_account_form
        )

    @app.before_first_request
    def before_first_request():

        # This is just an example setup for the database.
        # Obviously if we run in production this would be replaced
        # with something a little less archaic. It works for now though.

        # Create a cart in the session
        if 'cart' not in session:
            session['cart'] = []

        # Clean out the database if we have to
        db.drop_all()

        # Create any database tables that don't exist yet.
        db.create_all()

        # Create the Role "admin" -- unless it already exists
        user_datastore.find_or_create_role(name='admin', description='Administrator')

        # Create two Users for testing purposes -- unless they already exists.
        # In each case, use Flask-Security utility function to encrypt the password.
        user_datastore.create_user(email='someone@example.com', password=hash_password('password'))
        user_datastore.create_user(email='admin@example.com', password=hash_password('password'))

        # Commit any database changes; the User and Roles must exist before we can add a Role to the User
        db.session.commit()

        user_datastore.add_role_to_user('admin@example.com', 'admin')
        db.session.commit()

        db.session.add(Post(title='Test Post', body='Lorem Ipsum'))
        db.session.commit()

    return app
