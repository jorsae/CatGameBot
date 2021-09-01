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
    
    def is_moderator():
        def predicate(ctx):
            is_admin = ctx.message.author.id in constants.ADMIN_LIST
            if is_admin:
                return True
            return ctx.message.author.id in constants.MODERATOR_LIST
        return commands.check(predicate)
    
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
    @commands.command(name='stop', help='Stops ping reminders', hidden=True)
    async def stop(self, ctx):
        self.settings.run_ping_reminder = False
        await ctx.send('Ping reminder stopped successfully')
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        username = f'[{ctx.message.author.id}] {ctx.message.author.name}#{ctx.message.author.discriminator}'
        logging.error(f'on_command_error {username}: {error}')