from mongoengine.fields import *
from mongoengine.errors import ValidationError

from model.db import database as db
from wtforms import validators, fields as f, widgets

class TeamField(IntField):
    def validate(self, value):
        n = db.fms.find_one({"_type":"team", "team_number": value})
        if n is None:
            raise ValidationError("%s is not a valid team." % value)
    def to_form_field(self, model, kwargs):
        return f.IntegerField(**kwargs)
