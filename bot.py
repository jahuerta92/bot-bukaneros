import asyncio
import discord
import unidecode

from src.evento import ARGUMENT_TYPES, LEGAL_DAYS_SET, Evento, Dia

from discord.ext.commands import Bot
from datetime import date


BOT_PREFIX = "+"
TOKEN = 'NTQwNTA5MDU3MTc0NDcwNjg2.Xkf4_g.fOur5nnRHLhBGUnTh1nfqSgmFGw'  # Get at discordapp.com/developers/applications/me
TAG = '[EventoBukanero]'
bot = Bot(command_prefix=BOT_PREFIX,
          description='Organiza las partidas de rol. Si no conoces los comandos usa ++ayuda')

def simple_cmp(a,b):
    a_sub = unidecode.unidecode(a).lower()
    b_sub = unidecode.unidecode(b).lower()
    return a_sub == b_sub

def parse(*args, optional_fields, required_fields):
    opt_fields = [('-' + ARGUMENT_TYPES[k].alias, '--' + ARGUMENT_TYPES[k].name) for k in optional_fields]
    req_fields = [('-' + ARGUMENT_TYPES[k].alias, '--' + ARGUMENT_TYPES[k].name) for k in required_fields]

    all_fields = opt_fields + req_fields

    alias_prefix, name_prefix = '-', '--'
    arg_names = [item for item in args if alias_prefix == item[0]]

    for field in all_fields:
        alias, name = field
        if alias not in arg_names and name not in arg_names:
            if field in req_fields:
                return False, '*Error*: El argumento *{}* es requerido, pero falta en el comando.'.format(name)

    for item in arg_names:
        if item not in [item for field in all_fields for item in field]:
            return False, '*Error*: El argumento *{}* no esta permitido para este comando.'.format(item)

    parsed_dict = dict()

    for key, item in ARGUMENT_TYPES.items():
        arg_alias = alias_prefix + item.alias
        arg_name = name_prefix + item.name
        value = None

        if arg_alias in args and arg_name in args:
            return False, '*Error*: Argumentos *{}* y *{}* están repetidos.'.format(arg_alias, arg_name)
        elif arg_alias in args:
            if args.count(arg_alias) > 1:
                return False, '*Error*: Argumento *{}* aparece por duplicado.'.format(arg_alias)
            idx = args.index(arg_alias)
        elif arg_name in args:
            if args.count(arg_name) > 1:
                return False, '*Error*: Argumento *{}* aparece por duplicado.'.format(arg_name)
            idx = args.index(arg_name)

        if arg_alias in args or arg_name in args:
            if idx >= len(args) - 1:
                return False, '*Error*: Falta un valor para el argumento {}'.format(args[idx])
            elif args[idx + 1][0] == alias_prefix:
                return False, '*Error*: Falta un valor para el argumento {}'.format(args[idx])

            value_list = []
            idx += 1

            while idx < len(args) and args[idx][0] != alias_prefix:
                value_list.append(args[idx])
                idx += 1

            value = ' '.join(value_list)

        parsed_dict[key] = value

    return True, parsed_dict

@bot.command(name='apuntar',
             description="Apunta a un jugador a una partida",
             aliases=['añadir', 'apuntame', 'añademe'],
             pass_context=True)
async def apuntar(ctx, idnt=None, *args):
    optional_fields = {'Jugadores'}
    required_fields = set()
    check, value = parse(*args, optional_fields=optional_fields, required_fields=required_fields)

    if not check:
        await ctx.send(value)
        return False

    if idnt is None:
        await ctx.send('*Error*: Falta identificador de la partida, el primer argumento.')
        return

    author = ctx.message.author

    if len(args) < 1:
        value['Jugadores'] = author.nick if author.nick is not None else author.name

    pinned = await ctx.pins()

    try:
        old_events = [Evento(message) for message in pinned if TAG in message.content]
    except:
        await ctx.send(
            "*Error*: Ha ocurrido un error al intentar recuperar los eventos."
            "Por favor revisa que los mensajes anclados tengan el formato correcto."
            "Si usas *+plantilla* te mandaré un ejemplo de como tienen que estar escritos los eventos.")
        return False

    this_events = [event for event in old_events if simple_cmp(event.event_dict['Id'], idnt)]
    if len(this_events) < 1:
        await ctx.send("*Error*: No existe la partida *{}* \n".format(idnt))
        return False
    elif len(this_events) > 1:
        await ctx.send("*Error*: Hay múltiples partidas de *{}*, por favor revisa los mensajes anclados. \n".format(idnt))
        return False

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

    if not check:
        await ctx.send(value)
        return False

    if idnt is None:
        await ctx.send('*Error*: Falta identificador de la partida, el primer argumento.')
        return False

    author = ctx.message.author

    if len(args) < 1:
        value['Jugadores'] = author.nick if author.nick is not None else author.name
    
    pinned = await ctx.pins()

    try:
        old_events = [Evento(message) for message in pinned if TAG in message.content]
    except:
        await ctx.send(
            "*Error*: Ha ocurrido un error al intentar recuperar los eventos.\n"
            "Por favor revisa que los mensajes anclados tengan el formato correcto.\n"
            "Si usas *+plantilla* te mandaré un ejemplo de como tienen que estar escritos los eventos.")
        return False

    this_events = [event for event in old_events if simple_cmp(event.event_dict['Id'], idnt)]
    if len(this_events) < 1:
        await ctx.send("*Error*: No existe la partida *{}* \n".format(idnt))
        return False
    elif len(this_events) > 1:
        await ctx.send("*Error*: Hay múltiples partidas de *{}*, por favor revisa los mensajes anclados. \n".format(idnt))
        return False

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

    if not check:
        await ctx.send(value)
        return False

    if idnt is None:
        await ctx.send('*Error*: Falta identificador de la partida, el primer argumento.')
        return False

    value['Id'] = idnt

    channel = ctx.message.channel

    if value['Dia'] is None:
        tmp = channel.name.split('-')
        if len(tmp) < 2:
            ctx.send(
                '*Error*: El dia no se puede establecer automaticamente en este canal. '
                'Prueba a especificarlo con -d o --dia.')
            return False
        elif tmp[1] not in LEGAL_DAYS_SET:
            ctx.send(
                '*Error*: El dia no se puede establecer automaticamente en este canal. '
                'Prueba a especificarlo con -d o --dia.')
            return False
        value['Dia'] = Dia(tmp[1])

    author = ctx.message.author

    value['Director'] = author.nick if author.nick is not None else author.name

    new_event = Evento(**value)

    pinned = await ctx.pins()

    try:
        old_events = [Evento(message) for message in pinned if TAG in message.content]
    except:
        await ctx.send(
            "*Error*: Ha ocurrido un error al intentar recuperar los eventos.\n"
            "Por favor revisa que los mensajes anclados tengan el formato correcto.\n"
            "Si usas *+plantilla* te mandaré un ejemplo de como tienen que estar escritos los eventos.")
        return False

    if new_event in old_events:
        await ctx.send("*Error*: Ya existe la partida *{}*".format(new_event.event_dict['Id']))
        return False

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

    if not check:
        await ctx.send(value)
        return False

    if idnt is None:
        await ctx.send('*Error*: Falta identificador de la partida, el primer argumento.')
        return

    author = ctx.message.author

    pinned = await ctx.pins()

    try:
        old_events = [Evento(message) for message in pinned if TAG in message.content]
    except:
        await ctx.send("*Error*: Ha ocurrido un error al intentar recuperar los eventos.\n"
                       "Por favor revisa que los mensajes anclados tengan el formato correcto.\n"
                       "Si usas *+plantilla* te mandaré un ejemplo de como tienen que estar escritos los eventos.")
        return False

    this_events = [event for event in old_events if simple_cmp(event.event_dict['Id'], idnt)]

    if len(this_events) < 1:
        await ctx.send("*Error*: No existe la partida *{}* \n".format(idnt))
        return False
    elif len(this_events) > 1:
        await ctx.send("*Error*: Hay múltiples partidas de *{}*, por favor revisa los mensajes anclados. \n".format(idnt))
        return False

    nick = author.nick if author.nick is not None else author.name

    this_event = this_events[0]
    if nick != this_event.event_dict['Director']:
        await ctx.send("*Error*: No puedes anular una partida que no diriges")
        return False

    await ctx.send("Anulada partida " + idnt)
    await this_event.unpin()
    return True

bot.remove_command('help')

@bot.command(name='help',
             aliases=['ayuda', '?', 'ayudame'],
             pass_ctx=True)
async def help(ctx):
    embed = discord.Embed(title="Botkanero", description='''
Bienvenido al organizador de partidas de Bukaneros. Soy el panel de ayuda de este bot. Las indicaciones entre corchetes son opcionales, se rellenan automaticamente siempre que pueden.''',
                          color=0xeee657)

    embed.add_field(name='+apuntar id [-j jugador][--jugador jugador]',
                    value="Para apuntarte a la partida con ID, puedes apuntar a otra persona si incluyes -j o --jugador. \n"
                          "Ejemplos: (+apuntar D&D -j Alberto) o (+apuntar D&D)",
                    inline=False)
    embed.add_field(name='+quitar id [-j jugador][--jugador jugador]',
                    value="Para salirte de la partida con ID, puedes apuntar a otra persona si incluyes -j o --jugador. \n"
                          "Ejemplos: (+quitar D&D -j Alberto) o (+quitar D&D)",
                    inline=False)
    embed.add_field(name='+crear id --nombre nombre de la partida [-d dd/mm][--dia dd/mm] [-i hh:mm][--inicio hh:mm]'
                         '[-f hh:mm][--fin hh:mm] [-m maximo][--maximo maximo] [-N notas][--notas notas] [-t tipo][--tipo tipo]',
                    value="Crea una partida con una id y un nombre. Si tu partida está fuera de los canales diarios indica el dia con -d. \n"
                          "¡El resto de argumentos son opcionales! \n"
                          'Ejemplos: (+crear D&D --nombre La maldicion -d Jueves) o (+crear D&D -n La maldicion -d Jueves -N ¡Venid antes de las 6 para hacer fichas!)',
                    inline=False)
    embed.add_field(name='+anular id',
                    value="Anula una partida que tu dirijas."
                          "Ejemplo: [+anular D&D]"
                    , inline=False)
    embed.add_field(name='+listar',
                    value="Lista todas las partidas disponibles del servidor",
                    inline=False)
    embed.add_field(name='+ayuda',
                    value="Es lo que estas leyendo, grumete",
                    inline=False)

    await ctx.message.author.send(embed=embed)


@bot.command(name='plantilla',
             aliases=['ejemplo'],
             pass_ctx=True)
async def plantilla(ctx):
    await ctx.message.author.send('Este es un ejemplo del formato de la partida. Copia y pega el contenido del mensaje para'
                                  'que sea compatible con el bot.\n\n'
                                  '[EventoBukanero] Partida de rol. Id: D&D · Nombre: La Maldición de Strahd ·'
                                  ' Dia: Miércoles 12/02/2020 · Inicio: 15:30 · Fin: 19:30 · Director: Javi ·'
                                  ' Maximo: 5 · Notas: Hola caracola \n'
                                  '[Jugadores]\n'
                                  '- Abel\n'
                                  '- Bea\n'
                                  '- Carlos\n'
                                  '-')


@bot.command(name='listar',
             description="Devuelve un listado de partidas en todo el servidor",
                pass_context=True)
async def listar(ctx):
    try:
        event_list = [Evento(message) for channel in ctx.guild.text_channels
                      for message in await channel.pins()
                      if TAG in message.content]
    except:
        await ctx.send("*Error*: Ha ocurrido un error al intentar recuperar los eventos."
                       "Por favor revisa que los mensajes anclados tengan el formato correcto."
                       "Si usas *+plantilla* te mandaré un ejemplo de como tienen que estar escritos los eventos.")
        return False

    if len(event_list) < 1:
        ctx.send('No hay partidas')
        return False

    event_list.sort(key=lambda x: x.event_dict['Dia'].date)

    embed = discord.Embed(title="Tablero de partidas",
                          color=0xeee657)

    for idx, item in enumerate(event_list):
        idg, date, players = item.summary()
        embed.add_field(name=date, value='{} --> {}'.format(idg, players), inline=False)

    await ctx.message.author.send(embed=embed)
    return True

async def list_servers():
    await bot.wait_until_ready()
    while not bot.is_closed:
        print("Current servers:")
        for server in bot.servers:
            print(server.name)
        await asyncio.sleep(600)


@bot.listen()
async def on_message(message):
    day = date.today()
    for msg in await message.channel.pins():
        if TAG in msg.content and Evento(msg).event_dict['Dia'].date < day:
            await msg.unpin()

    return True

bot.loop.create_task(list_servers())
bot.run(TOKEN)
