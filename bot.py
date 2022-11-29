#bot.py
import os


import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
from discord.ext import tasks
from discord.utils import get

def setup_logging():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    
    main_logger = logging.getLogger('mainscript')
    main_logger.setLevel(logging.DEBUG)
    main_handler = logging.FileHandler(filename='logs/mainscript.log', encoding='utf-8', mode='w')
    main_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    main_logger.addHandler(handler)


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        watching = discord.Activity(type=discord.ActivityType.watching, name="/")
        super().__init__(command_prefix = '?',intents=intents, activity=watching, status=discord.Status.online)

    async def setup_cogs(self):
        num_cogs=0
        for cog in os.listdir("cogs/"):
            if cog[-3:] == '.py':
                num_cogs +=1 

        cog_index = 0
        print('cogs loaded :\n')
        for cog in os.listdir("cogs/"):

            if cog[-3:] == '.py':
                if cog_index ==0:
                    print(len(cog)* '-')
                else:
                    pass
                cog_name = f"cogs.{cog[:-3]}"
                await commands.Bot.load_extension(self,name=cog_name)
                cog_index+=1
                if cog_index == num_cogs:
                    print(len(cog)*"-"+"\n")

                    
    async def setup_hook(self) -> None:
        await self.setup_cogs()
        await self.tree.sync()
        print(f"synced slash commands for {self.user}.")
    
    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)
 





async def setup_cogs(bot):
    num_cogs=0
    for cog in os.listdir("cogs/"):
        if cog[-3:] == '.py':
            num_cogs +=1 

    cog_index = 0
    print('cogs loaded :\n')
    for cog in os.listdir("cogs/"):

        if cog[-3:] == '.py':
            if cog_index ==0:
                print(len(cog)* '-')
            else:
                pass
            
            await bot.load_extension(f"cogs.{cog[:-3]}")
            cog_index+=1
            if cog_index == num_cogs:
                print(len(cog)*"-"+"\n")
    
bot = Bot()
        
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

# intents = discord.Intents.default()
# intents.members = True
# #bot = discord.Client()
# watching = discord.Activity(type=discord.ActivityType.watching, name="/")
# bot = commands.Bot('?',intents=intents, activity=watching, status=discord.Status.online)

setup_logging()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    
    print(f'{bot.user} is connected to the following guilds:\n')
    
    for guild in bot.guilds:
        print(f'{guild.name}(id: {guild.id})')
        global guilds













# @bot.event
# async def on_command_error(ctx,error):
#     if isinstance(error, commands.CommandNotFound):
#         await ctx.send( "No such command")
#     else:
#         #print("error with command "+str(error))
#         raise error


async def setup_cogs(bot):
    num_cogs=0
    for cog in os.listdir("cogs/"):
        if cog[-3:] == '.py':
            num_cogs +=1 

    cog_index = 0
    print('cogs loaded :\n')
    for cog in os.listdir("cogs/"):

        if cog[-3:] == '.py':
            if cog_index ==0:
                print(len(cog)* '-')
            else:
                pass
            
            await bot.load_extension(f"cogs.{cog[:-3]}")
            cog_index+=1
            if cog_index == num_cogs:
                print(len(cog)*"-"+"\n")

#bot.setup_cogs()

bot.run(TOKEN)