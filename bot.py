import asyncio
import discord
import unidecode
import yaml

import pandas as pd

from dotenv import dotenv_values

from src.evento import LEGAL_DAYS_SET, Evento, Dia
from src.utils import parse, simple_cmp

from discord.ext.commands import Bot
from datetime import date

config = dotenv_values(".env")

BOT_PREFIX = "+"
TAG = '[EventoBukanero]'
TOKEN = config['BETA_TOKEN']

bot = Bot(command_prefix=BOT_PREFIX,
          description='Organiza las partidas de rol. Si no conoces los comandos usa ++ayuda',
          intents=discord.Intents.all())


async def check_error(cond, message):
    if cond:
        await message.channel.send(message)
        return False
    return True

@bot.command(name='mover',
            description='Mueve a un jugador de una partida a otra',
            pass_context=True)
async def mover(ctx, idnt1, idnt2, *args):
    optional_fields = {'Jugadores'}
    required_fields = set()
    check, value = parse(*args, optional_fields=optional_fields, required_fields=required_fields)

    assert await check_error(not check, value)
    assert await check_error(idnt1 is None, 'Falta identificador de la primera partida, el primer argumento.')
    assert await check_error(idnt2 is None, 'Falta identificador de la segunda partida, el segundo argumento.')

    author = ctx.message.author

    if len(args) < 1:
        value['Jugadores'] = author.nick if author.nick is not None else author.name

    pinned = await ctx.pins()

    old_events = []
    for message in pinned:
        if TAG in message.content:
            try:
                old_events.append(Evento(message))
            except:
                print("The following message produced an error:\n\n" + message.content)
                await ctx.send("**Error**: Ha ocurrido un error al intentar recuperar los eventos.\n " 
                               "Por favor revisa que los mensajes anclados tengan el formato correcto.\n "
                               "Si usas **+plantilla** te mandaré un ejemplo de como tienen que estar escritos los eventos.")
                return False

    this_events_1 = [event for event in old_events if simple_cmp(event.event_dict['Id'], idnt1)]
    this_events_2 = [event for event in old_events if simple_cmp(event.event_dict['Id'], idnt2)]

    assert await check_error(len(this_events_1) < 1, f'No existe la partida **{idnt1}**')
    assert await check_error(len(this_events_1) > 1, f'Hay múltiples partidas de **{idnt1}**, por favor revisa los mensajes anclados.')
    assert await check_error(len(this_events_2) < 1, f'No existe la partida **{idnt2}**')
    assert await check_error(len(this_events_2) > 1, f'Hay múltiples partidas de **{idnt2}**, por favor revisa los mensajes anclados.')

    this_event_1 = this_events_1[0]
    this_event_2 = this_events_2[0]

    check, fail = this_event_1.remove_player(value['Jugadores'])
    assert await check_error(not check, fail.format(value['Jugadores'], idnt1))
    
    check, fail = this_event_2.new_player(value['Jugadores'])
    assert await check_error(not check, fail.format(value['Jugadores'], idnt2))

    new_message_1 = await ctx.send(str(this_event_1))
    new_message_2 = await ctx.send(str(this_event_2))

    await this_event_1.unpin()
    await this_event_2.unpin()
    await new_message_1.pin()
    await new_message_2.pin()

    return True


@bot.command(name='apuntar',
             description="Apunta a un jugador a una partida",
             aliases=['añadir', 'apuntame', 'añademe'],
             pass_context=True)
async def apuntar(ctx, idnt=None, *args):
    optional_fields = {'Jugadores'}
    required_fields = set()
    check, value = parse(*args, optional_fields=optional_fields, required_fields=required_fields)

    assert await check_error(not check, value)
    assert await check_error(idnt is None, 'Falta identificador de la partida, el primer argumento.')

    author = ctx.message.author

    if len(args) < 1:
        value['Jugadores'] = author.nick if author.nick is not None else author.name

    pinned = await ctx.pins()

    old_events = []
    for message in pinned:
        if TAG in message.content:
            try:
                old_events.append(Evento(message))
            except:
                print("The following message produced an error:\n\n" + message.content)
                await ctx.send("**Error**: Ha ocurrido un error al intentar recuperar los eventos.\n " 
                               "Por favor revisa que los mensajes anclados tengan el formato correcto.\n "
                               "Si usas **+plantilla** te mandaré un ejemplo de como tienen que estar escritos los eventos.")
                return False

    this_events = [event for event in old_events if simple_cmp(event.event_dict['Id'], idnt)]
    
    assert await check_error(len(this_events) < 1, f'No existe la partida **{idnt}**')
    assert await check_error(len(this_events) > 1, f'Hay múltiples partidas de **{idnt}**, por favor revisa los mensajes anclados.')

    this_event = this_events[0]
    check, fail = this_event.new_player(value['Jugadores'])
    if not check:
        await ctx.send(fail.format(value['Jugadores'], idnt))
        return False

    new_message = await ctx.send(str(this_events[0]))
    await this_event.unpin()
    await new_message.pin()
    return True


@bot.command(name='quitar',
             description="Quita a un jugador a una partida",
             aliases=['borrar', 'quitame', 'borrame'],
             pass_context=True)
async def quitar(ctx, idnt=None, *args):
    optional_fields = {'Jugadores'}
    required_fields = set()
    check, value = parse(*args, optional_fields=optional_fields, required_fields=required_fields)

    assert await check_error(not check, value)
    assert await check_error(idnt is None, 'Falta identificador de la partida, el primer argumento.')

    author = ctx.message.author

    if len(args) < 1:
        value['Jugadores'] = author.nick if author.nick is not None else author.name

    pinned = await ctx.pins()
    old_events = []
    for message in pinned:
        if TAG in message.content:
            try:
                old_events.append(Evento(message))
            except:
                print("The following message produced an error:\n\n" + message.content)
                await ctx.send("**Error**: Ha ocurrido un error al intentar recuperar los eventos.\n " 
                               "Por favor revisa que los mensajes anclados tengan el formato correcto.\n "
                               "Si usas **+plantilla** te mandaré un ejemplo de como tienen que estar escritos los eventos.")
                return False

    this_events = [event for event in old_events if simple_cmp(event.event_dict['Id'], idnt)]
    
    assert await check_error(len(this_events) < 1, f'No existe la partida **{idnt}**')
    assert await check_error(len(this_events) > 1, f'Hay múltiples partidas de **{idnt}**, por favor revisa los mensajes anclados.')

    this_event = this_events[0]
    check, fail = this_event.remove_player(value['Jugadores'])
    if not check:
        await ctx.send(fail.format(value['Jugadores'], idnt))
        return False

    new_message = await ctx.send(str(this_events[0]))
    await this_event.unpin()
    await new_message.pin()
    return True


@bot.command(name='crear',
             description="Crea una partida para dirigir",
             pass_context=True)
async def crear(ctx, idnt=None, *args):
    optional_fields = {'EventoBukanero', 'Inicio', 'Fin', 'Maximo', 'Dia', 'Notas'}
    required_fields = {'Nombre'}
    check, value = parse(*args, optional_fields=optional_fields, required_fields=required_fields)

    assert await check_error(not check, value)
    assert await check_error(idnt is None, 'Falta identificador de la partida, el primer argumento.')

    value['Id'] = idnt

    channel = ctx.message.channel

    if value['Dia'] is None:
        tmp = channel.name.split('-')
        
        assert await check_error(len(tmp) < 2, '**Error**: El dia no se puede establecer automaticamente en este canal.')
        assert await check_error(tmp[1] not in LEGAL_DAYS_SET, '**Error**: El dia no se puede establecer automaticamente en este canal.')
                  
        value['Dia'] = Dia(tmp[1])

    author = ctx.message.author

    value['Director'] = author.nick if author.nick is not None else author.name

    new_event = Evento(**value)

    pinned = await ctx.pins()

    old_events = []
    for message in pinned:
        if TAG in message.content:
            try:
                old_events.append(Evento(message))
            except:
                print("The following message produced an error:\n\n" + message.content)
                await ctx.send("**Error**: Ha ocurrido un error al intentar recuperar los eventos.\n " 
                               "Por favor revisa que los mensajes anclados tengan el formato correcto.\n "
                               "Si usas **+plantilla** te mandaré un ejemplo de como tienen que estar escritos los eventos.")
                return False

    evid = new_event.event_dict["Id"]
    assert await check_error(new_event in old_events, f'Ya existe la partida **{evid}**')

    new_message = await ctx.send(new_event)
    await new_message.pin()
    return True


@bot.command(name='anular',
             description="Anula una partida que diriges",
             pass_ctx=True)
async def anular(ctx, idnt=None, *args):
    optional_fields = set()
    required_fields = set()
    check, value = parse(*args, optional_fields=optional_fields, required_fields=required_fields)

    assert await check_error(not check, value)
    assert await check_error(idnt is None, 'Falta identificador de la partida, el primer argumento.')
    
    author = ctx.message.author

    pinned = await ctx.pins()

    old_events = []
    for message in pinned:
        if TAG in message.content:
            try:
                old_events.append(Evento(message))
            except:
                print("The following message produced an error:\n\n" + message.content)
                await ctx.send("**Error**: Ha ocurrido un error al intentar recuperar los eventos.\n " 
                               "Por favor revisa que los mensajes anclados tengan el formato correcto.\n "
                               "Si usas **+plantilla** te mandaré un ejemplo de como tienen que estar escritos los eventos.")
                return False

    this_events = [event for event in old_events if simple_cmp(event.event_dict['Id'], idnt)]

    assert await check_error(len(this_events) < 1, f'No existe la partida **{idnt}**')
    assert await check_error(len(this_events) > 1, f'Hay múltiples partidas de **{idnt}**, por favor revisa los mensajes anclados.')
    
    nick = author.nick if author.nick is not None else author.name

    this_event = this_events[0]
    
    assert await check_error(nick != this_event.event_dict['Director'], 'No puedes anular una partida que no diriges')

    await ctx.send("Anulada partida " + idnt)
    await this_event.unpin()
    return True


@bot.command(name='modificar',
             description="Modifica una partida que diriges",
             pass_ctx=True)
async def modificar(ctx, idnt=None, *args):
    optional_fields = {'EventoBukanero', 'Inicio', 'Fin', 'Maximo', 'Dia', 'Notas', 'Nombre', 'Id'}
    required_fields = set()
    check, value = parse(*args, optional_fields=optional_fields, required_fields=required_fields)

    assert await check_error(not check, value)
    assert await check_error(idnt is None, 'Falta identificador de la partida, el primer argumento.')
    assert await check_error(len(args) < 1, 'No se ha indicado nada que modificar.')

    author = ctx.message.author

    pinned = await ctx.pins()

    old_events = []
    for message in pinned:
        if TAG in message.content:
            try:
                old_events.append(Evento(message))
            except:
                print("The following message produced an error:\n\n" + message.content)
                await ctx.send("**Error**: Ha ocurrido un error al intentar recuperar los eventos.\n " 
                               "Por favor revisa que los mensajes anclados tengan el formato correcto.\n "
                               "Si usas **+plantilla** te mandaré un ejemplo de como tienen que estar escritos los eventos.")
                return False

    this_events = [event for event in old_events if simple_cmp(event.event_dict['Id'], idnt)]

    assert await check_error(len(this_events) < 1, f'No existe la partida **{idnt}**')
    assert await check_error(len(this_events) > 1, f'Hay múltiples partidas de **{idnt}**, por favor revisa los mensajes anclados.')

    nick = author.nick if author.nick is not None else author.name

    this_event = this_events[0]
    
    assert await check_error(nick != this_event.event_dict['Director'], 'No puedes modificar una partida que no diriges')

    await this_event.unpin()

    for key, val in value.items():
        if val is not None:
            this_event.update(key, val)

    new_message = await ctx.send(this_event)
    await new_message.pin()

    return True

bot.remove_command('help')

@bot.command(name='help',
             aliases=['ayuda', '?', 'ayudame'],
             pass_ctx=True)
async def help(ctx):
    with open('strings.yaml', 'r') as stream:
        help_dict = yaml.safe_load(stream)
        
    embed = discord.Embed(title="Botkanero", description= help_dict['intro'],
                          color=0xeee657)
    embed.add_field(name='Primeros pasos',
                    value=help_dict['primeros_pasos'],
                    inline=False)
    embed.add_field(name=help_dict['apuntar']['cmd'],
                    value=help_dict['apuntar']['txt'],
                    inline=False)
    embed.add_field(name=help_dict['quitar']['cmd'],
                    value=help_dict['quitar']['txt'],
                    inline=False)
    embed.add_field(name=help_dict['crear']['cmd'],
                    value=help_dict['crear']['txt'],
                    inline=False)
    embed.add_field(name=help_dict['modificar']['cmd'],
                    value=help_dict['modificar']['txt'],
                    inline=False)
    embed.add_field(name=help_dict['mover']['cmd'],
                    value=help_dict['mover']['txt'],
                    inline=False)
    embed.add_field(name=help_dict['anular']['cmd'],
                    value=help_dict['anular']['txt'],
                    inline=False)
    embed.add_field(name=help_dict['listar']['cmd'],
                    value=help_dict['listar']['txt'],
                    inline=False)
    embed.add_field(name=help_dict['ejemplo']['cmd'],
                    value=help_dict['ejemplo']['txt'],
                    inline=False)
    embed.add_field(name=help_dict['ayuda']['cmd'],
                    value=help_dict['ayuda']['txt'],
                    inline=False)

    await ctx.message.author.send(embed=embed)


@bot.command(name='plantilla',
             aliases=['ejemplo'],
             pass_ctx=True)
async def plantilla(ctx):
    await ctx.message.author.send(
        'Este es un ejemplo del formato de la partida. Copia y pega el contenido del mensaje para'
        'que sea compatible con el bot.\n\n'
        '```[EventoBukanero] Partida de rol. Id: D&D · Nombre: La Maldición de Strahd ·'
        ' Dia: Miércoles 12/02/2020 · Inicio: 15:30 · Fin: 19:30 · Director: Javi ·'
        ' Maximo: 5 · Notas: Hola caracola \n'
        '[Jugadores]\n'
        '- Abel\n'
        '- Bea\n'
        '- Carlos\n'
        '-```')

@bot.command(name='listar',
             description="Devuelve un listado de partidas en todo el servidor",
             pass_context=True)
async def listar(ctx):
    event_list = []
    
    
    to_check = []
    # Retrieve all channels and threads, exhaustive search
    for channel in ctx.guild.channels:
        if channel.type == discord.ChannelType.text:
            to_check.append(channel)
            for thread in channel.threads:
                to_check.append(thread)
        elif channel.type == discord.ChannelType.forum:
            for thread in channel.threads:
                to_check.append(thread)
    
    
    # Retrieve all pinned messages in the channels
    for channel in to_check:
        pins = await channel.pins()
        for message in pins:           
            if TAG in message.content:
                try:
                    event_list.append(Evento(message))
                except:
                    print("The following message produced an error:\n\n" + message.content)
                    await ctx.send("**Error**: Ha ocurrido un error al intentar recuperar los eventos.\n " 
                                   "Por favor revisa que los mensajes anclados tengan el formato correcto.\n "
                                   "Si usas **+plantilla** te mandaré un ejemplo de como tienen que estar escritos los eventos.")
                    return False

    assert await check_error(len(event_list) < 1, 'No hay partidas')

    event_list.sort(key=lambda x: x.event_dict['Dia'].date)
    games = pd.DataFrame([event.event_dict for event in event_list]).set_index('Dia')
    games['Jugadores'] = games['Jugadores'].apply(lambda x: len(x))
    games['Jugadores'] = games[['Jugadores', 'Maximo']].apply(lambda x: f'{x[0]}/{x[1]}', axis=1)
    games.drop(columns=['EventoBukanero', 'Id', 'Maximo'], inplace=True)
    
    message = f'''# Tablero de partidas
```
{games.to_markdown()}
```
'''    

    await ctx.message.author.send(message)
    return True

@bot.listen()
async def on_message(message):
    await asyncio.sleep(60)
    
    day = date.today()
    for msg in await message.channel.pins():
        if TAG in msg.content and Evento(msg).event_dict['Dia'].date < day:
            await msg.unpin()
    
    return True

@bot.event
async def on_error(event, *args, **kwargs):
    if isinstance(args[0], discord.HTTPException) and args[0].status == 429:
        retry_after = args[0].headers.get("Retry-After")
        if retry_after:
            await asyncio.sleep(int(retry_after) + 1) 
        else:
            await asyncio.sleep(5)  
    else:
        print(f"An error occurred: {args[0]}")


bot.run(TOKEN)
