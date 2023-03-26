from functools import wraps
from db.database import Database

def check_whitelist(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = Database()
        ctx = args[1]
        results = db.whitelist_get(
            user_id=ctx.author.id
        )
        if len(results) < 1:
            await ctx.send("No Permission.")
            return

        for i in results:
            if i[2] == ctx.invoked_with:
                return await func(*args, **kwargs)
            
        await ctx.send("No Permission.")
    return wrapper