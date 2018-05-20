import os

from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from sqlalchemy import event

from KaminariMerch.libs.strike import Strike
from config import STRIKE_API_KEY

strike = Strike(STRIKE_API_KEY)
db = SQLAlchemy()

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

order_products = db.Table(
    'order_products',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
)


class Role(db.Model, RoleMixin):

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime())
    modified_at = db.Column(db.DateTime())
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )
    orders = db.relationship('Order', back_populates='user')

    def __repr__(self):
        return self.email

    def create_order(self, products):

        total = 0
        description = ''

        # Generates payment text to be displayed in wallets.
        for product in products:
            total += product.price
            if description:
                description = description + ', ' + product.name
            else:
                description = product.name

        # Truncates payment description if it's too long.
        description = (description[:252] + '...') if len(description) > 256 else description

        charge = strike.create_charge(total, 'btc', description)

        # This should work most of the time but we check just in case.
        if charge:

            return Order(
                user_id=self.id,
                user=self,
                description=description,
                total_cost=total,
                products=products,
                charge_id=charge['id'],
                payment_request=charge['payment_request']
            )

        else:
            return None

    def get_orders(self):
        return Order.query.filter_by(user=self).all()

    def get_order_ids(self):
        return db.session.query(Order.id).filter(Order.user == self).all()


class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='orders')
    description = db.Column(db.String(256))
    charge_id = db.Column(db.String(64), unique=True)
    total_cost = db.Column(db.Integer)
    payment_request = db.Column(db.String(512))
    paid = db.Column(db.Boolean)
    products = db.relationship(
        'Product',
        secondary=order_products,
        backref=db.backref('orders', lazy='dynamic')
    )

    def __repr__(self):
        return 'Order #{}'.format(self.id)

    def check_paid(self):

        paid = strike.get_charge(self.charge_id)['paid']

        if paid:
            self.paid = True
            db.session.commit()

        return paid


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Integer, default=0)
    image = db.Column(db.String, unique=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return self.name

    @property
    def filepath(self):
        if self.image is None:
            return
        return url_for('static', filename='images/' + self.image)


@event.listens_for(Product, 'after_delete')
def del_image(_mapper, _connection, target):
    if target.image is not None:
        try:
            os.remove(target.image)
        except OSError:
            pass
