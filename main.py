import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TARGET_STRING = os.getenv('TARGET_STRING')
DELAY_SECONDS = int(os.getenv('DELAY_SECONDS'))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='--', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logado como {bot.user} (ID: {bot.user.id})")
    print('------')

@bot.tree.command(name="delete", description="Deleta mensagens contendo uma string específica do canal.")
@app_commands.describe(amount="Número máximo de mensagens para deletar", search_str="String para procurar nas mensagens")
@app_commands.checks.has_permissions(manage_messages=True)
async def delete_slash(interaction: discord.Interaction, amount: int, search_str: str):
    """
    Deleta mensagens contendo uma string específica do canal via comando de barra.
    Esta função pesquisa no histórico do canal e deleta mensagens que contêm
    a string de busca especificada (não diferencia maiúsculas/minúsculas). Irá deletar até
    o número máximo de mensagens especificado.
    Args:
        interaction (discord.Interaction): O objeto de interação do Discord.
        amount (int): Número máximo de mensagens para deletar.
        search_str (str): String para procurar nas mensagens (não diferencia maiúsculas/minúsculas).
    Raises:
        discord.errors.Forbidden: Quando o bot não tem permissão para deletar mensagens.
        discord.errors.HTTPException: Quando ocorre um erro HTTP durante a deleção.
    Notas:
        - A busca é limitada às últimas 1000 mensagens no canal.
        - Uma mensagem de confirmação é enviada e auto-deletada após 5 segundos.
        - Mensagens de erro são auto-deletadas após 5 segundos.
    """
    await interaction.response.defer(ephemeral=True)

    deleted_messages = []
    channel = interaction.channel

    async for message in channel.history(limit=1000):
        if search_str.lower() in message.content.lower():
            try:
                await message.delete()
                deleted_messages.append(message)
                if len(deleted_messages) >= amount:
                    break
            except discord.errors.Forbidden:
                await interaction.followup.send("Não possuo permissão para deletar mensagens.", ephemeral=True)
                return
            except discord.errors.HTTPException as e:
                await interaction.followup.send(f"Ocorreu um erro: {e}", ephemeral=True)
                return

    await interaction.followup.send(f'Deletadas {len(deleted_messages)} mensagens contendo "{search_str}".', ephemeral=True)

@bot.command(name='delete', help='Deleta mensagens contendo uma string específica do canal.')
@commands.has_permissions(manage_messages=True)
async def delete_prefix(ctx, amount: int, *, search_str: str):
    """
    Deleta mensagens contendo uma string específica do canal via comando de prefixo (--).
    Esta função pesquisa no histórico do canal e deleta mensagens que contêm
    a string de busca especificada (não diferencia maiúsculas/minúsculas). Irá deletar até
    o número máximo de mensagens especificado.
    Args:
        interaction (discord.Interaction): O objeto de interação do Discord.
        amount (int): Número máximo de mensagens para deletar.
        search_str (str): String para procurar nas mensagens (não diferencia maiúsculas/minúsculas).
    Raises:
        discord.errors.Forbidden: Quando o bot não tem permissão para deletar mensagens.
        discord.errors.HTTPException: Quando ocorre um erro HTTP durante a deleção.
    Notas:
        - A busca é limitada às últimas 1000 mensagens no canal.
        - Uma mensagem de confirmação é enviada e auto-deletada após 5 segundos.
        - Mensagens de erro são auto-deletadas após 5 segundos.
    """
    await ctx.message.delete()

    deleted_messages = []
    channel = ctx.channel

    async for message in channel.history(limit=1000):
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

    await ctx.send(f'Deletadas {len(deleted_messages)} mensagens contendo "{search_str}".', delete_after=5)

@bot.event
async def on_message(message):
    """
    Manipula eventos de mensagem no Discord.
    Esta função é chamada automaticamente quando uma mensagem é enviada em qualquer canal
    que o bot tem acesso. Ela verifica se a mensagem contém uma string específica e,
    caso positivo, deleta a mensagem após um delay configurado.
    Args:
        message (discord.Message): O objeto de mensagem recebido do Discord.
    Raises:
        discord.errors.Forbidden: Quando o bot não tem permissão para deletar mensagens.
        discord.errors.HTTPException: Quando ocorre um erro na comunicação com a API do Discord.
    """

    if message.author == bot.user:
        return

    if TARGET_STRING.lower() in message.content.lower():
        try:
            await asyncio.sleep(DELAY_SECONDS)
            await message.delete()
            await message.channel.send(f'Mensagem contendo "{TARGET_STRING}" deletada.', delete_after=5)
        except discord.errors.Forbidden:
            await message.channel.send("Não possuo permissão para deletar mensagens.", delete_after=5)
        except discord.errors.HTTPException as e:
            await message.channel.send(f"Ocorreu um erro: {e}", delete_after=5)

    await bot.process_commands(message)

bot.run(TOKEN)
