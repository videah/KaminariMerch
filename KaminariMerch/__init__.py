from os import path

from flask import Flask, render_template, redirect, session, request, jsonify, abort, url_for
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_qrcode import QRcode
from flask_htmlmin import HTMLMIN
from flask_socketio import SocketIO, join_room

from flask_security.utils import hash_password, verify_password
from flask_security import Security, SQLAlchemyUserDatastore, url_for_security, LoginForm, login_required, current_user

from KaminariMerch.models import User, Order, Product, Role, db
from KaminariMerch.forms import DeleteAccountForm, PasswordResetForm
from KaminariMerch.utils import generate_example_products, in_cart, add_product_to_cart, remove_product_from_cart
from KaminariMerch.views import IndexView, UserView, OrderView, ProductView

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
        'KaminariMerch Admin',
        index_view=OrderView(Order, db.session, url='/admin'),
        template_mode='bootstrap3'
    )


    # Registers pages to the administration page.
    admin.add_link(MenuLink(name='Home', endpoint='store_page'))
    admin.add_view(ProductView(session=db.session, name='Products', endpoint='products', model=Product))
    admin.add_view(UserView(session=db.session, name='Users', endpoint='users', model=User))

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

        products = Product.query.all()

        if 'cart' not in session:
            session['cart'] = []

        for item in products:
            if not item.active:
                products.remove(item)

        return render_template('index.html', products=products, cart=session['cart'], in_cart=in_cart)

    @app.route('/cart')
    def shopping_cart():

        """
        The user cart page, allows removal of items as well as finalizing
        an order before payment.
        """

        total = 0

        if 'cart' in session:
            products = Product.query.filter(Product.id.in_(session['cart'])).all()
            for product in products:
                total += product.price
        else:
            products = []

        return render_template('cart.html', cart=products, total=total)

    @app.route('/add_to_cart', methods=['POST'])
    @login_required
    def add_to_cart():

        """
        API endpoint that adds an item to the request session using
        a provided Product ID.
        """

        product = Product.query.get(request.form['id'])

        if not any(str(product.id) in d for d in session['cart']):
            add_product_to_cart(product)

        return jsonify({'success': True})

    @app.route('/remove_from_cart', methods=['POST'])
    @login_required
    def remove_from_cart():

        """
        API endpoint that removes an item from the request session using a
        provided Product ID.
        """

        product = Product.query.get(request.form['id'])

        if any(str(product.id) in d for d in session['cart']):
            remove_product_from_cart(product)

        return jsonify({'success': True})

    @app.route('/check_payment', methods=['POST'])
    @login_required
    def check_payment():

        """
        Manual payment checking API endpoint for orders.
        TODO: Authorization.
        """

        order = Order.query.get(request.form['id'])
        return jsonify({'paid': order.check_paid()})

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

    @app.route('/checkout')
    def checkout():

        """
        Here validate users checkouts before attempting to create an order. If the
        order was successful then we redirect the user to it.
        """

        products = Product.query.filter(Product.id.in_(session['cart'])).all()
        order = current_user.create_order(products)

        # Checks to make sure the order actually was created. It's possible for this
        # to fail in certain edge cases.
        if order:

            db.session.add(order)
            db.session.commit()

            session['cart'] = []

            return redirect(url_for('show_order', order_id=order.id))

        else:
            return 'Error: Could not create order. Please contact store administration.'

    @app.route('/order/<int:order_id>')
    @login_required
    def show_order(order_id):

        """
        Order page that takes an integer as the id. Checks to make sure the user is linked
        to the order before displaying it.
        """

        if any(order_id in i for i in current_user.get_order_ids()):

            order = Order.query.get(order_id)

            if not order.paid:
                order.check_paid()

            return render_template('order.html', order=order)

        else:
            return abort(404)

    @app.route('/confirm_payment', methods=['POST'])
    def payment_webhook():

        """
        This is a payment webhook that triggers when a payment is received.

        Because this webhook isn't authenticated, we don't trust the payment information on its own.
        We check the payment status ourselves before updating.
        """

        charge = request.get_json()
        charge_id = charge['data']['id']
        order = Order.query.filter_by(charge_id=charge_id).first()

        if order:
            order.check_paid()
            if order.paid:
                return jsonify({'success': True}), 200, {'ContentType': 'application/json'}

        return jsonify({'success': False}), 400, {'ContentType': 'application/json'}

    @app.route('/example_products')
    @login_required
    def example():

        """
        Generates example products for quick evaluation of storefront functionality.
        """

        if current_user.has_role('admin'):
            generate_example_products()
            return redirect(url_for('store_page'))
        else:
            return abort(404)

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

    return app


def create_socketed_app(environment=None):

    """
    This creates a wrapper around the app that enables websocket functionality.
    We can update order status the instant a payment is received without the
    user having to interact. It's completely optional but is recommended for a smooth
    user experience.
    """

    app = create_app(environment)
    socket = SocketIO(app)

    @socket.on('subscribe')
    def subscribe_webhook(data):

        """
        Subscribes a user to a websocket room to make it easier to
        notify of successful payments.
        """

        join_room(data['order'])

    @app.route('/confirm_payment_socket', methods=['POST'])
    def payment_webhook_socket():

        """
        This is an extended webhook that includes websockets.
        From here we can send out a message to the user telling them that their payment's
        been received and the order was successful.
        """

        charge = request.get_json()
        charge_id = charge['data']['id']
        order = Order.query.filter_by(charge_id=charge_id).first()

        if order:
            order.check_paid()
            if order.paid:
                socket.emit('confirm_payment', True, room=order.id)
                return jsonify({'success': True}), 200, {'ContentType': 'application/json'}

        return jsonify({'success': False}), 400, {'ContentType': 'application/json'}

    return app, socket
