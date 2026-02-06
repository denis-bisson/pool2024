from operator import index
import sys
import os
# from selenium import webdriver
# from selenium.webdriver.edge.options import Options
import time
# import bs4
import itertools
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
import pandas as pd


console = Console(highlight=False)
gExternalPath = 'https://global6.com/bluberipool/20252026/'

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
    def __init__(self, box_number, box_style: BoxStyle, nhl_id, name, team_abreviation, nb_goals, nb_assists, nb_points, nb_wins):
        self.box_number = box_number
        self.box_style = box_style
        self.nhl_id = nhl_id
        self.name = name
        self.team_abreviation = team_abreviation
        self.found = False
        self.nb_goals = nb_goals
        self.nb_assists = nb_assists
        self.nb_points = nb_points
        self.nb_wins = nb_wins
        self.who_chose = []        


class Participant:
    def __init__(self, name, choices: list, param_sex: SexType, param_country: CountryType, param_office: OfficeType):
        self.name = name
        self.lowest_round = -1
        self.total_points = 0
        if len(choices) != 20:
            raise ValueError(f"Participant must have 20 choices but has {len(choices)} for {name}")
        self.choices = choices
        self.rank = -1
        self.native_index = -1
        self.office_total_points = 0
        self.sex_type = param_sex
        self.country = param_country
        self.office = param_office


class Box:
    def __init__(self, name):
        self.name = name
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
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Tampa Bay Lightning", "TBL", 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Carolina Hurricanes", "CAR", 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Dallas Stars", "DAL", 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Vegas Golden Knights", "VGK", 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Florida Panthers", "FLA", 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "0000000", "Colorado Avalanche", "COL", 0, 0, 0, 0))

    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "New Jersey Devils", "NJD", 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Edmonton Oilers", "EDM", 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Toronto Maple Leafs", "TOR", 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Washington Capitals", "WSH", 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Winnipeg Jets", "WPG", 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "0000000", "Los Angeles Kings", "LAK", 0, 0, 0, 0))

    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "Montréal Canadiens", "MTL", 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "Columbus Blue Jackets", "CBJ", 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "St. Louis Blues", "STL", 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "Minnesota Wild", "MIN", 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "Ottawa Senators", "OTT", 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "0000000", "New York Rangers", "NYR", 0, 0, 0, 0))

    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "Anaheim Ducks", "ANA", 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "Vancouver Canucks", "VAN", 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "Seattle Kraken", "SEA", 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "New York Islanders", "NYI", 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "Detroit Red Wings", "DET", 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "0000000", "Philadelphia Flyers", "PHI", 0, 0, 0, 0))

    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8478402", "Connor McDavid", "EDM", 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8476453", "Nikita Kucherov", "TBL", 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8477492", "Nathan MacKinnon", "COL", 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8477934", "Leon Draisaitl", "EDM", 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_SKATERS, "8478864", "Kirill Kaprizov", "MIN", 0, 0, 0, 0))

    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8479318", "Auston Matthews", "TOR", 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8478420", "Mikko Rantanen", "DAL", 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8478403", "Jack Eichel", "VGK", 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8479343", "Clayton Keller", "UTA", 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_SKATERS, "8478483", "Mitch Marner", "VGK", 0, 0, 0, 0))

    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8480018", "Nick Suzuki", "MTL", 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8478550", "Artemi Panarin", "LAK", 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8477956", "David Pastrnak", "BOS", 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8477939", "William Nylander", "TOR", 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "8479407", "Jesper Bratt", "NJD", 0, 0, 0, 0))

    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8471675", "Sidney Crosby", "PIT", 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8480069", "Cale Makar", "COL", 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8479542", "Brandon Hagel", "TBL", 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8480039", "Martin Necas", "COL", 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "8478398", "Kyle Connor", "WPG", 0, 0, 0, 0))

    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8482116", "Tim Stützle", "OTT", 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8480027", "Jason Robertson", "DAL", 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8478010", "Brayden Point", "TBL", 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "8476468", "J.T. Miller", "NYR", 0, 0, 0, 0))

    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "8476460", "Mark Scheifele", "WPG", 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "8484144", "Connor Bedard", "CHI", 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "8482078", "Lucas Raymond", "DET", 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "8477933", "Sam Reinhart", "FLA", 0, 0, 0, 0))

    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "8477404", "Jake Guentzel", "TBL", 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "8476887", "Filip Forsberg", "NSH", 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "8478427", "Sebastian Aho", "CAR", 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "8477946", "Dylan Larkin", "DET", 0, 0, 0, 0))

    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8481557", "Matt Boldy", "MIN", 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8471214", "Alex Ovechkin", "WSH", 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8482093", "Seth Jarvis", "CAR", 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "8478440", "Dylan Strome", "WSH", 0, 0, 0, 0))

    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8480002", "Nico Hischier", "NJD", 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8483431", "Logan Cooley", "UTA", 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8482175", "JJ Peterka", "UTA", 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "8482740", "Wyatt Johnston", "DAL", 0, 0, 0, 0))

    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "8477960", "Adrian Kempe", "LAK", 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "8481540", "Cole Caufield", "MTL", 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "8478439", "Travis Konecny", "PHI", 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "8484801", "Macklin Celebrini", "SJS", 0, 0, 0, 0))

    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8480012", "Elias Pettersson", "VAN", 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8479420", "Tage Thompson", "BUF", 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8478449", "Roope Hintz", "DAL", 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "8480801", "Brady Tkachuk", "OTT", 0, 0, 0, 0))

    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8475166", "John Tavares", "TOR", 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8479385", "Jordan Kyrou", "STL", 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8477949", "Alex Tuch", "BUF", 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "8478445", "Mathew Barzal", "NYI", 0, 0, 0, 0))

    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8480800", "Quinn Hughes", "VAN", 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8480839", "Rasmus Dahlin", "BUF", 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8483457", "Lane Hutson", "MTL", 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8480803", "Evan Bouchard", "EDM", 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_SKATERS, "8479323", "Adam Fox", "NYR", 0, 0, 0, 0))

    choices.append(Choice(17, BoxStyle.TBS_GOALIE, "8478499", "Adin Hill", "VGK", 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_GOALIE, "8476945", "Connor Hellebuyck", "WPG", 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_GOALIE, "8479979", "Jake Oettinger", "DAL", 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_GOALIE, "8476883", "Andrei Vasilevskiy", "TBL", 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_GOALIE, "8478048", "Igor Shesterkin", "NYR", 0, 0, 0, 0))

    choices.append(Choice(18, BoxStyle.TBS_GOALIE, "8479973", "Stuart Skinner", "EDM", 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_GOALIE, "8475683", "Sergei Bobrovsky", "FLA", 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_GOALIE, "8474593", "Jacob Markstrom", "NJD", 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_GOALIE, "8478007", "Elvis Merzlikins", "CBJ", 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_GOALIE, "8481692", "Dustin Wolf", "CGY", 0, 0, 0, 0))

    choices.append(Choice(19, BoxStyle.TBS_GOALIE, "8475311", "Darcy Kuemper", "LAK", 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_GOALIE, "8478470", "Samuel Montembeault", "MTL", 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_GOALIE, "8480313", "Logan Thompson", "WSH", 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_GOALIE, "8479406", "Filip Gustavsson", "MIN", 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_GOALIE, "8476999", "Linus Ullmark", "OTT", 0, 0, 0, 0))


def init_boxes(choices: list, boxes: list) -> None:
    boxes.append(Box("Teams 1"))
    boxes.append(Box("Teams 2"))
    boxes.append(Box("Teams 3"))
    boxes.append(Box("Point-getters 1"))
    boxes.append(Box("Point-getters 2"))
    boxes.append(Box("Point-getters 3"))
    boxes.append(Box("Point-getters 4"))
    boxes.append(Box("Point-getters 5"))
    boxes.append(Box("Point-getters 6"))
    boxes.append(Box("Point-getters 7"))
    boxes.append(Box("Point-getters 8"))
    boxes.append(Box("Point-getters 9"))
    boxes.append(Box("Point-getters 10"))
    boxes.append(Box("Point-getters 11"))
    boxes.append(Box("Point-getters 12"))
    boxes.append(Box("Point-getters 13"))
    boxes.append(Box("Point-getters 14"))
    boxes.append(Box("Goalies 1"))
    boxes.append(Box("Goalies 2"))
    boxes.append(Box("Goalies 3"))

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


def init_participants(participants: list) -> None:
    participants.append(Participant("Denis Bisson", [4, 7, 12, 23, 28, 31, 34, 40, 45, 51, 52, 59, 63, 65, 68, 72, 78, 84, 87, 92], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Craig Vinciguerra", [3, 9, 15, 19, 27, 31, 36, 40, 45, 51, 52, 59, 60, 64, 70, 73, 79, 83, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Hugues Labrecque", [2, 10, 15, 19, 25, 31, 36, 40, 46, 49, 52, 57, 61, 66, 69, 72, 76, 82, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Yves Lavoie", [1, 10, 12, 19, 24, 31, 34, 43, 45, 51, 54, 59, 60, 65, 68, 73, 78, 82, 90, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Dylan Howe", [5, 7, 12, 19, 26, 31, 37, 39, 47, 48, 54, 56, 60, 65, 68, 72, 76, 82, 86, 92], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("François Vigneault", [3, 8, 14, 18, 24, 33, 37, 39, 46, 48, 52, 57, 63, 64, 69, 72, 76, 81, 86, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Brandon Smith", [5, 7, 15, 22, 26, 33, 36, 40, 45, 51, 53, 57, 60, 64, 69, 72, 79, 83, 88, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Pierre Guay", [5, 7, 16, 19, 24, 33, 36, 40, 45, 51, 52, 57, 60, 67, 70, 72, 76, 82, 87, 91], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Andrew McCallum", [3, 9, 14, 19, 24, 31, 34, 40, 47, 51, 52, 59, 60, 65, 70, 73, 76, 82, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Jeremie Cormier", [3, 10, 16, 19, 27, 31, 35, 40, 44, 48, 54, 59, 60, 64, 71, 73, 79, 81, 86, 95], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Patrick Bellavance Marcoux", [5, 7, 17, 19, 24, 30, 36, 40, 45, 51, 54, 58, 63, 64, 70, 75, 79, 85, 87, 95], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Eric Colgan", [3, 10, 12, 19, 24, 31, 34, 43, 46, 48, 54, 57, 63, 66, 69, 72, 76, 82, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Yvan Paradis", [3, 8, 16, 19, 24, 30, 36, 43, 44, 50, 52, 56, 61, 67, 68, 75, 76, 81, 88, 92], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Jeff Baker", [3, 8, 15, 22, 28, 31, 36, 39, 45, 51, 52, 57, 60, 66, 71, 72, 76, 82, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Samantha Poisson", [4, 8, 13, 22, 24, 31, 35, 43, 45, 50, 52, 58, 62, 65, 71, 72, 80, 81, 86, 91], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Bruno Aird", [3, 9, 13, 21, 27, 29, 38, 39, 44, 49, 52, 56, 60, 64, 71, 75, 77, 85, 86, 91], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Charles Rutherford", [3, 9, 12, 19, 24, 33, 36, 43, 45, 48, 54, 57, 63, 66, 70, 74, 76, 82, 86, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Dominic Lachance", [2, 10, 14, 19, 25, 31, 36, 40, 46, 51, 52, 59, 63, 65, 70, 72, 76, 82, 87, 92], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Luc McCutcheon", [3, 7, 16, 19, 27, 31, 36, 39, 44, 51, 52, 57, 60, 65, 71, 72, 77, 82, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Olivier Lafrenière", [2, 8, 15, 22, 24, 33, 35, 43, 44, 49, 52, 59, 63, 67, 68, 72, 77, 83, 88, 94], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("François Hébert", [3, 10, 12, 22, 25, 33, 36, 43, 46, 48, 52, 57, 60, 66, 69, 72, 76, 85, 89, 92], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Francois Leger", [3, 7, 17, 19, 24, 33, 35, 40, 46, 51, 52, 58, 63, 67, 71, 72, 76, 82, 87, 91], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Benoit Lapolice", [3, 9, 12, 19, 25, 33, 34, 43, 46, 50, 52, 57, 61, 65, 70, 72, 76, 82, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Sandra St-Onge", [2, 8, 16, 19, 24, 29, 36, 43, 45, 51, 54, 57, 60, 65, 69, 72, 76, 82, 86, 95], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Vince Catalano", [3, 8, 15, 19, 24, 33, 36, 40, 46, 51, 52, 59, 63, 67, 69, 72, 76, 81, 87, 91], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Derek Pacuk", [3, 7, 15, 22, 26, 31, 37, 43, 45, 51, 52, 58, 62, 67, 69, 75, 76, 82, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Scott McSorley", [2, 10, 15, 22, 27, 33, 36, 43, 45, 51, 52, 57, 60, 66, 69, 72, 76, 82, 90, 93], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Nick Lape", [3, 7, 16, 23, 27, 30, 34, 39, 47, 50, 55, 59, 62, 65, 68, 75, 77, 84, 90, 92], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_RENO))
    participants.append(Participant("Gabe Herod", [4, 6, 17, 23, 26, 30, 37, 42, 44, 49, 55, 56, 61, 65, 68, 75, 78, 85, 89, 92], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Quentin Langelot", [5, 8, 12, 21, 26, 30, 38, 40, 44, 50, 54, 57, 61, 67, 68, 72, 76, 84, 87, 95], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Stéphan Généreux", [3, 6, 15, 19, 24, 30, 36, 42, 47, 50, 55, 56, 60, 65, 71, 75, 76, 85, 90, 94], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Mike Wabschall", [3, 10, 17, 20, 25, 33, 36, 43, 44, 51, 54, 59, 60, 65, 69, 73, 76, 82, 90, 91], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Mohamed Amine Daoud", [2, 7, 17, 22, 24, 31, 36, 43, 46, 49, 52, 57, 63, 67, 69, 72, 78, 82, 87, 95], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Marc Plante", [5, 9, 14, 18, 25, 30, 35, 42, 44, 48, 54, 59, 60, 66, 70, 74, 77, 83, 89, 95], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Joe Kaszupski", [3, 7, 15, 22, 27, 33, 34, 40, 45, 51, 52, 57, 60, 66, 69, 73, 76, 82, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Andrew Burke", [3, 7, 17, 19, 24, 29, 34, 43, 45, 49, 53, 57, 63, 65, 70, 72, 79, 81, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Miguel Piette", [3, 7, 12, 20, 24, 33, 34, 40, 47, 48, 52, 56, 61, 64, 69, 72, 79, 82, 87, 94], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Alex Goguen", [4, 7, 12, 19, 24, 31, 34, 40, 44, 51, 54, 59, 61, 67, 71, 75, 76, 81, 87, 95], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Mélanie Toutant", [1, 8, 12, 19, 25, 31, 34, 43, 46, 48, 53, 59, 60, 65, 69, 72, 76, 82, 86, 93], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Michael Stazio", [3, 10, 15, 22, 25, 31, 36, 43, 46, 48, 52, 57, 60, 66, 69, 72, 76, 81, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Luc Carignan", [2, 9, 15, 22, 27, 33, 36, 43, 46, 51, 52, 59, 63, 64, 69, 72, 76, 82, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Olivier Samson", [3, 7, 14, 18, 24, 31, 34, 39, 46, 51, 52, 57, 63, 64, 70, 72, 76, 81, 86, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Karine Descheneaux", [3, 10, 15, 23, 25, 31, 34, 43, 44, 51, 52, 56, 60, 64, 69, 72, 76, 82, 87, 93], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Mélanie Markis", [5, 10, 15, 19, 26, 33, 34, 40, 46, 49, 54, 58, 60, 65, 69, 75, 76, 83, 87, 93], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Ralph Benjamin Libao", [3, 8, 16, 19, 27, 31, 37, 40, 44, 51, 52, 57, 60, 65, 68, 72, 76, 81, 86, 92], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Dalin Son", [3, 10, 12, 19, 25, 33, 34, 40, 47, 51, 52, 56, 63, 67, 69, 73, 77, 82, 88, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Sophie Chabot", [1, 10, 12, 19, 28, 31, 37, 40, 45, 51, 55, 56, 60, 66, 69, 72, 77, 84, 87, 93], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Armando Macias", [3, 8, 16, 19, 26, 33, 36, 41, 46, 48, 52, 59, 60, 64, 70, 72, 76, 84, 87, 91], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Robert Brillon", [4, 8, 12, 22, 24, 33, 34, 43, 47, 51, 53, 57, 62, 65, 70, 72, 78, 82, 87, 91], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Claire Seemayer", [4, 9, 15, 21, 25, 31, 34, 43, 47, 49, 54, 57, 60, 64, 71, 72, 79, 84, 88, 94], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Erick Ndjomo", [1, 7, 17, 20, 25, 30, 34, 39, 44, 48, 53, 57, 63, 65, 71, 75, 79, 84, 86, 94], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Tommy Hamel", [3, 10, 12, 19, 24, 33, 34, 43, 46, 51, 52, 57, 61, 65, 69, 72, 76, 82, 87, 93], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))

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

        if cumulate_choices != "012345678910111213141516171819":
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

                with open(f"{filename}", "r", encoding="utf-8") as f:
                    data = json.load(f)

                if choice.box_style == BoxStyle.TBS_SKATERS:
                    choice.nb_assists = data["featuredStats"]["regularSeason"]["subSeason"]["assists"]
                    choice.nb_goals = data["featuredStats"]["regularSeason"]["subSeason"]["goals"]
                    choice.nb_points = choice.nb_assists + choice.nb_goals
                    choice.found = True
                    # console.print(f"Choice {choice.name} - Goals: {choice.nb_goals}, Assists: {choice.nb_assists}, Points: {choice.nb_points}", style="green")
                elif choice.box_style == BoxStyle.TBS_GOALIE:
                    choice.nb_wins = data["featuredStats"]["regularSeason"]["subSeason"]["wins"]
                    choice.nb_points = choice.nb_wins * 2
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
        url = f"https://api-web.nhle.com/v1/standings/now"
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
                    choice.nb_wins = team["wins"]
                    choice.nb_points = choice.nb_wins * 2
                    choice.found = True
                    # console.print(f"Choice {choice.name} - Wins: {choice.nb_wins}, Points: {choice.nb_points}", style="green")
    console.print("Finished parsing teams standings!", style="bold green")

# def get_choices_skaters_stats(choices: List[Choice], download_directory: str) -> None:
#     for i in range(7):
#         url = f"https://www.nhl.com/stats/skaters?reportType=season&seasonFrom=20252026&seasonTo=20252026&gameType=2&sort=points,goals,assists&page={i}&pageSize=100"
#         filename = f"{download_directory}\\skaters{i}.lst"
#         get_page_content(url, filename)
#         fill_choices_skaters(choices, filename)


# def get_choices_goalies_stats(choices: List[Choice], download_directory: str) -> None:
#     url = f"https://www.nhl.com/stats/goalies?reportType=season&seasonFrom=20252026&seasonTo=20252026&gameType=2&sort=wins,savePct&page=0&pageSize=100"
#     filename = f"{download_directory}\\goalies.lst"
#     get_page_content(url, filename)
#     fill_choices_goalies(choices, filename)


# def get_choices_teams_stats(choices: List[Choice], download_directory: str) -> None:
#     # url = f"https://www.nhl.com/standings/2025-04-18/league"
#     url = f"https://www.nhl.com/stats/teams"
#     url = f"https://www.nhl.com/stats/teams?reportType=season&seasonFrom=20252026&seasonTo=20252026&gameType=2&sort=points,wins&page=0&pageSize=50"
#     filename = f"{download_directory}\\teams.lst"
#     get_page_content(url, filename)
#     fill_choices_teams(choices, filename)


# def get_officepools_points(participants: List[Participant], download_directory: str) -> None:
#     url1 = f"https://www.officepools.com/nhl/classic/auth/2025/regular/Bluberi2026/Bluberi2026"
#     url2 = f"https://www.officepools.com/nhl/classic/404165/standings#/?page=2"
#     filename1 = f"{download_directory}\\officepools1.lst"
#     filename2 = f"{download_directory}\\officepools2.lst"
#     get_page_content(url1, filename1, url2, filename2)
#     fill_office_points(participants, filename1)
#     fill_office_points(participants, filename2)

def get_officepools_points_manually(participants: List[Participant], download_directory: str) -> None:
    filename = f"{download_directory}\\officepools_manual.lst"
    fill_office_points_manually(participants, filename)

def get_officepools_points_from_excel_file(participants: List[Participant], excel_filename: str) -> None:
    console.print()
    console.print("Parsing Excel file for office pools points...", style="yellow")
    df = pd.read_excel(excel_filename)

    # Process in blocks of 20 rows
    for start in range(0, len(df), 20):
        block = df.iloc[start:start+20]
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


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix


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

        f.write(".inner-table {\n")
        f.write(" table-layout: fixed;\n")
        f.write(" border: 1px solid silver;\n")
        f.write(" border-collapse: collapse;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".inner-table th {\n")
        f.write(" width: 230px;\n")
        f.write(" height: 20px;\n")
        f.write(" border-bottom: 1px solid silver;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".outer-table {\n")
        f.write(" border: 3px solid black;\n")
        f.write(" border-collapse: collapse;\n")
        f.write("}\n")
        f.write("\n")

        f.write(".outer-table th.colspan-4 {\n")
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


def write_footer(generation_timestamp: str, f, use_external_path: bool = False) -> None:
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
    f.write("<a href=\"https://www.officepools.com/nhl/classic/auth/2025/regular/Bluberi2026/Bluberi2026\" target=\"officepools\">OfficePools</a>\n")
    f.write("  </td>\n")

    f.write(" </tr>\n")
    f.write("</table>\n")


def write_header(generation_timestamp: str, f, use_external_path: bool = False) -> None:
    if use_external_path:
        sub_path = gExternalPath
    else:
        sub_path = ""
    f.write("<table class=\"page-header-table\">\n")

    f.write(" <tr>\n")
    f.write("  <th>\n")

    f.write(f"  <img src=\"{sub_path}bluberi_logo.png\" alt=\"Bluberi Logo\">&nbsp;")
    f.write("  Bluberi Hockey Pool 2025-2026\n")
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
    f.write("<a href=\"https://www.officepools.com/nhl/classic/auth/2025/regular/Bluberi2026/Bluberi2026\" target=\"officepools\">OfficePools</a>\n")
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
    sorted_office_participant = sorted(offices, key=lambda x: x.average_points, reverse=True)

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
        console.print(f"{office_participant.average_points} - {office_participant.name}", style="bold green")

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
        f.write(f"    <title>Bluberi Hockey Pool 2025-2026 (Generated on {generation_timestamp})</title>\n")
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

            write_header(generation_timestamp, f)

            f.write("     <table class=\"outer-table\">\n")

            header_line = f"{ordinal(participant.rank)} - {participant.name} - {participant.total_points} points"
            f.write("       <tr>\n")
            f.write(f"         <th colspan=\"4\" class=\"colspan-4\">{header_line}</th>\n")
            f.write("       </tr>            \n")

            for i in range(5):
                f.write("      <tr>\n")
                max_choices = max(boxes[i*4].nb_choices, boxes[i*4+1].nb_choices, boxes[i*4+2].nb_choices, boxes[i*4+3].nb_choices)
                for j in range(4):
                    f.write(f"        <td>\n")
                    f.write(f"          <table  class=\"inner-table\" border='0'>\n")
                    box_number = (i*4)+j
                    f.write(f"            <tr>\n")
                    if participant.lowest_round == box_number:
                        th_class_name = '"box_header_dropped"'
                    else:
                        th_class_name = '"box_header_normal"'
#                   f.write(f"              <th colspan='2' class={th_class_name}>{box_number+1}. {boxes[box_number].name}</th>\n")
                    f.write(f"              <th colspan='2' class={th_class_name}>Box #{box_number+1}</th>\n")
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

                            f.write(f"            <tr class={tr_participant}>\n")
                            f.write(f"              <td>{choice.name}</td>\n")
                            f.write(f"              <td style=\"text-align: right;\">{choice.nb_points}&nbsp;</td>\n")
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

            write_footer(generation_timestamp, f)

            f.write("  </body>\n")
            f.write("\n")
            f.write("</html>\n")


def do_all_the_work(flag_compare_nhl_vs_officepools: bool) -> None:
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
    get_officepools_points_from_excel_file(participants, r'c:\Users\DBisson\Downloads\custom.xls')

    validate_choices(choices, participants)
    validate_officepools_points(participants)

    set_best_and_worse_choices_per_boxes(boxes, choices)
    set_lowest_round(participants, choices)
    set_total_points(participants, choices)
    set_who_chose_who(participants, choices)
    sort_participants(participants)

    if flag_compare_nhl_vs_officepools == True:
        compare_nhl_vs_officepools(participants)

    copy_required_ressources(for_website_directory, offices, countries)
    procedure_css_file(for_website_directory)
    produce_personal_grid(report_datetime, for_website_directory, boxes, choices, participants)
    produce_ranking_grid(report_datetime, for_website_directory, participants)
    produce_sex_grid(report_datetime, for_website_directory, participants)
    produce_country_grid(report_datetime, for_website_directory, participants, countries)
    produce_office_grid(report_datetime, for_website_directory, participants, offices)
    produce_email_message(report_datetime, for_website_directory, participants, offices)

    compress_website_directory(for_website_directory, f'c:\\tmp\\bluberi_pool_{today_string}.zip')


if __name__ == "__main__":
    freeze_start = time.perf_counter()   # high‑precision timer

    # Set the locale to French
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    console.print('----------------------------------', style='bold green')
    console.print('BLUBERI POOL GENERATOR - ver 1.0.1', style='bold green')
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

    do_all_the_work(flag_compare_nhl_vs_officepools)

    # Ask the user to press a key to exit
    console.print()

    freeze_end = time.perf_counter()

    elapsed_ms = (freeze_end - freeze_start) * 1000
    print(f"Elapsed: {elapsed_ms:.2f} ms")
