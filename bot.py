import os
import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

async def setup(bot):
    for i in os.listdir("./commands"):
        for n in os.listdir(f"./commands/{i}"):
            if n.endswith(".py"):
                await bot.load_extension(f"commands.{i}.{n[:-3]}")

@bot.event
async def on_ready():
    await setup(bot)
    print(f'We have logged in as {bot.user}')

bot.run('OTI0NzEzMjIyMzE2MTE4MDU3.GSMBKb.78ssvSrfcTr5mlfN4gMJJCBMGdU_Ua3rwMm8tc')