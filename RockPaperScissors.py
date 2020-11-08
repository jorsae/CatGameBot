from peewee import *
import discord
import datetime
import logging
from random import randint

import constants

database = SqliteDatabase(constants.DATABASE_FILE)

def help():
    embed = discord.Embed(colour=discord.Colour.orange(), title='Rock, Paper, Scissors Help')
    embed.add_field(name=f'{constants.PREFIX}rps help', value='To display this message', inline=False)
    embed.add_field(name=f'{constants.PREFIX}rps rank', value='To display the top ranks', inline=False)
    embed.add_field(name=f'{constants.PREFIX}rps profile', value='To view your stats', inline=False)
    embed.add_field(name=f'{constants.PREFIX}rps rock', value='To select rock', inline=False)
    embed.add_field(name=f'{constants.PREFIX}rps paper', value='To select paper', inline=False)
    embed.add_field(name=f'{constants.PREFIX}rps scissors', value='To select scissors', inline=False)
    return embed

def rank():
    try:
        query = RockPaperScissorsModel.select(RockPaperScissorsModel).order_by(RockPaperScissorsModel.wins.desc()).limit(10)
        
        embed = discord.Embed(colour=discord.Colour.orange(), title=f'Rock, Paper, Scissors Rankings!')
        rank = 1
        for user in query:
            embed.add_field(name=f'{rank}. {user.username}: {user.wins} wins', value=f'Draw: {user.draw}, Loss: {user.loss}', inline=False)
            rank += 1
        return embed
    except Exception as e:
        logging.critical(f'RockPaperScissors.profile: {e}')
    embed = discord.Embed(colour=discord.Colour.red(), title=f'Error')
    return embed

def profile(author):
    try:
        user = RockPaperScissorsModel.get(RockPaperScissorsModel.user_id == author.id)
        embed = discord.Embed(colour=discord.Colour.orange(), title=f'{str(author.name)} Profile')
        embed.add_field(name=f"Wins: {user.wins}, Loss: {user.loss}, Draw: {user.draw}", value=f'Total games played: {user.wins+user.loss+user.draw}\nLast game played: {user.last_played}\nFirst game played: {user.created_date}')
        return embed
    except DoesNotExist:
        embed = discord.Embed(colour=discord.Colour.orange(), title=f'{str(author.name)} Profile')
        embed.add_field(name=f'You have not played any games!', value=f'"{constants.PREFIX}rps help" to get started')
        return embed
    except Exception as e:
        logging.critical(f'RockPaperScissors.profile: {e}')
    embed = discord.Embed(colour=discord.Colour.red(), title=f'Error')
    return embed

def game(author, selection):
    user_selection = get_user_selection(selection)
    if user_selection == -1:
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name=f'Rock, Paper, Scissors Error')
        embed.add_field(name="You need to make a valid selection", value='Selections are: "rock", "paper" or "scissors"')
        return embed
    
    channel, _ = RockPaperScissorsModel.get_or_create(user_id=author.id, username=str(author))

    comp_selection = randint(0, 2)
    result = simulate(user_selection, comp_selection)
    embed = None
    if result:
        embed = discord.Embed(colour=discord.Colour.green(),
                            title=f"You won!\nYou {get_selection_word(user_selection)} vs {get_selection_word(comp_selection)} CatGameBot")
        RockPaperScissorsModel.update(wins=RockPaperScissorsModel.wins + 1,
                                    last_played=datetime.datetime.now()).where(
                                    RockPaperScissorsModel.username == str(author)).execute()
    elif result is False:
        embed = discord.Embed(colour=discord.Colour.red(),
                            title=f"You lost!\nYou {get_selection_word(user_selection)} vs {get_selection_word(comp_selection)} CatGameBot")
        RockPaperScissorsModel.update(loss=RockPaperScissorsModel.loss + 1,
                                    last_played=datetime.datetime.now()).where(
                                    RockPaperScissorsModel.username == str(author)).execute()
    else:
        embed = discord.Embed(colour=discord.Colour.orange(),
                            title=f"You drew!\nYou {get_selection_word(user_selection)} vs {get_selection_word(comp_selection)} CatGameBot")
        RockPaperScissorsModel.update(draw=RockPaperScissorsModel.draw + 1,
                                    last_played=datetime.datetime.now()).where(
                                    RockPaperScissorsModel.username == str(author)).execute()
    return embed

def simulate(user_selection, comp_selection):
    # Computer win
    if ((user_selection + 1) % 3) == comp_selection:
        return False
    # User win
    elif ((comp_selection + 1) % 3) == user_selection:
        return True
    # Draw
    else:
        return None

def get_selection_word(number):
    if number == 0:
        return ":fist:"
    elif number == 1:
        return ":raised_hand:"
    elif number == 2:
        return ":v:"
    else:
        return "Error"

def get_user_selection(selection):
    if selection == 'rock' or selection == 'r':
        return 0
    elif selection == 'paper' or selection == 'p':
        return 1
    elif selection == 'scissors' or selection == 's':
        return 2
    else:
        return -1

class RockPaperScissorsModel(Model):
    user_id = PrimaryKeyField()
    username = TextField()
    wins = IntegerField(default=0)
    loss = IntegerField(default=0)
    draw = IntegerField(default=0)
    last_played = DateTimeField(default=datetime.datetime.now)
    created_date = DateTimeField(default=datetime.datetime.now)
    class Meta:
        database = database
        db_table = 'RockPaperScissors'

def setup_database():
    database.create_tables([RockPaperScissorsModel])