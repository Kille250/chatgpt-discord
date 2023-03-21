from discord.ext import commands
import openai, os
from dotenv import load_dotenv

class Chatgpt(commands.Cog):
    def __init__(self, bot: commands.Bot):
        load_dotenv()
        self.conversation = {}

        self.bot = bot
        self.ai = openai

        self.ai.api_key = os.getenv("AI_KEY")
        self.model = os.getenv("MODEL")

    @commands.command(name="conv")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def conv(self, ctx: commands.Context, arg1, arg2=None):
        user_id = ctx.author.id

        allowed_params = [
            "start",
            "close"
        ]

        if arg1 not in allowed_params:
            await ctx.send("Please type start or close for the first parameter.")
            return
        
        if arg2 is None and arg1 != "close":
            await ctx.send("You need to specify a role.")

        if arg1 == "start":
            if user_id in self.conversation.keys():
                await ctx.send("Conversation already opened.")
                return

        if arg1 == "close":
            if user_id in self.conversation.keys():
                self.conversation.pop(user_id)
            await ctx.send("Conversation removed.")
            return

        self.conversation[user_id] = [
            {
            "role": "system",
            "content": arg2
            }
        ]

        await ctx.send("Conversation started.")
        return

    @commands.command(name="ask")
    async def ask(self, ctx: commands.Context, arg1):
        conv_data = self.conversation.get(ctx.author.id)

        if conv_data == None:
            await ctx.send("You need to start a conversation first.")
            return
        
        message = {"role": "user", "content": arg1}
        
        conv_data.append(message)

        response = await self.ai.ChatCompletion.acreate(
            model=self.model,
            messages=conv_data
        )
        
        content = response["choices"][0]["message"]['content']
        role = response["choices"][0]["message"]['role']

        response = {"role": role, "content": content}

        conv_data.append(response)
        self.conversation[ctx.author.id] = conv_data

        await ctx.send(content)

async def setup(bot):
    await bot.add_cog(Chatgpt(bot))