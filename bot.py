import asyncio
import discord
from src.evento import ARGUMENT_TYPES, LEGAL_DAYS_SET, Evento, Dia

from discord.ext.commands import Bot
from datetime import date

BOT_PREFIX = "++"
TOKEN = 'NTQwNTA5MDU3MTc0NDcwNjg2.Xkf4_g.fOur5nnRHLhBGUnTh1nfqSgmFGw'  # Get at discordapp.com/developers/applications/me
TAG = '[EventoBukanero]'
bot = Bot(command_prefix=BOT_PREFIX,
          description='Organiza las partidas de rol. Si no conoces los comandos usa ++ayuda')


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
                return False, 'Error: Argumento {} requerido faltante'.format(alias)

    for item in arg_names:
        if item not in [item for field in all_fields for item in field]:
            return False, 'Error: Argumento {} no legal'.format(item)

    parsed_dict = dict()

    for key, item in ARGUMENT_TYPES.items():
        arg_alias = alias_prefix + item.alias
        arg_name = name_prefix + item.name
        value = None

        if arg_alias in args and arg_name in args:
            return False, 'Error: Argumentos {} y {} son identicos'.format(arg_alias, arg_name)
        elif arg_alias in args:
            if args.count(arg_alias) > 1:
                return False, 'Error: Argumento {} duplicado'.format(arg_alias)
            idx = args.index(arg_alias)
        elif arg_name in args:
            if args.count(arg_name) > 1:
                return False, 'Error: Argumento {} duplicado'.format(arg_name)
            idx = args.index(arg_name)

        if arg_alias in args or arg_name in args:
            if idx >= len(args) - 1:
                return False, 'Error: Falta un valor para {}'.format(args[idx])
            elif args[idx + 1][0] == alias_prefix:
                return False, 'Error: Falta un valor para {}'.format(args[idx])

            value_list = []
            idx += 1

            while idx < len(args) and args[idx][0] != alias_prefix:
                value_list.append(args[idx])
                idx += 1

            value = ' '.join(value_list)

        parsed_dict[key] = value

    return True, parsed_dict

@bot.command(name='listar',
             description="Devuelve un listado de partidas en todo el servidor",
             pass_context=True)
async def listar(ctx):
    event_list = [Evento(message.content) for channel in ctx.guild.text_channels
                  for message in await channel.pins()
                  if TAG in message.content]

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

@bot.command(name='apuntar',
             description="Apunta a un jugador a una partida",
             pass_context=True)
async def apuntar(ctx, idnt=None, *args):
    optional_fields = {'Jugadores'}
    required_fields = set()
    check, value = parse(*args, optional_fields=optional_fields, required_fields=required_fields)

    if not check:
        await ctx.send(value)
        return False

    if idnt is None:
        await ctx.send('Falta identificador de la partida, el primer argumento.')
        return

    author = ctx.message.author
    channel = ctx.message.channel

    if len(args) < 1:
        value['Jugadores'] = author.nick if author.nick is not None else author.name

    pinned = await ctx.pins()
    old_event = [message for message in pinned if
                 TAG in message.content and Evento(message.content).event_dict['Id'] == idnt]
    if len(old_event) != 1:
        await ctx.send("No hay partida de {}\n".format(idnt))
        return False

    old_event_object = Evento(old_event[0].content)
    check = old_event_object.new_player(value['Jugadores'])
    if not check:
        await ctx.send("El jugador {} ya esta apuntado a la partida {} \n".format(value['Jugadores'], idnt))
        return False

    new_message = await ctx.send(str(old_event_object))
    await old_event[0].unpin()
    await new_message.pin()
    return True


@bot.command(name='quitar',
             description="Quita a un jugador a una partida",
             pass_context=True)
async def quitar(ctx, idnt=None, *args):
    optional_fields = {'Jugadores'}
    required_fields = set()
    check, value = parse(*args, optional_fields=optional_fields, required_fields=required_fields)

    if not check:
        await ctx.send(value)
        return False

    if idnt is None:
        await ctx.send('Falta identificador de la partida. Usa --id ID o -a ID.')
        return False

    author = ctx.message.author

    if len(args) < 1:
        value['Jugadores'] = author.nick if author.nick is not None else author.name
    
    pinned = await ctx.pins()
    old_event = [message for message in pinned if TAG in message.content and Evento(message.content).event_dict['Id'] == idnt]
    if len(old_event) != 1:
        await ctx.send("El jugador {} no esta apuntado a la partida {} \n".format(value['Jugadores'], idnt))
        return False

    old_event_object = Evento(old_event[0].content)
    check = old_event_object.remove_player(value['Jugadores'])
    if not check:
        await ctx.send("No estas apuntado a la partida de {}".format(idnt))
        return False

    new_message = await ctx.send(str(old_event_object))
    await old_event[0].unpin()
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
        await ctx.send('Falta identificador de la partida. Usa --id ID o -a ID.')
        return False

    value['Id'] = idnt

    channel = ctx.message.channel

    if value['Dia'] is None:
        tmp = channel.name.split('-')
        if len(tmp) < 2:
            ctx.send(
                'El dia no se puede establecer automaticamente en este canal. Prueba a especificarlo con -d o --dia.')
            return False
        elif tmp[1] not in LEGAL_DAYS_SET:
            ctx.send(
                'El dia no se puede establecer automaticamente en este canal. Prueba a especificarlo con -d o --dia.')
            return False
        value['Dia'] = Dia(tmp[1])

    author = ctx.message.author

    value['Director'] = author.nick if author.nick is not None else author.name

    new_event = Evento(**value)

    pinned = await ctx.pins()
    old_events = [Evento(message.content) for message in pinned if TAG in message.content]

    if new_event in old_events:
        await ctx.send("Ya existe la partida " + new_event.event_dict['Id'] + "\n")
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
        await ctx.send('Falta identificador de la partida. Usa --id ID o -a ID.')
        return

    author = ctx.message.author
    channel = ctx.message.channel

    pinned = await ctx.pins()
    old_message = [message for message in pinned
                   if TAG in message.content and Evento(message.content).event_dict['Id'] == idnt]

    if len(old_message) != 1:
        await ctx.send("No existe la partida " + idnt + "\n")
        return False

    nick = author.nick if author.nick is not None else author.name

    message = old_message[0]
    if nick != Evento(message.content).event_dict['Director']:
        await ctx.send("No puedes anular una partida que no diriges")
        return False

    await ctx.send("Anulada partida " + idnt)
    await message.unpin()
    return True

bot.remove_command('help')

@bot.command(name='help',
             aliases=['ayuda', '?'],
             pass_ctx=True)
async def help(ctx):
    embed = discord.Embed(title="Botkanero", description='''
Bienvenido al organizador de partidas de Bukaneros. Soy el panel de ayuda de este bot. Las indicaciones entre corchetes son opcionales, se rellenan automaticamente siempre que pueden.''',
                          color=0xeee657)

    embed.add_field(name='++apuntar id [-j jugador][--jugador jugador]',
                    value="Para apuntarte a la partida con ID, puedes apuntar a otra persona si incluyes -j o --jugador",
                    inline=False)
    embed.add_field(name='++quitar id [-j jugador][--jugador jugador]',
                    value="Para salirte de la partida con ID, puedes apuntar a otra persona si incluyes -j o --jugador",
                    inline=False)
    embed.add_field(name='++crear id --nombre nombre de la partida [-d dd/mm][--dia dd/mm] [-i hh:mm][--inicio hh:mm]'
                         '[-f hh:mm][--fin hh:mm] [-m maximo][--maximo maximo] [-N notas][--notas notas] [-t tipo][--tipo tipo]',
                    value="Crea una partida con una id y un nombre. Si tu partida está fuera de los canales diarios indica el dia con -d. ¡El resto de opciones son opcionales!",
                    inline=False)
    embed.add_field(name='++anular id',
                    value="Anula una partida que tu dirijas."
                    , inline=False)
    embed.add_field(name='++listar',
                    value="Lista todas las partidas disponibles del servidor",
                    inline=False)
    embed.add_field(name='++ayuda',
                    value="Es lo que estas leyendo, grumete",
                    inline=False)

    await ctx.message.author.send(embed=embed)


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
        if TAG in msg.content and Evento(msg.content).event_dict['Dia'].date < day:
            await msg.unpin()

    return True

bot.loop.create_task(list_servers())
bot.run(TOKEN)
