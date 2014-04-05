from mongoengine.fields import *
from mongoengine import errors as me_errors
import flask

from wtforms import validators, fields as f, widgets
from wtforms.validators import ValidationError as wtf_ValidationError
import types

__ALL__ = ["TeamField", "MatchField", "LessThanField"]

class TeamField(IntField):
    def validate(self, value):
        from model import fms
        try:
            fms.Team.objects.get(team_number=value)
        except Exception, e:
            print e
            raise me_errors.ValidationError("%s is not a valid team." % value)
    def to_form_field(self, model, kwargs):
        kwargs["validators"].append(
            TeamValidator(self)
        )
        return f.IntegerField(**kwargs)
class MatchField(IntField):
    def to_form_field(self, model, kwargs):
        fr = MatchWTField(**kwargs)
        return fr
class MatchWTField(f.IntegerField):
    override = False
    def process_formdata(self, valuelist):
        print valuelist
        if valuelist:
            v = valuelist[0]
            if v[0] == "_":
                v = v[1:]
                self.override = True
            try:
                self.data = int(v)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid integer value'))
        
class TeamValidator(object):
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        from model import fms
        event = form["event"].data
        match_num = form['match_num'].data
        comp_level = form['match_type'].data
        team_num = field.data
        try:
            match = fms.Match.objects.get(event=event, match_number=match_num, comp_level=comp_level)
        except me_errors.DoesNotExist:
            # if not form['match_num'].override:
            flask.flash("Match {} not found.", "error")#" Prefix with _ if this is intentional".format(match_num),
                        #"warning")
            raise wtf_ValidationError()
            # else:
            #     flask.flash("Match Check Overridden", "warning")
            #     return 
        if team_num not in match.team_nums:
            raise wtf_ValidationError('Team %s not in match %s. (teams: %s)'
                % (team_num, match_num, ', '.join(str(i) for i in match.team_nums)) )

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