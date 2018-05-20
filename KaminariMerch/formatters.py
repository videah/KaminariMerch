from flask import url_for
from flask_admin import form
from markupsafe import Markup


def payment_status_formatter(_view, _context, model, name):

    """
    Displays a label showing the payment status in the admin orders page.
    """

    status = getattr(model, name)

    if status:
        label = 'label-success'
        text = 'PAID'
    else:
        label = 'label-danger'
        text = 'UNPAID'

    return Markup('<span title="{0}" class="label {1}">{2}</span>'.format(
        'test',
        label,
        text
    ))


def product_image_formatter(_view, _context, model, _name):

    """
    Displays a thumbnail of a products image in the admin orders page.
    """

    if not model.image:
        return 'No Image Available'

    return Markup(
        '<img src="{0}">'.format(
            url_for('static', filename=form.thumbgen_filename('images/' + model.image))
        )
    )
