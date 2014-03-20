from model.commit import MatchCommit
from model.db import database as db

"""
### Place to do team-based doc collection
### (Should collect every commit related to a team)
"""

def average(sequence):
    n = 0.0
    m = 0
    for i in sequence:
        n += int(i)
        m += 1
    return (n / m) if m else "N/A"



class Team(object):
    def __init__(self, team_num, event):
        self.team_num = team_num
        self.tba_data = db.fms.find_one({"_type":"team", "team_number": team_num})
        if not self.tba_data: raise ValueError("No team %s"%team_num)
        self.nickname = self.tba_data['nickname']
        self.objects = []
        self.matches = set()
        for i in MatchCommit.objects(team=team_num, event=event).order_by("-time"):
            match = i.match_type + i.match_num
            if match in self.matches:
                continue
            self.matches.add(match)
            self.objects.append(i)
        self.matches_played = len(self.matches)
        self.matches_won = "N/A"
        flag = False
        self.auto_contrib = "N/A"
        self.tele_contrib = "N/A"
        self.contrib = self.auto_contrib + self.tele_contrib if flag else "N/A"
        self.attrs = [""]*6
    def __iter__(self):
        return match_objects
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        attr = attr.split("_")
        print attr
        if len(attr) < 2:
            return super(Team, self).__getattr__(attr)
        op = attr[0]
        name = "_".join(attr[1:])
        # try:
        if op == "sum":
            return sum((getattr(i, name) for i in self.objects))
        elif op=="avg":
            if attr[-1] == "made":
                other = name.replace("_made", "_total")
                made = sum(getattr(i, name) for i in self.objects)
                total = sum(getattr(i, other) for i in self.objects)
                print made, ":", total
                # if (made != 0) or (total != 0):
                return made / float(total) if total != 0 else 0
            else:
                return average((getattr(i, name) for i in self.objects))
        # except Exception, e:
        #     print e
        #     raise AttributeError("No numeric attribute %s" % attr)

