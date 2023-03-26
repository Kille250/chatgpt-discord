from discord import Embed
from discord.ext import commands
from db.database import Database
from permission import check_whitelist

class Profile(commands.Cog):
    def __init__(self, bot):
        self.empty = "No Content available."
        self.bot = bot
        self.db = Database()

    @commands.command("profile")
    @check_whitelist
    async def profile(self, ctx: commands.Context):
        title = f"Profile from {ctx.author.name}"

        user_messages =self.db.convmessages_role_get(
                user_id=ctx.author.id,
                role="user"
            )
        
        if len(user_messages) > 0:
            user_messages = len(user_messages)
        else:
            user_messages = None
        
        last_bot_message = self.db.convmessages_role_get(
                user_id=ctx.author.id,
                role="assistant",
                limit=1
            )
        
        if len(last_bot_message) > 0:
            last_bot_message = last_bot_message[0][4]
        else:
            last_bot_message = None

        fields = {
            "AI-Requests": user_messages,
            "Last Answer Received": last_bot_message
            }

        for key in fields.keys():

            if fields[key] is None:
                fields[key] = self.empty

        # WIP
        embed = Embed(
            title=title, 
            description="Description is WIP. Will get changable."
            )

        embed.set_thumbnail(url=ctx.author.avatar.url)

        for key in fields.keys():
            embed.add_field(
                name=key,
                value=fields[key]
                )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))