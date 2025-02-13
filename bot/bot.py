import asyncio
import discord
import unidecode
import yaml
import os
import argparse
import pandas as pd

from dotenv import dotenv_values, load_dotenv

from discord.ext import commands
from pymongo import MongoClient
import logging


####
# CONFIG BOT
####
load_dotenv() # Quitar en deploy

BOT_PREFIX = '+'
ADMIN_TAG = 'administrador'

argparse = argparse.ArgumentParser(description='EventoBukanero')
argparse.add_argument('--mode', 
                      type=str, 
                      default='beta', 
                      help='Execution mode', 
                      choices=['beta', 'deploy'])
args = argparse.parse_args()
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

if args.mode == 'beta':
    TOKEN = os.getenv('BETA_TOKEN')
elif args.mode == 'deploy':
    TOKEN = os.getenv('DEPLOY_TOKEN')

MONGO_USER = os.getenv('MONGO_USER')
MONGO_SECRET = os.getenv('MONGO_SECRET')
GUILD_ID = os.getenv('GUILD_ID')
#URI_DATABASE = f"mongodb://{MONGO_USER}:{MONGO_SECRET}@bukadb/Bukaneros?authSource=admin" # Docker
URI_DATABASE = f"mongodb://{MONGO_USER}:{MONGO_SECRET}@localhost/Bukaneros?authSource=admin" # Local

####
# BOT SETUP
####
class Client(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.db_client = MongoClient(URI_DATABASE)

bot = Client(command_prefix='+',
             description='Bot de Bukaneros.',
             status=discord.Game(name="Sid Meier's Pirates!"),
             intents=discord.Intents.all())

@bot.event
async def on_ready():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

    print(f' <SYSTEM> Bot is ready.')

####
# COGS SETUP AND AND ADMINISTRATION
####


@bot.command()
@commands.has_role(ADMIN_TAG)
async def sync(ctx):
    try:
        await ctx.message.delete()
        print(f' <SYSTEM> Syncing commands. Wait a moment...')
        tmp_message = await ctx.send(f'`<SYSTEM>` Sync commands, may take a while!')
        synced_commands = await bot.tree.sync()
        await tmp_message.delete()
        print(f' <SYSTEM> Synced {len(synced_commands)} commands globally.')
        await ctx.send(f'`<SYSTEM>` Synced {len(synced_commands)} commands!')

    except Exception as e:
        print(f' <SYSTEM> Error syncing commands: {e}')

@bot.command()
@commands.has_role(ADMIN_TAG)
async def reload(ctx, extension=None):
    try:
        await ctx.message.delete()

        if extension == None:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    await bot.unload_extension(f'cogs.{filename[:-3]}')
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f' <SYSTEM>  {filename[:-3]} module reloaded!')
            await ctx.send(f'`<SYSTEM>` All modules reloaded!')
        else:
            await bot.unload_extension(f'cogs.{extension}')
            await bot.load_extension(f'cogs.{extension}')
            print(f' <SYSTEM>  {extension} module reloaded!')
            await ctx.send(f'`<SYSTEM>` "{extension}" module reloaded!')
    except Exception as e:
        print(f' <SYSTEM> Error reloading modules: {e}') 

@bot.command()
@commands.has_role(ADMIN_TAG)
async def load(ctx, extension):
    try:
        await ctx.message.delete()
        
        await bot.load_extension(f'cogs.{extension}')
        print(f' <SYSTEM>  {extension} module loaded!')
        await ctx.send(f'`<SYSTEM>` "{extension}" module loaded!')
    except Exception as e:
        print(f' <SYSTEM> Error loading modules: {e}') 

@bot.command()
@commands.has_role(ADMIN_TAG)
async def unload(ctx, extension):
    try:
        await ctx.message.delete()

        await bot.unload_extension(f'cogs.{extension}')
        print(f' <SYSTEM>  {extension} module unloaded!')
        await ctx.send(f'`<SYSTEM>` "{extension}" module unloaded!')
    except Exception as E:
        print(f' <SYSTEM> Error unloading modules: {E}') 

        
print(' <SYSTEM> Starting bot...')
bot.run(TOKEN, log_handler=handler)
