from typing import List, Literal, NamedTuple, Optional, Tuple, Union
import discord
import pandas as pd
import io
import asyncio
import hashlib
import re

from discord.ext import commands, tasks
from discord import app_commands
import pymongo
import pymongo.collection
from unidecode import unidecode
from copy import copy, deepcopy

from datetime import date
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import yaml

ADMIN_TAG = 'administrador'
POLIZON_TAG = 'polizón'

#########################################################################
# DIA CLASS                                                             #
#########################################################################
class Dia:
    LEGAL_DAYS = [['lunes', 'l', 'lun', 'Lunes'],
                  ['martes', 'm', 'mar', 'Martes'],
                  ['miercoles', 'x', 'mie', 'Miércoles'],
                  ['jueves', 'j', 'jue', 'Jueves'],
                  ['viernes', 'v', 'vie', 'Viernes'],
                  ['sabado', 's', 'sab', 'sabados', 'Sábado'],
                  ['domingo', 'd', 'dom', 'domingos', 'Domingo']]

    LEGAL_DAYS_SET = set([item for sublist in LEGAL_DAYS for item in sublist])
    
    def __init__(self, fecha=None, *args, **kwargs):
        # Si no se pasa ningún argumento, se toma la fecha de mañana
        if fecha is None:
            self.date = date.today() + relativedelta(days=1)
        
        # Si se pasa un argumento, se comprueba si es un Dia
        elif isinstance(fecha, Dia):
            self.date = copy(fecha.date)

        # Si se pasa un argumento, se comprueba si es una fecha
        elif isinstance(fecha, date):
            self.date = copy(fecha)
        
        # Si se pasa un argumento, se comprueba si es un string
        elif isinstance(fecha, str):
            today = date.today()
            is_date_format = False
            
            # Si el argumento es un string que se puede parsear a fecha
            try:
                target_date = parse(fecha, dayfirst=True, fuzzy=True).date()
                is_date_format = True
            except Exception as e:
                pass
            
            # Si el argumento es contenido en la lista de días de la semana
            if not is_date_format and unidecode(fecha).lower() in self.LEGAL_DAYS_SET:
                # Se busca el índice del día de la semana
                for idx, days in enumerate(self.LEGAL_DAYS):
                    if unidecode(fecha).lower() in days:
                        weekday_idx = idx

                # Se calcula la diferencia de días entre el día de la semana y el día actual
                time_diff = weekday_idx - today.weekday()
                increment = relativedelta(days=time_diff) if time_diff > 0 else relativedelta(days=7 + time_diff)
                target_date = today + increment
            
            # Si el string es una fecha en formato dd/mm
            elif not is_date_format and ' ' not in fecha and (len(fecha.split('/')) == 2 or len(fecha.split('-')) == 2):
                # Se comprueba si el string es una fecha en formato dd/mm o dd-mm
                if len(fecha.split('/')) == 2:
                    tmp = fecha.split('/')
                elif len(fecha.split('-')) == 2:
                    tmp = fecha.split('-')
                
                # Se crea la fecha con el día y mes del string y el año actual
                target_date = date(day=int(tmp[0]), month=int(tmp[1]), year=today.year)
            
            # Si el string es un número, se toma como el día del mes
            elif not is_date_format and fecha.isnumeric():
                day = int(fecha)
                    
                target_date = date(day=day, month=today.month, year=today.year)
                
                # Si el día es anterior al día actual, se toma el mes siguiente
                if today.day > day:
                    target_date = target_date + relativedelta(months=1)

            
            # Si el string es 'mañana', se toma la fecha de mañana
            elif not is_date_format and fecha.lower() == 'mañana':
                # Si el string es 'mañana', se toma la fecha de mañana
                target_date = today + relativedelta(days=1)
            
            # Si no se ha podido parsear el string a fecha
            elif not is_date_format:
                raise ValueError('No se ha podido parsear el string a fecha.')
            
            self.date = target_date            
            

    def __str__(self):
        i = self.date.weekday()
        weekday = self.LEGAL_DAYS[i][-1]
        return f'{weekday} {self.date.day}/{self.date.month}/{self.date.year}'

#########################################################################
# HORA CLASS                                                            #
#########################################################################

class Hora:
    def __init__(self, hour=None, *args, **kwargs):
        
        # Si no se pasa ningún argumento, se toma la hora por defecto (00.00)
        if hour is None:
            self.hour = 0
            self.minute = 0
        
        elif isinstance(hour, str):
            if ':' not in hour and '.' not in hour:
                h, m = int(hour), 0
            else:
                if ':' in hour:
                    tmp = hour.split(':')
                elif '.' in hour:
                    tmp = hour.split('.')
                h, m  = int(tmp[0]), int(tmp[1])        
            
            if h < 0 or h > 23:
                h = 23
            if m < 0 or m > 59:
                m = 59
                    
            self.hour = h
            self.minute = m

    def __str__(self):
        return f'{self.hour:02}:{self.minute:02}'

#########################################################################
# JUGADORES CLASS                                                       #
#########################################################################

class Jugadores:
    
    def __init__(self, players = None, maximo = None, *args, **kwargs):
        
        self.maximo = maximo
        

        if players is None:
            self.players = []
        
        elif isinstance(players, str):
            player_finder = re.compile(r'\*\s+`(.*)`\n')
            p, m = players.split('🧑‍🤝‍🧑 ')
            clean = player_finder.findall(p)
            
            _, str_max = m.split('/')
            self.maximo = int(str_max)
            
            self.players = [x.strip() for x in clean]

        elif isinstance(players, players):
            self.players = copy(players.players)
        else:
            raise ValueError('Jugadores no es una lista.')

        if self.maximo is None:
            self.maximo = 5

        self.players = [x for x in self.players if x != '']
        
        if len(self.players) > self.maximo:
            raise ValueError('Hay demasiados jugadores en la partida.')

    @staticmethod
    def from_str(players):
        player_finder = re.compile(r'\*\s+`(.*)`\n')
        p, m = players.split('🧑‍🤝‍🧑 ')
        clean = player_finder.findall(p)
        _, str_max = m.split('/')
        maximo = int(str_max)
        
        return [c.strip() for c in clean if c.strip() != ''] , maximo
    
    def add_player(self, player):
        if len(self.players) >= self.maximo:
            return False, 'Hay demasiados jugadores en la partida.'
        
        if player in self.players:
            return False, f'El jugador {player} ya está en la lista.'
        
        self.players.append(player)
        return True, f'Jugador {player} añadido con éxito.'
    
    def remove_player(self, player):
        if player not in self.players:
            return False, f'El jugador {player} no está en la lista.'
        
        self.players.remove(player)
        return True, f'Jugador {player} eliminado con éxito.'
    
    def sort_players(self):
        self.players.sort()
    
    def __str__(self):
        
        player_str = ''
        for player in self.players:
            player_str += f'* `{player}`\n'
        n_players = len(self.players)
        return f'{player_str}\n🧑‍🤝‍🧑 {n_players}/{self.maximo}'

#########################################################################
# EVENTO CLASS                                                          #
#########################################################################

class Evento:
    EVENT_TAG = f'🏴‍☠️ Evento Bukanero 🏴‍☠️'
    def __init__(self, 
                 tipo: str = None, 
                 id: str = None, 
                 nombre: str = None, 
                 dia: Dia | str = None, 
                 inicio: Hora | str = None, 
                 fin: Hora | str = None, 
                 director: str = None, 
                 jugadores: Jugadores | str = None, 
                 maximo: int | str  = None, 
                 notas: str = None,
                 link: str = None,
                 *args,
                 **kwargs):
        
        self.tipo = tipo if tipo is not None else 'Partida de rol (Presencial)' 
        self.id = id
        self.nombre = nombre
        
        self.dia = Dia(dia)
        self.inicio = Hora(inicio) if inicio is not None else Hora('17:00')
        self.fin = Hora(fin) if fin is not None else Hora('21:00')
        
        self.director = director
        self.jugadores = Jugadores(jugadores, maximo)
        self.notas = notas if notas is not None else '-'

        self.link = link
        
    def __str__(self):
        # Se devuelve una cadena con los campos del evento
        return f'{self.tipo} | {self.nombre} | {self.dia} | {self.inicio} | {self.fin} | {self.director} | {self.jugadores} | {self.notas}'
        
    # Métodos de clase    
    @staticmethod
    def from_embed(embed):
        embd_dct = {dct['name'].lower(): dct['value'] for dct in embed.to_dict()['fields']}
        return Evento(**embd_dct)
    
    @staticmethod
    def from_dict(dct):
        return Evento(**dct)
    
    @staticmethod
    def create(inputs=None, *args, **kwargs):
        try:
            if inputs is None:
                return True, Evento(*args, **kwargs)
            elif isinstance(inputs, discord.Embed):
                return True, Evento.from_embed(inputs)
            elif isinstance(inputs, dict):
                return True, Evento.from_dict(inputs)
            elif isinstance(inputs, Evento):
                return True, inputs.copy()
            else:
                return False, 'Tipo de dato no soportado.'
        
        except Exception as e:
            return (False, f'El evento no pudo ser creado | Motivo: {e}')

    def set_link(self, link):
        self.link = link
    
    def copy(self):
        return deepcopy(self)
    
    # Métodos de instancia
    def update_field(self, **kwargs):
        # Se actualizan los campos del evento
        for key, value in kwargs.items():
            if value is not None:
                casting_type = str
                if key == 'dia':
                    casting_type = Dia
                elif key == 'inicio' or key == 'fin':
                    casting_type = Hora
                
                if key == 'maximo':
                    self.jugadores.maximo = int(value)
                else:
                    setattr(self, key, casting_type(value))
    
    def add_player(self, player):
        return self.jugadores.add_player(player)
    
    def remove_player(self, player):
        return self.jugadores.remove_player(player)
    
    def sort_players(self):
        self.jugadores.sort_players()
    
    def to_embed(self, interaction: discord.Interaction):
        # Se crea un embed con los campos del evento
        embed = discord.Embed(title=self.tipo)
        last_update = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        icon_director = interaction.user.display_avatar
        icon_guild = interaction.guild.icon
        icon_bot = interaction._client.user.display_avatar
        
        embed.set_footer(text=f'{self.EVENT_TAG} - {last_update} - Arrr!', 
                         icon_url= None if icon_bot is None else icon_bot.url)
        embed.set_author(name=self.director, 
                         icon_url= None if icon_director is None else icon_director.url)
        embed.set_thumbnail(url= None if icon_guild is None else icon_guild.url)
        
        for key, value in self.__dict__.items():
            key = key.capitalize()
            inline = key not in {'Jugadores', 'Notas', 'Nombre'}
            embed.add_field(name=key, value=str(value)[:1024], inline=inline)
        return embed

    def to_dict(self):
        # Se devuelve un diccionario con los campos del evento
        dict_event = {key: str(value) for key, value in self.__dict__.items()}
        return dict_event
    
    def summarize(self):
        # Se devuelve una cadena con los campos del evento
        if len(self.jugadores.players) > 0:
            participantes_str = f'Participan:\n{str(self.jugadores)}'
        else:
            participantes_str = 'No hay participantes todavía.'
        return f'```{self.tipo} \n {self.director} dirige {self.nombre} el dia {self.dia} de {self.inicio} a {self.fin}\n{participantes_str}```'
    
    def is_eq(self, evento):
        return unidecode(self.id.lower()) == unidecode(evento.id.lower())
    
    def is_eq_id(self, id):
        return unidecode(self.id.lower()) == unidecode(id.lower())
    
    def unique_id(self):
        # Se devuelve un hash único para el evento
        return hashlib.sha256(str(self.link).encode()).hexdigest()


#########################################################################
# ADDITIONAL METHODS                                                    #
#########################################################################

async def _manage_check(interaction, check, msg) -> Tuple[bool, str]:
    if check:
        await interaction.followup.send(content=msg, ephemeral=True)
    
    assert not check, f' <EVENTOS> Error..., {msg}'


def _log_event(db, event:Evento, status:str='ACTIVE', ongoing:bool=True) -> None:
        event_dict = event.to_dict()
        
        for key, value in event_dict.items():
            event_dict[key] = str(value) # Sanitize values
        
        event_dict['timestamp'] = datetime.combine(Dia(event_dict['dia']).date, datetime.min.time())
        event_dict['last_updated'] = datetime.now()
        event_dict['unique_id'] = event.unique_id()
        event_dict['status'] = status
        event_dict['ongoing'] = ongoing
        
        player_list, max_players = Jugadores.from_str(event_dict['jugadores'])
        event_dict['jugadores'] = player_list
        event_dict['numero'] = len(player_list)
        event_dict['maximo'] = max_players
        filter = {'unique_id': event_dict['unique_id']}
        
        check = db.find_one(filter)
        
        
        if check is None:
            db.insert_one(event_dict)
        else:
            db.update_one(filter, {'$set': event_dict})
            
        print(f' <EVENTOS:DATABASE> Evento {event_dict["id"]} registrado con éxito.')

def _manage_author(user: Union[discord.User, discord.Member, str], is_invited = 0) -> str:  
    author = user.nick if user.nick is not None else user.name
    for role in user.roles:
        if unidecode(role.name.lower()) == unidecode(POLIZON_TAG.lower()):
            author = f'{author} (Polizón)'
            break
    if is_invited > 0:
        author = f'Invitado {is_invited} de {author}'
    return author
        
#########################################################################
# BUTTONS                                                               #
#########################################################################

class EventsButton(discord.ui.View):
    def __init__(self, *, database, timeout=None):
        super().__init__(timeout=timeout)
        self.database = database
            
    @discord.ui.button(label="Apuntarme", style=discord.ButtonStyle.success, emoji="✔️")
    async def apuntar_boton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        author = _manage_author(interaction.user)
        
        message = interaction.message
        check, event = Evento.create(message.embeds[0])
        
        await _manage_check(interaction, not check, event)
            
        check, msg = event.add_player(author)
                
        await _manage_check(interaction, not check, msg)
        
        await message.edit(content=event.summarize(), embed=event.to_embed(interaction))
        await interaction.followup.send(content=f'{author} se ha apuntado a **{event.id}**.', ephemeral=True)
        _log_event(self.database, event, status='ACTIVE', ongoing=True)

    @discord.ui.button(label="Quitarme", style=discord.ButtonStyle.grey, emoji="❌")
    async def quitar_boton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        author = _manage_author(interaction.user)
        
        message = interaction.message
        check, event = Evento.create(message.embeds[0])
        
        await _manage_check(interaction, not check, event)
            
        check, msg = event.remove_player(author)
                
        await _manage_check(interaction, not check, msg)
                    
        await message.edit(content=event.summarize(), embed=event.to_embed(interaction))
        await interaction.followup.send(content=f'{author} se ha quitado de **{event.id}**.', ephemeral=True)
        _log_event(self.database, event, status='ACTIVE', ongoing=True)
    
    @discord.ui.button(label="Anular (Solo directores)", style=discord.ButtonStyle.danger, emoji="💀")
    async def anular_boton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        author = _manage_author(interaction.user)

        message = interaction.message
        check, event = Evento.create(message.embeds[0])
        
        await _manage_check(interaction, not check, event)
        is_admin = any(unidecode(role.name.lower()) == unidecode(ADMIN_TAG.lower()) for role in interaction.user.roles)
        await _manage_check(interaction, 
                            not is_admin and event.director != author, 
                            f'No eres el director del evento **{event.id}**.')
        
        await message.unpin()
        await message.edit(view=None)
        await interaction.followup.send(content=f'Evento **{event.id}** anulado con éxito.', ephemeral=True)
        _log_event(self.database, event, status='CANCELLED', ongoing=False)


#########################################################################
# COG                                                               #
#########################################################################

class Events(commands.Cog):
    with open('strings.yaml', 'r') as stream:
        HELP_DICT = yaml.safe_load(stream)

    def __init__(self, client: pymongo.MongoClient):
        self.client = client
        print(f' <EVENTOS> Conectando a la base de datos...')
        self.database = client.db_client['Bukaneros']['Eventos']
        print(f' <EVENTOS> Conexión establecida.')        

    async def _retrieve_pinned(self, channel: discord.abc.GuildChannel) -> List[Tuple[bool, Evento, discord.Message]]:
        pinned = await channel.pins()
        events = []
        for message in pinned:
            embeds = message.embeds
            if len(embeds) == 1:
                embed = embeds[0]
                if Evento.EVENT_TAG in embed.footer.text:
                    check, event = Evento.create(embed)
                    events.append((check, event, message))
        return events
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(' [Eventos] cog loaded.')

    @app_commands.command(name='ayuda',
                          description=HELP_DICT['ayuda']['cmd'],
                          )
    async def ayuda(self, interaction: discord.Interaction):
        '''
        Muestra la ayuda de los comandos de eventos.
        '''
        await interaction.response.defer(ephemeral=True)
        
            
        embed = discord.Embed(title="Botkanero", description= self.HELP_DICT['intro'],
                            color=0xeee657)
        embed.add_field(name='Primeros pasos',
                        value=self.HELP_DICT['primeros_pasos'],
                        inline=False)
        embed.add_field(name=self.HELP_DICT['apuntar']['cmd'],
                        value=self.HELP_DICT['apuntar']['txt'],
                        inline=False)
        embed.add_field(name=self.HELP_DICT['quitar']['cmd'],
                        value=self.HELP_DICT['quitar']['txt'],
                        inline=False)
        embed.add_field(name=self.HELP_DICT['crear']['cmd'],
                        value=self.HELP_DICT['crear']['txt'],
                        inline=False)
        embed.add_field(name=self.HELP_DICT['modificar']['cmd'],
                        value=self.HELP_DICT['modificar']['txt'],
                        inline=False)
        embed.add_field(name=self.HELP_DICT['mover']['cmd'],
                        value=self.HELP_DICT['mover']['txt'],
                        inline=False)
        embed.add_field(name=self.HELP_DICT['anular']['cmd'],
                        value=self.HELP_DICT['anular']['txt'],
                        inline=False)
        embed.add_field(name=self.HELP_DICT['listar']['cmd'],
                        value=self.HELP_DICT['listar']['txt'],
                        inline=False)
        embed.add_field(name=self.HELP_DICT['ayuda']['cmd'],
                        value=self.HELP_DICT['ayuda']['txt'],
                        inline=False)

        for role in interaction.user.roles:
            if unidecode(role.name.lower()) == unidecode(ADMIN_TAG.lower()):
                embed.add_field(name=self.HELP_DICT['recoger']['cmd'],
                                value=self.HELP_DICT['recoger']['txt'],
                                inline=False)
                embed.add_field(name=self.HELP_DICT['finalizar']['cmd'],
                                value=self.HELP_DICT['finalizar']['txt'],
                                inline=False)
        
        await interaction.user.send(embed=embed)
        await interaction.followup.send(content='¡Ayuda bukanera mandada!', ephemeral=True)  
    
    @app_commands.command(name='crear',
                          description=HELP_DICT['crear']['cmd'],
                          )
    async def crear(self, 
                    interaction: discord.Interaction,
                    id: str,
                    nombre: str,
                    dia: str = None,
                    inicio: str = None,
                    fin: str = None,
                    maximo: app_commands.Range[int, 0, None] = None,
                    notas: str = None,
                    tipo: Literal["Partida de rol (Presencial)", "Partida de rol (Online)", "Juegos de mesa", "Miniaturas", "Otros"] = None,
                    ):
        '''
        Crea un evento para dirigir.
        
        Args:
            id (str): Identificador del evento.
            nombre (str): Nombre del evento.
            dia (str): Día del evento.
            inicio (str): Hora de inicio del evento.
            fin (str): Hora de fin del evento.
            maximo (int): Número máximo de jugadores.
            notas (str): Notas adicionales.
            tipo (str): Tipo de evento
            
        '''
        await interaction.response.defer(ephemeral=True)
        print(' <EVENTOS> Creando evento...')
        author = _manage_author(interaction.user)            
        check, event = Evento.create(
                        tipo=tipo,
                        id=id,
                        nombre=nombre,
                        dia=dia,
                        inicio=inicio,
                        director=author,
                        fin=fin,
                        maximo=maximo,
                        notas=notas
                    )
        
           
        await _manage_check(interaction, not check, event)
        
        today = date.today()
        
        await _manage_check(interaction, 
                            event.dia.date < today, 
                            'No se puede crear un evento en el pasado.')
            
        # Check if there are any old events pinned:
        old_events = await self._retrieve_pinned(interaction.channel)

        # Check if any of the old events is the same as the new one:
        await _manage_check(interaction, 
                            any(event.is_eq(e) for _, e, _ in old_events), 
                            f'Ya existe un evento con id **{id}**.')       
        
        contents = f'¡Nuevo evento! @here\n{event.summarize()}'
        message = await interaction.channel.send(content=contents,
                                                 embed=event.to_embed(interaction),
                                                 )
        event.set_link(message.jump_url)
        await message.edit(embed=event.to_embed(interaction), view=EventsButton(database=self.database))
        await message.pin()
        
        await interaction.followup.send(content=f'Evento **{event.id}** creado con éxito.\n **Link**: {event.link}', ephemeral=True)
        _log_event(self.database, event, status='ACTIVE', ongoing=True)   
        print(' <EVENTOS> Evento creado con exito...')
    
    @app_commands.command(name='anular',
                          description=HELP_DICT['anular']['cmd'],
                          )
    async def anular(self, 
                     interaction: discord.Interaction,
                     id: str,
                     ):
        '''
        Anula un evento que diriges.
        
        Args:
            id (str): Identificador del evento.
        '''
        await interaction.response.defer(ephemeral=True)
        print(' <EVENTOS> Anulando evento...')
        
        author = _manage_author(interaction.user)

        old_events = await self._retrieve_pinned(interaction.channel)
        
        for ok, event, message in old_events:
            if event.is_eq_id(id):
                is_admin = any(unidecode(role.name.lower()) == unidecode(ADMIN_TAG.lower()) for role in interaction.user.roles)
                await _manage_check(interaction, 
                                    not is_admin and event.director != author, 
                                    f'No eres el director del evento **{event.id}**.')        
                await message.unpin()
                await message.edit(view=None)
                await interaction.followup.send(content=f'Evento **{id}** anulado con éxito.', ephemeral=True)
                print(' <EVENTOS> Evento anulado con exito')        
                _log_event(self.database, event, status='CANCELLED', ongoing=False)   
                return 
        
        await interaction.followup.send(content=f'No se ha encontrado la evento **{id}**.', ephemeral=True)
    
    @app_commands.command(name='finalizar',
                          description=HELP_DICT['finalizar']['cmd'],
                          )
    @commands.has_role(ADMIN_TAG)
    async def finalizar(self, 
                     interaction: discord.Interaction,
                     id: str,
                     ):
        '''
        Finaliza un evento manualmente (Solo administradores).
        
        Args:
            id (str): Identificador del evento.
        '''
        await interaction.response.defer(ephemeral=True)
        print(' <EVENTOS> Finalizando evento...')
        
        # NO check for polizon, as it is an admin command
        old_events = await self._retrieve_pinned(interaction.channel)
        
        for ok, event, message in old_events:
            if event.is_eq_id(id):       
                await message.unpin()
                await message.edit(view=None)
                await interaction.followup.send(content=f'Evento **{id}** finalizado con éxito.', ephemeral=True)
                _log_event(self.database, event, status='FINALIZED', ongoing=False)
                print(' <EVENTOS> Evento finalizado con exito')        
                return 
        
        await interaction.followup.send(content=f'No se ha encontrado el evento **{id}**.', ephemeral=True)

    @app_commands.command(name='apuntar',
                            description=HELP_DICT['apuntar']['cmd'],
                            )
    async def apuntar(self,
                      interaction: discord.Interaction,
                      id: str,
                      jugador: discord.Member = None,
                      es_invitado: app_commands.Range[int, 0, None] = 0,   
                      ):
        '''
        Apuntate a un evento.
        
        Args:
            id (str): Identificador del evento.
            jugador (str): Nombre del jugador a apuntar.
            es_invitado (bool): Indica si el jugador es un invitado del que lanza el comando.
        '''
          
        await interaction.response.defer(ephemeral=True)
        print(' <EVENTOS> Apuntando al evento...')
        
        if jugador is None: author = _manage_author(interaction.user, es_invitado)
        else: author = _manage_author(jugador, es_invitado)    
        
        old_events = await self._retrieve_pinned(interaction.channel)
            
        for ok, event, message in old_events:
            if event.is_eq_id(id):
                check, msg = event.add_player(author)
                
                await _manage_check(interaction, not check, msg)
                    
                await message.edit(content=event.summarize(), embed=event.to_embed(interaction))
                await interaction.followup.send(content=f'{author} se ha apuntado a **{id}**. \n **Link**: {event.link}', ephemeral=True)
                _log_event(self.database, event, status='ACTIVE', ongoing=True)   

                print(' <EVENTOS> Apuntado con exito')
                return 
            
        await interaction.followup.send(content=f'No se ha encontrado el evento **{id}**.', ephemeral=True)

    @app_commands.command(name='quitar',
                          description=HELP_DICT['quitar']['cmd'],
                            )
    async def quitar(self,
                     interaction: discord.Interaction,
                     id: str,
                     jugador: discord.Member = None,
                     es_invitado: app_commands.Range[int, 0, None] = 0,
                     ):
        '''
        Desapuntate de un evento.
        
        Args:
            id (str): Identificador del evento.
            jugador (str): Nombre del jugador a desapuntar.
        '''
        await interaction.response.defer(ephemeral=True)
        print(' <EVENTOS> Quitando de la evento...')
            
        if jugador is None: author = _manage_author(interaction.user, es_invitado)
        else: author = _manage_author(jugador, es_invitado)    
            
        old_events = await self._retrieve_pinned(interaction.channel)
            
        for ok, event, message in old_events:
            if event.is_eq_id(id):
                check, msg = event.remove_player(author)
                
                await _manage_check(interaction, not check, msg)
                    
                await message.edit(content=event.summarize(), embed=event.to_embed(interaction))
                await interaction.followup.send(content=f'{author} ha salido de **{id}**.', ephemeral=True)
                _log_event(self.database, event, status='ACTIVE', ongoing=True)   
                print(' <EVENTOS> Quitado con exito')
                return 
            
        await interaction.followup.send(content=f'No se ha encontrado el evento **{id}**.', ephemeral=True)

    @app_commands.command(name='modificar',
                            description=HELP_DICT['modificar']['cmd'],
                            )
    async def modificar(self,
                        interaction: discord.Interaction,
                        id: str,
                        director: discord.Member = None,
                        nueva_id: str = None,
                        nombre: str = None,
                        dia: str = None,
                        inicio: str = None,
                        fin: str = None,
                        maximo: app_commands.Range[int, 0, None] = None,
                        notas: str = None,
                        tipo: Literal["Partida de rol (Presencial)", "Partida de rol (Online)", "Juegos de mesa", "Miniaturas", "Otros"] = None,
                        ):
        '''
        Modifica un evento que diriges.
        
        Args:
            id (str): Identificador del evento.
            nueva_id (str): Nuevo identificador del evento.
            nombre (str): Nuevo nombre del evento.
            dia (str): Nuevo día del evento.
            inicio (str): Nueva hora de inicio del evento.
            fin (str): Nueva hora de fin del evento.
            maximo (int): Nuevo número máximo de jugadores.
            notas (str): Nuevas notas adicionales.
            tipo (str): Nuevo tipo de evento
        '''
        
        await interaction.response.defer(ephemeral=True)
        print(' <EVENTOS> Modificando evento...')
        
        author = _manage_author(interaction.user)
        other_director = None if director is None else _manage_author(director)
        
        old_events = await self._retrieve_pinned(interaction.channel)
        
        for ok, event, message in old_events:
            if event.is_eq_id(id):
                is_admin = any(unidecode(role.name.lower()) == unidecode(ADMIN_TAG.lower()) for role in interaction.user.roles)
                await _manage_check(interaction, 
                                    not is_admin and event.director != author, 
                                    f'No eres el director del evento **{event.id}**.')        
                
                try:
                    event.update_field(id=nueva_id,
                                       director=other_director if other_director is not None else author, 
                                       nombre=nombre, 
                                       dia=dia, 
                                       inicio=inicio, 
                                       fin=fin, 
                                       maximo=maximo, 
                                       notas=notas, 
                                       tipo=tipo,
                                       )
                except Exception as e:
                    await interaction.followup.send(content=f'Error al modificar la evento: {e}', ephemeral=True)
                    return
                
                await message.edit(content=event.summarize(), embed=event.to_embed(interaction))
                await interaction.followup.send(content=f'Evento **{id}** modificado con éxito. \n **Link**: {event.link}', ephemeral=True)
                _log_event(self.database, event, status='ACTIVE', ongoing=True)
                print(' <EVENTOS> Evento modificado con exito')   
                return
        
        await interaction.followup.send(content=f'No se ha encontrado el evento **{id}**.', ephemeral=True)
    
    @app_commands.command(name='mover',
                            description=HELP_DICT['mover']['cmd'],
                            )
    async def mover(self,
                    interaction: discord.Interaction,
                    id: str,
                    nueva_id: str,
                    jugador: discord.Member = None,
                    es_invitado: app_commands.Range[int, 0, None] = 0,
                    ):
        '''
        Mueve un jugador a otro evento.
        
        Args:
            id (str): Identificador del evento de origen.
            nueva_id (str): Identificador del evento de destino.
            jugador (str): Nombre del jugador a mover.       
            es_invitado (bool): Indica si el jugador es un invitado del que lanza el comando. 
        '''
        await interaction.response.defer(ephemeral=True)
        print(' <EVENTOS> Moviendo jugador...')
        
        if jugador is None: author = _manage_author(interaction.user, es_invitado)
        else: author = _manage_author(jugador, es_invitado)    
        
        old_events = await self._retrieve_pinned(interaction.channel)
        
        check_event = False
        for ok, event, message in old_events:
            if event.is_eq_id(id):                
                check, msg = event.remove_player(author)
                
                await _manage_check(interaction, not check, msg)
                
                await message.edit(content=event.summarize(), 
                                   embed=event.to_embed(interaction))
                
                check_event = True
        
        await _manage_check(interaction, not check_event, f'No se ha encontrado el evento de origen **{id}**.')
        
        for ok, event, message in old_events:
            if event.id == nueva_id:
                await _manage_check(interaction, not ok, msg)
                                
                check, msg = event.add_player(author)
                
                await _manage_check(interaction, not check, msg)
                
                await message.edit(content=event.summarize(), 
                                   embed=event.to_embed(interaction))
                await interaction.followup.send(content=f'{author} se ha movido de **{id}** a **{nueva_id}**. \n **Link**: {event.link}', ephemeral=True)
                _log_event(self.database, event, status='ACTIVE', ongoing=True)  
                print(' <EVENTOS> Movido con exito')
                return
            
        await interaction.followup.send(content=f'No se ha encontrado el evento de destino **{nueva_id}**.', ephemeral=True)
        
    @app_commands.command(name='listar',
                            description=HELP_DICT['listar']['cmd'],
                            )
    async def listar(self, interaction: discord.Interaction):
        '''
        Muestra las partidas en curso.
        '''
        
        await interaction.response.defer(ephemeral=True)
                
        retrieved_events = self.database.find({'ongoing': True})
                        
        games = pd.DataFrame(retrieved_events)
        
        if len(games) == 0:
            await interaction.followup.send(content='No hay eventos en curso.', ephemeral=True)
            return
        
        games.columns = [x.capitalize() for x in games.columns]
        games.set_index('Dia', inplace=True)
        games.sort_index(inplace=True)
        
        games.drop(columns=['_id', 'Ongoing', 'Status', 'Unique_id', 'Timestamp'], inplace=True)
        
        file = games.to_csv().encode()
        enc_file = io.BytesIO(file)
        file_games = discord.File(enc_file, filename='eventos.csv')
            
        games.drop(columns=['Tipo', 'Id', 'Notas', 'Fin'], inplace=True)
        
        message = 'Estos son los eventos en curso:\n'
        for idx, row in games.iterrows():
            nombre = row['Nombre'].capitalize()
            director = row['Director']
            inicio = row['Inicio']
            jugadores = row['Numero']
            maximo = row['Maximo']
            link = row['Link']
            restantes = int(maximo-jugadores)
            
            if restantes == 0:
                slots_message = f'No quedan huecos. Consulta con **{director}** si puedes unirte.'
            elif restantes == 1:
                slots_message = f'Queda **{restantes}** hueco libre.'
            else:
                slots_message = f'Quedan **{restantes}** huecos libres.'
                
            message += f'# {idx}\n* {nombre}, Dirige **{director}** a las **{inicio}**\n* {slots_message}\n* Encuentra el evento en {link}\n'
        
        if len(message) > 2000:
            message = 'Hay demasiados eventos en curso. Consulta el archivo .csv adjunto.'

        await interaction.followup.send(content='Los eventos en curso están en tus mensajes privados...', ephemeral=True)
        await interaction.user.send(content=message, file=file_games)
        #await interaction.followup.send(content=message, file=file_games, ephemeral=True)

    @app_commands.command(name='recoger',
                          description=HELP_DICT['recoger']['cmd'],
                          )
    @app_commands.choices(margen=[
        app_commands.Choice(name="Mes", value="m"),
        app_commands.Choice(name="Trimestre", value="t"),
        app_commands.Choice(name="Año", value="y"),
        app_commands.Choice(name="Todo", value="a"),
        ], 
                          finalizados=[
        app_commands.Choice(name="Finalizados", value=1),
        app_commands.Choice(name="Todos", value=0),]
                          )
    @commands.has_role(ADMIN_TAG)
    async def recoger(self, 
                      interaction: discord.Interaction, 
                      margen: app_commands.Choice[str], 
                      finalizados: app_commands.Choice[int]
                      ):
        '''
        Recoge los eventos finalizados.
        
        Args:
            margen (str): Margen temporal para recoger los eventos. Todo el periodo en margen, hasta el primer dia del mes/año
            finalizados (int): Si se recogen los eventos finalizados o todos.        
        '''
        await interaction.response.defer(ephemeral=True)

        day = datetime.now()
        first_day = day.replace(day=1)
        first_month = day.replace(day=1, month=1)
        if margen.value == 'm':
            start_date = first_day - relativedelta(months=1)
        elif margen.value == 't':
            start_date = first_day - relativedelta(months=3)
        elif margen.value == 'y':
            start_date = first_month - relativedelta(years=1)
        
        query = {}
            
        if margen.value != 'a':
            query['timestamp'] = {'$gt': start_date}
        str_fin = ''
        if finalizados.value:
            str_fin = ' finalizados'
            query['status'] = 'FINALIZED'
        
        retrieved_events = self.database.find(query)
        
        await interaction.followup.send(content=f'Los eventos{str_fin} están en tus mensajes privados...', ephemeral=True)
        
        df_events = pd.DataFrame(retrieved_events).explode('jugadores')
        csv_data = df_events.to_csv().encode()
        csv_file = io.BytesIO(csv_data)
        discord_file = discord.File(csv_file, filename='eventos.csv')
        
        await interaction.user.send(content=f'Eventos{str_fin}:', file=discord_file)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        valid_message = not (message.content.startswith('+') or message.content.startswith('/')) and not message.author.bot
        
        if valid_message:
            day = date.today()

            old_events = await self._retrieve_pinned(message.channel)
            for _, event, msg in old_events:
                if event.dia.date < day:
                    print(f' <EVENTOS> Evento {event.id} está en tiempo de descuento.')
                    _log_event(self.database, event, status='ACTIVE', ongoing=False)
                if event.dia.date < day - relativedelta(days=1):
                    print(f' <EVENTOS> Evento {event.id} ha finalizado.')
                    await msg.unpin()
                    await msg.edit(view=None)
                    _log_event(self.database, event, status='FINALIZED', ongoing=False)
                else:
                    print(f' <EVENTOS> Evento {event.id} sigue en curso.')
                    await msg.edit(view=EventsButton(database=self.database))
                    _log_event(self.database, event, status='ACTIVE', ongoing=True)
        
        await asyncio.sleep(20)
    
    @tasks.loop(minutes=60.0) 
    async def clean_database(self): 
        day = datetime.now()
        if day.hour == 4:
            # Clean the database at 4.AM
            query = {'timestamp': {'$lt': day}, 'status': 'ACTIVE'}
            self.database.update_many(query, {'$set': {'ongoing': False}})
            
            query = {'timestamp': {'$lt': day - relativedelta(days=1)}, 'status': 'ACTIVE'}
            self.database.update_many(query, {'$set': {'status': 'FINALIZED'}})

            print(' <EVENTOS> Base de datos limpiada.')
                
async def setup(client):
    await client.add_cog(Events(client))