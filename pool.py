from operator import index
from random import choices
import sys
import os
# from selenium import webdriver
# from selenium.webdriver.edge.options import Options
import time
# import bs4
import itertools
import re
import html
from enum import Enum
from typing import List
import datetime
# import ftplib
import argparse
from rich.console import Console
import shutil
import locale
import requests
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker


console = Console(highlight=False)
gExternalPath = 'https://global6.com/bluberipool/20262027/'
gFlagSelectionGrid = False
gPlotOfRankingOverTime = False
gProcessChoixesFromTmp = True

# https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#get-specific-player-info


class BoxStyle(Enum):
    TBS_TEAM = 1
    TBS_SKATERS = 2
    TBS_GOALIE = 3


class SexType(Enum):
    SEX_FEMALE = 1
    SEX_MALE = 2


class CountryType(Enum):
    COUNTRY_CANADA = 1
    COUNTRY_USA = 2


class OfficeType(Enum):
    OFFICE_DRUMMONDVILLE = 1
    OFFICE_LAS_VEGAS = 2
    OFFICE_RENO = 3
    OFFICE_MONCTON = 4
    OFFICE_AUSTIN = 5
    OFFICE_ATLANTA = 6


class Sexe:
    def __init__(self, sex_type: SexType, sex_name: str, icon_filename: str) -> None:
        self.name = sex_name
        self.sex_type = sex_type
        self.number = 0
        self.total_points = 0
        self.average_points = 0
        self.icon_filename = icon_filename


class CountryData:
    def __init__(self, country_type: CountryType, country_name: str, icon_filename: str) -> None:
        self.name = country_name
        self.country_type = country_type
        self.number = 0
        self.total_points = 0
        self.average_points = 0
        self.icon_filename = icon_filename
        self.rank = -1


class OfficeData:
    def __init__(self, office_type: OfficeType, office_name: str, icon_filename: str) -> None:
        self.name = office_name
        self.office_type = office_type
        self.number = 0
        self.total_points = 0
        self.average_points = 0
        self.icon_filename = icon_filename
        self.rank = -1


class Choice:
    def __init__(self, box_number, box_style: BoxStyle, nhl_id, name, team_abreviation, nb_gameplayed, nb_goals, nb_assists, nb_points, nb_wins):
        self.box_number = box_number
        self.box_style = box_style
        self.nhl_id = nhl_id
        self.name = name
        self.team_abreviation = team_abreviation
        self.found = False
        self.nb_gameplayed = nb_gameplayed
        self.nb_goals = nb_goals
        self.nb_assists = nb_assists
        self.nb_points = nb_points
        self.nb_wins = nb_wins
        self.day_by_day_stats = []
        self.who_chose = []        
        self.player_full_name = ""
        self.injury_comment = ""


class Participant:
    def __init__(self, name, choices: list, param_sex: SexType, param_country: CountryType, param_office: OfficeType):
        self.name = name
        self.lowest_round = -1
        self.total_points = 0
        if len(choices) != 24:
            raise ValueError(f"Participant must have 24 choices but has {len(choices)} for {name}")
        self.choices = choices
        self.rank = -1
        self.native_index = -1
        self.office_total_points = 0
        self.sex_type = param_sex
        self.country = param_country
        self.office = param_office
        self.day_by_day_points = []
        self.rank_day_by_day = []

class Box:
    def __init__(self, name, box_style): 
        self.name = name
        self.box_style = box_style
        self.choices = []
        self.nb_choices = 0
        self.best_points = 0
        self.worse_points = 0


def GeneratePlayersChoices(choices: list) -> None:
    # Open the file "ChoicesToExtractFrom.txt" per block of 23 lines that will be stored into a list of strings that we will process
    with open("ChoicesToExtractFrom.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Process the lines in blocks of 23
    for i in range(0, len(lines), 23):
        block = lines[i:i + 23]
        # We isolate the name of the participant.
        # It will always be in the first line of the block.
        # It will beggin after the substring " - " and will stop at the character ":"
        participant_name = block[0].strip().split(" - ")[1].split(":")[0]
        # print(f"Processing participant: {participant_name }")
        # We then process the lines 2 to 21 to get the choices.
        # For each of these lines, the choice begins aften a tab character and ends before on of these two substrings: " (" or ", ".
        participant_choices = []
        AllChoices = []
        for j in range(2, 22):
            iBox = j - 2
            line = block[j].strip()
            if line == "":
                continue
            choice = line.split("\t")[1].split(" (")[0].split(", ")[0]

            # We scan each element of the parameter "choices" to find the first one that contains the name of the choice.
            # Once found, we set the variable "i_found_index" with the position it was found in the list.
            i_found_index = -1
            for k, c in enumerate(choices):
                if c.box_number == iBox and choice in c.name:
                    i_found_index = k
                    break

            if i_found_index == -1:
                raise ValueError(f"The choice {choice} was not found in the list of choices.")
            else:
                AllChoices.append(i_found_index)

        # We print the list "AllChoices" with element separated by commas.
        sStringChoices = ', '.join(str(e) for e in AllChoices)
        print(f'participants.append(Participant("{participant_name}", [{sStringChoices}], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))')


def init_choices(choices: list):
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Carolina Hurricanes", "CAR", 0, 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Colorado Avalanche", "COL", 0, 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Dallas Stars", "DAL", 0, 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Florida Panthers", "FLA", 0, 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "New Jersey Devils", "NJD", 0, 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Vegas Golden Knights", "VGK", 0, 0, 0, 0, 0))

    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Buffalo Sabres", "BUF", 0, 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Detroit Red Wings", "DET", 0, 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Edmonton Oilers", "EDM", 0, 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Ottawa Senators", "OTT", 0, 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Philadelphia Flyers", "PHI", 0, 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Utah Mammoth", "UTA", 0, 0, 0, 0, 0))

    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "Boston Bruins", "BOS", 0, 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "Montréal Canadiens", "MTL", 0, 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "Minnesota Wild", "MIN", 0, 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "Pittsburgh Penguins", "PIT", 0, 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "Tampa Bay Lightning", "TBL", 0, 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "Washington Capitals", "WSH", 0, 0, 0, 0, 0))

    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "Calgary Flames", "CGY", 0, 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "Columbus Blue Jackets", "CBJ", 0, 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "New York Rangers", "NYR", 0, 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "Seattle Kraken", "SEA", 0, 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "Toronto Maple Leafs", "TOR", 0, 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "Winnipeg Jets", "WPG", 0, 0, 0, 0, 0))

    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8484801", "Macklin Celebrini", "SJS", 0, 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8477934", "Leon Draisaitl", "EDM", 0, 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8476453", "Nikita Kucherov", "TBL", 0, 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8477492", "Nathan MacKinnon", "COL", 0, 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8478402", "Connor McDavid", "EDM", 0, 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8477956", "David Pastrnak", "BOS", 0, 0, 0, 0, 0))

    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8481540", "Cole Caufield", "MTL", 0, 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8478403", "Jack Eichel", "VGK", 0, 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8480039", "Martin Necas", "COL", 0, 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8480027", "Jason Robertson", "DAL", 0, 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8476460", "Mark Scheifele", "WPG", 0, 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8480018", "Nick Suzuki", "MTL", 0, 0, 0, 0, 0))

    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8478398", "Kyle Connor", "WPG", 0, 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8477404", "Jake Guentzel", "TBL", 0, 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8478864", "Kirill Kaprizov", "MIN", 0, 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8479343", "Clayton Keller", "UTA", 0, 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8478483", "Mitch Marner", "VGK", 0, 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8479318", "Auston Matthews", "TOR", 0, 0, 0, 0, 0))

    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8481557", "Matt Boldy", "MIN", 0, 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8479337", "Alex DeBrincat", "DET", 0, 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8482740", "Wyatt Johnston", "DAL", 0, 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8477939", "William Nylander", "TOR", 0, 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8478550", "Artemi Panarin", "LAK", 0, 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8479314", "Matthew Tkachuk", "FLA", 0, 0, 0, 0, 0))

    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8478427", "Sebastian Aho", "CAR", 0, 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8481559", "Jack Hughes", "NJD", 0, 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8478420", "Mikko Rantanen", "DAL", 0, 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8482078", "Lucas Raymond", "DET", 0, 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8482116", "Tim Stützle", "OTT", 0, 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8479420", "Tage Thompson", "BUF", 0, 0, 0, 0, 0))

    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "8471675", "Sidney Crosby", "PIT", 0, 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "8477940", "Nikolaj Ehlers", "CAR", 0, 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "8476887", "Filip Forsberg", "NSH", 0, 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "8479542", "Brandon Hagel", "TBL", 0, 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "8475158", "Ryan O'Reilly", "NSH", 0, 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "8480801", "Brady Tkachuk", "FLA", 0, 0, 0, 0, 0))

    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "8479407", "Jesper Bratt", "NJD", 0, 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "8484153", "Leo Carlsson", "ANA", 0, 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "8475786", "Zach Hyman", "EDM", 0, 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "8477960", "Adrian Kempe", "LAK", 0, 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "8477946", "Dylan Larkin", "DET", 0, 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "8477951", "Nick Schmaltz", "UTA", 0, 0, 0, 0, 0))

    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8478445", "Mathew Barzal", "NYI", 0, 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8481604", "Pavel Dorofeyev", "NYR", 0, 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8477500", "Bo Horvat", "NYI", 0, 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8476468", "J.T. Miller", "NYR", 0, 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8475151", "Kyle Palmieri", "NYI", 0, 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8476459", "Mika Zibanejad", "NYR", 0, 0, 0, 0, 0))

    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8479987", "Morgan Geekie", "BOS", 0, 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8477933", "Sam Reinhart", "FLA", 0, 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8475810", "Bryan Rust", "PIT", 0, 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8482699", "Dylan Guenther", "UTA", 0, 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8480023", "Robert Thomas", "STL", 0, 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8477949", "Alex Tuch", "WSH", 0, 0, 0, 0, 0))

    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "8483445", "Cutter Gauthier", "ANA", 0, 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "8482093", "Seth Jarvis", "CAR", 0, 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "8478439", "Travis Konecny", "PHI", 0, 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "8480893", "Kirill Marchenko", "TOR", 0, 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "8480014", "Gabriel Vilardi", "WPG", 0, 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "8481533", "Trevor Zegras", "PHI", 0, 0, 0, 0, 0))

    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8478463", "Anthony Beauvillier", "WSH", 0, 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8480865", "Noah Dobson", "MTL", 0, 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8476456", "Jonathan Huberdeau", "CGY", 0, 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8482109", "Alexis Lafrenière", "NYR", 0, 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8477511", "Anthony Mantha", "NJD", 0, 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8476539", "Jonathan Marchessault", "NSH", 0, 0, 0, 0, 0))

    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8477964", "Ivan Barbashev", "VGK", 0, 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8484984", "Ivan Demidov", "MTL", 0, 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8476881", "Tomas Hertl", "VGK", 0, 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8482775", "Oliver Kapanen", "MTL", 0, 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8483515", "Juraj Slafkovský", "MTL", 0, 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8477447", "Shea Theodore", "VGK", 0, 0, 0, 0, 0))

    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8481523", "Kirby Dach", "MTL", 0, 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8476455", "Gabriel Landeskog", "COL", 0, 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8471724", "Kris Letang", "PIT", 0, 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8480064", "Josh Norris", "BUF", 0, 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8476454", "Ryan Nugent-Hopkins", "EDM", 0, 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8475913", "Mark Stone", "VGK", 0, 0, 0, 0, 0))

    choices.append(Choice(17, BoxStyle.TBS_SKATERS, "8474141", "Patrick Kane", "CHI", 0, 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_SKATERS, "8471215", "Evgeni Malkin", "PIT", 0, 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_SKATERS, "8475754", "Brock Nelson", "COL", 0, 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_SKATERS, "8471214", "Alex Ovechkin", "WSH", 0, 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_SKATERS, "8474564", "Steven Stamkos", "NSH", 0, 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_SKATERS, "8475166", "John Tavares", "TOR", 0, 0, 0, 0, 0))

    choices.append(Choice(18, BoxStyle.TBS_SKATERS, "8480803", "Evan Bouchard", "EDM", 0, 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_SKATERS, "8480839", "Rasmus Dahlin", "BUF", 0, 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_SKATERS, "8480800", "Quinn Hughes", "MIN", 0, 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_SKATERS, "8483457", "Lane Hutson", "MTL", 0, 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_SKATERS, "8480069", "Cale Makar", "COL", 0, 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_SKATERS, "8478460", "Zach Werenski", "CBJ", 0, 0, 0, 0, 0))

    choices.append(Choice(19, BoxStyle.TBS_SKATERS, "8474590", "John Carlson", "TBL", 0, 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_SKATERS, "8479323", "Adam Fox", "NYR", 0, 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_SKATERS, "8476906", "Shayne Gostisbehere", "CAR", 0, 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_SKATERS, "8474578", "Erik Karlsson", "PIT", 0, 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_SKATERS, "8485366", "Matthew Schaefer", "NYI", 0, 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_SKATERS, "8478178", "Darren Raddysh", "TOR", 0, 0, 0, 0, 0))

    choices.append(Choice(20, BoxStyle.TBS_SKATERS, "8479345", "Jakob Chychrun", "WSH", 0, 0, 0, 0, 0))
    choices.append(Choice(20, BoxStyle.TBS_SKATERS, "8480036", "Miro Heiskanen", "DAL", 0, 0, 0, 0, 0))
    choices.append(Choice(20, BoxStyle.TBS_SKATERS, "8474600", "Roman Josi", "NSH", 0, 0, 0, 0, 0))
    choices.append(Choice(20, BoxStyle.TBS_SKATERS, "8482105", "Jake Sanderson", "OTT", 0, 0, 0, 0, 0))
    choices.append(Choice(20, BoxStyle.TBS_SKATERS, "8481542", "Moritz Seider", "DET", 0, 0, 0, 0, 0))
    choices.append(Choice(20, BoxStyle.TBS_SKATERS, "8479410", "Mikhail Sergachev", "UTA", 0, 0, 0, 0, 0))

    choices.append(Choice(21, BoxStyle.TBS_GOALIE, "8478406", "Mackenzie Blackwood", "COL", 0, 0, 0, 0, 0))
    choices.append(Choice(21, BoxStyle.TBS_GOALIE, "8483548", "Brandon Bussi", "CAR", 0, 0, 0, 0, 0))
    choices.append(Choice(21, BoxStyle.TBS_GOALIE, "8480045", "Ukko-Pekka Luukkonen", "BUF", 0, 0, 0, 0, 0))
    choices.append(Choice(21, BoxStyle.TBS_GOALIE, "8474593", "Jacob Markstrom", "FLA", 0, 0, 0, 0, 0))
    choices.append(Choice(21, BoxStyle.TBS_GOALIE, "8479979", "Jake Oettinger", "DAL", 0, 0, 0, 0, 0))
    choices.append(Choice(21, BoxStyle.TBS_GOALIE, "8476883", "Andrei Vasilevskiy", "TBL", 0, 0, 0, 0, 0))

    choices.append(Choice(22, BoxStyle.TBS_GOALIE, "8476945", "Connor Hellebuyck", "WPG", 0, 0, 0, 0, 0))
    choices.append(Choice(22, BoxStyle.TBS_GOALIE, "8480981", "Joel Hofer", "STL", 0, 0, 0, 0, 0))
    choices.append(Choice(22, BoxStyle.TBS_GOALIE, "8478009", "Ilya Sorokin", "NYI", 0, 0, 0, 0, 0))
    choices.append(Choice(22, BoxStyle.TBS_GOALIE, "8476999", "Linus Ullmark", "OTT", 0, 0, 0, 0, 0))
    choices.append(Choice(22, BoxStyle.TBS_GOALIE, "8475809", "Scott Wedgewood", "COL", 0, 0, 0, 0, 0))
    choices.append(Choice(22, BoxStyle.TBS_GOALIE, "8482661", "Jesper Wallstedt", "MIN", 0, 0, 0, 0, 0))

    choices.append(Choice(23, BoxStyle.TBS_GOALIE, "8475683", "Sergei Bobrovsky", "TOR", 0, 0, 0, 0, 0))
    choices.append(Choice(23, BoxStyle.TBS_GOALIE, "8482487", "Jakub Dobes", "MTL", 0, 0, 0, 0, 0))
    choices.append(Choice(23, BoxStyle.TBS_GOALIE, "8477465", "Tristan Jarry", "EDM", 0, 0, 0, 0, 0))
    choices.append(Choice(23, BoxStyle.TBS_GOALIE, "8480280", "Jeremy Swayman", "BOS", 0, 0, 0, 0, 0))
    choices.append(Choice(23, BoxStyle.TBS_GOALIE, "8480313", "Logan Thompson", "WSH", 0, 0, 0, 0, 0))
    choices.append(Choice(23, BoxStyle.TBS_GOALIE, "8478872", "Karel Vejmelka", "UTA", 0, 0, 0, 0, 0))

    # choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8484144", "Connor Bedard", "CHI", 0, 0, 0, 0, 0))
    # choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8478010", "Brayden Point", "TBL", 0, 0, 0, 0, 0))
    # choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8478440", "Dylan Strome", "WSH", 0, 0, 0, 0, 0))
    # choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8480002", "Nico Hischier", "NJD", 0, 0, 0, 0, 0))
    # choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8483431", "Logan Cooley", "UTA", 0, 0, 0, 0, 0))
    # choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8482175", "JJ Peterka", "UTA", 0, 0, 0, 0, 0))
    # choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8480012", "Elias Pettersson", "VAN", 0, 0, 0, 0, 0))
    # choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8478449", "Roope Hintz", "DAL", 0, 0, 0, 0, 0))
    # choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8479385", "Jordan Kyrou", "STL", 0, 0, 0, 0, 0))
    # choices.append(Choice(17, BoxStyle.TBS_SKATERS, "8473419", "Brad Marchand", "FLA", 0, 0, 0, 0, 0))
    # choices.append(Choice(19, BoxStyle.TBS_SKATERS, "8479325", "Charlie McAvoy", "BOS", 0, 0, 0, 0, 0))
    # choices.append(Choice(17, BoxStyle.TBS_GOALIE, "8478499", "Adin Hill", "VGK", 0, 0, 0, 0, 0))
    # choices.append(Choice(17, BoxStyle.TBS_GOALIE, "8478048", "Igor Shesterkin", "NYR", 0, 0, 0, 0, 0))
    # choices.append(Choice(18, BoxStyle.TBS_GOALIE, "8479973", "Stuart Skinner", "EDM", 0, 0, 0, 0, 0))
    # choices.append(Choice(18, BoxStyle.TBS_GOALIE, "8478007", "Elvis Merzlikins", "CBJ", 0, 0, 0, 0, 0))
    # choices.append(Choice(18, BoxStyle.TBS_GOALIE, "8481692", "Dustin Wolf", "CGY", 0, 0, 0, 0, 0))
    # choices.append(Choice(19, BoxStyle.TBS_GOALIE, "8475311", "Darcy Kuemper", "LAK", 0, 0, 0, 0, 0))
    # choices.append(Choice(19, BoxStyle.TBS_GOALIE, "8478470", "Samuel Montembeault", "MTL", 0, 0, 0, 0, 0))
    # choices.append(Choice(22, BoxStyle.TBS_GOALIE, "8479406", "Filip Gustavsson", "MIN", 0, 0, 0, 0, 0))

def process_choice_files(choices: List[Choice], folder_path: str) -> None:

    """
    Scans a folder for .txt files, checks each line against a choices list,
    and prints the filename along with the 0-based match indices (or -1).
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Directory '{folder_path}' does not exist.")
        return

    # 1. Get list of files ending with .txt
    txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]

    # 2. Iterate through each file
    for filename in sorted(txt_files):
        file_path = os.path.join(folder_path, filename)
        
        # 3. Initialize tracking strings
        choices_made = ""
        choices_done = ""
        
        indices = []
        
        # 4. Read the lines of text from the file
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            for line in lines:
                clean_line = line.strip()

                # Some correction on the fly
                if 'Jake Dobes'.lower() in clean_line.lower():
                    clean_line = 'Jakub Dobes'
                
                # 5. Find position in choices (-1 if not found)
                pos = -1
                for i, choice in enumerate(choices):
                    if choice.name.lower() in clean_line.lower():
                        pos = i
                        break

                indices.append(pos)

        # 6. Sort our indices numerically before converting to strings
        indices.sort()

        # 7. Convert all indices to strings for joining
        indices = [str(i) for i in indices]

        # 6 & 7. Format indices with commas
        choices_made = ",".join(indices)
        choices_done = choices_made

        # 8. Output filename without extension + choices_done value
        filename_without_ext = os.path.splitext(filename)[0]

        # 9. Print the final output using "filename_without_ext" and "choices_done" following this format:
        #    participants.append(Participant("{filename_without_ext}", [choices_done], SexType, CountryType, OfficeType))
        print(f"participants.append(Participant(\"{filename_without_ext}\", [{choices_done}], SexType, CountryType, OfficeType))")

def export_choices_to_csv(choices: List[Choice], filename: str) -> None:
    box_style_to_label = {
        BoxStyle.TBS_TEAM: "Team",
        BoxStyle.TBS_SKATERS: "Forward",
        BoxStyle.TBS_GOALIE: "Goalie",
    }

    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Box_Number", "Box_Type", "Option_Name", "Team"])
        for choice in choices:
            writer.writerow([choice.box_number + 1, box_style_to_label[choice.box_style], choice.name, choice.team_abreviation])


def init_boxes(choices: list, boxes: list) -> None:
    boxes.append(Box("1. Elite Contenders", BoxStyle.TBS_TEAM))
    boxes.append(Box("2. Heavy Hitters", BoxStyle.TBS_TEAM))
    boxes.append(Box("3 Frontline Squads", BoxStyle.TBS_TEAM))
    boxes.append(Box("4. Serious Challengers", BoxStyle.TBS_TEAM))
    boxes.append(Box("5. 100-Point Hunters", BoxStyle.TBS_SKATERS))
    boxes.append(Box("6. Premier Superstars", BoxStyle.TBS_SKATERS))
    boxes.append(Box("7. Hart Contenders", BoxStyle.TBS_SKATERS))
    boxes.append(Box("8. Heavy Producers", BoxStyle.TBS_SKATERS))
    boxes.append(Box("9. Offensive Anchors", BoxStyle.TBS_SKATERS))
    boxes.append(Box("10. Solid 70-Pointers", BoxStyle.TBS_SKATERS))
    boxes.append(Box("11. Top Line Weapons", BoxStyle.TBS_SKATERS))
    boxes.append(Box("12. Big Apple Scorers", BoxStyle.TBS_SKATERS))
    boxes.append(Box("13. Key Contributors", BoxStyle.TBS_SKATERS))
    boxes.append(Box("14. Unsung Heroes", BoxStyle.TBS_SKATERS))
    boxes.append(Box("15. Extra Cheese Poutine", BoxStyle.TBS_SKATERS))
    boxes.append(Box("16. Sainte-Flanelle vs Neon", BoxStyle.TBS_SKATERS))
    boxes.append(Box("17. Porcelain Skaters", BoxStyle.TBS_SKATERS))
    boxes.append(Box("18. Museum Pieces", BoxStyle.TBS_SKATERS))
    boxes.append(Box("19. Blue Line Gunners", BoxStyle.TBS_SKATERS))
    boxes.append(Box("20. Offensive Quarterbacks", BoxStyle.TBS_SKATERS))
    boxes.append(Box("21. Rearguard Producers", BoxStyle.TBS_SKATERS))
    boxes.append(Box("22. Brick Wall Club", BoxStyle.TBS_GOALIE))
    boxes.append(Box("23. Win Stealers", BoxStyle.TBS_GOALIE))
    boxes.append(Box("24. Puck Magnets", BoxStyle.TBS_GOALIE))

    for iChoiceIndex, choice in enumerate(choices):
        if choices[iChoiceIndex].box_number < len(boxes):
            boxes[choices[iChoiceIndex].box_number].choices.append(iChoiceIndex)
            boxes[choices[iChoiceIndex].box_number].nb_choices += 1
        else:
            raise ValueError(f"The choice {choices[iChoiceIndex].name} has an invalid choice index {choices[iChoiceIndex].box_number}")


def init_countries(countries: list[CountryData]) -> None:
    countries.append(CountryData(CountryType.COUNTRY_CANADA, "Canada", "canada.png"))
    countries.append(CountryData(CountryType.COUNTRY_USA, "USA", "usa.png"))


def init_offices(offices: list[OfficeData]) -> None:
    offices.append(OfficeData(OfficeType.OFFICE_DRUMMONDVILLE, "Drummondville", "drummondville.png"))
    offices.append(OfficeData(OfficeType.OFFICE_LAS_VEGAS, "Las Vegas", "las_vegas.png"))
    offices.append(OfficeData(OfficeType.OFFICE_RENO, "Reno", "reno.png"))
    offices.append(OfficeData(OfficeType.OFFICE_MONCTON, "Moncton", "moncton.png"))
    offices.append(OfficeData(OfficeType.OFFICE_AUSTIN, "Austin", "austin.png"))
    offices.append(OfficeData(OfficeType.OFFICE_ATLANTA, "Atlanta", "atlanta.png"))


def init_participants(participants: list) -> None:
    participants.append(Participant("Adam Dyer", [2,7,16,22,27,31,41,47,48,59,64,66,73,78,87,92,97,102,112,116,121,130,136,138], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Alex Goguen", [1,8,13,19,28,35,41,44,49,57,65,71,73,78,88,91,101,103,112,115,121,128,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Armando Macias", [0,6,16,19,28,31,36,42,50,57,63,66,73,78,88,91,99,107,113,116,120,131,136,139], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Brandon Smith", [1,6,13,22,28,34,38,45,50,54,61,71,75,78,87,91,101,107,112,115,121,130,137,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Bruno Aird", [0,10,14,21,27,32,39,42,51,58,63,71,72,80,89,94,98,105,113,116,123,126,132,138], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Charles Rutherford", [1,8,13,19,28,32,40,45,50,54,62,66,74,81,85,94,101,103,111,116,123,127,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Chris Maples", [1,6,13,19,26,32,38,45,49,54,61,71,76,78,88,94,101,103,108,115,121,127,135,139], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Christophe Diamond", [1,6,13,22,28,33,38,45,50,54,61,71,73,81,85,91,101,107,112,115,121,131,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Claire Seemayer", [1,8,13,20,26,30,40,45,50,59,61,71,74,82,85,91,96,102,111,118,121,131,132,139], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Craig Vinciguerra", [3,8,13,23,27,31,38,47,49,56,61,67,72,78,87,91,101,104,112,115,121,130,137,141], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Denis Bisson", [5,9,13,22,28,35,36,45,49,57,65,67,73,81,85,91,96,102,109,118,122,130,134,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Derek Pacuk", [1,6,17,22,28,31,38,44,49,54,61,68,73,78,87,94,101,107,112,118,122,131,137,143], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Dirk Geere", [3,8,16,22,28,31,41,47,48,57,62,69,73,80,85,95,97,105,112,116,121,131,132,142], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Dominic Lachance", [1,6,13,19,28,35,38,45,49,54,61,71,73,78,87,94,101,106,110,115,122,130,135,143], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Dylan Howe", [3,8,13,21,25,35,40,45,49,54,62,68,73,78,88,94,101,103,112,118,123,131,132,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Éric Colgan", [1,8,16,19,28,31,40,47,49,59,61,68,77,80,88,94,101,103,110,115,124,131,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Eric Loat", [1,8,13,22,28,30,41,45,49,54,62,71,73,83,89,94,101,103,112,119,122,130,134,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Erick James", [5,8,12,22,27,33,36,42,48,54,62,71,73,78,84,90,101,103,109,116,121,130,136,138], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Erick Ndjomo", [0,6,14,23,28,35,36,43,50,56,61,71,76,78,87,91,100,103,109,116,121,126,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("François Désilets", [5,9,12,20,28,30,38,45,49,54,62,68,73,78,87,91,101,105,110,116,125,128,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("François Hébert", [1,6,16,19,26,32,38,45,49,54,61,71,76,78,88,94,101,103,108,115,121,127,136,141], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("François Leger", [0,11,17,22,28,33,38,42,50,59,65,66,75,78,87,94,101,106,112,115,122,130,137,143], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("François Pelletier", [1,8,16,22,28,32,38,44,50,59,63,71,73,78,87,94,101,107,108,115,121,131,137,142], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("François Vigneault", [1,6,16,19,26,32,37,44,50,57,62,71,74,81,88,94,99,103,113,116,121,131,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Gabe Herod", [1,11,16,19,28,32,38,42,50,54,61,71,73,78,88,91,101,103,112,115,122,131,137,142], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Ginette Mckay", [0,8,16,22,28,32,38,45,50,57,62,66,75,83,87,91,100,107,108,117,123,130,136,143], SexType.SEX_FEMALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Giuseppe Vacirca", [3,8,13,20,28,31,40,45,53,54,61,71,72,81,89,91,100,106,109,115,121,131,135,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Hugues Labrecque", [1,6,16,19,28,31,36,45,50,54,64,71,76,80,88,94,100,107,112,115,121,131,132,142], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Israel Trudel Denis", [1,10,13,19,24,30,39,47,48,54,63,69,72,82,85,94,96,105,111,119,123,128,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Jacob Zydorowicz", [2,8,16,18,27,32,38,47,50,54,61,71,73,79,87,94,101,102,112,118,124,131,132,142], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Jaymz Latour", [1,11,13,22,28,32,38,45,50,57,61,71,73,81,88,91,101,103,111,118,123,127,137,142], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Jeff Baker", [0,9,13,19,28,31,40,45,50,54,64,66,74,78,87,91,99,103,113,116,122,127,136,143], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Jeremie Cormier", [1,9,14,18,28,31,40,42,52,57,61,71,77,78,86,92,100,103,110,117,123,128,135,140], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Joe Kaszupski", [1,8,17,22,28,31,40,42,48,59,61,69,77,83,85,90,101,102,110,118,125,131,132,142], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Karine Descheneaux", [1,10,13,19,24,35,38,42,50,59,61,66,73,78,85,94,101,102,112,115,121,130,137,139], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Keith Menchin", [3,8,13,22,24,32,38,44,49,57,60,66,77,80,88,91,100,107,112,119,121,131,134,142], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_ATLANTA))
    participants.append(Participant("Keith Santos", [5,8,13,21,24,31,40,47,48,54,61,71,75,78,89,92,101,105,108,117,125,127,132,139], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Keith Wilcox", [3,8,13,22,24,33,41,47,52,57,61,71,73,81,87,91,101,107,108,118,125,127,137,139], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_RENO))
    participants.append(Participant("Kevin Peake", [2,7,16,21,27,33,41,44,50,59,64,66,73,83,87,94,101,102,112,115,121,130,136,142], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Luc Carignan", [1,6,12,23,26,32,38,45,50,57,62,68,76,78,88,94,101,103,108,116,123,127,136,141], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Luc McCutcheon", [0,6,13,19,26,32,38,45,50,54,61,71,73,78,88,91,101,103,112,115,123,127,135,139], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Marc Mathews", [5,11,13,22,27,31,40,47,51,54,65,67,77,81,85,91,101,105,113,116,124,131,137,143], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Marc Plante", [0,11,13,21,25,34,38,46,50,59,65,71,75,81,85,94,96,106,113,116,124,128,134,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Marcel Lachance", [1,8,13,21,27,30,38,47,50,56,61,70,76,78,87,94,96,103,111,114,122,128,135,138], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Maxime Villandré", [1,6,16,19,26,32,38,45,49,54,61,71,76,78,88,94,101,103,108,118,121,130,137,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Mélanie Markis", [1,6,13,22,27,32,38,44,49,59,61,68,75,78,87,94,97,102,112,118,120,130,137,139], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Melanie Toutant", [0,10,13,22,26,35,38,45,50,59,64,68,74,80,85,91,99,106,111,117,122,131,134,139], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Miguel Piette", [1,8,13,22,28,35,38,44,50,54,60,66,75,78,87,91,101,107,112,119,122,131,135,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Mike Horn", [1,8,13,21,27,31,37,45,51,56,61,67,76,82,85,92,101,104,110,115,123,131,135,140], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Mike Wabschall", [1,6,16,19,28,33,38,44,50,57,61,71,75,78,88,94,101,106,108,118,122,131,137,143], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Minhye Kim", [1,8,16,20,28,32,38,45,49,54,61,71,73,79,88,94,101,103,108,115,121,131,132,141], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Mohamed Amine Daoud", [1,8,16,19,28,32,38,44,50,54,61,71,75,78,87,94,101,107,108,115,121,131,137,142], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Olivier Lafrenière", [2,8,17,22,28,31,40,47,50,54,61,71,73,81,87,94,97,103,108,115,121,130,137,142], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Olivier Samson", [2,8,13,20,28,33,36,44,50,54,62,69,75,78,85,91,100,107,108,115,124,130,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Pierre Guay", [1,8,13,19,28,32,38,47,50,57,61,71,73,78,88,91,101,103,108,115,121,131,137,142], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Quentin Langelot", [1,9,14,20,28,32,40,44,51,56,63,67,73,81,88,93,98,103,111,116,121,127,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Ralph Benjamin Libao", [1,6,13,21,28,32,38,45,52,57,61,71,77,81,88,90,101,107,108,115,121,127,136,139], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Robert Brillon", [1,8,13,22,28,35,40,46,50,54,61,68,73,78,88,91,101,107,112,116,122,131,134,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Sandra St-Onge", [1,10,13,22,28,31,36,42,49,57,61,71,73,78,88,94,101,103,108,116,122,131,136,143], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Scott McSorley", [1,7,16,19,28,32,36,45,49,54,64,71,76,80,88,94,101,102,112,115,123,127,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Simon Belley", [0,8,13,19,27,35,41,45,48,59,63,69,77,82,87,94,96,105,110,117,125,127,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Simon Courtemanche", [1,6,13,22,28,32,40,44,49,54,61,66,76,81,87,91,97,105,112,118,121,130,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Simon Papineau", [5,6,13,19,24,31,40,46,53,55,61,69,77,78,85,94,96,102,111,117,122,131,132,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Sophie Chabot", [0,9,13,22,27,30,36,44,52,58,63,66,73,80,89,94,98,102,111,115,125,128,135,139], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Stéphan Généreux", [1,6,16,19,27,32,38,43,49,59,63,67,75,78,87,91,97,107,112,119,123,129,134,143], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Tatiana Beaubien", [1,6,13,19,24,30,40,47,53,57,63,71,77,81,85,91,101,105,111,118,121,128,136,139], SexType.SEX_FEMALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Tim Russo", [1,8,16,19,27,32,37,45,48,57,62,71,73,79,88,94,101,104,112,116,121,127,136,140], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Tommy Hamel", [1,8,13,22,28,35,38,45,49,54,61,66,73,78,85,94,101,103,111,115,121,127,136,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Vincent Boisvert", [3,8,14,22,28,31,40,42,53,54,61,66,76,78,87,94,97,107,112,118,121,129,136,139], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Yvan Paradis", [1,8,17,22,28,33,39,42,52,57,61,66,73,78,87,94,99,107,110,118,120,131,136,142], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Yves Lavoie", [0,6,13,19,24,35,40,44,50,55,61,66,75,79,87,91,97,103,111,118,122,131,135,139], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))

    # participants.append(Participant("John Doe Drummondville", [0,6,12,18,24,30,36,42,48,54,60,66,72,78,84,90,96,102,108,114,120,126,132,138], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    # participants.append(Participant("John Doe Las Vegas", [1,7,13,19,25,31,37,43,49,55,61,67,73,79,85,91,97,103,109,115,121,127,133,139], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    # participants.append(Participant("John Doe Reno", [2,8,14,20,26,32,38,44,50,56,62,68,74,80,86,92,98,104,110,116,122,128,134,140], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_RENO))
    # participants.append(Participant("John Doe Moncton", [3,9,15,21,27,33,39,45,51,57,63,69,75,81,87,93,99,105,111,117,123,129,135,141], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    # participants.append(Participant("John Doe Austin", [4,10,16,22,28,34,40,46,52,58,64,70,76,82,88,94,100,106,112,118,124,130,136,142], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    # participants.append(Participant("John Doe Atlanta", [5,11,17,23,29,35,41,47,53,59,65,71,77,83,89,95,101,107,113,119,125,131,137,143], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_ATLANTA))

    for iParticipantIndex, participant in enumerate(participants):
        participant.native_index = iParticipantIndex

def validate_choices(choices: list, participants: list):
    console.print()
    console.print("Validating if choices for our participants are valid...", style="yellow")

    for participant in participants:
        cumulate_choices = ""
        for iChoiceIndex, choice in enumerate(participant.choices):
            if participant.choices[iChoiceIndex] < len(choices):
                cumulate_choices += str(choices[participant.choices[iChoiceIndex]].box_number)
            else:
                raise ValueError(f"Participant {participant.name} has an invalid choice index {participant.choices[iChoiceIndex]}")

        if cumulate_choices != "01234567891011121314151617181920212223":
            raise ValueError(f"Participant {participant.name} has invalid choices {cumulate_choices}")
    console.print("If we've reached this point, there are all valid!", style="bold green")

    console.print()
    console.print("Validating that we found stats from NHL web site for all choices...", style="yellow")
    nbErrors = 0
    for choice in choices:
        if not choice.found:
            if choice.name != "William Karlsson":
                print(f"Choice {choice.name} was not found in the NHL web site!")
                nbErrors += 1
            else:
                console.print(f"WARNING: Choice {choice.name} was not found in the NHL web site, but it's normal for the moment!", style="bold bright_yellow")

    if nbErrors > 0:
        raise ValueError(f"There are {nbErrors} choices that were not found in the NHL web site!")
    console.print("If we've reached this point, all choices were found in the NHL web site!", style="bold green")


# def get_page_content(url1: str, filename1: str, url2=None, filename2=None) -> None:
#     nb_pages_already_downloaded = 0

#     try:
#         with open(filename1, 'r', encoding='utf-8') as f:
#             nb_pages_already_downloaded += 1
#     except FileNotFoundError:
#         pass

#     if url2 and filename2:
#         try:
#             with open(filename2, 'r', encoding='utf-8') as f:
#                 nb_pages_already_downloaded += 1
#         except FileNotFoundError:
#             pass

#     if url2 and filename2:
#         if nb_pages_already_downloaded == 2:
#             return
#     else:
#         if nb_pages_already_downloaded == 1:
#             return

#     # Set up Edge options for headless mode
#     options = Options()
#     options.add_argument('--headless')

#     # Set up Edge webdriver
#     driver = webdriver.Edge()

#     # Open the webpage
#     driver.get(url1)
#     time.sleep(20)

#     # Now we save the page content to a file
#     with open(filename1, 'w', encoding='utf-8') as f:
#         f.write(driver.page_source)

#     if url2 and filename2:
#         # Open the webpage
#         driver.get(url2)
#         time.sleep(20)
#         driver.refresh()
#         time.sleep(20)

#         # Now we save the page content to a file
#         with open(filename2, 'w', encoding='utf-8') as f:
#             f.write(driver.page_source)

#     driver.quit()


def fill_choices_skaters(choices: List[Choice], filename):
    with open(filename, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'html.parser')

    table = soup.find('table')

    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 9:
            skater_name = cells[1].get_text()

            choice_iter = itertools.dropwhile(lambda p: skater_name not in p.name, choices)
            choice = next(choice_iter, None)
            if choice:
                if (skater_name != "Elias Pettersson") or ((skater_name == "Elias Pettersson") and (cells[5].get_text() == "C")):
                    choice.found = True
                    choice.nb_goals = int(cells[7].get_text())
                    choice.nb_passes = int(cells[8].get_text())
                    choice.nb_points = choice.nb_goals+choice.nb_passes


def fill_choices_goalies(choices: List[Choice], filename):
    with open(filename, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'html.parser')

    table = soup.find('table')

    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 8:
            goalie_name = cells[1].get_text()
            choice_iter = itertools.dropwhile(lambda p: goalie_name not in p.name, choices)
            choice = next(choice_iter, None)
            if choice:
                choice.found = True
                choice.team_abreviation = cells[2].get_text()
                choice.nb_wins = int(cells[7].get_text())
                choice.nb_points = choice.nb_wins * 2


def fill_choices_teams(choices: List[Choice], filename):
    with open(filename, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'html.parser')

    table = soup.find('table')

    # Parse table row by row
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 5:
            team_name = cells[1].get_text()
            choice_iter = itertools.dropwhile(lambda p: team_name not in p.name, choices)
            choice = next(choice_iter, None)
            if choice:
                choice.found = True
                choice.nb_wins = int(cells[4].get_text())
                choice.nb_points = choice.nb_wins * 2


def fill_office_points(participants: List[Participant], filename: str) -> None:
    with open(filename, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'html.parser')

    # Find all <a> tags with the specified class
    # and extract the text from each link
    links = soup.find_all('a', class_='hidden-print ng-binding')
    office_participants = [link.get_text() for link in links]

    # Find all <div> tags with the data-col attribute set to "2"
    # and extract the text from each div
    divs = soup.find_all(lambda tag: tag.name == "div" and tag.get("data-col") == "2")
    office_total_points = [div.get_text() for div in divs]

    if len(office_participants) != len(office_total_points):
        raise ValueError(f"The number of participants {len(office_participants)} does not match the number of points {len(office_total_points)} found in the file {filename}!")

    # We will enumerate all the element from office_participants to see if there are present in our participants list
    # If so, the matching participant will have its total_points set to the corresponding value
    for index_seeker, office_participant in enumerate(office_participants):
        for participant in participants:
            if office_participant == participant.name:
                participant.office_total_points = int(office_total_points[index_seeker])
                break

def fill_office_points_manually(participants: List[Participant], filename: str) -> None:
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        # Check if participant line hold a participant name
        for participant in participants:
            if participant.name in line:
                # Get the first word after the participant name in the line.
                points = line.split(participant.name)[1].strip().split()[0]
                print(f"Manually setting participant {participant.name} with points {points}")
                participant.office_total_points = int(points)
                break

def extract_daily_goals_assists(json_path):
    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Exit if there is no gameDate in the data
    if "gameDate" not in data["gameLog"]:
        return []

    # Extract game log into a DataFrame
    df = pd.DataFrame(data["gameLog"])

    # Convert gameDate to datetime
    df["gameDate"] = pd.to_datetime(df["gameDate"])

    # Keep only the columns we need
    df = df[["gameDate", "goals", "assists"]]

    # Build the full date range
    start_date = pd.to_datetime("2026-09-29")
    end_date = pd.to_datetime(datetime.datetime.now().date())
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    # Reindex so every day exists; missing days become NaN
    df = df.set_index("gameDate").reindex(all_days)

    # Replace NaN with zeros
    df = df.fillna(0).astype(int)

    # Convert to list of tuples
    result = list(df[["goals", "assists"]].itertuples(index=False, name=None))

    return result

def extract_daily_wins_losses(json_path):
    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract game log into DataFrame
    df = pd.DataFrame(data["gameLog"])

    # Exit if there is no gameDate in the data
    if "gameDate" not in data["gameLog"]:
        return []

    # Convert gameDate to datetime
    df["gameDate"] = pd.to_datetime(df["gameDate"])

    # Keep only date + decision
    df = df[["gameDate", "decision"]]

    # Create numeric W/L columns
    df["W"] = (df["decision"] == "W").astype(int)
    df["L"] = (df["decision"] == "L").astype(int)

    # Remove the non-numeric column
    df = df.drop(columns=["decision"])

    # Build full date range
    start_date = pd.to_datetime("2026-09-29")
    end_date = pd.to_datetime(datetime.datetime.now().date())
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    # Reindex so every day exists
    df = df.set_index("gameDate").reindex(all_days)

    # Fill missing days with zeros
    df = df.fillna(0).astype(int)

    # Convert to list of tuples (W, L)
    result = list(df[["W", "L"]].itertuples(index=False, name=None))

    return result

def extract_daily_team_results(json_path, team_abbrev):
    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    games = data["games"]
    df = pd.DataFrame(games)

    df["gameDate"] = pd.to_datetime(df["gameDate"])

    # Determine if team is home or away
    df["is_home"] = df["homeTeam"].apply(lambda t: t["abbrev"] == team_abbrev)
    df["is_away"] = df["awayTeam"].apply(lambda t: t["abbrev"] == team_abbrev)

    # Safe score extraction
    def safe_score(team_dict):
        return team_dict.get("score", 0)

    def get_team_score(row):
        return safe_score(row["homeTeam"]) if row["is_home"] else safe_score(row["awayTeam"])

    def get_opponent_score(row):
        return safe_score(row["awayTeam"]) if row["is_home"] else safe_score(row["homeTeam"])

    df["team_score"] = df.apply(get_team_score, axis=1)
    df["opp_score"] = df.apply(get_opponent_score, axis=1)

    # Win = 1 if team_score > opp_score
    df["W"] = (df["team_score"] > df["opp_score"]).astype(int)

    # --- FIX: aggregate duplicate dates ---
    df = df.groupby("gameDate").agg({
        "W": "max",
        "team_score": "sum"
    })

    # Build full date range
    start_date = pd.to_datetime("2026-09-29")
    end_date = pd.to_datetime(datetime.datetime.now().date())
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")

    # Reindex to full daily timeline
    df = df.reindex(all_days)

    # Fill missing days with zeros
    df = df.fillna(0).astype(int)

    # Convert to list of tuples (W, score)
    return list(df[["W", "team_score"]].itertuples(index=False, name=None))

def get_choices_individual_teams_stats2(choices: List[Choice], download_directory: str) -> None:
    console.print()
    console.print("Downloading individual teams stats from NHL web site...", style="yellow")
    for index, choice in enumerate(choices):
        if choice.box_style == BoxStyle.TBS_TEAM:
            sTeamdID = choice.team_abreviation
            if sTeamdID != "":
                filename = f"{download_directory}\\choice_{index}_daybyday.json"
                # if "filename" already exists, we skip the download
                # Let's check if the file exists
                if not os.path.exists(filename):
                    #url = f"https://api-web.nhle.com/v1/scoreboard/{sTeamdID}/now"
                    url = f"https://api-web.nhle.com/v1/club-schedule-season/{sTeamdID}/20262027"
                    response = requests.get(url)

                    # Save raw text (JSON) to a file
                    with open(f"{filename}", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    # console.print(f"Downloaded day by day stats for team {choice.name}...", style="green")
                    console.print('.', end='', style="green")

                choice.day_by_day_stats = extract_daily_team_results(filename, sTeamdID)
                choice.found = True

def get_choices_skaters_stats2(choices: List[Choice], download_directory: str) -> None:
    console.print()
    console.print("Downloading skaters and goalies stats from NHL web site...", style="yellow")
    for index, choice in enumerate(choices):
        if (choice.box_style == BoxStyle.TBS_SKATERS) or (choice.box_style == BoxStyle.TBS_GOALIE):
            sPlayerID = choice.nhl_id
            if sPlayerID != "0000000":
                filename = f"{download_directory}\\choice_{index}.json"
                # if "filename" already exists, we skip the download
                # Let's check if the file exists
                if not os.path.exists(filename):
                    url = f"https://api-web.nhle.com/v1/player/{sPlayerID}/landing"
                    response = requests.get(url)

                    # Save raw text (JSON) to a file
                    with open(f"{filename}", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    # console.print(f"Downloaded stats for skater player ID {sPlayerID} - {choice.name}...", style="green")
                    console.print('.', end='', style="green")

                filename_daybyday = f"{download_directory}\\choice_{index}_daybyday.json"
                # if "filename_daybyday" already exists, we skip the download
                if not os.path.exists(filename_daybyday):
                    url_daybyday = f"https://api-web.nhle.com/v1/player/{sPlayerID}/game-log/20262027/2"
                    response_daybyday = requests.get(url_daybyday)

                    # Save raw text (JSON) to a file
                    with open(f"{filename_daybyday}", "w", encoding="utf-8") as f:
                        f.write(response_daybyday.text)
                    # console.print(f"Downloaded day by day stats for skater player ID {sPlayerID} - {choice.name}...", style="green")
                    console.print('.', end='', style="green")

                with open(f"{filename}", "r", encoding="utf-8") as f:
                    data = json.load(f)

                season = data["featuredStats"]["season"]

                if choice.box_style == BoxStyle.TBS_SKATERS:
                    choice.player_full_name = data["firstName"]["default"] + " " + data["lastName"]["default"]
                    if choice.name != choice.player_full_name:
                        raise ValueError(f"Name mismatch for skater player ID {sPlayerID}: expected {choice.player_full_name}, got {choice.name}")

                    TeamAbreviation = data["currentTeamAbbrev"]
                    if choice.team_abreviation != TeamAbreviation:
                        raise ValueError(f"Team abbreviation mismatch for skater player named {choice.name} : expected {TeamAbreviation}, got {choice.team_abreviation}")

                    # print(f"Processing stats for skater player named: {choice.player_full_name}")
                    if (season == 20262027):
                        choice.nb_gameplayed = data["featuredStats"]["regularSeason"]["subSeason"]["gamesPlayed"]
                        choice.nb_assists = data["featuredStats"]["regularSeason"]["subSeason"]["assists"]
                        choice.nb_goals = data["featuredStats"]["regularSeason"]["subSeason"]["goals"]
                        choice.nb_points = choice.nb_assists + choice.nb_goals
                        choice.day_by_day_stats = extract_daily_goals_assists(filename_daybyday)
                    choice.found = True
                    # console.print(f"Choice {choice.name} - Goals: {choice.nb_goals}, Assists: {choice.nb_assists}, Points: {choice.nb_points}", style="green")
                elif choice.box_style == BoxStyle.TBS_GOALIE:
                    choice.player_full_name = data["firstName"]["default"] + " " + data["lastName"]["default"]
                    if choice.name != choice.player_full_name:
                        raise ValueError(f"Name mismatch for skater player ID {sPlayerID}: expected {choice.player_full_name}, got {choice.name}")

                    TeamAbreviation = data["currentTeamAbbrev"]
                    if choice.team_abreviation != TeamAbreviation:
                        raise ValueError(f"Team abbreviation mismatch for skater player named {choice.name} : expected {TeamAbreviation}, got {choice.team_abreviation}")

                    if (season == 20262027):
                        choice.nb_gameplayed = data["featuredStats"]["regularSeason"]["subSeason"]["gamesPlayed"]
                        choice.nb_wins = data["featuredStats"]["regularSeason"]["subSeason"]["wins"]
                        choice.nb_points = choice.nb_wins * 2
                        choice.day_by_day_stats = extract_daily_wins_losses(filename_daybyday)
                    choice.found = True
                    # console.print(f"Choice {choice.name} - Wins: {choice.nb_wins}, Points: {choice.nb_points}", style="green")

    console.print()  # moves to next line
    console.print("Finished downloading skaters and goalies stats from NHL web site!", style="bold green")


def get_choices_teams_stats2(choices: List[Choice], download_directory: str) -> None:
    filename = f"{download_directory}\\teams_standing.json"

    # Let's check if the file exists
    if not os.path.exists(filename):
        console.print()
        console.print(f"Downloading teams standings...", style="yellow")

        # 2026-10-01:DB-When it's the very first day of activiy, when a team has not played a game yet, we need to go by a date.
        #               Otherwise, we see incomplete standings.
        url = f"https://api-web.nhle.com/v1/standings/now"
        # url = f"https://api-web.nhle.com/v1/standings/2026-09-30"
        
        response = requests.get(url)

        # Save raw text (JSON) to a file
        with open(f"{filename}", "w", encoding="utf-8") as f:
            f.write(response.text)
        console.print("Downloaded successfully!", style="bold green")

    with open(f"{filename}", "r", encoding="utf-8") as f:
        data = json.load(f)

    console.print()
    console.print("Parsing teams standings...", style="yellow")
    for choice in choices:
        if choice.box_style == BoxStyle.TBS_TEAM:
            for team in data["standings"]:
                if team["teamName"]["default"] == choice.name:
                    choice.nb_gameplayed = team["gamesPlayed"]
                    choice.nb_wins = team["wins"]
                    choice.nb_points = choice.nb_wins * 2
                    choice.found = True
                    # console.print(f"Choice {choice.name} - Game Played: {choice.nb_gameplayed}, Wins: {choice.nb_wins}, Points: {choice.nb_points}", style="green")
    console.print("Finished parsing teams standings!", style="bold green")


def strip_html_tags(raw_html: str) -> str:
    # Remove any nested tags (e.g. the <a> around a player's name) then unescape entities.
    text = re.sub(r"<[^>]*>", "", raw_html)
    return html.unescape(text).strip()


def get_injury_report(choices: List[Choice], download_directory: str) -> None:
    filename = f"{download_directory}\\espn_injuries.html"

    if not os.path.exists(filename):
        console.print()
        console.print("Downloading NHL injury report from ESPN...", style="yellow")
        url = "https://www.espn.com/nhl/injuries"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

        with open(f"{filename}", "w", encoding="utf-8") as f:
            f.write(response.text)
        console.print("Downloaded successfully!", style="bold green")

    with open(f"{filename}", "r", encoding="utf-8") as f:
        page_content = f.read()

    console.print()
    console.print("Parsing NHL injury report...", style="yellow")

    # The ESPN injury table has no column headers worth keeping, so a plain row-by-row regex scan is enough.
    nb_matched = 0
    for row_match in re.finditer(r"<tr[^>]*>(.*?)</tr>", page_content, re.S | re.I):
        cells = [strip_html_tags(cell) for cell in re.findall(r"<td[^>]*>(.*?)</td>", row_match.group(1), re.S | re.I)]

        if len(cells) < 4 or cells[0] == "":
            continue

        player_name = cells[0]
        status = cells[3]
        comment = cells[4] if len(cells) >= 5 else ""

        injury_comment = f"{status} - {comment}" if comment else status

        for choice in choices:
            if choice.box_style in (BoxStyle.TBS_SKATERS, BoxStyle.TBS_GOALIE) and choice.name.lower() == player_name.lower():
                choice.injury_comment = injury_comment
                nb_matched += 1
                break

    console.print(f"Finished parsing NHL injury report, matched {nb_matched} player(s)!", style="bold green")


def get_officepools_points_manually(participants: List[Participant], download_directory: str) -> None:
    filename = f"{download_directory}\\officepools_manual.lst"
    fill_office_points_manually(participants, filename)

def get_officepools_points_from_excel_file(participants: List[Participant], excel_filename: str) -> None:
    console.print()
    console.print("Parsing Excel file for office pools points...", style="yellow")
    df = pd.read_excel(excel_filename)

    # Process in blocks of 24 rows
    for start in range(0, len(df), 24):
        block = df.iloc[start:start+24]
        iTotalPoints = 0
        iLowestValue = 1000000

        for index,row in block.iterrows():
            sParticipantName = row.iloc[0]   # Column A
            iBoxPoints = row.iloc[10]  # Column K
            iTotalPoints += int(iBoxPoints)
            if int(iBoxPoints) < iLowestValue:
                iLowestValue = int(iBoxPoints)

        for participant in participants:
            if participant.name == sParticipantName:
                participant.office_total_points = (iTotalPoints - iLowestValue)
                # console.print(f"Participant {participant.name} - Office Total Points: {participant.office_total_points}", style="green")
                break
    console.print("Finished parsing Excel file for office pools points!", style="bold green")

    

def validate_officepools_points(participants: List[Participant]) -> None:
    for participant in participants:
        if participant.office_total_points == 0:
            raise ValueError(f"Participant {participant.name} has not been found in the office pools web site!")


def compare_nhl_vs_officepools(participants: List[Participant]) -> None:
    console.print()
    console.print("Comparing NHL points with OfficePools points...", style="yellow")
    nb_errors = 0
    for participant in participants:
        if participant.total_points != participant.office_total_points:
            nb_errors += 1
            print("-----------------------------------------------------")
            print(f"ERROR: Participant:{participant.name} - NHL:{participant.total_points} - OfficePools:{participant.office_total_points}")
            print(f"Choices: {participant.choices}")

            
    if nb_errors > 0:
        console.print("There are errors in the following participants:", style="bold red")
        # Let's ask user if they abort the process or continue
        user_input = input("Do you want to abort the process? (y/n): ")
        if user_input.lower() == 'y':
            raise ValueError(f"There are {nb_errors} participants that have different points between NHL and OfficePools!")
        else:
            console.print("Continuing the process despite the errors...", style="bold yellow")
    else:
        console.print("If we've reached this point, all participants have the same points between NHL and OfficePools!", style="bold green")


def set_lowest_round(participants: List[Participant], choices: List[Choice]) -> None:
    for participant in participants:
        lowest_round = -1
        lowest_round_value = 1000000
        for choice_index in participant.choices:
            if choices[choice_index].nb_points < lowest_round_value:
                lowest_round_value = choices[choice_index].nb_points
                lowest_round = choices[choice_index].box_number
        participant.lowest_round = lowest_round


def set_points_per_day(participants: List[Participant], choices: List[Choice]) -> None:
    for participant in participants:
        cumulative_points = []
        for box_number in range(len(participant.choices)):
            cumulative_points.append(0)

        for day_number in range(len(choices[participant.choices[0]].day_by_day_stats)):
            participant.day_by_day_points.append(0)

            for box_number, choice_index in enumerate(participant.choices):
                if (len(choices[choice_index].day_by_day_stats) > 0):
                    if choices[choice_index].box_style == BoxStyle.TBS_SKATERS:
                        iDailyPoints = (choices[choice_index].day_by_day_stats[day_number][0] + choices[choice_index].day_by_day_stats[day_number][1])
                    elif choices[choice_index].box_style == BoxStyle.TBS_GOALIE:
                        iDailyPoints = (choices[choice_index].day_by_day_stats[day_number][0] * 2)
                    elif choices[choice_index].box_style == BoxStyle.TBS_TEAM:
                        iDailyPoints= (choices[choice_index].day_by_day_stats[day_number][0] * 2)

                cumulative_points[box_number] += iDailyPoints

            min_index = 0
            min_value = cumulative_points[0]

            for box_number in range(1, len(cumulative_points)):
                if cumulative_points[box_number] < min_value:
                    min_value = cumulative_points[box_number]
                    min_index = box_number

            # We assume you already computed this:
            # min_index = index of smallest element
            total_except_min = 0

            for box_number in range(len(cumulative_points)):
                if box_number != min_index:
                    total_except_min += cumulative_points[box_number]

            participant.day_by_day_points[day_number] = total_except_min

        # print(f"Participant: {participant.name} - Points per day: {participant.day_by_day_points}")
        # print(f"cumulative_points: {cumulative_points}")


def set_total_points(participants: List[Participant], choices: List[Choice]) -> None:
    for participant in participants:
        participant.total_points = 0
        for box_number, choice_index in enumerate(participant.choices):
            if box_number != participant.lowest_round:
                participant.total_points += choices[choice_index].nb_points


def set_who_chose_who(participants: List[Participant], choices: List[Choice]) -> None:
    for choice_index, choice in enumerate(choices):
        for participant_index, participant in enumerate(participants):
            if choice_index in participant.choices:
                choice.who_chose.append(participant_index)


def sort_participants(participants: List[Participant]) -> None:
    sorted_participants = sorted(participants, key=lambda x: x.total_points, reverse=True)

    iPreviousTotalPoints = -1
    participant_index = 0
    iRank = -1

    for participant_index, participant in enumerate(sorted_participants):
        if participant.total_points != iPreviousTotalPoints:
            iRank = participant_index + 1
            iPreviousTotalPoints = participant.total_points
        participant.rank = iRank

def sort_participants_day_by_day(participants: List[Participant]) -> None:
    if len(participants) == 0:
        return

    # Loop through each index of the list
    for i in range(len(participants[0].day_by_day_points)):

        # Sort participants based on the i-th element of their list
        sorted_participants = sorted(
            participants,
            key=lambda p: p.day_by_day_points[i],
            reverse=True
        )

        iPreviousTotalPoints = -1
        participant_index = 0
        iRank = -1

        for participant_index, participant in enumerate(sorted_participants):
            if participant.day_by_day_points[i] != iPreviousTotalPoints:
                iRank = participant_index + 1
                iPreviousTotalPoints = participant.day_by_day_points[i]
            participant.rank_day_by_day.append(iRank)

    # For each participant, print the list of their ranks day by day
    # for participant in participants:
    #     print(f"Participant: {participant.name} - Ranks day by day: {participant.rank_day_by_day}")

def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix


def plot_rankings_over_time(participants, output_path):
    if not participants:
        return

    sorted_participants = sorted(participants, key=lambda x: x.total_points, reverse=True)

    num_days = len(sorted_participants[0].rank_day_by_day)
    start_date = datetime.datetime(2026, 9, 29)
    x_values = [start_date + datetime.timedelta(days=i) for i in range(num_days)]

    for target in sorted_participants:

        plt.figure(figsize=(16, 9), dpi=100)

        for p in sorted_participants:
            if len(p.rank_day_by_day) != num_days:
                continue

            # Legend label now includes rank
            legend_label = f"{p.name} ({p.rank})"

            if p is target:
                plt.plot(
                    x_values,
                    p.rank_day_by_day,
                    linewidth=3.0,
                    alpha=1.0,
                    label=legend_label
                )
            else:
                plt.plot(
                    x_values,
                    p.rank_day_by_day,
                    linewidth=1.0,
                    alpha=0.3,
                    label=legend_label
                )

        plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(matplotlib.ticker.LinearLocator(numticks=12))
        plt.gcf().autofmt_xdate()
        plt.xlim(x_values[0], x_values[-1])

        plt.gca().invert_yaxis()
        plt.yticks([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 52])

        plt.xlabel("Date")
        plt.ylabel("Rang / Rank")
        plt.title(
            f"Rang à travers le temps / Ranking Over Time — "
            f"{target.name} {ordinal(target.rank)} avec/with {target.total_points} points"
        )
        plt.grid(True, linestyle="--", alpha=0.3)

        plt.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.12),
            ncol=8,
            fontsize=8
        )

        plt.tight_layout()

        filename = f"rankings_{target.native_index}.png"
        output_filename = os.path.join(output_path, filename)
        plt.savefig(output_filename)
        plt.close()


def set_best_and_worse_choices_per_boxes(boxes: List[Box], choices: List[Choice]) -> None:
    for box in boxes:
        box.best_choice_points = -1
        box.worse_choice_points = 1000000
        for choice_index in box.choices:
            if choices[choice_index].nb_points > box.best_choice_points:
                box.best_choice_points = choices[choice_index].nb_points
            if choices[choice_index].nb_points < box.worse_choice_points:
                box.worse_choice_points = choices[choice_index].nb_points
            box.best_points = box.best_choice_points
            box.worse_points = box.worse_choice_points

# Compress to a zip file the website directory


def compress_website_directory(website_directory: str, output_zip_filename: str) -> None:
    console.print()
    console.print(f"Compressing website directory '{website_directory}' to zip file '{output_zip_filename}'...", style="yellow")

    # Let's delete the zip file if it already exists
    try:
        os.remove(output_zip_filename)
    except FileNotFoundError:
        pass

    shutil.make_archive(output_zip_filename.replace('.zip', ''), 'zip', website_directory)
    console.print(f"Website directory compressed to '{output_zip_filename}'!", style="bold green")

# Function that will copy specific files to the website directory.
# These files are coming from the directory .\ressources of the script.


def copy_required_ressources(for_website_directory: str, param_offices: List[OfficeData], param_countries: List[CountryData]) -> None:
    console.print()
    console.print("Copying resource files...", style="yellow")

    shutil.copy(".\\ressources\\bluberi_logo.png", f"{for_website_directory}\\bluberi_logo.png")
    shutil.copy(".\\ressources\\global6.ico", f"{for_website_directory}\\global6.ico")

    for office in param_offices:
        shutil.copy(f".\\ressources\\{office.icon_filename}", f"{for_website_directory}\\{office.icon_filename.split('\\')[-1]}")

    for country in param_countries:
        shutil.copy(f".\\ressources\\{country.icon_filename}", f"{for_website_directory}\\{country.icon_filename.split('\\')[-1]}")

    console.print("Resource files copied!", style="bold green")


def procedure_css_file(for_website_directory: str) -> None:
    with open(f"{for_website_directory}\\pool_style.css", 'w', encoding='utf-8', newline='\r\n') as f:
        f.write("body {\n")
        f.write("  background-color: #ffffff;\n")
        f.write("  font-family: Arial, sans-serif;\n")
        f.write("}\n")
        f.write("\n")

        f.write("a {\n")
        f.write("  text-decoration: none; /* Removes the underline */\n")
        f.write("  color: blue; /* Sets the default link color */\n")
        f.write("}\n")
        f.write("\n")

        f.write("a:visited {\n")
        f.write("  color: blue; /* Keeps the color the same after the link is visited */\n")
        f.write("}\n")
        f.write("\n")

        f.write(".box_header_normal {\n")
        f.write("  background-color: yellow;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".box_header_dropped {\n")
        f.write("  background-color: lightgray;\n")
        f.write("  color: #808080;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".participant_choice_best {\n")
        f.write("  background-color: #e0ffe0;\n")
        f.write("  color: #008000;\n")
        f.write("  font-weight: bold;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".participant_choice_worse {\n")
        f.write("  background-color: #ffe0e0;\n")
        f.write("  color: #800000;\n")
        f.write("  font-weight: bold;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".participant_choice_normal {\n")
        f.write("  background-color: #e0e0ff;\n")
        f.write("  color: #000080;\n")
        f.write("  font-weight: bold;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".participant_choice_dropped {\n")
        f.write("  background-color: #e0e0e0;\n")
        f.write("  color: #808080;\n")
        f.write("  font-weight: bold;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".participant_not_choice_normal {\n")
        f.write("  background-color: white;\n")
        f.write("  color: black;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".participant_not_choice_dropped {\n")
        f.write("  background-color: white;\n")
        f.write("  color: #808080;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".outer-table {\n")
        f.write(" border: 3px solid black;\n")
        f.write(" border-collapse: collapse;\n")
        f.write("}\n")
        f.write("\n")

        # f.write(".outer-table {\n")
        # f.write("    width: 100%;\n")
        # f.write("    table-layout: fixed;\n")
        # f.write("}\n")

        # f.write(".outer-table th,\n")
        # f.write(".outer-table td {\n")
        # f.write("    width: 25%;\n")
        # f.write("  background-color: darkblue;\n")
        # f.write("  color: #ffffff;\n")
        # f.write("  font-size: 20px;\n")
        # f.write("  font-weight: bold;\n")
        # f.write("  text-align: center;\n")
        # f.write("}        \n")

        f.write(".inner-table {\n")
        f.write(" table-layout: fixed;\n")
        f.write(" border: 1px solid silver;\n")
        f.write(" border-collapse: collapse;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".inner-table th {\n")

        if gFlagSelectionGrid:
            f.write(" width: 280px;\n")
        else:
            f.write(" width: 360px;\n")
            
        f.write(" height: 20px;\n")
        f.write(" border-bottom: 1px solid silver;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".outer-table th.colspan-4 {\n")
        f.write("  background-color: darkblue;\n")
        f.write("  color: #ffffff;\n")
        f.write("  font-size: 20px;\n")
        f.write("  font-weight: bold;\n")
        f.write("  text-align: center;\n")
        f.write("}\n")

        f.write(".outer-table th.colspan-3 {\n")
        f.write("  background-color: darkblue;\n")
        f.write("  color: #ffffff;\n")
        f.write("  font-size: 20px;\n")
        f.write("  font-weight: bold;\n")
        f.write("  text-align: center;\n")
        f.write("}\n")

        f.write(".outer-ranking-table {\n")
        f.write(" border: 0px solid black;\n")
        f.write(" border-collapse: collapse;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".outer-ranking-table th.colspan-2 {\n")
        f.write("  background-color: darkblue;\n")
        f.write("  color: #ffffff;\n")
        f.write("  font-size: 30px;\n")
        f.write("  font-weight: bold;\n")
        f.write("  text-align: center;\n")
        f.write("}\n")

        f.write(".outer-ranking-table td {\n")
        f.write("padding: 0;\n")
        f.write("margin: 0;\n")
        f.write("vertical-align: top;\n")
        f.write("}\n")

        f.write(".page-header-table {\n")
        f.write(" border: 0px solid black;\n")
        f.write(" border-collapse: collapse;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".page-header-table th {\n")
        f.write("  background-color: darkblue;\n")
        f.write("  color: #ffffff;\n")
        f.write("  font-size: 30px;\n")
        f.write("  font-weight: bold;\n")
        f.write("  text-align: center;\n")
        f.write("  padding: 5px 5px;\n")
        f.write("  vertical-align: middle;\n")
        f.write("  display: flex;\n")
        f.write("  justify-content: center;\n")
        f.write("  align-items: center;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".page-header-table td {\n")
        f.write("  background-color: darkblue;\n")
        f.write("  color: #ffffff;\n")
        f.write("  font-size: 15px;\n")
        f.write("  text-align: center;\n")
        f.write("  padding: 0px 0px;\n")
        f.write("  vertical-align: middle;\n")
        f.write("  display: flex;\n")
        f.write("  justify-content: center;\n")
        f.write("  align-items: center;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".page-header-table td.link-td {\n")
        f.write("  background-color: darkblue;\n")
        f.write("  color: #ffff00;\n")
        f.write("  font-size: 15px;\n")
        f.write("  text-align: left;\n")
        f.write("  padding: 5px 5px;\n")
        f.write("  vertical-align: middle;\n")
        f.write("  display: flex;\n")
        f.write("  justify-content: left;\n")
        f.write("  align-items: center;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".page-header-table td.link-td a {\n")
        f.write("  color: #ffff00;\n")  # Always yellow
        f.write("  text-decoration: underline;\n")  # Always underlined
        f.write("}\n")
        f.write("\n")

        f.write(".page-footer-table {\n")
        f.write(" border: 0px solid black;\n")
        f.write(" border-collapse: collapse;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".page-footer-table th, .page-footer-table td {\n")
        f.write("  background-color: white;\n")
        f.write("  color: #black;\n")
        f.write("  font-size: 15px;\n")
        f.write("  font-style: italic;\n")
        f.write("  text-align: left;\n")
        f.write("  padding: 0px 0px;\n")
        f.write("  vertical-align: middle;\n")
        f.write("  display: flex;\n")
        f.write("  justify-content: left;\n")
        f.write("  align-items: left;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".page-footer-table th a, .page-footer-table td a {\n")
        f.write("    color: black;\n")
        f.write("    text-decoration: underline;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".ranking-table {\n")
        f.write(" border: 1px solid black;\n")
        f.write(" border-collapse: collapse;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".ranking_header {\n")
        f.write("  background-color: yellow;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".ranking-table th.colspan-3 {\n")
        f.write("  background-color: darkblue;\n")
        f.write("  color: #ffffff;\n")
        f.write("  vertical-align: middle;\n")
        f.write("  display: table-cell;\n")
        f.write("}\n")

        f.write(".ranking-table th.colspan-4 {\n")
        f.write("  background-color: darkblue;\n")
        f.write("  color: #ffffff;\n")
        f.write("  font-size: 20px;\n")
        f.write("  font-weight: bold;\n")
        f.write("  text-align: center;\n")
        f.write("}\n")

        f.write(".just_center {\n")
        f.write("  text-align: center;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".just_center_vertical {\n")
        f.write("  vertical-align: middle;\n")
        f.write("  display: flex;\n")
        f.write("  align-items: center;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".row_even {\n")
        f.write("  background-color: #f0f0f0;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".row_odd {\n")
        f.write("  background-color: #f8f8f8;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".header {\n")
        f.write("  background-color: black;\n")
        f.write("  color: white;\n")
        f.write("  font-weight: bold;\n")
        f.write("  padding: 3px;\n")
        f.write("  text-align: left;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".header .small-text {\n")
        f.write("  font-size: smaller;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".header .links a {\n")
        f.write("  color: white;\n")
        f.write("  margin: 0 10px;\n")
        f.write("  text-decoration: none;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".who-chose-table {\n")
        f.write("  width: 1080px;\n")
        f.write("  table-layout: fixed;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".who-chose-table .col-choice {\n")
        f.write("  width: 200px;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".who-chose-table .col-points, .who-chose-table .col-nb {\n")
        f.write("  width: 50px;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".who-chose-table .col-participants {\n")
        f.write("  width: 780px;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".who-chose-table td.col-participants {\n")
        f.write("  font-weight: normal;\n")
        f.write("  color: black;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".participant-hover-link, .participant-hover-link:visited {\n")
        f.write("  color: inherit;\n")
        f.write("  text-decoration: none;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".participant-hover-link:hover, .participant-hover-link:visited:hover {\n")
        f.write("  color: blue;\n")
        f.write("  text-decoration: underline;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".who-chose-own-participant {\n")
        f.write("  font-weight: bold;\n")
        f.write("  color: navy;\n")
        f.write("  text-shadow: 0 0 5px #ffff00, 0 0 10px #ffff00;\n")
        f.write("}\n")
        f.write("\n")





def write_ranking_table(f, participants: List[Participant], sorted_by_rank: bool) -> None:
    f.write("     <table class=\"ranking-table\">\n")

    if sorted_by_rank:
        header_line = f"Sorted by total points"
    else:
        header_line = f"Sorted by name"

    f.write("       <tr>\n")
    f.write(f"         <th colspan=\"3\" class=\"colspan-3\">{header_line}</th>\n")
    f.write("       </tr>            \n")

    f.write("       <tr>\n")
    f.write("         <th class=\"ranking_header\">Rank</th>\n")
    f.write("         <th class=\"ranking_header\">Name</th>\n")
    f.write("         <th class=\"ranking_header\">Total Points</th>\n")
    f.write("       </tr>\n")

    if sorted_by_rank:
        sorted_participants = sorted(participants, key=lambda x: x.total_points, reverse=True)
    else:
        sorted_participants = sorted(participants, key=lambda x: locale.strxfrm(x.name))
#       sorted_participants = sorted(participants, key=lambda x: x.name)

    row_color = "row_odd"
    previous_rank = -1

    for participant in sorted_participants:
        if participant.rank != previous_rank:
            if row_color == "row_even":
                row_color = "row_odd"
            else:
                row_color = "row_even"
            previous_rank = participant.rank

        f.write(f"       <tr class=\"{row_color}\">\n")
        f.write(f"         <td class=\"just_center\">{participant.rank}</td>\n")
        f.write(f"         <td><a href=\"poolparticipant{participant.native_index}.html\">{participant.name}</a></td>\n")
        f.write(f"         <td class=\"just_center\">{participant.total_points}</td>\n")
        f.write("       </tr>\n")

    f.write("     </table>\n")


def write_footer(generation_timestamp: str, f, use_external_path: bool = False, participant_native_index: "int | None" = None) -> None:
    if participant_native_index is not None:
        who_chose_who_link = f"who_chose_who{participant_native_index}.html"
    else:
        who_chose_who_link = "who_chose_who.html"

    f.write("<br>\n")
    f.write("<table class=\"page-footer-table\">\n")
    f.write(" <tr>\n")
    f.write("  <td>\n")
    f.write(f"Generated on {generation_timestamp}\n")
    f.write("  </td>\n")

    f.write("  <td>\n")
    f.write(f"<a href=\"{gExternalPath}ranking.html\">Ranking</a>\n")
    f.write("&nbsp;")
    f.write(f"<a href=\"{gExternalPath}country_stats.html\">CANADA vs USA</a>\n")
    f.write("&nbsp;")
    f.write(f"<a href=\"{gExternalPath}office_stats.html\">Bluberi Offices</a>\n")
    f.write("&nbsp;")
    f.write(f"<a href=\"{gExternalPath}{who_chose_who_link}\">Who Selected Who</a>\n")
    # f.write("&nbsp;")
    # f.write("<a href=\"https://www.officepools.com/nhl/classic/auth/2025/regular/Bluberi2026/Bluberi2026\" target=\"officepools\">OfficePools</a>\n")
    f.write("  </td>\n")

    f.write(" </tr>\n")
    f.write("</table>\n")


def write_header(generation_timestamp: str, f, use_external_path: bool = False, participant_native_index: "int | None" = None) -> None:
    if use_external_path:
        sub_path = gExternalPath
    else:
        sub_path = ""

    if participant_native_index is not None:
        who_chose_who_link = f"who_chose_who{participant_native_index}.html"
    else:
        who_chose_who_link = "who_chose_who.html"

    f.write("<table class=\"page-header-table\">\n")

    f.write(" <tr>\n")
    f.write("  <th>\n")

    f.write(f"  <img src=\"{sub_path}bluberi_logo.png\" alt=\"Bluberi Logo\">&nbsp;")
    f.write("  Bluberi Hockey Pool 2026-2027\n")
    f.write(f"  &nbsp;<img src=\"{sub_path}bluberi_logo.png\" alt=\"Bluberi Logo\">")
    f.write("  </th>\n")
    f.write(" </tr>\n")

    f.write(" <tr>\n")
    f.write("  <td>\n")
    f.write(f"   Generated on {generation_timestamp}\n")
    f.write("  </td>\n")
    f.write(" </tr>\n")

    f.write(" <tr>\n")
    f.write("  <td class=link-td>\n")
    f.write(f"<a href=\"{sub_path}ranking.html\">Ranking</a>\n")
    f.write("&nbsp;")
    f.write(f"<a href=\"{sub_path}country_stats.html\">CANADA vs USA</a>\n")
    f.write("&nbsp;")
    f.write(f"<a href=\"{sub_path}office_stats.html\">Bluberi Offices</a>\n")
    f.write("&nbsp;")
    f.write(f"<a href=\"{sub_path}{who_chose_who_link}\">Who Selected Who</a>\n")
    # f.write("&nbsp;")
    # f.write("<a href=\"https://www.officepools.com/nhl/classic/auth/2025/regular/Bluberi2026/Bluberi2026\" target=\"officepools\">OfficePools</a>\n")
    f.write("  </td>\n")
    f.write(" </tr>\n")

    f.write("</table>\n")
    f.write("<br>\n")


def produce_ranking_grid(generation_timestamp: str, for_website_directory: str, participants: List[Participant]) -> None:
    # Let's generate a html file with the results
    with open(f"{for_website_directory}\\ranking.html", 'w', encoding='utf-8', newline='\r\n') as f:
        # Let's create a table of 20 tables arranged 5 rows of 4 columns
        f.write("<!DOCTYPE html>\n")
        f.write("<html lang=\"en\">\n")
        f.write("  <head>\n")
        f.write("     <meta charset=\"UTF-8\">\n")
        f.write(f"    <title>Ranking (Generated on {generation_timestamp})</title>\n")
        f.write(f"    <link rel=\"stylesheet\" type=\"text/css\" href=\"pool_style.css?v=1.1\">\n")
        f.write(f"    <link rel=\"icon\" href=\"global6.ico\" type=\"image/x-icon\">\n")
        f.write("  </head>\n")

        f.write("\n")
        f.write("  <body>\n")

        write_header(generation_timestamp, f)

        # Let's create a table with three elements
        # 1. One with a table with participants sorted by their point
        # 2. One empty area
        # 3. One with a table with participants sorted by their name
        f.write("     <table class=\"outer-ranking-table\">\n")
        f.write("       <tr>\n")
        f.write(f"         <th colspan=\"2\" class=\"colspan-2\">Ranking</th>\n")
        f.write("       </tr>\n")

        f.write("       <tr>\n")
        f.write("         <td>\n")
        write_ranking_table(f, participants, True)
        f.write("         </td>\n")
        f.write("         <td>\n")
        write_ranking_table(f, participants, False)
        f.write("         </td>\n")
        f.write("       </tr>\n")
        f.write("     </table>\n")

        write_footer(generation_timestamp, f)

        f.write("  </body>\n")
        f.write("</html>\n")


def produce_sex_grid(generation_timestamp: str, for_website_directory: str, participants: List[Participant]) -> None:
    sex_participants = []
    sex_participants.append(Sexe(SexType.SEX_MALE, "Men", "men.png"))
    sex_participants.append(Sexe(SexType.SEX_FEMALE, "Women", "women.png"))

    for participant in participants:
        for sex_participant in sex_participants:
            if participant.sex_type == sex_participant.sex_type:
                sex_participant.number += 1
                sex_participant.total_points += participant.total_points
                break

    for sex_participant in sex_participants:
        if sex_participant.number != 0:
            sex_participant.average_points = sex_participant.total_points / sex_participant.number
        else:
            sex_participant.average_points = 0
        sex_participant.average_points = f"{sex_participant.average_points:.2f}"

    # Let's sort based on the average points
    sorted_sex_participant = sorted(sex_participants, key=lambda x: x.average_points, reverse=True)

    console.print()
    console.print("Stats by Gender", style="yellow")
    for sex_participant in sorted_sex_participant:
        console.print(f"{sex_participant.average_points} - {sex_participant.name}", style="bold green")

    # Let's generate a html file with the results
    with open(f"{for_website_directory}\\gender_stats.html", 'w', encoding='utf-8', newline='\r\n') as f:
        # Let's create a table of 20 tables arranged 5 rows of 4 columns
        f.write("<!DOCTYPE html>\n")
        f.write("<html lang=\"en\">\n")
        f.write("  <head>\n")
        f.write("     <meta charset=\"UTF-8\">\n")
        f.write(f"    <title>Stats by Gender (Generated on {generation_timestamp})</title>\n")
        f.write(f"    <link rel=\"stylesheet\" type=\"text/css\" href=\"pool_style.css?v=1.1\">\n")
        f.write(f"    <link rel=\"icon\" href=\"global6.ico\" type=\"image/x-icon\">\n")
        f.write("  </head>\n")

        f.write("\n")
        f.write("  <body>\n")

        # Let's create a table with three elements
        f.write("     <table class=\"ranking-table\">\n")

        f.write("       <tr>\n")
        f.write(f"         <th colspan=\"3\" class=\"colspan-3\">&nbsp;Stats by Gender&nbsp;</th>\n")
        f.write("       </tr>\n")

        f.write("       <tr>\n")
        f.write("         <th class=\"ranking_header\">Gender</th>\n")
        f.write("         <th class=\"ranking_header\">Nb</th>\n")
        f.write("         <th class=\"ranking_header\">Avg</th>\n")
        f.write("       </tr>\n")

        for sex_participant in sorted_sex_participant:
            f.write("       <tr>\n")
            f.write("         <td>\n")
            f.write(f"         <img src=\"{sex_participant.icon_filename}\" alt=\"{sex_participant.name}\">&nbsp;{sex_participant.name}\n")
            f.write("         </td>\n")
            f.write("         <td style=\"text-align: right;\">\n")
            f.write(f"         {sex_participant.number}&nbsp;\n")
            f.write("         </td>\n")
            f.write("         <td style=\"text-align: right;\">\n")
            f.write(f"         {sex_participant.average_points}&nbsp;\n")
            f.write("         </td>\n")
            f.write("       </tr>\n")

        f.write("     </table>\n")

        write_footer(generation_timestamp, f)

        f.write("  </body>\n")
        f.write("</html>\n")


def write_ranking_country_table(f, participants: List[Participant], country: CountryData) -> None:
    f.write("     <table class=\"ranking-table\">\n")

    f.write("       <tr>\n")
    f.write(f"         <th colspan=\"3\" class=\"colspan-3\"><img src=\"{country.icon_filename}\" alt=\"{country.name}\">&nbsp;{country.name}&nbsp;<img src=\"{country.icon_filename}\" alt=\"{country.name}\"></th>\n")
    f.write("       </tr>            \n")

    f.write("       <tr>\n")
    f.write("         <th class=\"ranking_header\">Rank</th>\n")
    f.write("         <th class=\"ranking_header\">Name</th>\n")
    f.write("         <th class=\"ranking_header\">Total Points</th>\n")
    f.write("       </tr>\n")

    sorted_participants = sorted(participants, key=lambda x: x.total_points, reverse=True)

    # We now remove all the participants that are not from the country we are looking for
    sorted_participants = [participant for participant in sorted_participants if participant.country == country.country_type]

    row_color = "row_odd"
    previous_rank = -1

    for participant in sorted_participants:
        if participant.rank != previous_rank:
            if row_color == "row_even":
                row_color = "row_odd"
            else:
                row_color = "row_even"
            previous_rank = participant.rank

        f.write(f"       <tr class=\"{row_color}\">\n")
        f.write(f"         <td class=\"just_center\">{participant.rank}</td>\n")
        f.write(f"         <td><a href=\"poolparticipant{participant.native_index}.html\">{participant.name}</a></td>\n")
        f.write(f"         <td class=\"just_center\">{participant.total_points}</td>\n")
        f.write("       </tr>\n")

    f.write("     </table>\n")


def produce_country_grid(generation_timestamp: str, for_website_directory: str, participants: List[Participant], countries: List[CountryData]) -> None:
    for participant in participants:
        for country_participant in countries:
            if participant.country == country_participant.country_type:
                country_participant.number += 1
                country_participant.total_points += participant.total_points
                break

    for country_participant in countries:
        if country_participant.number != 0:
            country_participant.average_points = country_participant.total_points / country_participant.number
        else:
            country_participant.average_points = 0
        country_participant.average_points = f"{country_participant.average_points:.2f}"

    # Let's sort based on the average points
    sorted_country_participant = []
    sorted_country_participant = sorted(countries, key=lambda x: x.average_points, reverse=True)

    iPreviousTotalPoints = -1
    country_participant_index = 0
    iRank = -1

    for country_participant_index, country_participant in enumerate(sorted_country_participant):
        if country_participant.total_points != iPreviousTotalPoints:
            iRank = country_participant_index + 1
            iPreviousTotalPoints = country_participant.total_points
        country_participant.rank = iRank

    console.print()
    console.print("Stats by Country", style="yellow")
    for country_participant in sorted_country_participant:
        console.print(f"{country_participant.average_points} - {country_participant.name}", style="bold green")

    # Let's generate a html file with the results
    with open(f"{for_website_directory}\\country_stats.html", 'w', encoding='utf-8', newline='\r\n') as f:
        # Let's create a table of 20 tables arranged 5 rows of 4 columns
        f.write("<!DOCTYPE html>\n")
        f.write("<html lang=\"en\">\n")
        f.write("  <head>\n")
        f.write("     <meta charset=\"UTF-8\">\n")
        f.write(f"    <title>Stats by Country (Generated on {generation_timestamp})</title>\n")
        f.write(f"    <link rel=\"stylesheet\" type=\"text/css\" href=\"pool_style.css?v=1.1\">\n")
        f.write(f"    <link rel=\"icon\" href=\"global6.ico\" type=\"image/x-icon\">\n")
        f.write("  </head>\n")

        f.write("\n")
        f.write("  <body>\n")

        write_header(generation_timestamp, f)

        # Let's create a table with three elements
        f.write("     <table class=\"ranking-table\">\n")

        f.write("       <tr>\n")
        f.write(f"         <th colspan=\"4\" class=\"colspan-4\">Stats by Country</th>\n")
        f.write("       </tr>\n")

        f.write("       <tr>\n")
        f.write("         <th class=\"ranking_header\">Rank</th>\n")
        f.write("         <th class=\"ranking_header\">Country</th>\n")
        f.write("         <th class=\"ranking_header\">Participants</th>\n")
        f.write("         <th class=\"ranking_header\">Average</th>\n")
        f.write("       </tr>\n")

        row_color = "row_odd"
        previous_rank = -1

        for country_participant in sorted_country_participant:
            if country_participant.rank != previous_rank:
                if row_color == "row_even":
                    row_color = "row_odd"
                else:
                    row_color = "row_even"
                previous_rank = country_participant.rank

            f.write(f"       <tr class=\"{row_color}\">\n")
            f.write("         <td class=\"just_center\">\n")
            f.write(f"        {country_participant.rank}\n")
            f.write("         </td>\n")
            f.write("         <td>\n")
            f.write(f"         <img src=\"{country_participant.icon_filename}\" alt=\"{country_participant.name}\">&nbsp;{country_participant.name}\n")
            f.write("         </td>\n")
            f.write("         <td class=\"just_center\">\n")
            f.write(f"         {country_participant.number}\n")
            f.write("         </td>\n")
            f.write("         <td  class=\"just_center\">\n")
            f.write(f"         {country_participant.average_points}\n")
            f.write("         </td>\n")
            f.write("       </tr>\n")

        f.write("     </table>\n")

        f.write("<BR>\n")

        # Let's create a table with three elements
        # 1. One with a table with participants sorted by their point
        # 2. One empty area
        # 3. One with a table with participants sorted by their name
        f.write("     <table class=\"outer-ranking-table\">\n")

        # f.write("       <tr>\n")
        # f.write(f"         <th colspan=\"2\" class=\"colspan-2\">Ranking (generated on {generation_timestamp})</th>\n")
        # f.write("       </tr>\n")

        f.write("       <tr>\n")
        f.write("         <td>\n")
        write_ranking_country_table(f, participants, sorted_country_participant[0])
        f.write("         </td>\n")
        f.write("         <td>\n")
        f.write("         &nbsp;\n")
        f.write("         </td>\n")
        f.write("         <td>\n")
        write_ranking_country_table(f, participants, sorted_country_participant[1])
        f.write("         </td>\n")
        f.write("       </tr>\n")
        f.write("     </table>\n")

        write_footer(generation_timestamp, f)

        f.write("  </body>\n")
        f.write("</html>\n")


def write_ranking_office_table(f, participants: List[Participant], office: OfficeData) -> None:
    f.write("     <table class=\"ranking-table\">\n")

    f.write("       <tr>\n")
    f.write(f"       <th colspan=\"3\" class=\"colspan-3\">\n")
    f.write(f"         <img src=\"{office.icon_filename}\" alt=\"{office.name}\">&nbsp;{office.name}&nbsp;<img src=\"{office.icon_filename}\" alt=\"{office.name}\">\n")
    f.write(f"       </th>\n")
    f.write("       </tr>\n")

    f.write("       <tr>\n")
    f.write("         <th class=\"ranking_header\">Rank</th>\n")
    f.write("         <th class=\"ranking_header\">Name</th>\n")
    f.write("         <th class=\"ranking_header\">Total Points</th>\n")
    f.write("       </tr>\n")

    sorted_participants = sorted(participants, key=lambda x: x.total_points, reverse=True)

    # We now remove all the participants that are not from the office we are looking for
    sorted_participants = [participant for participant in sorted_participants if participant.office == office.office_type]

    row_color = "row_odd"
    previous_rank = -1

    for participant in sorted_participants:
        if participant.rank != previous_rank:
            if row_color == "row_even":
                row_color = "row_odd"
            else:
                row_color = "row_even"
            previous_rank = participant.rank

        f.write(f"       <tr class=\"{row_color}\">\n")
        f.write(f"         <td class=\"just_center\">{participant.rank}</td>\n")
        f.write(f"         <td><a href=\"poolparticipant{participant.native_index}.html\">{participant.name}</a></td>\n")
        f.write(f"         <td class=\"just_center\">{participant.total_points}</td>\n")
        f.write("       </tr>\n")

    f.write("     </table>\n")


def produce_office_grid(generation_timestamp: str, for_website_directory: str, participants: List[Participant], offices: List[OfficeData]) -> None:
    for participant in participants:
        for office_participant in offices:
            if participant.office == office_participant.office_type:
                office_participant.number += 1
                office_participant.total_points += participant.total_points
                break

    for office_participant in offices:
        if office_participant.number != 0:
            office_participant.average_points = office_participant.total_points / office_participant.number
        else:
            office_participant.average_points = 0
        office_participant.average_points = f"{office_participant.average_points:.2f}"

    # Let's sort based on the average points
    sorted_office_participant = []
    sorted_office_participant = sorted(offices, key=lambda x: float(x.average_points),reverse=True)

    iPreviousTotalPoints = -1
    office_participant_index = 0
    iRank = -1

    for office_participant_index, office_participant in enumerate(sorted_office_participant):
        if office_participant.total_points != iPreviousTotalPoints:
            iRank = office_participant_index + 1
            iPreviousTotalPoints = office_participant.total_points
        office_participant.rank = iRank

    console.print()
    console.print("Stats by Offices", style="yellow")
    for office_participant in sorted_office_participant:
        console.print(f"{float(office_participant.average_points):7.2f} - {office_participant.name}", style="bold green")

    # Let's generate a html file with the results
    with open(f"{for_website_directory}\\office_stats.html", 'w', encoding='utf-8', newline='\r\n') as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html lang=\"en\">\n")
        f.write("  <head>\n")
        f.write("     <meta charset=\"UTF-8\">\n")
        f.write(f"    <title>Stats by Offices (Generated on {generation_timestamp})</title>\n")
        f.write(f"    <link rel=\"stylesheet\" type=\"text/css\" href=\"pool_style.css?v=1.1\">\n")
        f.write(f"    <link rel=\"icon\" href=\"global6.ico\" type=\"image/x-icon\">\n")
        f.write("  </head>\n")

        f.write("\n")
        f.write("  <body>\n")

        write_header(generation_timestamp, f)

        # Let's create a table with three elements
        f.write("     <table class=\"ranking-table\">\n")

        f.write("       <tr>\n")
        f.write(f"         <th colspan=\"4\" class=\"colspan-4\">Stats by Offices</th>\n")
        f.write("       </tr>\n")

        f.write("       <tr>\n")
        f.write("         <th class=\"ranking_header\">Rank</th>\n")
        f.write("         <th class=\"ranking_header\">Office</th>\n")
        f.write("         <th class=\"ranking_header\">Participants</th>\n")
        f.write("         <th class=\"ranking_header\">Average</th>\n")
        f.write("       </tr>\n")

        row_color = "row_odd"
        previous_rank = -1

        for office_participant in sorted_office_participant:
            if office_participant.rank != previous_rank:
                if row_color == "row_even":
                    row_color = "row_odd"
                else:
                    row_color = "row_even"
                previous_rank = office_participant.rank

            f.write(f"       <tr class=\"{row_color}\">\n")
            f.write("         <td class=\"just_center\">\n")
            f.write(f"        {office_participant.rank}\n")
            f.write("         </td>\n")
            f.write("         <td class=\"just_center_vertical\">\n")
            f.write(f"         <img src=\"{office_participant.icon_filename}\" alt=\"{office_participant.name}\">&nbsp;{office_participant.name}\n")
            f.write("         </td>\n")
            f.write("         <td class=\"just_center\">\n")
            f.write(f"         {office_participant.number}\n")
            f.write("         </td>\n")
            f.write("         <td  class=\"just_center\">\n")
            f.write(f"         {office_participant.average_points}\n")
            f.write("         </td>\n")
            f.write("       </tr>\n")

        f.write("     </table>\n")

        f.write("<BR>\n")
        # Let's create a table with three elements
        # 1. One with a table with participants sorted by their point
        # 2. One empty area
        # 3. One with a table with participants sorted by their name
        f.write("     <table class=\"outer-ranking-table\">\n")
        f.write("       <tr>\n")
        for office_participant in sorted_office_participant:
            f.write("         <td>\n")
            write_ranking_office_table(f, participants, office_participant)
            f.write("         </td>\n")
            f.write("         <td>\n")
            f.write("         &nbsp;\n")
            f.write("         </td>\n")
        f.write("       </tr>\n")
        f.write("     </table>\n")

        write_footer(generation_timestamp, f)

        f.write("  </body>\n")
        f.write("</html>\n")


def produce_email_message(generation_timestamp: str, for_website_directory: str, participants: List[Participant], offices: List[OfficeData]) -> None:
    # Copy to email_participants list all the participants sorted by their total points
    email_participants = sorted(participants, key=lambda x: x.total_points, reverse=True)

    # Let's generate a html file with the results
    with open(f"{for_website_directory}\\email_message.html", 'w', encoding='utf-8', newline='\r\n') as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html lang=\"en\">\n")
        f.write("  <head>\n")
        f.write("     <meta charset=\"UTF-8\">\n")
        f.write(f"    <title>Bluberi Hockey Pool 2026-2027 (Generated on {generation_timestamp})</title>\n")
        f.write(f"    <link rel=\"stylesheet\" type=\"text/css\" href=\"pool_style.css?v=1.1\">\n")
        f.write(f"    <link rel=\"icon\" href=\"global6.ico\" type=\"image/x-icon\">\n")
        f.write("  </head>\n")

        f.write("\n")
        f.write("  <body>\n")

        write_header(generation_timestamp, f, use_external_path=True)

        # Let's create a table with three elements
        f.write("     <table class=\"ranking-table\">\n")

        f.write("       <tr>\n")
        f.write("         <th class=\"ranking_header\">Rank</th>\n")
        f.write("         <th class=\"ranking_header\">Participants</th>\n")
        f.write("         <th class=\"ranking_header\">Points</th>\n")
        f.write("       </tr>\n")

        row_color = "row_odd"
        previous_rank = -1

        for office_participant in email_participants:
            if office_participant.rank != previous_rank:
                if row_color == "row_even":
                    row_color = "row_odd"
                else:
                    row_color = "row_even"
                previous_rank = office_participant.rank

            f.write(f"       <tr class=\"{row_color}\">\n")
            f.write("         <td class=\"just_center\">\n")
            f.write(f"          {office_participant.rank}\n")
            f.write("         </td>\n")
            f.write("         <td class=\"just_center_vertical\">\n")
            f.write(f"          <a href=\"{gExternalPath}poolparticipant{office_participant.native_index}.html\">{office_participant.name}</a>\n")
            f.write("         </td>\n")
            f.write("         <td  class=\"just_center\">\n")
            f.write(f"          {office_participant.total_points}\n")
            f.write("         </td>\n")
            f.write("       </tr>\n")

        f.write("     </table>\n")

        write_footer(generation_timestamp, f, use_external_path=True)

        f.write("  </body>\n")
        f.write("</html>\n")


def produce_injury_report_grid(generation_timestamp: str, for_website_directory: str, choices: List[Choice]) -> None:
    injured_choices = [choice for choice in choices if choice.injury_comment != ""]
    injured_choices.sort(key=lambda choice: locale.strxfrm(choice.name))

    with open(f"{for_website_directory}\\injury_report.html", 'w', encoding='utf-8', newline='\r\n') as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html lang=\"en\">\n")
        f.write("  <head>\n")
        f.write("     <meta charset=\"UTF-8\">\n")
        f.write(f"    <title>Injury Reports (Generated on {generation_timestamp})</title>\n")
        f.write(f"    <link rel=\"stylesheet\" type=\"text/css\" href=\"pool_style.css?v=1.1\">\n")
        f.write(f"    <link rel=\"icon\" href=\"global6.ico\" type=\"image/x-icon\">\n")
        f.write("  </head>\n")

        f.write("\n")
        f.write("  <body>\n")

        write_header(generation_timestamp, f)

        f.write("     <table class=\"ranking-table\">\n")

        f.write("       <tr>\n")
        f.write("         <th colspan=\"3\" class=\"colspan-3\">Injury Reports</th>\n")
        f.write("       </tr>\n")

        f.write("       <tr>\n")
        f.write("         <th class=\"ranking_header\">Player</th>\n")
        f.write("         <th class=\"ranking_header\">Team</th>\n")
        f.write("         <th class=\"ranking_header\">Status / Comment</th>\n")
        f.write("       </tr>\n")

        row_color = "row_odd"

        for choice in injured_choices:
            row_color = "row_even" if row_color == "row_odd" else "row_odd"

            f.write(f"       <tr class=\"{row_color}\">\n")
            f.write(f"         <td>{choice.name}</td>\n")
            f.write(f"         <td class=\"just_center\">{choice.team_abreviation}</td>\n")
            f.write(f"         <td>{choice.injury_comment}</td>\n")
            f.write("       </tr>\n")

        f.write("     </table>\n")

        write_footer(generation_timestamp, f)

        f.write("  </body>\n")
        f.write("</html>\n")


def write_who_chose_who_box_table(f, box: Box, choices: List[Choice], participants: List[Participant], owner_participant: "Participant | None" = None) -> None:
    f.write("     <table class=\"ranking-table who-chose-table\">\n")

    # table-layout:fixed derives column widths from the first row, so an explicit colgroup is required.
    f.write("       <colgroup>\n")
    f.write("         <col class=\"col-choice\">\n")
    f.write("         <col class=\"col-points\">\n")
    f.write("         <col class=\"col-nb\">\n")
    f.write("         <col class=\"col-participants\">\n")
    f.write("       </colgroup>\n")

    f.write("       <tr>\n")
    f.write(f"         <th colspan=\"4\" class=\"colspan-4\">{box.name}</th>\n")
    f.write("       </tr>\n")

    f.write("       <tr>\n")
    f.write("         <th class=\"ranking_header col-choice\">Choice</th>\n")
    f.write("         <th class=\"ranking_header col-points\">Points</th>\n")
    f.write("         <th class=\"ranking_header col-nb\">Nb</th>\n")
    f.write("         <th class=\"ranking_header col-participants\">Participants</th>\n")
    f.write("       </tr>\n")

    row_color = "row_odd"

    for choice_index in box.choices:
        choice = choices[choice_index]

        chosen_by = [participant for participant in participants if choice_index in participant.choices]

        # Multi-level sort key:
        # 1) Owner first: (participant is not owner_participant) returns False (0) for owner, True (1) for others
        # 2) Primary sort: participant.rank
        # 3) Secondary sort (tie-breaker): locale.strxfrm(participant.name)
        chosen_by.sort(
            key=lambda participant: (
                owner_participant is not None and participant is not owner_participant,
                participant.rank,
                locale.strxfrm(participant.name)
            )
        )

        chosen_by_links = []
        for participant in chosen_by:
            link = f"<a class=\"participant-hover-link\" href=\"poolparticipant{participant.native_index}.html\">{participant.rank}-{participant.name}</a>"
            if owner_participant is not None and participant is owner_participant:
                link = f"<span class=\"who-chose-own-participant\">{link}</span>"
            chosen_by_links.append(link)



        if owner_participant is not None:
            if owner_participant.choices[choice.box_number] == choice_index:
                if owner_participant.lowest_round == choice.box_number:
                    row_class = "participant_choice_dropped"
                elif choice.nb_points == box.best_points:
                    row_class = "participant_choice_best"
                elif choice.nb_points == box.worse_points:
                    row_class = "participant_choice_worse"
                else:
                    row_class = "participant_choice_normal"
            else:
                if owner_participant.lowest_round == choice.box_number:
                    row_class = "participant_not_choice_dropped"
                else:
                    row_class = "participant_not_choice_normal"
        else:
            row_color = "row_even" if row_color == "row_odd" else "row_odd"
            row_class = row_color

        f.write(f"       <tr class=\"{row_class}\">\n")
        f.write(f"         <td class=\"col-choice\">{choice.name} ({choice.team_abreviation.lower()})</td>\n")
        f.write(f"         <td class=\"just_center col-points\">{choice.nb_points}</td>\n")
        f.write(f"         <td class=\"just_center col-nb\">{len(chosen_by)}</td>\n")
        f.write(f"         <td class=\"col-participants\">{', '.join(chosen_by_links)}</td>\n")
        f.write("       </tr>\n")

    f.write("     </table>\n")


def produce_who_chose_who_grid(generation_timestamp: str, for_website_directory: str, boxes: List[Box], choices: List[Choice], participants: List[Participant]) -> None:
    # Let's generate a html file showing, for each box, who chose which choice.
    with open(f"{for_website_directory}\\who_chose_who.html", 'w', encoding='utf-8', newline='\r\n') as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html lang=\"en\">\n")
        f.write("  <head>\n")
        f.write("     <meta charset=\"UTF-8\">\n")
        f.write(f"    <title>Who Chose Who (Generated on {generation_timestamp})</title>\n")
        f.write(f"    <link rel=\"stylesheet\" type=\"text/css\" href=\"pool_style.css?v=1.1\">\n")
        f.write(f"    <link rel=\"icon\" href=\"global6.ico\" type=\"image/x-icon\">\n")
        f.write("  </head>\n")

        f.write("\n")
        f.write("  <body>\n")

        write_header(generation_timestamp, f)

        for box in boxes:
            write_who_chose_who_box_table(f, box, choices, participants)
            f.write("<BR>\n")

        write_footer(generation_timestamp, f)

        f.write("  </body>\n")
        f.write("</html>\n")

    # Let's generate one html file per participant, highlighting their own choices.
    for participant in participants:
        with open(f"{for_website_directory}\\who_chose_who{participant.native_index}.html", 'w', encoding='utf-8', newline='\r\n') as f:
            f.write("<!DOCTYPE html>\n")
            f.write("<html lang=\"en\">\n")
            f.write("  <head>\n")
            f.write("     <meta charset=\"UTF-8\">\n")
            f.write(f"    <title>Who Chose Who: {participant.name} (Generated on {generation_timestamp})</title>\n")
            f.write(f"    <link rel=\"stylesheet\" type=\"text/css\" href=\"pool_style.css?v=1.1\">\n")
            f.write(f"    <link rel=\"icon\" href=\"global6.ico\" type=\"image/x-icon\">\n")
            f.write("  </head>\n")

            f.write("\n")
            f.write("  <body>\n")

            write_header(generation_timestamp, f)

            f.write("     <table class=\"ranking-table who-chose-table\">\n")
            f.write("       <tr>\n")
            f.write(f"         <th colspan=\"4\" class=\"colspan-4\">{ordinal(participant.rank)} - {participant.name} - {participant.total_points} points</th>\n")
            f.write("       </tr>\n")
            f.write("     </table>\n")
            f.write("<BR>\n")

            for box in boxes:
                write_who_chose_who_box_table(f, box, choices, participants, owner_participant=participant)
                f.write("<BR>\n")

            write_footer(generation_timestamp, f)

            f.write("  </body>\n")
            f.write("</html>\n")


def produce_personal_grid(generation_timestamp: str, for_website_directory: str, boxes: List[Box], choices: List[Choice], participants: List[Participant]) -> None:
    # Let's generate a html file with the results
    for iParticipantIndex, participant in enumerate(participants):
        with open(f"{for_website_directory}\\poolparticipant{iParticipantIndex}.html", 'w', encoding='utf-8', newline='\r\n') as f:
            # Let's create a table of 20 tables arranged 5 rows of 4 columns

            f.write("<!DOCTYPE html>\n")
            f.write("<html lang=\"en\">\n")
            f.write("  <head>\n")
            f.write("     <meta charset=\"UTF-8\">\n")
            f.write(f"    <title>Participant: {participant.name}</title>\n")
            f.write(f"    <link rel=\"stylesheet\" type=\"text/css\" href=\"pool_style.css?v=1.1\">\n")
            f.write(f"    <link rel=\"icon\" href=\"global6.ico\" type=\"image/x-icon\">\n")
            f.write("\n")
            f.write("  </head>\n")

            f.write("\n")
            f.write("  <body>\n")

            if not gFlagSelectionGrid:
                write_header(generation_timestamp, f, participant_native_index=participant.native_index)

            f.write("     <table class=\"outer-table\">\n")

            NumberOfRow = 3

            if gFlagSelectionGrid:
                header_line = 'Grille de Sélection / Selection Grid'
            else:
                header_line = f"{ordinal(participant.rank)} - {participant.name} - {participant.total_points} points"

            f.write("       <tr>\n")
            f.write(f"         <th colspan=\"{NumberOfRow}\" class=\"colspan-{NumberOfRow}\">{header_line}</th>\n")
            f.write("       </tr>            \n")

            for i in range(8):
                f.write("      <tr>\n")
                # max_choices = max(boxes[i*NumberOfRow].nb_choices, boxes[i*NumberOfRow+1].nb_choices, boxes[i*NumberOfRow+2].nb_choices)
                max_choices = 6
                for j in range(3):
                    f.write(f"        <td>\n")
                    f.write(f"          <table  class=\"inner-table\" border='0'>\n")

                    box_number = (i*NumberOfRow)+j

                    f.write(f"            <tr>\n")
                    if participant.lowest_round == box_number:
                        th_class_name = '"box_header_dropped"'
                    else:
                        th_class_name = '"box_header_normal"'

                    if gFlagSelectionGrid:
                        th_class_name = '"box_header_normal"'

                    if gFlagSelectionGrid:
                        f.write(f"              <th colspan='3' class={th_class_name}>{boxes[box_number].name}</th>\n")
                    else:
                        if (boxes[box_number].box_style == BoxStyle.TBS_TEAM) or (boxes[box_number].box_style == BoxStyle.TBS_GOALIE):
                            f.write(f"              <th colspan='5' class={th_class_name}>{boxes[box_number].name}</th>\n")
                        if boxes[box_number].box_style == BoxStyle.TBS_SKATERS:
                            f.write(f"              <th colspan='6' class={th_class_name}>{boxes[box_number].name}</th>\n")
                    f.write(f"            </tr>\n")

                    f.write(f'            <tr class={"participant_choice_normal"}>\n')
                    if (boxes[box_number].box_style == BoxStyle.TBS_TEAM):
                        f.write(f"              <td style=\"text-align: center;\">Teams</td>\n")
                        if not gFlagSelectionGrid:
                            f.write(f"              <td style=\"text-align: center;\">GP</td>\n")
                            f.write(f"              <td style=\"text-align: center;\">W</td>\n")
                            f.write(f"              <td style=\"text-align: center;\">Pts</td>\n")
                        f.write(f"              <td style=\"text-align: center;\">Avg</td>\n")
                        if gFlagSelectionGrid:
                            f.write(f"              <td style=\"text-align: center;\">\"X\"</td>\n")

                    if boxes[box_number].box_style == BoxStyle.TBS_SKATERS:
                        f.write(f"              <td style=\"text-align: center;\">Players</td>\n")
                        if not gFlagSelectionGrid:
                            f.write(f"              <td style=\"text-align: center;\">GP</td>\n")
                            f.write(f"              <td style=\"text-align: center;\">G</td>\n")
                            f.write(f"              <td style=\"text-align: center;\">A</td>\n")
                            f.write(f"              <td style=\"text-align: center;\">Pts</td>\n")
                        f.write(f"              <td style=\"text-align: center;\">Avg</td>\n")
                        if gFlagSelectionGrid:
                            f.write(f"              <td style=\"text-align: center;\">\"X\"</td>\n")

                    if (boxes[box_number].box_style == BoxStyle.TBS_GOALIE):
                        f.write(f"              <td style=\"text-align: center;\">Players</td>\n")
                        if not gFlagSelectionGrid:
                            f.write(f"              <td style=\"text-align: center;\">GP</td>\n")
                            f.write(f"              <td style=\"text-align: center;\">W</td>\n")
                            f.write(f"              <td style=\"text-align: center;\">Pts</td>\n")
                        f.write(f"              <td style=\"text-align: center;\">Avg</td>\n")
                        if gFlagSelectionGrid:
                            f.write(f"              <td style=\"text-align: center;\">\"X\"</td>\n")
                    f.write(f"            </tr>\n")

                    for k in range(max_choices):
                        if k < len(boxes[box_number].choices):
                            choice = choices[boxes[box_number].choices[k]]

                            if participant.choices[box_number] == boxes[box_number].choices[k]:
                                if participant.lowest_round == box_number:
                                    tr_participant = '"participant_choice_dropped"'
                                elif choice.nb_points == boxes[box_number].best_points:
                                    tr_participant = '"participant_choice_best"'
                                elif choice.nb_points == boxes[box_number].worse_points:
                                    tr_participant = '"participant_choice_worse"'
                                else:
                                    tr_participant = '"participant_choice_normal"'
                            else:
                                if participant.lowest_round == box_number:
                                    tr_participant = '"participant_not_choice_dropped"'
                                else:
                                    tr_participant = '"participant_not_choice_normal"'

                            if gFlagSelectionGrid:
                                tr_participant = '"participant_not_choice_normal"'

                            f.write(f"            <tr class={tr_participant}>\n")

                            if boxes[box_number].box_style == BoxStyle.TBS_TEAM:
                                f.write(f"              <td>{choice.name}</td>\n")

                            if (boxes[box_number].box_style == BoxStyle.TBS_SKATERS) or (boxes[box_number].box_style == BoxStyle.TBS_GOALIE):
                                f.write(f"              <td>{choice.name} ({choice.team_abreviation.lower()})</td>\n")

                            if not gFlagSelectionGrid:
                                if (boxes[box_number].box_style == BoxStyle.TBS_TEAM) or (boxes[box_number].box_style == BoxStyle.TBS_GOALIE):
                                    f.write(f"              <td style=\"text-align: right;\">{choice.nb_gameplayed}&nbsp;</td>\n")  
                                    f.write(f"              <td style=\"text-align: right;\">{choice.nb_wins}&nbsp;</td>\n")
                                if boxes[box_number].box_style == BoxStyle.TBS_SKATERS:
                                    f.write(f"              <td style=\"text-align: right;\">{choice.nb_gameplayed}&nbsp;</td>\n")  
                                    f.write(f"              <td style=\"text-align: right;\">{choice.nb_goals}&nbsp;</td>\n")
                                    f.write(f"              <td style=\"text-align: right;\">{choice.nb_assists}&nbsp;</td>\n")
                                f.write(f"              <td style=\"text-align: right;\">{choice.nb_points}&nbsp;</td>\n")

                            # Write the average under with two decimals after the point of choice.nb_points over choice.nb_gameplayed
                            f.write(f"              <td style=\"text-align: right;\">{(choice.nb_points / choice.nb_gameplayed) if choice.nb_gameplayed > 0 else 0:.2f}&nbsp;</td>\n")
                            if gFlagSelectionGrid:
                                f.write(f"              <td style=\"text-align: center;\">&nbsp;&nbsp;</td>\n")
                            f.write(f"            </tr>\n")
                        else:
                            f.write(f"            <tr>\n")
                            f.write(f"              <td>&nbsp;</td>\n")
                            f.write(f"              <td>&nbsp;</td>\n")
                            f.write(f"            </tr>\n")
                    f.write(f"          </table>\n")
                    f.write(f"        </td>\n")
                f.write("      </tr>\n")
            f.write("    </table>\n")


            # Now, add the personal graphic image showing the ranking over time for this participant.
            # It's an image. The image is generated in the plot_rankings_over_time function and is named personal_ranking_{iParticipantIndex}.png
            if gPlotOfRankingOverTime:
                f.write("<BR>\n")
                sub_path = ""
                f.write(f"<img src=\"{sub_path}rankings_{iParticipantIndex}.png\" alt=\"Ranking over time for {participant.name}\" class=\"personal-ranking-image\">\n")

            if not gFlagSelectionGrid:
                write_footer(generation_timestamp, f, participant_native_index=participant.native_index)

            f.write("  </body>\n")
            f.write("\n")
            f.write("</html>\n")


def do_all_the_work(flag_compare_nhl_vs_officepools: bool) -> None:
    global gProcessChoixesFromTmp

    today_string = datetime.date.today().strftime("%Y-%m-%d")
    today_directory = f'.\\{today_string}'

    # Let's set a variable of type string of the format YYYY-MM-DD @ hh:mm
    now = datetime.datetime.now()
    report_datetime = now.strftime("%Y-%m-%d @ %H:%M")

    os.makedirs(today_directory, exist_ok=True)
    download_directory = os.path.join(today_directory, "downloads")
    os.makedirs(download_directory, exist_ok=True)
    for_website_directory = os.path.join(today_directory, "for_website")
    os.makedirs(for_website_directory, exist_ok=True)

    choices = []
    init_choices(choices)

    # We want to generate the players choices only once at the begining of the season, from OfficePools report, we call this function and it will generate the choies.
    # GeneratePlayersChoices(choices)
    # sys.exit(0)

    boxes = []
    init_boxes(choices, boxes)
    export_choices_to_csv(choices, os.path.join(for_website_directory, "choices.csv"))
    if gProcessChoixesFromTmp:
        process_choice_files(choices, r'c:\tmp\Participants')

    # For current debugging prupose, halt script execution here.
    # sys.exit(0)

    participants = []
    init_participants(participants)

    countries = []
    init_countries(countries)

    offices = []
    init_offices(offices)

    # get_choices_skaters_stats(choices, download_directory)
    # get_choices_goalies_stats(choices, download_directory)
    # get_choices_teams_stats(choices, download_directory)
    # get_officepools_points(participants, download_directory)
    # get_officepools_points_manually(participants, download_directory)

    get_choices_skaters_stats2(choices, download_directory)
    get_choices_teams_stats2(choices, download_directory)
    get_choices_individual_teams_stats2(choices, download_directory)
    get_injury_report(choices, download_directory)

    # 2026-09-20:DB-Let's try for this year not using Office Pools!
    # get_officepools_points_from_excel_file(participants, r'c:\Users\DBisson\Downloads\custom.xls')

    validate_choices(choices, participants)

    # 2026-09-20:DB-Let's try for this year not using Office Pools!
    # validate_officepools_points(participants)

    set_best_and_worse_choices_per_boxes(boxes, choices)
    set_lowest_round(participants, choices)
    set_total_points(participants, choices)
    set_points_per_day(participants, choices)
    set_who_chose_who(participants, choices)
    sort_participants(participants)
    sort_participants_day_by_day(participants)

    if flag_compare_nhl_vs_officepools == True:
        compare_nhl_vs_officepools(participants)

    # 2026-09-20:DB-For the moment, no graph with evolution.
    if gPlotOfRankingOverTime:
        plot_rankings_over_time(participants, for_website_directory)

    copy_required_ressources(for_website_directory, offices, countries)
    procedure_css_file(for_website_directory)
    produce_personal_grid(report_datetime, for_website_directory, boxes, choices, participants)
    produce_ranking_grid(report_datetime, for_website_directory, participants)
    produce_sex_grid(report_datetime, for_website_directory, participants)
    produce_country_grid(report_datetime, for_website_directory, participants, countries)
    produce_office_grid(report_datetime, for_website_directory, participants, offices)
    produce_email_message(report_datetime, for_website_directory, participants, offices)
    produce_who_chose_who_grid(report_datetime, for_website_directory, boxes,choices,participants)
    produce_injury_report_grid(report_datetime, for_website_directory, choices)

    compress_website_directory(for_website_directory, f'c:\\tmp\\bluberi_pool_{today_string}.zip')


if __name__ == "__main__":
    freeze_start = time.perf_counter()   # high‑precision timer

    # Set the locale to French
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    console.print('----------------------------------', style='bold green')
    console.print('BLUBERI POOL GENERATOR - ver 1.1.0', style='bold green')
    console.print('----------------------------------', style='bold green')
    console.print()
    console.print(f'Number of argument:{len(sys.argv)}', style='yellow')
    for sArgument in sys.argv:
        console.print(f'                   {sArgument}', style='yellow')

    parser = argparse.ArgumentParser(description="BLUBERI POOL GENERATOR")
    parser.add_argument('--nocompare', action='store_true', help='Do not compare the NHL results with the OfficePools results')

    parser.print_help()
    console.print()

    args = parser.parse_args()

    flag_compare_nhl_vs_officepools = True
    if args.nocompare:
        flag_compare_nhl_vs_officepools = False

    # 2026-09-20:DB-Let's try for this year not using Office Pools!
    flag_compare_nhl_vs_officepools = False

    do_all_the_work(flag_compare_nhl_vs_officepools)

    # Ask the user to press a key to exit
    console.print()

    freeze_end = time.perf_counter()

    elapsed_ms = (freeze_end - freeze_start) * 1000
    print(f"Elapsed: {elapsed_ms:.2f} ms")
