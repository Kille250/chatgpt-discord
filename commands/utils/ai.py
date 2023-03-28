from discord.ext import commands
import openai
import os
from dotenv import load_dotenv
from retry import retry
import replicate
from db.database import Database
from permission import check_whitelist


class Chatgpt(commands.Cog):
    def __init__(self, bot: commands.Bot):
        load_dotenv()

        self.bot = bot
        self.ai = openai
        self.replicate = replicate

        self.database = Database()

        self.replicate_model = "cjwbw/dreamshaper:ed6d8bee9a278b0d7125872bddfb9dd3fc4c401426ad634d8246a660e387475b"

        self.ai.api_key = os.getenv("AI_KEY")
        self.model = os.getenv("MODEL")
        self.max_tokens = os.getenv("MAX_TOKENS")

    @retry(delay=1, backoff=2, max_delay=120, tries=3)
    async def ai_chat_call_retry(self, messages):

        response = await self.ai.ChatCompletion.acreate(
            model=self.model,
            messages=messages,
            max_tokens=int(self.max_tokens)
        )

        return response

    @commands.command(name="conv")
    async def conv(self, ctx: commands.Context, arg1):
        user = self.database.conv_get(
            user_id=ctx.author.id
        )

        allowed_params = [
            "start",
            "close"
        ]

        if arg1 not in allowed_params:
            await ctx.send(
                "Please type start or close as a parameter"
                )
            return

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

        await ctx.send(f"Conversation started with the id {conv_id}.")
        return

    @commands.command(name="role")
    async def role(self, ctx: commands.Context, *, arg):
        conv = self.database.conv_get(
            user_id=ctx.author.id
        )

        if len(conv) < 1:
            await ctx.send("You need to create a conversation first.")
            return

        conv_id = conv[0][0]

        self.database.convmessage_insert(
            user_id=ctx.author.id,
            conv_id=conv_id,
            role="system",
            message=arg
        )

        await ctx.send("Role successfully updated.")

    @commands.command(name="ask")
    @check_whitelist
    async def ask(self, ctx: commands.Context, *, arg):
        conv = self.database.conv_get(
            user_id=ctx.author.id
        )

        if len(conv) < 1:
            await ctx.send("You need to start a conversation first.")
            return

        conv_id = conv[0][0]

        role_message = self.database.convmessages_system_get(
            user_id=ctx.author.id,
            conv_id=conv_id
        )

        if len(role_message) < 1:
            await ctx.send("You need to set up a role first.")
            return

        messages = []

        conv_messages = self.database.convmessages_get(
            user_id=ctx.author.id,
            conv_id=conv_id
        )

        for message in conv_messages:
            messages.append(
                {"role": message[3], "content": message[4]}
            )

        messages.append({
            "role": role_message[0][3],
            "content": role_message[0][4],
            })

        messages.append({"role": "user", "content": arg})

        try:
            response = await self.ai_chat_call_retry(
                messages=messages
            )
        except Exception as e:
            await ctx.send(f"A Error Occured: {e}")
            return

        self.database.convmessage_insert(
            user_id=ctx.author.id,
            conv_id=conv_id,
            role="user",
            message=arg
        )

        content = response["choices"][0]["message"]['content']

        self.database.convmessage_insert(
            user_id=ctx.author.id,
            conv_id=conv_id,
            role=response["choices"][0]["message"]['role'],
            message=content
        )

        await ctx.reply(content)

    @commands.command("imagine")
    @check_whitelist
    async def imagine(self, ctx: commands.Context, *, arg):
        arguments = {
            "prompt": arg
        }

        result = self.replicate.run(
            self.replicate_model,
            input=arguments
        )

        await ctx.send(result[0])

    @commands.command("remix")
    @check_whitelist
    async def remix(self, ctx: commands.Context, *, arg):
        prompt = arg

        try:
            image = ctx.message.attachments[0]
            image_data = await image.read()
            mask = ctx.message.attachments[1]
            mask_data = await mask.read()
        except Exception:
            await ctx.send(
                "You must provide two square PNG files less than 4MB each."
                )

        try:
            response = self.ai.Image.create_edit(
                image_data,
                mask_data,
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            output = response['data'][0]['url']
            await ctx.send(output)
        except self.ai.error.OpenAIError as e:
            await ctx.send("Error Code: " + str(e.http_status))
            await ctx.send(e.error)


async def setup(bot):
    await bot.add_cog(Chatgpt(bot))
