import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TARGET_STRING = os.getenv('TARGET_STRING')
DELAY_SECONDS = os.getenv('DELAY_SECONDS')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='--', intents=intents)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def delete(ctx, amount: int, *, search_str: str):
    """
    Deleta mensagens contendo uma string específica do canal.
    Esta função pesquisa no histórico do canal e deleta mensagens que contêm
    a string de busca especificada (não diferencia maiúsculas/minúsculas). Irá deletar até
    o número máximo de mensagens especificado.
    Args:
        ctx: O objeto de contexto que representa o contexto de invocação do comando
        amount (int): Número máximo de mensagens para deletar
        search_str (str): String para procurar nas mensagens (não diferencia maiúsculas/minúsculas)
    Raises:
        discord.errors.Forbidden: Quando o bot não tem permissão para deletar mensagens
        discord.errors.HTTPException: Quando ocorre um erro HTTP durante a deleção
    Notas:
        - A mensagem do comando é deletada primeiro
        - A busca é limitada às últimas 1000 mensagens no canal
        - Uma mensagem de confirmação é enviada e auto-deletada após 5 segundos
        - Mensagens de erro são auto-deletadas após 5 segundos
    """
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
    Returns:
        None: Esta função não retorna valores.
    """
    
    if message.author == bot.user:
        return

    if TARGET_STRING.lower() in message.content.lower():
        try:
            await asyncio.sleep(int(DELAY_SECONDS))
            await message.delete()
            await message.channel.send(f'Mensagem contendo "{TARGET_STRING}" deletada.', delete_after=5)
        except discord.errors.Forbidden:
            await message.channel.send("Não possuo permissão para deletar mensagens.", delete_after=5)
        except discord.errors.HTTPException as e:
            await message.channel.send(f"Ocorreu um erro: {e}", delete_after=5)

    await bot.process_commands(message)
        
bot.run(TOKEN)