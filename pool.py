import sys
import os
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time
import bs4
import itertools
from enum import Enum
from typing import List
import datetime
import ftplib
import argparse
from rich.console import Console
import shutil
import locale

console = Console(highlight=False)


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
    def __init__(self, box_number, box_style: BoxStyle, name, team_abreviation, nb_goals, nb_assists, nb_points, nb_wins):
        self.box_number = box_number
        self.box_style = box_style
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


def init_choices(choices: list):
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "Florida Panthers", "FLA", 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "Colorado Avalanche", "COL", 0, 0, 0, 0))
    choices.append(Choice(0, BoxStyle.TBS_TEAM, "Carolina Hurricanes", "CAR", 0, 0, 0, 0))

    choices.append(Choice(1, BoxStyle.TBS_TEAM, "Edmonton Oilers", "EDM", 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "Vegas Golden Knights", "VGK", 0, 0, 0, 0))
    choices.append(Choice(1, BoxStyle.TBS_TEAM, "Dallas Stars", "DAL", 0, 0, 0, 0))

    choices.append(Choice(2, BoxStyle.TBS_TEAM, "New Jersey Devils", "NJD", 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "Toronto Maple Leafs", "TOR", 0, 0, 0, 0))
    choices.append(Choice(2, BoxStyle.TBS_TEAM, "New York Rangers", "NYR", 0, 0, 0, 0))

    choices.append(Choice(3, BoxStyle.TBS_TEAM, "Vancouver Canucks", "VAN", 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "Tampa Bay Lightning", "TBL", 0, 0, 0, 0))
    choices.append(Choice(3, BoxStyle.TBS_TEAM, "Winnipeg Jets", "WPG", 0, 0, 0, 0))

    choices.append(Choice(4, BoxStyle.TBS_TEAM, "St. Louis Blues", "STL", 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_TEAM, "Minnesota Wild", "MIN", 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_TEAM, "Nashville Predators", "NSH", 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_TEAM, "Los Angeles Kings", "LAK", 0, 0, 0, 0))
    choices.append(Choice(4, BoxStyle.TBS_TEAM, "Boston Bruins", "BOS", 0, 0, 0, 0))

    choices.append(Choice(5, BoxStyle.TBS_TEAM, "Montréal Canadiens", "MTL", 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_TEAM, "Washington Capitals", "WSH", 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_TEAM, "Ottawa Senators", "OTT", 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_TEAM, "New York Islanders", "NYI", 0, 0, 0, 0))
    choices.append(Choice(5, BoxStyle.TBS_TEAM, "Columbus Blue Jackets", "CBJ", 0, 0, 0, 0))

    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "Connor McDavid", "EDM", 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "Nathan MacKinnon", "COL", 0, 0, 0, 0))
    choices.append(Choice(6, BoxStyle.TBS_SKATERS, "Nikita Kucherov", "TBL", 0, 0, 0, 0))

    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "Kirill Kaprizov", "MIN", 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "Leon Draisaitl", "EDM", 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "Mikko Rantanen", "COL", 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "Artemi Panarin", "NYR", 0, 0, 0, 0))
    choices.append(Choice(7, BoxStyle.TBS_SKATERS, "David Pastrnak", "BOS", 0, 0, 0, 0))

    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "Jack Hughes", "NJD", 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "J.T. Miller", "VAN", 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "Cale Makar", "COL", 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "Auston Matthews", "TOR", 0, 0, 0, 0))
    choices.append(Choice(8, BoxStyle.TBS_SKATERS, "Mitch Marner", "TOR", 0, 0, 0, 0))

    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "William Nylander", "TOR", 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "Elias Pettersson", "VAN", 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "Jake Guentzel", "TBL", 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "Matthew Tkachuk", "FLA", 0, 0, 0, 0))
    choices.append(Choice(9, BoxStyle.TBS_SKATERS, "Sidney Crosby", "PIT", 0, 0, 0, 0))

    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "Lucas Raymond", "DET", 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "Mathew Barzal", "NYI", 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "Brady Tkachuk", "OTT", 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "Connor Bedard", "CHI", 0, 0, 0, 0))
    choices.append(Choice(10, BoxStyle.TBS_SKATERS, "Sam Reinhart", "FLA", 0, 0, 0, 0))

    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "Brayden Point", "TBL", 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "Filip Forsberg", "NSH", 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "Sebastian Aho", "CAR", 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "Aleksander Barkov", "FLA", 0, 0, 0, 0))
    choices.append(Choice(11, BoxStyle.TBS_SKATERS, "Clayton Keller", "UTA", 0, 0, 0, 0))

    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "Nick Suzuki", "MTL", 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "Jordan Kyrou", "STL", 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "Tim Stützle", "OTT", 0, 0, 0, 0))
    choices.append(Choice(12, BoxStyle.TBS_SKATERS, "Kevin Fiala", "LAK", 0, 0, 0, 0))

    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "Jack Eichel", "VGK", 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "Shea Theodore", "VGK", 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "Mark Stone", "VGK", 0, 0, 0, 0))
    choices.append(Choice(13, BoxStyle.TBS_SKATERS, "William Karlsson", "VGK", 0, 0, 0, 0))

    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "Kirby Dach", "MTL", 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "Mike Matheson", "MTL", 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "Cole Caufield", "MTL", 0, 0, 0, 0))
    choices.append(Choice(14, BoxStyle.TBS_SKATERS, "Juraj Slafkovsky", "MTL", 0, 0, 0, 0))

    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "Evan Bouchard", "EDM", 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "Adam Fox", "NYR", 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "Quinn Hughes", "VAN", 0, 0, 0, 0))
    choices.append(Choice(15, BoxStyle.TBS_SKATERS, "Roman Josi", "NSH", 0, 0, 0, 0))

    choices.append(Choice(16, BoxStyle.TBS_GOALIE, "Juuse Saros", "NSH", 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_GOALIE, "Sergei Bobrovsky", "FLA", 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_GOALIE, "Connor Hellebuyck", "WPG", 0, 0, 0, 0))
    choices.append(Choice(16, BoxStyle.TBS_GOALIE, "Igor Shesterkin", "NYR", 0, 0, 0, 0))

    choices.append(Choice(17, BoxStyle.TBS_GOALIE, "Andrei Vasilevskiy", "TBL", 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_GOALIE, "Frederik Andersen", "CAR", 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_GOALIE, "Stuart Skinner", "EDM", 0, 0, 0, 0))
    choices.append(Choice(17, BoxStyle.TBS_GOALIE, "Jake Oettinger", "DAL", 0, 0, 0, 0))

    choices.append(Choice(18, BoxStyle.TBS_GOALIE, "Ukko-Pekka Luukkonen", "BUF", 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_GOALIE, "Alexandar Georgiev", "COL", 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_GOALIE, "Jacob Markstrom", "NJD", 0, 0, 0, 0))
    choices.append(Choice(18, BoxStyle.TBS_GOALIE, "Charlie Lindgren", "WSH", 0, 0, 0, 0))

    choices.append(Choice(19, BoxStyle.TBS_GOALIE, "Tristan Jarry", "PIT", 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_GOALIE, "Jordan Binnington", "STL", 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_GOALIE, "Ilya Sorokin", "NYI", 0, 0, 0, 0))
    choices.append(Choice(19, BoxStyle.TBS_GOALIE, "Darcy Kuemper", "COL    ", 0, 0, 0, 0))


def init_boxes(choices: list, boxes: list) -> None:
    boxes.append(Box("High Expectations"))
    boxes.append(Box("Cup Contenders"))
    boxes.append(Box("Playoff Bound"))
    boxes.append(Box("Dark Horses"))
    boxes.append(Box("Wild Cards"))
    boxes.append(Box("Surprise Us"))
    boxes.append(Box("Top Guns"))
    boxes.append(Box("Top Guns"))
    boxes.append(Box("Ice Kings"))
    boxes.append(Box("Slapshot Stars"))
    boxes.append(Box("Puck Masters"))
    boxes.append(Box("Goal Getters"))
    boxes.append(Box("Stickhandlers"))
    boxes.append(Box("Las Vegas Stars"))
    boxes.append(Box("Canadian Hopes"))
    boxes.append(Box("Defensive Dynamos"))
    boxes.append(Box("Brick Walls"))
    boxes.append(Box("Net Ninjas"))
    boxes.append(Box("Save Machines"))
    boxes.append(Box("Glove Savers"))

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
    participants.append(Participant("Denis Bisson", [0, 3, 7, 9, 13, 17, 22, 26, 32, 35, 43, 48, 50, 54, 60, 63, 67, 72, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Kevin Nguyen", [0, 5, 8, 9, 16, 20, 22, 26, 33, 38, 44, 47, 50, 55, 60, 63, 67, 73, 75, 81], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("François Vigneault", [0, 3, 7, 11, 16, 18, 22, 26, 33, 38, 44, 48, 51, 56, 58, 62, 67, 72, 77, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Hugues Labrecque", [2, 3, 7, 11, 16, 20, 22, 26, 33, 35, 41, 47, 53, 54, 60, 62, 68, 71, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Pierre Guay", [0, 3, 7, 10, 16, 20, 22, 26, 33, 35, 44, 45, 52, 54, 60, 64, 67, 73, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("François Léger", [1, 3, 6, 9, 14, 19, 22, 26, 33, 35, 43, 45, 52, 54, 60, 62, 69, 73, 75, 81], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Louis-Philippe Perreault", [2, 3, 6, 10, 16, 19, 24, 26, 31, 38, 41, 45, 50, 55, 61, 64, 67, 71, 74, 81], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Miguel Piette", [0, 3, 7, 10, 16, 20, 22, 26, 33, 35, 43, 47, 50, 54, 60, 64, 69, 73, 76, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Derek Pacuk", [1, 3, 8, 9, 14, 20, 22, 27, 33, 35, 43, 48, 52, 57, 60, 64, 68, 70, 76, 81], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Mike Wabschall", [2, 4, 6, 10, 15, 20, 22, 27, 33, 39, 44, 47, 50, 54, 60, 64, 67, 73, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_AUSTIN))
    participants.append(Participant("Mélanie Toutant", [2, 5, 8, 11, 16, 18, 24, 28, 33, 39, 44, 46, 50, 55, 60, 64, 67, 71, 75, 79], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Tommy Hamel", [1, 5, 8, 11, 14, 17, 22, 26, 33, 38, 44, 46, 50, 54, 61, 65, 69, 73, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Olivier Lafrenière", [1, 5, 7, 9, 14, 18, 22, 26, 34, 38, 43, 49, 52, 54, 60, 62, 69, 73, 76, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Jeff Baker", [1, 5, 8, 9, 16, 18, 23, 28, 33, 39, 43, 46, 50, 54, 58, 64, 69, 73, 76, 78], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Éric Colgan", [0, 3, 8, 11, 14, 20, 22, 28, 33, 37, 43, 47, 52, 54, 58, 64, 69, 71, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Dalton Perse", [0, 4, 8, 10, 12, 19, 23, 27, 31, 37, 40, 48, 51, 57, 58, 63, 68, 73, 74, 79], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("François Hébert", [0, 5, 8, 11, 16, 18, 24, 29, 33, 35, 44, 46, 50, 56, 58, 64, 67, 71, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Yves Lavoie", [0, 3, 8, 11, 12, 17, 22, 26, 33, 35, 43, 47, 50, 54, 58, 65, 67, 70, 77, 81], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Alex Goguen", [0, 4, 8, 9, 16, 17, 22, 26, 33, 39, 43, 47, 50, 54, 60, 64, 67, 70, 75, 78], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_MONCTON))
    participants.append(Participant("Karim Bahsoun", [1, 3, 7, 9, 14, 17, 23, 27, 33, 35, 44, 46, 52, 54, 58, 64, 67, 71, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Dominic Lachance", [0, 5, 8, 9, 16, 20, 22, 26, 33, 38, 43, 46, 50, 54, 60, 64, 67, 71, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Yvan Paradis", [1, 3, 7, 11, 16, 20, 22, 26, 33, 37, 43, 47, 50, 55, 60, 64, 67, 71, 75, 80], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Marc Plante", [0, 5, 7, 9, 15, 20, 23, 26, 34, 38, 44, 47, 53, 54, 61, 65, 69, 70, 74, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Sandra St-Onge", [1, 3, 8, 11, 14, 18, 22, 26, 31, 35, 44, 47, 50, 54, 60, 62, 67, 71, 75, 79], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Craig Vinciguerra", [2, 4, 8, 11, 16, 18, 24, 29, 32, 37, 44, 48, 50, 54, 60, 64, 69, 73, 74, 79], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Stéphan Généreux", [0, 3, 8, 11, 16, 17, 22, 26, 33, 39, 43, 46, 50, 57, 60, 64, 67, 71, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Casey Whalen", [0, 3, 7, 9, 15, 17, 22, 26, 33, 38, 43, 46, 53, 54, 60, 63, 67, 72, 75, 81], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Frédéric Gilbert", [0, 5, 8, 11, 14, 20, 22, 26, 33, 39, 41, 46, 53, 56, 60, 63, 68, 73, 75, 78], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Marcel Lachance", [0, 5, 6, 10, 15, 17, 22, 25, 32, 38, 43, 46, 53, 55, 61, 62, 67, 71, 77, 81], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Karine Descheneaux", [0, 4, 7, 9, 16, 20, 22, 29, 33, 36, 44, 48, 50, 54, 61, 64, 67, 70, 77, 79], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("François Dubreuil", [0, 4, 6, 9, 16, 19, 23, 25, 30, 38, 43, 47, 51, 54, 58, 63, 67, 72, 75, 81], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Mélanie Markis", [1, 3, 8, 9, 16, 19, 23, 26, 33, 36, 43, 47, 50, 54, 61, 63, 69, 71, 77, 81], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Luc Carignan", [2, 3, 8, 9, 16, 20, 22, 29, 33, 38, 43, 46, 50, 54, 58, 64, 68, 71, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("François Pelletier", [0, 3, 7, 9, 16, 18, 22, 26, 33, 37, 44, 47, 50, 56, 60, 64, 67, 70, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Bruno Aird", [1, 5, 7, 11, 16, 19, 22, 26, 32, 37, 44, 47, 53, 55, 61, 63, 69, 73, 74, 81], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Mike Perry", [1, 5, 8, 9, 14, 20, 22, 26, 33, 38, 43, 45, 52, 54, 60, 62, 69, 73, 75, 80], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Andrew Burke", [0, 4, 7, 10, 15, 17, 22, 26, 33, 38, 43, 47, 50, 54, 59, 63, 67, 70, 77, 79], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Sébastien Morin", [1, 4, 6, 9, 14, 20, 22, 29, 33, 36, 44, 48, 50, 54, 61, 64, 67, 70, 77, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Armando Macias", [0, 3, 7, 11, 15, 20, 23, 26, 31, 38, 44, 48, 53, 56, 60, 62, 67, 73, 75, 81], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Martin Pelletier", [2, 3, 7, 10, 16, 18, 22, 26, 34, 35, 44, 46, 50, 55, 58, 62, 66, 72, 75, 78], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Sébastien Blanchet", [0, 3, 7, 10, 13, 18, 23, 26, 33, 37, 44, 48, 53, 54, 60, 65, 66, 70, 77, 80], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Nicolas Gamache", [1, 3, 8, 9, 16, 18, 22, 25, 34, 38, 43, 49, 50, 55, 61, 62, 67, 71, 75, 78], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Samantha Poisson", [0, 4, 7, 9, 16, 20, 22, 25, 32, 39, 43, 45, 51, 56, 61, 63, 68, 72, 76, 78], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Sophie Chabot", [1, 3, 7, 11, 16, 20, 23, 27, 32, 36, 43, 48, 50, 56, 58, 62, 67, 73, 77, 78], SexType.SEX_FEMALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Robert Brillon", [1, 5, 7, 9, 13, 17, 23, 29, 31, 37, 44, 45, 50, 56, 60, 62, 67, 72, 75, 81], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Jessica Jercinovic", [2, 4, 8, 9, 16, 20, 22, 26, 30, 39, 41, 48, 51, 54, 61, 63, 66, 70, 76, 81], SexType.SEX_FEMALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))
    participants.append(Participant("Louis Gunning", [1, 4, 8, 11, 16, 17, 24, 29, 32, 39, 41, 48, 52, 54, 59, 65, 66, 72, 75, 78], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_RENO))
    participants.append(Participant("RJ Machado", [1, 4, 7, 9, 13, 17, 23, 27, 30, 39, 40, 48, 52, 57, 59, 62, 67, 71, 77, 80], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_RENO))
    participants.append(Participant("François-A. Désilets-Trempe", [1, 5, 8, 9, 16, 19, 23, 29, 31, 35, 43, 48, 50, 55, 60, 62, 68, 71, 74, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Mathieu Paquette", [1, 5, 8, 10, 16, 17, 22, 27, 33, 39, 44, 45, 51, 54, 60, 62, 69, 71, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Patrick Bellavance-Marcoux", [0, 5, 6, 10, 16, 21, 24, 27, 31, 37, 44, 45, 53, 54, 61, 63, 66, 73, 75, 78], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Luc McCutcheon", [0, 3, 7, 9, 14, 17, 22, 26, 33, 38, 43, 48, 50, 54, 60, 64, 67, 72, 74, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Benoît Lapolice", [0, 3, 8, 9, 16, 20, 22, 26, 33, 36, 41, 46, 50, 54, 60, 64, 69, 72, 76, 81], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Olivier Samson", [2, 3, 8, 10, 12, 17, 22, 26, 31, 39, 44, 48, 50, 54, 58, 62, 67, 71, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_CANADA, OfficeType.OFFICE_DRUMMONDVILLE))
    participants.append(Participant("Vince Catalano", [0, 3, 8, 10, 14, 20, 22, 26, 32, 38, 43, 47, 51, 54, 58, 64, 69, 73, 75, 79], SexType.SEX_MALE, CountryType.COUNTRY_USA, OfficeType.OFFICE_LAS_VEGAS))

    for iParticipantIndex, participant in enumerate(participants):
        participant.native_index = iParticipantIndex


def validate_choices(choices: list, participants: list):
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
    console.print("If we've reached this point, there are all valid!\n", style="bold green")

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
    console.print("If we've reached this point, all choices were found in the NHL web site!\n", style="bold green")


def get_page_content(url1: str, filename1: str, url2=None, filename2=None) -> None:
    nb_pages_already_downloaded = 0

    try:
        with open(filename1, 'r', encoding='utf-8') as f:
            nb_pages_already_downloaded += 1
    except FileNotFoundError:
        pass

    if url2 and filename2:
        try:
            with open(filename2, 'r', encoding='utf-8') as f:
                nb_pages_already_downloaded += 1
        except FileNotFoundError:
            pass

    if url2 and filename2:
        if nb_pages_already_downloaded == 2:
            return
    else:
        if nb_pages_already_downloaded == 1:
            return

    # Set up Edge options for headless mode
    options = Options()
    options.add_argument('--headless')

    # Set up Edge webdriver
    driver = webdriver.Edge()

    # Open the webpage
    driver.get(url1)
    time.sleep(20)

    # Now we save the page content to a file
    with open(filename1, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)

    if url2 and filename2:
        # Open the webpage
        driver.get(url2)
        time.sleep(20)
        driver.refresh()
        time.sleep(20)

        # Now we save the page content to a file
        with open(filename2, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)

    driver.quit()


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


def get_choices_skaters_stats(choices: List[Choice], download_directory: str) -> None:
    for i in range(7):
        url = f"https://www.nhl.com/stats/skaters?reportType=season&seasonFrom=20242025&seasonTo=20242025&gameType=2&sort=points,a_gamesPlayed&page={i}&pageSize=100"
        filename = f"{download_directory}\\skaters{i}.lst"
        get_page_content(url, filename)
        fill_choices_skaters(choices, filename)


def get_choices_goalies_stats(choices: List[Choice], download_directory: str) -> None:
    url = f"https://www.nhl.com/stats/goalies?reportType=season&seasonFrom=20242025&seasonTo=20242025&gameType=2&sort=wins,savePct&page=0&pageSize=100"
    filename = f"{download_directory}\\goalies.lst"
    get_page_content(url, filename)
    fill_choices_goalies(choices, filename)


def get_choices_teams_stats(choices: List[Choice], download_directory: str) -> None:
    # url = f"https://www.nhl.com/standings/2025-04-18/league"
    url = f"https://www.nhl.com/stats/teams"
    filename = f"{download_directory}\\teams.lst"
    get_page_content(url, filename)
    fill_choices_teams(choices, filename)


def get_officepools_points(participants: List[Participant], download_directory: str) -> None:
    url1 = f"https://www.officepools.com/nhl/classic/auth/2024/regular/Bluberi_Pool/bluberi2025"
    url2 = f"https://www.officepools.com/nhl/classic/387234/standings#/?page=2"
    filename1 = f"{download_directory}\\officepools1.lst"
    filename2 = f"{download_directory}\\officepools2.lst"
    get_page_content(url1, filename1, url2, filename2)
    fill_office_points(participants, filename1)
    fill_office_points(participants, filename2)


def validate_officepools_points(participants: List[Participant]) -> None:
    for participant in participants:
        if participant.office_total_points == 0:
            raise ValueError(f"Participant {participant.name} has not been found in the office pools web site!")


def compare_nhl_vs_officepools(participants: List[Participant]) -> None:
    nb_errors = 0
    for participant in participants:
        if participant.total_points != participant.office_total_points:
            nb_errors += 1
            print(f"ERROR: Participant:{participant.name} - NHL:{participant.total_points} - OfficePools:{participant.office_total_points}")
    if nb_errors > 0:
        raise ValueError(f"There are {nb_errors} participants that have different points between NHL and OfficePools!")


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

# Function that will copy specific files to the website directory.
# These files are coming from the directoru .\ressources of the script.


def copy_required_ressources(for_website_directory: str) -> None:
    console.print("Copying resource files...", style="yellow")
    shutil.copy(".\\ressources\\bluberi_logo.png", f"{for_website_directory}\\bluberi_logo.png")
    shutil.copy(".\\ressources\\usa.png", f"{for_website_directory}\\usa.png")
    shutil.copy(".\\ressources\\canada.png", f"{for_website_directory}\\canada.png")
    shutil.copy(".\\ressources\\global6.ico", f"{for_website_directory}\\global6.ico")
    console.print("Resource files copied!\n", style="bold green")
    console.print()


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
        f.write(" width: 200px;\n")
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
        f.write("  font-size: 20px;\n")
        f.write("  font-weight: bold;\n")
        f.write("  text-align: center;\n")
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


def write_footer(generation_timestamp: str, f) -> None:
    f.write("<br>\n")
    f.write("<table class=\"page-footer-table\">\n")
    f.write(" <tr>\n")
    f.write("  <td>\n")
    f.write(f"Generated on {generation_timestamp}\n")
    f.write("  </td>\n")

    f.write("  <td>\n")
    f.write("<a href=\"ranking.html\">Ranking</a>\n")
    f.write("&nbsp;")
    f.write("<a href=\"country_stats.html\">CANADA vs USA</a>\n")
    f.write("&nbsp;")
    f.write("<a href=\"https://www.officepools.com/nhl/classic/auth/2024/regular/Bluberi_Pool/bluberi2025\" target=\"officepools\">OfficePools</a>\n")
    f.write("  </td>\n")

    f.write(" </tr>\n")
    f.write("</table>\n")


def write_header(generation_timestamp: str, f) -> None:
    f.write("<table class=\"page-header-table\">\n")

    f.write(" <tr>\n")
    f.write("  <th>\n")

    f.write(f"  <img src=\"bluberi_logo.png\" alt=\"Bluberi Logo\">&nbsp;")
    f.write("  Bluberi Hockey Pool 2024-2025\n")
    f.write(f"  &nbsp;<img src=\"bluberi_logo.png\" alt=\"Bluberi Logo\">")
    f.write("  </th>\n")
    f.write(" </tr>\n")

    f.write(" <tr>\n")
    f.write("  <td>\n")
    f.write(f"   Generated on {generation_timestamp}\n")
    f.write("  </td>\n")
    f.write(" </tr>\n")

    f.write(" <tr>\n")
    f.write("  <td class=link-td>\n")
    f.write("<a href=\"ranking.html\">Ranking</a>\n")
    f.write("&nbsp;")
    f.write("<a href=\"country_stats.html\">CANADA vs USA</a>\n")
    f.write("&nbsp;")
    f.write("<a href=\"https://www.officepools.com/nhl/classic/auth/2024/regular/Bluberi_Pool/bluberi2025\" target=\"officepools\">OfficePools</a>\n")
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
        sex_participant.average_points = sex_participant.total_points / sex_participant.number
        sex_participant.average_points = round(sex_participant.average_points, 1)

    # Let's sort based on the average points
    sorted_sex_participant = sorted(sex_participants, key=lambda x: x.average_points, reverse=True)

    for sex_participant in sorted_sex_participant:
        print(f"{sex_participant.name}: {sex_participant.average_points}")

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
        country_participant.average_points = country_participant.total_points / country_participant.number
        country_participant.average_points = round(country_participant.average_points, 2)

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

    for country_participant in sorted_country_participant:
        print(f"{country_participant.name}: {country_participant.average_points}")

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
    f.write(f"         <th colspan=\"3\" class=\"colspan-3\"><img src=\"{office.icon_filename}\" alt=\"{office.name}\">&nbsp;{office.name}&nbsp;<img src=\"{office.icon_filename}\" alt=\"{office.name}\"></th>\n")
    f.write("       </tr>            \n")

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
        office_participant.average_points = office_participant.total_points / office_participant.number
        # office_participant.average_points = round(office_participant.average_points, 2)
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

    for office_participant in sorted_office_participant:
        print(f"{office_participant.name}: {office_participant.average_points}")

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
            f.write("         <td>\n")
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

        # f.write("       <tr>\n")
        # f.write(f"         <th colspan=\"2\" class=\"colspan-2\">Ranking (generated on {generation_timestamp})</th>\n")
        # f.write("       </tr>\n")

        f.write("       <tr>\n")

        for office_participant in sorted_office_participant:
            f.write("         <td>\n")
            write_ranking_office_table(f, participants, office_participant)
            f.write("         </td>\n")
            f.write("         &nbsp;\n")
        # f.write("         <td>\n")
        # write_ranking_country_table(f, participants, sorted_office_participant[0])
        # f.write("         </td>\n")
        # f.write("         <td>\n")
        # f.write("         &nbsp;\n")
        # f.write("         </td>\n")
        # f.write("         <td>\n")
        # write_ranking_country_table(f, participants, sorted_office_participant[1])
        # f.write("         </td>\n")
        f.write("       </tr>\n")
        f.write("     </table>\n")

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


def upload_files_to_ftps(for_website_directory: str, participants: List[Participant]) -> None:
    pass

def archive_all_files(for_website_directory: str, today_directory: str) -> str:
    # Let's compress all the files in a zip file that will have the form: YYYY-MM-DD@hh-mm-ss.zip
    compressed_filename = os.path.join(today_directory, f"{datetime.date.today().strftime('%Y-%m-%d')}@{datetime.datetime.now().strftime('%H-%M-%S')}.zip")
    shutil.make_archive(compressed_filename, 'zip', for_website_directory)
    return compressed_filename


def do_all_the_work(upload_files: bool, flag_compare_nhl_vs_officepools: bool) -> None:
    today_directory = f'.\\{datetime.date.today().strftime("%Y-%m-%d")}'

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

    boxes = []
    init_boxes(choices, boxes)

    participants = []
    init_participants(participants)

    countries = []
    init_countries(countries)

    offices = []
    init_offices(offices)

    get_choices_skaters_stats(choices, download_directory)
    get_choices_goalies_stats(choices, download_directory)
    get_choices_teams_stats(choices, download_directory)
    get_officepools_points(participants, download_directory)

    validate_choices(choices, participants)
    validate_officepools_points(participants)

    set_best_and_worse_choices_per_boxes(boxes, choices)
    set_lowest_round(participants, choices)
    set_total_points(participants, choices)
    set_who_chose_who(participants, choices)
    sort_participants(participants)

    if flag_compare_nhl_vs_officepools == True:
        compare_nhl_vs_officepools(participants)

    copy_required_ressources(for_website_directory)
    procedure_css_file(for_website_directory)
    produce_personal_grid(report_datetime, for_website_directory, boxes, choices, participants)
    produce_ranking_grid(report_datetime, for_website_directory, participants)
    produce_sex_grid(report_datetime, for_website_directory, participants)
    produce_country_grid(report_datetime, for_website_directory, participants, countries)
    produce_office_grid(report_datetime, for_website_directory, participants, offices)


#   compressed_file = archive_all_files(for_website_directory, today_directory)

    if upload_files:
        upload_files_to_ftps(for_website_directory, participants)


if __name__ == "__main__":
    # Set the locale to French
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    flag_upload_to_ftp = False

    console.print('----------------------------------', style='bold green')
    console.print('BLUBERI POOL GENERATOR - ver 0.0.3', style='bold green')
    console.print('----------------------------------', style='bold green')
    console.print()
    console.print(f'Number of argument:{len(sys.argv)}', style='yellow')
    for sArgument in sys.argv:
        console.print(f'                   {sArgument}', style='yellow')

    parser = argparse.ArgumentParser(description="BLUBERI POOL GENERATOR")
    parser.add_argument('--upload', action='store_true', help='Once HTML file are generated, upload them to the FTP server')
    parser.add_argument('--nocompare', action='store_true', help='Do not compare the NHL results with the OfficePools results')

    parser.print_help()
    console.print()

    args = parser.parse_args()
    if args.upload:
        flag_upload_to_ftp = True

    flag_compare_nhl_vs_officepools = True
    if args.nocompare:
        flag_compare_nhl_vs_officepools = False

    do_all_the_work(flag_upload_to_ftp, flag_compare_nhl_vs_officepools)
