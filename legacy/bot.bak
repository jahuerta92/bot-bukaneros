import random
import asyncio
import re
import discord

from discord import Game
from discord.ext.commands import Bot

BOT_PREFIX = ("++")
TOKEN = 'NTQwNTA5MDU3MTc0NDcwNjg2.DzUKUw.Z4kVkYMNdyY0zNRygWaEFqMRUW4' # Get at discordapp.com/developers/applications/me

client = Bot(command_prefix=BOT_PREFIX)

def listPartys(pinned):
	target= "\%.*\%"
	partys= [ message.content for message in pinned if re.search(target, message.content) ]
	partys= [ re.sub("\\\\?\%","",re.search(target, str).group(0)) for str in partys]
	if len(partys) is 0: return "No hay partidas disponibles"
	return "Elige una de las siguientes partidas: " + ''.join("\n -> " + str  for str in partys)

@client.command(name= 'apuntar',
				description="Apunta a un jugador a una partida",
				pass_context=True)
async def apuntar(context, partida:str= None):
	if partida is None:
		await client.say('apuntar "nombre partida"')
		return False
	
	author = context.message.author
	channel = context.message.channel

	pinned = await client.pins_from(channel)
	oldParty = [ message for message in pinned if "\%"+partida+"\%" in message.content ]

	if len(oldParty) is not 1: 
		await client.say("No hay partida de " + partida + "\n" + listPartys(pinned))
		return False

	nick = author.nick if author.nick is not None else author.name

	newParty = await client.say(oldParty[0].content + "\n-" + nick)
	await client.unpin_message(oldParty[0])
	await client.pin_message(newParty)
	return True

@client.command(name= 'quitar',
				description="Quita a un jugador a una partida",
				pass_context=True)
async def quitar(context, partida:str= None):
	if partida is None:
		await client.say('quitar "nombre partida"')
		return False
	
	author = context.message.author
	channel = context.message.channel

	pinned = await client.pins_from(channel)
	oldParty = [ message for message in pinned if "\%" + partida + "\%" in message.content ]
	if len(oldParty) is not 1: 
		await client.say("No hay partida de " + partida + "\n" + listPartys(pinned))
		return False

	nick = author.nick if author.nick is not None else author.name

	messageText = oldParty[0].content
	newParty = await client.say(messageText.replace("\n-" + nick, ""))
	await client.unpin_message(oldParty[0])
	await client.pin_message(newParty)
	return True

@client.command(name= 'crear',
				description="Crea una partida para dirigir",
				pass_context=True)
async def crear(context, partida:str= None):
	if partida is None:
		await client.say('crear "nombre partida"')
		return False
	
	author = context.message.author
	channel = context.message.channel

	pinned = await client.pins_from(channel)
	oldParty = [ message for message in pinned if "\%"+partida+"\%" in message.content ]
	if len(oldParty) >= 1: 
		await client.say("Ya existe la partida " + partida + "\n" + listPartys(pinned))
		return False

	nick = author.nick if author.nick is not None else author.name

	newParty = await client.say("\%"+partida+"\%"+" Dirige: "+ nick)
	await client.pin_message(newParty)
	return True

@client.command(name= 'anular',
				description="Anula una partida que diriges",
				pass_context=True)
async def crear(context, partida:str= None):
	if partida is None:
		await client.say('anular "nombre partida"')
		return False

	author = context.message.author
	channel = context.message.channel

	pinned = await client.pins_from(channel)
	oldParty = [ message for message in pinned if "\%"+partida+"\%" in message.content ]
	if len(oldParty) is not 1: 
		await client.say("No existe la partida " + partida + "\n" + listPartys(pinned))
		return False

	nick = author.nick if author.nick is not None else author.name
	
	message = oldParty[0]
	if "Dirige: "+ nick not in message.content:
		await client.say("No puedes anular una partida que no diriges")
		return False
	
	await client.say("Anulada partida " + partida)
	await client.unpin_message(message)
	return True
	
client.remove_command('help')
@client.command(name= 'help',
				aliases= ['ayuda','?'],
				description="Anula una partida que diriges",
				pass_context=True)
async def help(context):
	embed = discord.Embed(title="Botkanero", description="Arrr, Grumete. Organiza tus partidas con estos comandos.", color=0xeee657)

	embed.add_field(name='++apuntar "nombre de partida"', value="Te apunta en la partida que indicas si existe.", inline=False)
	embed.add_field(name='++quitar "nombre de partida"', value="Te retira de la partida que indicas si existe.", inline=False)
	embed.add_field(name='++crear "nombre de partida"', value="Crea una partida y te apunta como director.\nUsa este comando solo si vas a dirigir.", inline=False)
	embed.add_field(name='++anular "nombre de partida"', value="Anula una partida que tu dirijas.", inline=False)
	embed.add_field(name='++ayuda', value="Es lo que estas leyendo, grumete", inline=False)

	await client.send_message(context.message.channel, embed=embed)

async def list_servers():
	await client.wait_until_ready()
	while not client.is_closed:
		print("Current servers:")
		for server in client.servers:
			print(server.name)
		await asyncio.sleep(600)

client.loop.create_task(list_servers())
client.run(TOKEN)