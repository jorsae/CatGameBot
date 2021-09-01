import discord
from discord.ext import commands
from datetime import datetime, timedelta
import logging
import math

import constants
import utility
from Bonus import Bonus
from EventTime import EventTime
import RockPaperScissors

class General(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    @commands.command(name='next', help="next <digit> will list the next <digit> events. Max is 9 events. e.g: !next 5")
    async def next(self, ctx, iterations: str="3"):
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)

        iterations = utility.clean_iterations(iterations)

        if len(self.settings.minievents) <= 0:
            embed.colour = constants.COLOUR_NEUTRAL
            embed.set_author(name=f'No minievent schedule set.\nPlease let {self.admin} know')
            await ctx.send(embed=embed)
            return

        if utility.is_event(self.settings) is False:
            embed.colour = constants.COLOUR_ERROR
            next_event = utility.get_next_event(self.settings)

            if next_event is None:
                embed.set_author(name='No event is currently running.')
                await ctx.send(embed=embed)
                return
            time_left = next_event - datetime.utcnow()

            difference = (datetime.utcnow() - next_event).total_seconds()
            event_iterations = math.floor(difference / constants.SIX_HOURS)
            start_event = (self.settings.start_event + event_iterations) % len(self.settings.minievents)
            embed.add_field(name=f'No event is currently running.\nNext event in {time_left}', value=f'Starting event is: {self.settings.minievents[start_event]}')
            await ctx.send(embed=embed)
            return
        
        difference = (datetime.utcnow() - self.settings.start_time).total_seconds()
        event_iterations = math.floor(difference / constants.SIX_HOURS)
        next_event = (self.settings.start_event + event_iterations) % len(self.settings.minievents)

        time_difference = constants.SIX_HOURS - (difference % constants.SIX_HOURS)
        
        event_text = 'event' if iterations <= 1 else f'{iterations} events'
        embed = discord.Embed(colour=constants.COLOUR_OK)
        embed.set_author(name=f'Next {event_text}')
        
        # Event is currently ongoing NOW
        if (constants.SIX_HOURS - time_difference) < 1800:
            time_left = constants.EVENT_DURATION - (constants.SIX_HOURS - time_difference)
            time_left = utility.format_timedelta(timedelta(seconds=time_left))
            embed.add_field(name=f'{self.settings.minievents[next_event]}', value=f'Time remaining: {time_left}')
            iterations -= 1
        
        for i in range(iterations):
            time_left = i * constants.SIX_HOURS + time_difference
            time_left = utility.format_timedelta(timedelta(seconds=time_left))
            event = (next_event + (i+1)) % len(self.settings.minievents)
            embed.add_field(name=f'{self.settings.minievents[event]}', value=f'Time until: {time_left}')

        await ctx.send(embed=embed)

    @commands.command(name='event', help='Lists current event times')
    async def list_events(self, ctx):
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        
        author = ctx.message.author
        is_admin = utility.is_admin(author, self.settings)
        
        embed.set_author(name=f'Current events [utc]')

        now = datetime.utcnow()
        index = 0
        for event in self.settings.event_times:
            name = 'Mini event'
            if is_admin:
                name = f'[{index}] {name}'
                if event.end_time <= now:
                    name = f'{name} | Finished'
                embed.add_field(name=name, value=f'{event.start_time} - {event.end_time}', inline=False)
            else:
                if event.end_time > now:
                    embed.add_field(name=name, value=f'{event.start_time} - {event.end_time}', inline=False)
            index += 1
        await ctx.send(embed=embed)

    @commands.command(name='time', aliases=['daily'], help='Lists the time till daily reset')
    async def time(self, ctx):
        embed = discord.Embed(colour=constants.COLOUR_OK)
        embed.set_author(name=f'Cat Game time')
        
        now = datetime.utcnow()
        seconds = ((24 - now.hour - 1) * 60 * 60) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        reset = timedelta(seconds=seconds)
        reset = utility.format_timedelta(reset)

        embed.add_field(name=f'Time till daily reset: {reset}', value=f'[utc] CatGame time: {now}\n', inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='calculator', aliases=['calc'], help='Cat Game Calculator to help you craft')
    async def calculator(self, ctx):
        await ctx.send(f'Visit https://CatGameCalculator.com to help your crafting needs')

    @commands.command(name='rps', help='Rock paper scissors mini game. !rps help for more details!')
    async def rps(self, ctx, selection: str='help'):
        selection = selection.lower()
        embed = None
        if selection == 'help':
            embed = RockPaperScissors.help(self.settings)
        elif selection == 'rank' or selection == 'ranks':
            embed = RockPaperScissors.rank()
        elif selection == 'profile':
            embed = RockPaperScissors.profile(ctx.message.author)
        else:
            embed = RockPaperScissors.game(ctx.message.author, selection)
        await ctx.send(embed=embed)

    @commands.command(name='ping', help='CatGameBot speed test')
    async def ping(self, ctx):
        ms = round(bot.latency, 3)
        await ctx.send(f'Pong! {ms} sec')

    @commands.command(name='help', help='Displays this help message')
    async def help(self, ctx):
        author = ctx.message.author
        
        cogs = []
        cogs.append(self.bot.get_cog('General'))
        cogs.append(self.bot.get_cog('Moderator'))
        cogs.append(self.bot.get_cog('Admin'))

        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.set_author(name=f'BMW Help')
        for cog in cogs:
            for command in cog.walk_commands():
                if await command.can_run(ctx):
                    embed.add_field(name=f'{self.settings.prefix}{command}{utility.get_aliases(command.aliases)}', value=command.help, inline=False)
        await ctx.send(embed=embed)