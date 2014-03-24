from mongoengine.fields import *
from mongoengine.errors import ValidationError as me_ValidationError
from wtforms.validators import ValidationError as wtf_ValidationError

from wtforms import validators, fields as f, widgets

class TeamField(IntField):
    def validate(self, value):
        from model.db import database as db
        n = db.fms.find_one({"_type":"team", "team_number": value})
        if n is None:
            raise me_ValidationError("%s is not a valid team." % value)
    def to_form_field(self, model, kwargs):
        kwargs["validators"].append(
            TeamValidator(self)
        )
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

class TeamValidator(object):
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        from model import fms
        event = form["event"].data
        match_num = int(form['match_num'].data.split('.')[0])
        comp_level = form['match_type'].data
        comp_level = "qm" if comp_level == 'q' else comp_level
        team_num = int(field.data)
        match = (fms.Match.objects(event=event, match_number=match_num, comp_level = comp_level)
            .order_by("-time")[0])
        if team_num not in match.team_nums:
            # message = field.gettext()
            raise wtf_ValidationError('Team %s not in match %s. (teams: %s)'
                % (team_num, match_num, ', '.join(str(i) for i in match.team_nums)) )