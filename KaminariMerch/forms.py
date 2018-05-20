from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class PasswordResetForm(FlaskForm):
    old_password = PasswordField('Old password')
    new_password = PasswordField('New password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match.')
    ])
    confirm = PasswordField('Confirm new password')
    submit_password = SubmitField('Update password')


class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match.')
    ])
    confirm = PasswordField('Confirm password')
    submit_delete_account = SubmitField('Delete account')
