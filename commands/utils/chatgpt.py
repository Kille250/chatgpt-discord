from discord.ext import commands
import openai
import os
from dotenv import load_dotenv
from db.database import Database


class Chatgpt(commands.Cog):
    def __init__(self, bot: commands.Bot):
        load_dotenv()

        self.bot = bot
        self.ai = openai

        self.database = Database()

        self.ai.api_key = os.getenv("AI_KEY")
        self.model = os.getenv("MODEL")

    @commands.command(name="conv")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def conv(self, ctx: commands.Context, arg1, arg2=None):
        user = self.database.conv_get(
            user_id=ctx.author.id
        )

        print(user)

        allowed_params = [
            "start",
            "close"
        ]

        if arg1 not in allowed_params:
            await ctx.send(
                "Please type start or close for the first parameter."
                )
            return

        if arg2 is None and arg1 != "close":
            await ctx.send("You need to specify a role.")

        if arg1 == "start":
            if len(user) > 0:
                await ctx.send("Conversation already opened.")
                return

        if arg1 == "close":
            if len(user) > 0:
                affected_rows = self.database.conv_update_status(
                                user_id=ctx.author.id
                            )
                if affected_rows < 1:
                    await ctx.send(
                        "A Error occured on closing the conversation."
                        )
                await ctx.send("Conversation successfully closed.")
                return
            await ctx.send("Nothing to close.")
            return

        conv_id = self.database.conv_insert(
            user_id=ctx.author.id,
            status=1
            )

        self.database.convmessage_insert(
            user_id=ctx.author.id,
            conv_id=conv_id,
            role="system",
            message=arg2
        )

        await ctx.send(f"Conversation started with the id {conv_id}.")
        return

    @commands.command(name="ask")
    async def ask(self, ctx: commands.Context, arg1):
        conv = self.database.conv_get(
            user_id=ctx.author.id
        )

        if len(conv) < 1:
            await ctx.send("You need to start a conversation first.")
            return

        conv_id = conv[0][0]

        conv_messages = self.database.convmessage_get(
            user_id=ctx.author.id,
            conv_id=conv_id
        )

        messages = []

        for message in conv_messages:
            messages.append(
                {"role": message[3], "content": message[4]}
            )

        messages.append({"role": "user", "content": arg1})

        response = await self.ai.ChatCompletion.acreate(
            model=self.model,
            messages=messages
        )

        self.database.convmessage_insert(
            user_id=ctx.author.id,
            conv_id=conv_id,
            role="user",
            message=arg1
        )

        content = response["choices"][0]["message"]['content']

        self.database.convmessage_insert(
            user_id=ctx.author.id,
            conv_id=conv_id,
            role=response["choices"][0]["message"]['role'],
            message=content
        )

        await ctx.send(content)


async def setup(bot):
    await bot.add_cog(Chatgpt(bot))