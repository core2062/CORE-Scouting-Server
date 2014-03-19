
from datetime import datetime
import mongoengine as me
import os.path

import config
from model.db import database as db
from frc_fields import *

class Commit(me.Document):
    time = me.DateTimeField(default=datetime.now)
    enabled = me.BooleanField(default=True)
    user = me.StringField()
    meta = {"allow_inheritance": True}

class MatchCommit(Commit):
    match_num = StringField(
        regex=r"^(\d+|\d+\.[12345])$",
        verbose_name = "Match #",
        help_text = "The number of the match scouted",
        max_length = 5,
        required = True
    )
    match_type = StringField( 
        choices=[("p", "Practice"),("q","Quals"),("qf","Quater Finals"),("sf","Semi Finals"),("f","Finals")],
        verbose_name = "Match Type",
        help_text = "The type of match scouted",
        required = "true",
    )
    event = StringField(
        default = "practice"
    )
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

    auto_high = BooleanField(
        verbose_name = "High Goal",
        help_text= "Did the team scouted shoot in the high goal in autonomous?",
        default = False
    )
    auto_low = BooleanField(
        verbose_name = "Low Goal",
        help_text= "Did the team scouted score in the low goal in autonomous?",
        default = False
    )
    auto_hot = BooleanField(
        verbose_name = "Hot Goal",
        help_text= "If the team scouted scored in autonomous, did they score in the hot goal?",
        default = False
    )
    auto_mobility = BooleanField(
        verbose_name = "Mobility",
        help_text= "Did the team receive mobility points in autonomous?",
        default = False
    )
    auto_goalie = BooleanField(
        verbose_name = "Goalie Zone",
        help_text= "Did the team scouted start the match in the goalie zone?",
        default = False
    )
    auto_balls = IntField(
        verbose_name = "Balls Scored",
        help_text= "The number of balls scored by the team scouted in Autonomous",
        max_value = 3,
        min_value = 0,
        default= 0
    )

    ###########
    ## Teleop
    ###########

    team_cycles = IntField(
        verbose_name =  "Team Cycles",
        help_text =  "The number of times the team contributes assist points.",
        min_value = 0,
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
    truss_made = IntField(
        verbose_name =  "Truss Shots Made",
        help_text =  "The number of times the team scouted successfully scored a truss shot",
        min_value = 0,
        default = 0
    )
    catch_total = IntField(
        verbose_name =  "Catch Total",
        help_text =  "The number of times the team scouted attempted to catch a ball over the truss",
        min_value = 0,
        default = 0
    )
    catch_made = IntField(
        verbose_name =  "Catches Made",
        help_text =  "The number of times the team scouted successfully caught a ball over the truss",
        min_value = 0,
        default = 0
    )
    high_total = IntField(
        verbose_name =  "High Goals Total",
        help_text =  "The number of times the team scouted attempted to score in the high goal",
        min_value = 0,
        default = 0
    )
    high_made = IntField(
        verbose_name =  "High Goals Made",
        help_text =  "The number of times the team scouted successfully scored in the high goal",
        min_value = 0,
        default = 0
    )
    low_total = IntField(
        verbose_name =  "Low Goal Total",
        help_text =  "The number of times the team scouted attempted to score in the low goal",
        min_value = 0,
        default = 0
    )
    low_made = IntField(
        verbose_name =  "Low Goals Made",
        help_text =  "The number of times the tea, scouted successfully scored in the low goal",
        min_value = 0,
        default = 0
    )
    pickup_total = IntField(
        verbose_name =  "Pickup Total",
        help_text =  "the number of times the team scouted attempted to pick up a ball",
        min_value = 0,
        default = 0
    )
    pickup_made = IntField(
        verbose_name =  "Pickups Made",
        help_text =  "The number of times the team scouted successfully picked up a ball",
        min_value = 0,
        default = 0
    )
    pass_total = IntField(
        verbose_name =  "Pass Total",
        help_text =  "The number of times the team scouted attempted to pass the ball ",
        min_value = 0,
        default = 0
    )
    pass_made = IntField(
        verbose_name =  "Passes Made",
        help_text =  "The number of times the team scouted successfully passed the ball",
        min_value = 0,
        default = 0
    )
    inbound_total = IntField(
        verbose_name =  "Inbound Total",
        help_text =  "The number of times the team attempted to inbound a ball ",
        min_value = 0,
        default = 0
    )
    inbound_made = IntField(
        verbose_name =  "Inbounds Made",
        help_text =  "The number of times the team successfully inbounded a ball",
        min_value = 0,
        default = 0
    )
    defense = BooleanField(
        verbose_name =  "Defense",
        help_text =  "Did the team scouted actively play defense on other robots?",
        default = False
    )


    #############
    ## Robot Info
    #############
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
        help_text =  "what kind of drive did the robot scouted have?",
        max_length = 999,
        default = ""
    )

    
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
