import discord
from discord.ext import commands
from datetime import datetime, timedelta
import logging

import constants
import utility
from Bonus import Bonus
from EventTime import EventTime

class Admin(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    def is_admin():
        def predicate(ctx):
            return ctx.message.author.id in constants.ADMIN_LIST
        return commands.check(predicate)
    
    @is_admin()
    @commands.command(name='addbonus', help='Adds a new bonus to the bonus schedule.\nExample: `!addbonus "1min crafting" @crafting`')
    async def bonus_add(self, ctx, event_name: str, tag: str):
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        self.settings.minievents.insert(len(self.settings.minievents), Bonus(event_name, tag))

        settings_saved = self.settings.save_settings()
        saved = 'Saved successfully' if settings_saved else 'Failed to save!'
        embed.set_author(name=f'Added bonus: {event_name}.\n{saved}')
        
        await ctx.send(embed=embed)

    @is_admin()
    @commands.command(name='delbonus', help='Clears the bonus schedule')
    async def bonus_delete(self, ctx):
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        settings_saved = self.settings.save_settings()
        saved = 'Saved successfully' if settings_saved else 'Failed to save!'
        embed.set_author(name=f'Deleted: {len(self.settings.minievents)} bonus.\n{saved}')
        self.settings.minievents.clear() 

        await ctx.send(embed=embed)

    @is_admin()
    @commands.command(name='start', help='Starts ping reminders')
    async def start(self, ctx):
        self.settings.run_ping_reminder = True
        if self.settings.is_running_ping_reminder is False:
            self.bot.loop.create_task(ping_reminder())
            await ctx.send('Bot was started successfully | 1')
            return
        
        await ctx.send('Bot was started successfully | 2')
    
    @is_admin()
    @commands.command(name='stop', help='Stops ping reminders')
    async def stop(self, ctx):
        self.settings.run_ping_reminder = False
        await ctx.send('Ping reminder stopped successfully')
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        username = f'[{ctx.message.author.id}] {ctx.message.author.name}#{ctx.message.author.discriminator}'
        logging.error(f'on_command_error {username}: {error}')