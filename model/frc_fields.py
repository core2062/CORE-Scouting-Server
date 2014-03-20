from mongoengine.fields import *
from mongoengine.errors import ValidationError as me_ValidationError
from wtforms.validators import ValidationError as wtf_ValidationError

from model.db import database as db
from wtforms import validators, fields as f, widgets

class TeamField(IntField):
    def validate(self, value):
        n = db.fms.find_one({"_type":"team", "team_number": value})
        if n is None:
            raise me_ValidationError("%s is not a valid team." % value)
    def to_form_field(self, model, kwargs):
        return f.IntegerField(**kwargs)

class LessThanField(IntField):
    def __init__(self, less_than=None, **kwargs):
        super(LessThanField, self).__init__(**kwargs)
        self.other = less_than
    def to_form_field(self, model, kwargs):
        kwargs["validators"].append(
            LessThanValidator(self.other)
        )
        return f.IntegerField(**kwargs)

class LessThanValidator(object):
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if field.data > other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            message = field.gettext('Field must be less than or equal to %(other_name)s.')

            raise wtf_ValidationError(message % d)