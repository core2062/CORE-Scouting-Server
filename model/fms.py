
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

    def calculate(self, event):
        self._event = event
        self.event = Event.objects.get(key=self._event)
        #print list(self.event.matches[5].teams),  2062 in self.event.matches[5].teams
        self.matches = [i for i in self.event.matches if self in i.teams]
        self._objects = []
        for n in self.matches:
            x = [i for i in n.commits if i.team == self.team_number]
            #print len(x), "results"
            if x:
                self._objects.append(x.pop(0))
        # for i in MatchCommit.objects(team=self.team_number, event=event, match_type="q").order_by("-time"):
        #     match = i.match_type + i.match_num
        #     if match in self.matches:
        #         continue
        #     self.matches.add(match)
        #     self._objects.append(i)

    @property
    def contrib(self):
        return self.avg_auto_contrib + self.avg_tele_contrib
    @property
    def win_record(self):
        return sum(.5 if (i.scored and i.is_winner(self.team_number) is None) 
            else 0 if i.is_winner(self.team_number) is None 
            else i.is_winner(self.team_number) for i in Match.objects(event=self._event) if self in i.teams)
    @property
    def matches_played(self):
        return len(filter(lambda x: not getattr(x, "no_show"), self._objects))
    @property
    def drive(self):
        s = sum(i.drive_type == "strafe" for i in self._objects)
        return "Strafe" if s > 1 else "Tank"
    _info = None
    @property
    def info(self):
        if self._info is None:
            self._info = [self.drive]
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
                return average((getattr(i, name) for i in self._objects if not i.no_show))
        return object.__getattribute__(self, attr_str)

class Alliance(NiceDoc, mongoengine.EmbeddedDocument):
    score = IntField(default=-1)
    teams = SortedListField(ReferenceField(Team), required=True)

    @property
    def team_nums(self):
        return (i.team_number for i in self)

    def __iter__(self):
        return self.teams.__iter__()
    

class Match(mongoengine.Document):
    key = StringField(primary_key=True, required=True, unique=True)
    comp_level = StringField(required=True,
        choices = ("p", "qm", "ef", "qf", "sf", "f"))
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
            match_type="q" if self.comp_level == "qm" else self.comp_level).order_by("-time")

    def is_winner(self, team):
        return (team in self.red.team_nums if self.winner=='red' 
            else team in self.blue.team_nums if self.winner=='blue'
            else None)

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
        "UNLABLED": -1
    }
    event_type = IntField(choices=event_types.values())

    teams = ListField(ReferenceField(Team), required=True)
    matches = ListField(ReferenceField(Match))

def match_from_tba(tba_doc):
    tba_doc['red'] = tba_doc['alliances']['red']
    tba_doc['blue'] = tba_doc['alliances']['blue']
    tba_doc['event'] = tba_doc['event_key']
    del tba_doc['alliances']
    return Match(**tba_doc)

wimi2014_practice_sched = [
    {'comp_level': 'p', 'match_number': 1, 'set_number': 1, 
    'key': '2014wimi_qm13', 'alliances': 
        {'blue': {'score': -1, 'teams': ['frc537', 'frc1622', 'frc3018']}, 
        'red': {'score': -1, 'teams': ['frc4143', 'frc2062', 'frc3197']}},
    'event_key': '2014wimi'},
]
