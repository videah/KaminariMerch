from os import path
from flask import url_for, redirect, request, abort
from flask_security import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, form

from KaminariMerch.formatters import payment_status_formatter, product_image_formatter
from KaminariMerch.utils import secure_uuid_filename

from config import basedir

imagedir = path.join(basedir, 'KaminariMerch/static/images')


class IndexView(AdminIndexView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    def _handle_view(self, name, **kwargs):

        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))


class OrderView(ModelView):

    column_list = ('id', 'user', 'products', 'total_cost', 'paid')
    column_editable_list = ('user', 'products')

    can_view_details = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    def _handle_view(self, name, **kwargs):

        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))

    can_export = True

    column_formatters = {
        'paid': payment_status_formatter
    }

    column_labels = {
        'id': 'ID',
        'paid': 'Payment Status',
        'total_cost': 'Total Cost (Satoshi)'
    }

    # This defines some things needed to be able to use this view
    # as the default view. Kinda hacky but oh well.
    def __init__(self, model, session, *args, **kwargs):
        super(OrderView, self).__init__(model, session, *args, **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'admin'
        self.name = 'Orders'


class UserView(ModelView):

    column_hide_backrefs = False
    column_list = ('email', 'roles', 'orders')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    def _handle_view(self, name, **kwargs):

        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))


class ProductView(ModelView):

    can_view_details = True
    column_list = ('image', 'name', 'description', 'price', 'active')
    column_editable_list = ('name', 'description', 'price', 'active')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    def _handle_view(self, name, **kwargs):

        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))

    column_formatters = {
        'image': product_image_formatter
    }

    form_extra_fields = {
        'image': form.ImageUploadField(
            'Image',
            base_path=imagedir,
            url_relative_path='images/',
            thumbnail_size=(200, 200, True),
            namegen=secure_uuid_filename)
    }

    can_export = True
