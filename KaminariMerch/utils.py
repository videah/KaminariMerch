from os import path
from uuid import uuid1

from flask import session
from werkzeug.utils import secure_filename
from KaminariMerch import db


def secure_uuid_filename(_obj, data):

    """
    Returns a secure filename that is mostly guaranteed to be unique.
    """

    _, ext = path.splitext(data.filename)
    uid = uuid1()
    return secure_filename('{}{}'.format(uid, ext))
