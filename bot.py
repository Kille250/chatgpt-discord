import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from db.database import Database

load_dotenv()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)


async def setup(bot):
    for i in os.listdir("./commands"):
        for n in os.listdir(f"./commands/{i}"):
            if n.endswith(".py"):
                await bot.load_extension(f"commands.{i}.{n[:-3]}")


def db_setup():
    db = Database()

    table_name = "Conv"

    table = [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id INTEGER NOT NULL",
        "status INTEGER NOT NULL"
    ]

    db.create_table(table_name=table_name, tables=table)

    table_name = "Convmessage"

    table = [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id INTEGER NOT NULL",
        "conv_id INTEGER NOT NULL",
        "role TEXT NOT NULL",
        "message TEXT NOT NULL",
        "FOREIGN KEY (conv_id) REFERENCES Conv(id)",
    ]

    db.create_table(table_name=table_name, tables=table)


@bot.event
async def on_ready():
    db_setup()

    await setup(bot)
    print(f'We have logged in as {bot.user}')

bot.run(os.getenv("DISCORD_API_KEY"))