import discord
from discord.ext import commands
from datetime import datetime
import logging

import constants
import utility
from Bonus import Bonus
from EventTime import EventTime

class AdminCog(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    @commands.command(name='start', help='Starts ping reminders', hidden=True)
    async def start(self, ctx):
        is_admin = utility.is_admin(ctx.message.author, self.settings)
        if is_admin is False:
            return
        
        self.settings.run_ping_reminder = True
        if self.settings.is_running_ping_reminder is False:
            self.bot.loop.create_task(ping_reminder())
            await ctx.send('Bot was started successfully | 1')
            return
        
        await ctx.send('Bot was started successfully | 2')

    @commands.command(name='stop', help='Stops ping reminders', hidden=True)
    async def stop(self, ctx):
        is_admin = utility.is_admin(ctx.message.author, self.settings)
        if is_admin is False:
            return
        
        self.settings.run_ping_reminder = False
        await ctx.send('Ping reminder stopped successfully')

    @commands.command(name='addevent', help='Adds a new mini event. Example: !addevent yyyy-mm-dd yyyy-mm-dd', hidden=True)
    async def add_event(self, ctx, start, stop):
        print(f'{start=}')
        print(f'{stop=}')
        is_admin = utility.is_admin(ctx.message.author, self.settings)
        if is_admin is False:
            return
        
        # Syntax: !addevent 2020-10-06 2020-16-06
        try:
            # Because it's parsed as aest, I have to remove 1day so it matches utc and therefore matches the in game times
            startTime = datetime.strptime(f'{start} 00:00:00', '%Y-%m-%d %H:%M:%S')
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

    @commands.command(name='delevent', help='Deletes a mini event. optional arg: number. Example: !delevent 3 2, deletes event nr. 3 and 2', hidden=True)
    async def delete_event(self, ctx, *number):
        is_admin = utility.is_admin(ctx.message.author, self.settings)
        if is_admin is False:
            return
        
        numbers = []
        if len(number) <= 0:
            for i in range(len(self.settings.event_times) - 1, -1 , -1):
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

    @commands.command(name='bonus', help='Lists the full bonus schedule', hidden=True)
    async def bonus_list(self, ctx):
        is_admin = utility.is_admin(ctx.message.author, self.settings)
        if is_admin is False:
            return
        
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.set_author(name=f'Current bonus order')
        for bonus in self.settings.minievents:
            embed.add_field(name=bonus.event_name, value=f'{bonus.tag}', inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='delbonus', help='Clears the bonus schedule', hidden=True)
    async def bonus_delete(self, ctx):
        is_admin = utility.is_admin(ctx.message.author, self.settings)
        if is_admin is False:
            return
        
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        settings_saved = self.settings.save_settings()
        saved = 'Saved successfully' if settings_saved else 'Failed to save!'
        embed.set_author(name=f'Deleted: {len(self.settings.minievents)} bonus.\n{saved}')
        self.settings.minievents.clear() 

        await ctx.send(embed=embed)

    @commands.command(name='addbonus', help='Adds a new bonus to the bonus schedule. Example: !addbonus "1min crafting" <@&689721344455213139>', hidden=True)
    async def bonus_add(self, ctx, event_name: str, tag: str):
        is_admin = utility.is_admin(ctx.message.author, self.settings)
        if is_admin is False:
            return
        
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        self.settings.minievents.insert(len(self.settings.minievents), Bonus(event_name, tag))

        settings_saved = self.settings.save_settings()
        saved = 'Saved successfully' if settings_saved else 'Failed to save!'
        embed.set_author(name=f'Added bonus: {event_name}.\n{saved}')
        
        await ctx.send(embed=embed)