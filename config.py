import os

basedir = os.path.abspath(os.path.dirname(__file__))

# !! IMPORTANT !!
# This is used to communicate with the Strike API for payment requests.
# Do NOT leak this!
STRIKE_API_KEY = 'put-strike-api-key-here'

# Dictates if CSRF protection should be enabled.
# If you don't know what that is, it's a safe bet that
# you probably want to leave this set to True.
CSRF_ENABLED = True

# !! IMPORTANT !!
# This dictates if debugging tools should be enabled, having this
# set to True when in production is seriously asking for trouble.
# ALWAYS turn this off before running in production.
DEBUG = True

# !! IMPORTANT !!
# Make sure this is set to something securely random
# failure to do so will cause a whole bunch of security issues.
SECRET_KEY = 'super-secret'

# !! IMPORTANT !!
# This is used to salt password hashes, it's very important
# that you set this to something unique.
SECURITY_PASSWORD_SALT = 'set-this-to-something-unique'

# What hashing cipher is used to hash passwords.
# Unless you know what you're doing, leave this alone.
SECURITY_PASSWORD_HASH = 'bcrypt'

# Disables email verification.
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False

# Where to store the database file.
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Minimizes HTML when generating templates if set to True.
MINIFY_PAGE = True
