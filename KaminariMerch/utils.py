from os import path
from uuid import uuid1

from flask import session
from werkzeug.utils import secure_filename
from KaminariMerch import Product, db


def secure_uuid_filename(_obj, data):

    """
    Returns a secure filename that is mostly guaranteed to be unique.
    """

    _, ext = path.splitext(data.filename)
    uid = uuid1()
    return secure_filename('{}{}'.format(uid, ext))


def generate_example_products():

    example_products = [
        Product(name='T-shirt', description='Really hip t-shirt that will get you all the ladies!', price=420),
        Product(name='Shoes', description='Snazzy shoes. Probably crocs though.', price=900),
        Product(name='Hat', description='Tophat designed for gentlemen.', price=50),
        Product(name='Jeans', description='Jeans that will get the people talking!', price=510),
        Product(name='Shorts', description='Why are you wearing shorts in Scotland', price=95),
        Product(name='Sunglasses', description='Sunglasses to make sure your eyes do not die.', price=83),
        Product(name='Socks', description='Some socks you can buy for your grandson\'s christmas. I\'m sure he will love it.', price=500),
        Product(name='Hoodie', description='Keeps your head warm I guess', price=1337),
        Product(name='Boots', description='Some good big boy shoes', price=250),
    ]

    for product in example_products:
        db.session.add(product)

    db.session.commit()


def in_cart(product):
    return any(str(product) in d for d in session['cart'])


def add_product_to_cart(product):


    """
    Adds a product to the users carts.
    """

    cart = session['cart']
    cart.append(str(product.id))
    session['cart'] = cart

def remove_product_from_cart(product):

    """
    Removes a product from the users cart.
    """

    cart = session['cart']
    cart.remove(str(product.id))
    session['cart'] = cart
