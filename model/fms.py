
import mongoengine; from mongoengine.fields import *
from model.commit import MatchCommit
from helper import average
import itertools
from helper import NiceDoc

##
# These models are derived from the Blue Alliance API
# Thank you! 
##

class Team(NiceDoc, mongoengine.Document):
    key = StringField(primary_key=True, required=True, unique=True)
    team_number=IntField(required=True, unique=True)
    name = StringField(required=True)
    nickname = StringField(required=True)

    website = StringField()
    locality = StringField()
    region = StringField()
    country = StringField()
    location = StringField()

    def calculate(self, event, match_ge=None):
        self._event = event
        self.event = Event.objects.get(key=self._event)
        self.matches = [i for i in self.event.matches if (self in i.teams and
                                (not match_ge or i.match_number >= match_ge))]
        self._objects = [i.get_commit(self) for i in self.matches if i.get_commit(self)]
        # self._objects = [i for i in MatchCommit.objects(event=self.event.key, team=self.team_number)]
    @property
    def win_record(self):
        return sum(.5 if (i.scored and i.is_winner(self.team_number) is None) 
            else 0 if i.is_winner(self.team_number) is None 
            else i.is_winner(self.team_number) for i in self.matches)
    @property
    def matches_scored(self):
        return sum(1 for i in self.matches if i.scored)
    @property
    def matches_played(self):
        return len(filter(lambda x: not getattr(x, "no_show"), self._objects))
    @property
    def drive(self):
        s = sum(i.drive_type == "strafe" for i in self._objects)
        t = sum(i.drive_type == "tank" for i in self._objects)
        n = 1 if self.matches_played > 1 else 0
        if s > n: return "Strafe"
        if t > n: return "Tank"
        return None
    _info = None
    @property
    def info(self):
        if self._info is None:
            self._info = [self.drive] if self.drive else []
            for ob in MatchCommit.r_infos:
                for i in self._objects:
                    if getattr(i, ob):
                        self._info.append(ob.title())
                        break
        return self._info
    def get_info(self, n):
        try:
            return self.info[n]
        except IndexError:
            return ""
    def __iter__(self):
        return self._objects
    def __getattr__(self, attr_str):
        attr = attr_str.split("_")
        # print attr
        if len(attr) < 2:
            return object.__getattribute__(self, attr_str)
        op = attr[0]
        name = "_".join(attr[1:])
        if op == "sum":
            return sum((getattr(i, name) for i in self._objects))
        elif op=="avg":
            if attr[-1] == "made":
                other = name.replace("_made", "_total")
                made = sum(getattr(i, name) for i in self._objects)
                total = sum(getattr(i, other) for i in self._objects)
                # print made, ":", total
                # if (made != 0) or (total != 0):
                return made / float(total) if total != 0 else 0
            else:
                if not hasattr(MatchCommit, name) and hasattr(MatchCommit, name+"_made"):
                    name += "_made"
                return average(getattr(i, name) for i in self._objects if not i.no_show)
        elif op == "max":
            return max(getattr(i, name) for i in self._objects if not i.no_show)
        elif op=="tq": # Third quartile estimation
            av = getattr(self, attr_str.replace("tq_", "avg_"))
            mx = getattr(self, attr_str.replace("tq_", "max_"))
            return (av+mx)/2.0
        return object.__getattribute__(self, attr_str)

class Alliance(NiceDoc, mongoengine.EmbeddedDocument):
    score = IntField(default=-1)
    teams = ListField(ReferenceField(Team), required=True)

    @property
    def team_nums(self):
        return (i.team_number for i in self)

    def __iter__(self):
        return self.teams.__iter__()
    

class Match(mongoengine.Document):
    key = StringField(primary_key=True, required=True, unique=True)
    comp_level = StringField(required=True,
        choices = ("p", "q", "ef", "qf", "sf", "f"))
    match_number = IntField(required=True)
    set_number = IntField(default=1)
    red = EmbeddedDocumentField(Alliance, required=True)
    blue = EmbeddedDocumentField(Alliance, required=True)
    event = ReferenceField('Event', required=True)

    @property
    def scored(self):
        return self.red.score != -1 and self.blue.score != -1
    @property
    def teams(self):
        return itertools.chain(self.red.teams, self.blue.teams)
    @property
    def team_nums(self):
        return (i.team_number for i in self.teams)
    @property
    def winner(self):
        return ("red" if self.red.score > self.blue.score 
            else "blue" if self.blue.score > self.red.score else None)
    @property
    def commits(self):
        return MatchCommit.objects(match_num=str(self.match_number), 
            match_type=self.comp_level, event=self.event.key).order_by("-time")

    def is_winner(self, team):
        return (team in self.red.team_nums if self.winner=='red' 
            else team in self.blue.team_nums if self.winner=='blue'
            else None)
    def get_commit(self, team):
        return MatchCommit.objects.with_id("{}_{}".format(self.key, team.team_number))

class Event(mongoengine.Document):
    key = StringField(primary_key=True, unique=True, required=True)
    name = StringField(required=True)
    short_name = StringField()
    event_code = StringField()
    event_type_string = StringField()
    event_types = {
        "REGIONAL": 0,
        "DISTRICT": 1,
        "DISTRICT_CMP": 2,
        "CMP_DIVISION": 3,
        "CMP_FINALS": 4,
        "OFFSEASON": 99,
        "PRESEASON": 100,
        "UNLABLED": -1 }
    event_type = IntField(choices=event_types.values())

    teams = ListField(ReferenceField(Team), required=True)
    matches = ListField(ReferenceField(Match))
