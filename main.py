import discord
from discord.ext import commands
from settings import Settings

bot = commands.Bot(command_prefix='$')

@bot.command(name='list')
async def test(ctx, arg):
    await ctx.send(arg)

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
    settings = Settings('settings.json')
    settings.parse_settings()
    bot.loop.create_task(do_tasks())
    bot.run(settings.token)