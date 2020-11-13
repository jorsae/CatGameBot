from discord import Colour

# Bot configurations
DEFAULT_PREFIX = '!'

# Discord
COLOUR_OK = Colour.green()
COLOUR_NEUTRAL = Colour.orange()
COLOUR_ERROR = Colour.red()


# Time constants for pinging/event tracking
ONE_HOUR = 3600
SIX_HOURS = 21600
EVENT_DURATION = 1800
WARNING_TIME = 300

# Rock, Paper, Scissors 
DATABASE_FILE = '../CatGameDatabase.db'
ROCK_NAMES = ['r', 'rock', 'rocks']
PAPER_NAMES = ['p', 'paper', 'papers']
SCISSOR_NAMES = ['s', 'scissor', 'scissors']