import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='--', intents=intents)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def delete(ctx, amount: int, *, search_str: str):
    await ctx.message.delete()

    deleted_messages = []
    async for message in ctx.channel.history(limit=1000):
        if search_str.lower() in message.content.lower():
            try:
                await message.delete()
                deleted_messages.append(message)
                if len(deleted_messages) >= amount:
                    break
            except discord.errors.Forbidden:
                await ctx.send("Não possuo permissão para deletar mensagens.", delete_after=5)
                return
            except discord.errors.HTTPException as e:
                await ctx.send(f"Ocorreu um erro: {e}", delete_after=5)
                return

    await ctx.send(f'Deletadas {len(deleted_messages)} mensagens, contendo "{search_str}".', delete_after=5)

bot.run(TOKEN)