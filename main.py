import discord
from datetime import datetime
from discord.ext import commands
from settings import Settings
import event

settings = Settings('settings.json')
bot = commands.Bot(command_prefix='!')

@bot.command(name='list')
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command(name='next')
async def next(ctx):
    await ctx.send(event.next(ctx, settings))

@bot.event
async def on_message(message: discord.Message):
    await bot.wait_until_ready()
    message.content = (
        message.content.replace("—", "--")
        .replace("'", "′")
        .replace("‘", "′")
        .replace("’", "′")
    )
    await bot.process_commands(message)

async def do_tasks():
    await bot.wait_until_ready()
    print(f"Logged in as {bot.user}")

if __name__ == '__main__':
    settings.parse_settings()
    print(settings)
    bot.loop.create_task(do_tasks())
    bot.run(settings.token)