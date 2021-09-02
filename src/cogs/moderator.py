import discord
from discord.ext import commands
from datetime import datetime, timedelta
import logging

import constants
import utility
from Bonus import Bonus
from EventTime import EventTime

class Moderator(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    def is_admin():
        def predicate(ctx):
            return ctx.message.author.id in constants.ADMIN_LIST
        return commands.check(predicate)
    
    def is_moderator():
        def predicate(ctx):
            is_admin = ctx.message.author.id in constants.ADMIN_LIST
            if is_admin:
                return True
            return ctx.message.author.id in constants.MODERATOR_LIST
        return commands.check(predicate)
    
    @is_moderator()
    @commands.command(name='addevent', help='Adds a new mini event.\nExample: `!addevent yyyy-mm-dd yyyy-mm-dd`')
    async def add_event(self, ctx, start, stop):
        # Syntax: !addevent 2020-10-06 2020-16-06
        try:
            # Because it's parsed as aest, I have to remove 1day so it matches utc and therefore matches the in game times
            startTime = datetime.strptime(f'{start} 00:00:00', '%Y-%m-%d %H:%M:%S') + timedelta(days=1)
            stopTime = datetime.strptime(f'{stop} 19:00:00', '%Y-%m-%d %H:%M:%S')

            self.settings.event_times.append(EventTime(startTime, stopTime))
            settings_saved = self.settings.save_settings()
            if settings_saved:
                await ctx.send(f'__Successfully added event:__\n{startTime} - {stopTime}')
            else:
                await ctx.send(f'Successfully added event, settings were not saved!\n{startTime} - {stopTime}')
        except Exception as e:
            logging.warning(f'Failed to add event time: {start} - {stop}. Exception: {e}')
            await ctx.send('Failed to add event time')

    @is_moderator()
    @commands.command(name='delevent', help='Deletes a mini event. optional arg: number.\nExample: `!delevent 3 2`, deletes event nr. 3 and 2')
    async def delete_event(self, ctx, *number):
        numbers = []
        if len(number) <= 0:
            now = datetime.utcnow()
            for i in range(len(self.settings.event_times) - 1, -1 , -1):
                if self.settings.event_times[i].end_time <= now:
                    numbers.append(i)
        else:
            numbers = utility.clean_number_input(number) # TODO: Add this to utility
        
        if numbers is None:
            await ctx.send('Bad user input')
        else:
            numbers = sorted(numbers)
        
        numbers = list(set(numbers))
        clean = utility.number_is_clean(numbers, self.settings.event_times) # TODO: Add this to utility
        if clean is False:
            await ctx.send('Bad user input')
        
        output = ''
        for i in reversed(numbers):
            logging.info(f'{ctx.message.author}: Deleted event: {self.settings.event_times[i]}')
            output += f'{self.settings.event_times[i]}\n'
            self.settings.event_times.pop(i)

        settings_saved = self.settings.save_settings()
        if settings_saved:
            await ctx.send(f'Successfully deleted: {output}')
        else:
            logging.error(f'{ctx.message.author} failed to delete: {output}')
            await ctx.send(f'Failed to delete: {output}')

    @is_moderator()
    @commands.command(name='bonus', help='Lists the full bonus schedule')
    async def bonus_list(self, ctx):
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.set_author(name=f'Current bonus order')
        for bonus in self.settings.minievents:
            embed.add_field(name=bonus.event_name, value=f'{bonus.tag}', inline=False)
        await ctx.send(embed=embed)