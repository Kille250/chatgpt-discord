from discord.ext import commands
from db.database import Database

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot_owner = 178558083688169472
        self.bot = bot
        self.db = Database()

    def user_get(self, user_id):
        result = self.db.whitelist_get(
            user_id=user_id
        )

        if len(result) < 1:
            return None
        
        return result
    
    def user_set(self, user_id, command):
        result = self.db.whitelist_set(
            user_id=user_id,
            command=command
        )

        if result is None:
            return None
        
        return result
    
    def user_delete(self, user_id, command):
        result = self.db.whitelist_remove(
            user_id=user_id,
            command=command
        )

        print(result)

        if result < 1:
            return None
        
        return result

    
    @commands.command("whitelist")
    async def whitelist(self, ctx: commands.Context, arg1, arg2, arg3):
        
        if self.bot_owner != ctx.author.id:
            await ctx.send("You can't use this command.")
            return
        
        match arg1:
            case "add":

                result = self.user_set(
                    user_id=arg2,
                    command=arg3
                )

                if result is None:
                    await ctx.send("Whitelist couldn't be added.")
                    return
                
                await ctx.send("Whitelist added.")

            case "remove":
                result = self.user_delete(
                    user_id=arg2,
                    command=arg3
                )

                if result is None:
                    await ctx.send("Whitelist couldn't get removed.")
                    return

                await ctx.send("Whitelist removed.")

async def setup(bot):
    await bot.add_cog(Whitelist(bot))