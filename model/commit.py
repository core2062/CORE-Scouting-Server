
from datetime import datetime
import mongoengine as me
import os.path

import config
from model.db import database as db
import types
from mongoengine.fields import *
from frc_fields import *

class MatchCommit(me.Document):
    time = me.DateTimeField(default=datetime.now)
    match_num = MatchField(
        # regex=r"^(\d+|\d+\.[12345])$",
        verbose_name = "Match #",
        help_text = "The number of the match scouted",
        # max_length = 5,
        required = True
    )

    match_type = StringField( 
        choices=[("p", "Practice"),("q","Quals"),("qf","Quater Finals"),
                 ("sf","Semi Finals"),("f","Finals")],
        verbose_name = "Match Type",
        help_text = "The type of match scouted",
        default="p",
        required = True,
    )
    event = StringField(
        default = config.event,
        required= "true"
    )

    key = StringField(
        primary_key = True,
        required = True,
        unique = True
    )
    key.to_form_field = types.MethodType(lambda self, model, kwargs: None, key, StringField)

    def clean(self):
        self.key = "{}_{}m{}_{}".format(self.event, self.match_type,
                                       self.match_num, self.team)

    scout = StringField(
        verbose_name = "Scout Name",
        help_text = "The name of the scout",
        max_length = 999,
        required = True
    )
    team = TeamField(
        verbose_name = "Team #",
        help_text = "Identification number of the team scouted",
        required = True
    )
    alliance = StringField(
        verbose_name = "Team's Alliance",
        choices = [('red', 'Red'),('blue', "Blue")],
        help_text = "The alliance of the team scouted, red or blue",
        required = True
    )
    fouls = IntField(
        verbose_name = "Fouls",
        help_text = "How many fouls the team being scouted received",
        min_value = 0,
        default = 0
    )
    tech_fouls = IntField(
         verbose_name = "Technical Fouls",
         help_text = "How many technical fouls the team being scouted received",
         min_value = 0,
         default = 0
    )
    @property
    def foul_contrib(self):
        return -1*(self.fouls * 20 + self.tech_fouls * 50)

    yellow = BooleanField(
         verbose_name = "Yellow Card",
         help_text = "Yellow card received",
         default = False
    )
    red = BooleanField(
         verbose_name = "Red Card",
         help_text = "Did the team being scouted receive a red card?",
         default = False
    )
    comments = StringField(
         verbose_name = "Comments",
         help_text = "Any comments from the scout regarding the team scouted",
         default = ""
    )
    disabled = BooleanField(
         verbose_name = "Disabled",
         help_text = "Was the robot scouted disabled?",
         default = False
    )
    no_show = BooleanField(
         verbose_name = "No Show",
         help_text = 'Was the team scouted a "no show" (not present at the match)',
         default = False
    )

    ###########
    ## Autonomous
    ###########

    auto_high = IntField(
        verbose_name = "High Goal",
        help_text= "How many balls did the team scouted shoot in the high goal in autonomous?",
        max_value = 3,
        min_value = 0,
        default = 0
    )
    @property
    def auto_high_s(self):
        return self.auto_high != 0
    auto_low = IntField(
        verbose_name = "Low Goal",
        help_text = "How many balls did the team scouted score in the low goal in autonomous?",
        max_value = 3,
        min_value = 0,
        default = 0
    )
    @property
    def auto_low_s(self):
        return self.auto_low != 0
    auto_hot = IntField(
        verbose_name = "Hot Goal",
        help_text = "How many hot scores did the team get in auto?",
        max_value = 3,
        min_value = 0,
        default = 0
    )
    @property
    def auto_hot_s(self):
        return self.auto_hot != 0
    @property
    def auto_balls(self):
        return self.auto_low+self.auto_high
    auto_mobility = BooleanField(
        verbose_name = "Mobility",
        help_text = "Did the team receive mobility points in autonomous?",
        default = False
    )
    auto_goalie = BooleanField(
        verbose_name = "Goalie Zone",
        help_text = "Did the team scouted start the match in the goalie zone?",
        default = False
    )
    # auto_balls = IntField(
    #     verbose_name = "Balls Scored",
    #     help_text= "The number of balls scored by the team scouted in Autonomous",
    #     max_value = 3,
    #     min_value = 0,
    #     default= 0
    # )

    @property
    def auto_contrib(self):
        return sum((
            self.auto_hot*15,
            self.auto_high*10,
            self.auto_low*5,
            self.auto_mobility * 5
        ))

    ###########
    ## Teleop
    ###########

    team_cycles = LessThanField(
        verbose_name =  "Team Cycles",
        help_text =  "The number of times the team contributes assist points.",
        min_value = 0,
        less_than = "alliance_cycles",
        default = 0
    )
    alliance_cycles = IntField(
        verbose_name =  "Alliance Cycles",
        help_text =  "The number of times that the entire alliance completes a full cycle.",
        min_value = 0,
        default = 0
    )
    truss_total = IntField(
        verbose_name =  "Truss Shot Total",
        help_text =  "The number of times the team scouted attempted to score a truss shot",
        min_value = 0,
        default = 0
    )
    truss_made = LessThanField(
        verbose_name =  "Truss Shots Made",
        help_text =  "The number of times the team scouted successfully scored a truss shot",
        min_value = 0,
        less_than = "truss_total",
        default = 0
    )
    catch_total = IntField(
        verbose_name =  "Catch Total",
        help_text =  "The number of times the team scouted attempted to catch a ball over the truss",
        min_value = 0,
        default = 0
    )
    catch_made = LessThanField(
        verbose_name =  "Catches Made",
        help_text =  "The number of times the team scouted successfully caught a ball over the truss",
        min_value = 0,
        less_than = "catch_total",
        default = 0
    )
    high_total = IntField(
        verbose_name =  "High Goals Total",
        help_text =  "The number of times the team scouted attempted to score in the high goal",
        min_value = 0,
        default = 0
    )
    high_made = LessThanField(
        verbose_name =  "High Goals Made",
        help_text =  "The number of times the team scouted successfully scored in the high goal",
        min_value = 0,
        less_than = "high_total",
        default = 0
    )
    low_total = IntField(
        verbose_name =  "Low Goal Total",
        help_text =  "The number of times the team scouted attempted to score in the low goal",
        min_value = 0,
        default = 0
    )
    low_made = LessThanField(
        verbose_name =  "Low Goals Made",
        help_text =  "The number of times the tea, scouted successfully scored in the low goal",
        min_value = 0,
        less_than = "low_total",
        default = 0
    )
    pickup_total = IntField(
        verbose_name =  "Pickup Total",
        help_text =  "the number of times the team scouted attempted to pick up a ball",
        min_value = 0,
        default = 0
    )
    pickup_made = LessThanField(
        verbose_name =  "Pickups Made",
        help_text =  "The number of times the team scouted successfully picked up a ball",
        min_value = 0,
        less_than = "pickup_total",
        default = 0
    )
    pass_total = IntField(
        verbose_name =  "Pass Total",
        help_text =  "The number of times the team scouted attempted to pass the ball ",
        min_value = 0,
        default = 0
    )
    pass_made = LessThanField(
        verbose_name =  "Passes Made",
        help_text =  "The number of times the team scouted successfully passed the ball",
        min_value = 0,
        less_than = "pass_total",
        default = 0
    )
    inbound_total = IntField(
        verbose_name =  "Inbound Total",
        help_text =  "The number of times the team attempted to inbound a ball ",
        min_value = 0,
        default = 0
    )
    inbound_made = LessThanField(
        verbose_name =  "Inbounds Made",
        help_text =  "The number of times the team successfully inbounded a ball",
        min_value = 0,
        less_than = "inbound_total",
        default = 0
    )
    defense = BooleanField(
        verbose_name =  "Defense",
        help_text =  "Did the team scouted actively play defense on other robots?",
        default = False
    )

    @property
    def tele_contrib(self):
        return sum((
            self.team_cycles*5,
            self.truss_made*10,
            self.catch_made*10,
            self.low_made*1,
            self.high_made*10
        ))


    #############
    ## Robot Info
    #############
    r_infos = ["shooter", "catcher", "pickup", "blocker", "goalie"]
    shooter = BooleanField(
        verbose_name =  "Shooter",
        help_text =  "Did the robot being scouted have a shooter mechanism?",
        default = False
    )
    catcher = BooleanField(
        verbose_name =  "Catcher",
        help_text =  "Did the robot being scouted have a catching mechanism",
        default = False
    )
    pickup = BooleanField(
        verbose_name =  "Pickup",
        help_text =  "Did the robot being scouted have a pickup mechanism?",
        default = False
    )
    blocker = BooleanField(
        verbose_name =  "Blocker",
        help_text =  "Did the robot being scouted have a blocking mechanism?",
        default = False
    )
    goalie = BooleanField(
        verbose_name =  "Goalie Mechanism",
        help_text =  "Did the robot being scouted have a goalie mechanism?",
        default = False
    )
    drive_type = StringField(
        verbose_name =  "Drive Type",
        choices = [("tank", "Tank"), ("strafe", "Strafe")],
        help_text =  "what kind of drive did the robot scouted have?",
        max_length = 999,
        default = ""
    )

    hp_front = StringField(
        verbose_name =  "Human Player Front",
        choices = (("",""),("+","+"),("-","-")),
        default = ""
    )
    hp_back = StringField(
        verbose_name =  "Human Player Back",
        choices = (("",""),("+","+"),("-","-")),
        default = ""
    )

    @property
    def match(self):
        from model import fms
        return fms.Match.objects.with_id("{}_{}m{}".format(
                self.event, self.match_type, self.match_num))
    @property
    def contrib(self):
        return self.auto_contrib + self.tele_contrib
    @property
    def n_hp_f(self):
        return 1 if self.hp_front == "+" else -1 if self.hp_front == "-" else 0
    @property
    def n_hp_b(self):
        return 1 if self.hp_back == "+" else -1 if self.hp_back == "-" else 0

def parse_cid(cid):
    cid = cid.split("_")
    try:
        e_key, match, team = cid
        match_type, match_num = match.split("m")
    except:
        raise ValueError("Commit id malformated.")
    return (e_key, match_type, match_num, team)

def get_commit(cid):
    # e_key, match_type, match_num, team = parse_cid(cid)
    return MatchCommit.objects.with_id(cid)

# ##############
# # Validators for differnt types
# ##############
# def validate_match(commit):
#   is_team(commit.data['team'])
#   is_match(commit.data['match'])
#   is_true(commit.data['alliance'] in ['red', 'blue'], 'Alliance is not red or blue')
#   try:
#       is_regional(commit.data['regional'])
#   except ex.BadRequest:
#       d = commit.data
#       d['regional'] = config.CURRENT_EVENT
#       commit.data = d


# #####################
# # Validation utils
# #####################
# def is_true(val, exp):
#   if not val:
#       raise ex.BadRequest(exp)

# MATCH_RE = re.compile(r"(p|q|qf|sf|f)(\d+)")
# def looks_like_match(val):
#   match = MATCH_RE.match(val)
#   if match is None:
#       raise ex.BadRequest(str(val) + ' is not a valid match')

# def is_team(team):
#   if not db.sourceTeams.find_one({'team': team}):
#       raise ex.BadRequest(str(team) + ' is not a valid team.')


# def is_regional(regional):
#   if not db.sourceEvent.find_one({'short_name': regional}):
#       raise ex.BadRequest(str(regional) + 'is not a valid regional')
