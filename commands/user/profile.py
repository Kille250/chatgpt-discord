from discord import Embed
from discord.ext import commands
from db.database import Database


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.command("profile")
    async def profile(self, ctx: commands.Context):
        title = f"Profile from {ctx.author.name}"

        fields = {
            "AI-Requests": len(self.db.convmessages_role_get(
                user_id=ctx.author.id,
                role="user"
            )),
            "Last Answer Recieved": self.db.convmessages_role_get(
                user_id=ctx.author.id,
                role="assistant",
                limit=1
            )[0][4]
        }

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