from typing import List, Tuple
import discord
import pandas as pd
import io
import os
import asyncio

from discord.ext import commands
from discord import app_commands
from unidecode import unidecode
from copy import copy, deepcopy

from datetime import date
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient

USER = os.getenv('MONGO_USER')
PWD = os.getenv('MONGO_PASSWORD')

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
        self.status = (True, 'Fecha válida')
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
            
            if today > target_date:
                raise ValueError('La fecha es anterior a hoy.')
            
            self.date = target_date            
            

    def __str__(self):
        i = self.date.weekday()
        weekday = self.LEGAL_DAYS[i][-1]
        return f'{weekday} {self.date.day}/{self.date.month}/{self.date.year}'

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

class Jugadores:
    def __init__(self, players = None, maximo = None, *args, **kwargs):
        
        self.maximo = maximo
        
        if players is None:
            self.players = []
        
        elif isinstance(players, str):
            p, m = players.split('-')
            clean = p.split('*')
            
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
            raise ValueError('Demasiados jugadores.')


    def add_player(self, player):
        if len(self.players) >= self.maximo:
            return False, 'Demasiados jugadores.'
        
        if player in self.players:
            return False, f'El jugador {player} ya está en la lista.'
        
        self.players.append(player)
        return True, f'Jugador {player} añadido.'
    
    def remove_player(self, player):
        if player not in self.players:
            return False, f'El jugador {player} no está en la lista.'
        
        self.players.remove(player)
        return True, f'Jugador {player} eliminado.'
    
    def sort_players(self):
        self.players.sort()
    
    def __str__(self):
        
        players = '\n* '.join(self.players)
        n_players = len(self.players)
        return f'* {players}\n- {n_players}/{self.maximo}'

class Evento:
    EVENT_TAG = f'🏴‍☠️ Evento Bukanero 🏴‍☠️'
    LOGO = 'https://pbs.twimg.com/profile_images/1781974320324980736/65c8ygwS_400x400.jpg'
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
        
        self.tipo = tipo if tipo is not None else 'Partida de rol' 
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
            return (False, f'El evento no pudos ser creado | Motivo: {e}')

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
    
    def to_embed(self, icon_director):
        # Se crea un embed con los campos del evento
        embed = discord.Embed(title=self.tipo)
        last_update = datetime.now().strftime('%d/%m/%Y %H:%M')
        embed.set_footer(text=f'{self.EVENT_TAG} - {last_update} - Arrr!', icon_url=self.LOGO)
        embed.set_author(name=self.director, icon_url=icon_director)
        embed.set_thumbnail(url=self.LOGO)
        
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
        return f'{self.tipo} \n **{self.nombre}** el dia **{self.dia}** de **{self.inicio}** a **{self.fin}**\n'
    
    def is_eq(self, evento):
        return unidecode(self.id.lower()) == unidecode(evento.id.lower())
    
    def is_eq_id(self, id):
        return unidecode(self.id.lower()) == unidecode(id.lower())
    
    def unique_id(self):
        return f'{self.id}_{self.director}_{self.dia}_{self.inicio}'

class EventsButton(discord.ui.View):
    def __init__(self, *, database, timeout=None):
        super().__init__(timeout=timeout or 180)
        self.database = database

    async def _manage_check(self, interaction, check, msg) -> Tuple[bool, str]:       
        if check:
            await interaction.followup.send(content=msg, ephemeral=True)
        
        assert not check, f' <EVENTOS> Error..., {msg}'

    def _log_event(self, event, status='CREATED', ongoing=True) -> None:
        event_dict = event.to_dict()
        event_dict['timestamp'] = datetime.now()
        event_dict['unique_id'] = event.unique_id()
        event_dict['status'] = status
        event_dict['ongoing'] = ongoing
        filter = {'unique_id': event_dict['unique_id']}
        
        if status == 'CREATED':
            self.database.insert_one(event_dict)
        else:
            self.database.update_one(filter, {'$set': event_dict})
            
    @discord.ui.button(label="Apuntarme", style=discord.ButtonStyle.success, emoji="✔️")
    async def apuntar_boton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        author = interaction.user.name
        message = interaction.message
        check, event = Evento.create(message.embeds[0])
        
        await self._manage_check(interaction, not check, event)
            
        check, msg = event.add_player(author)
                
        await self._manage_check(interaction, not check, msg)
        
        await message.edit(content=event.summarize(), embed=event.to_embed(interaction.user.display_avatar.url))
        await interaction.followup.send(content=f'{author} se ha apuntado a **{event.id}**.', ephemeral=True)
        self._log_event(event, status='ACTIVE', ongoing=True)

    @discord.ui.button(label="Quitarme", style=discord.ButtonStyle.grey, emoji="❌")
    async def quitar_boton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        author = interaction.user.name
        message = interaction.message
        check, event = Evento.create(message.embeds[0])
        
        await self._manage_check(interaction, not check, event)
            
        check, msg = event.remove_player(author)
                
        await self._manage_check(interaction, not check, msg)
                    
        await message.edit(content=event.summarize(), embed=event.to_embed(interaction.user.display_avatar.url))
        await interaction.followup.send(content=f'{author} se ha quitado de **{event.id}**.', ephemeral=True)
        self._log_event(event, status='ACTIVE', ongoing=True)
    
    @discord.ui.button(label="Anular", style=discord.ButtonStyle.danger, emoji="💀")
    async def anular_boton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        author = interaction.user.name
        message = interaction.message
        check, event = Evento.create(message.embeds[0])
        
        await self._manage_check(interaction, not check, event)
        await self._manage_check(interaction, event.director != author, f'No eres el director del evento **{event.id}**.')
        
        await message.unpin()
        await message.edit(view=None)
        await interaction.followup.send(content=f'Evento **{event.id}** anulado con éxito.', ephemeral=True)
        self._log_event(event, status='CANCELLED', ongoing=False)
        
class Events(commands.Cog):
    ADMIN_TAG = 'administrador'

    def __init__(self, client):
        self.client = client
        print(f' <EVENTOS> Conectando a la base de datos...')
        self.database = client.db_client['Bukaneros']['Eventos']
        print(f' <EVENTOS> Conexión establecida.')
    
    async def _manage_check(self, interaction, check, msg) -> Tuple[bool, str]:       
        if check:
            await interaction.followup.send(content=msg, ephemeral=True)
        
        assert not check, f' <EVENTOS> Error..., {msg}'
    
    async def _retrieve_pinned(self, interaction) -> List[Tuple[Evento, discord.Message]]:
        pinned = await interaction.channel.pins()
        events = []
        for message in pinned:
            embed = message.embeds[0]
            if Evento.EVENT_TAG in embed.footer.text:
                _, event = Evento.create(embed)
                events.append((event, message))
        return events
    
    def _log_event(self, event, status='CREATED', ongoing=True) -> None:
        event_dict = event.to_dict()
        event_dict['timestamp'] = datetime.now()
        event_dict['unique_id'] = event.unique_id()
        event_dict['status'] = status
        event_dict['ongoing'] = ongoing
        filter = {'unique_id': event_dict['unique_id']}
        
        check = self.database.find_one(filter)
        
        if check is None:
            self.database.insert_one(event_dict)
        else:
            self.database.update_one(filter, {'$set': event_dict})
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(' [Eventos] cog loaded.')

    @app_commands.command(name='crear',
                          description='Crea un evento para dirigir.',
                          )
    async def crear(self, 
                    interaction: discord.Interaction,
                    id: str,
                    nombre: str,
                    dia: str = None,
                    inicio: str = None,
                    fin: str = None,
                    maximo: int = None,
                    notas: str = None,
                    tipo: str = None,
                    ): 
        await interaction.response.defer()
        print(' <EVENTOS> Creando evento...')
        author = interaction.user.name
        
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
        
        await self._manage_check(interaction, not check, event)
        
        # Check if there are any old events pinned:
        old_events = await self._retrieve_pinned(interaction)

        # Check if any of the old events is the same as the new one:
        await self._manage_check(interaction, 
                                 any(event.is_eq(e) for e, _ in old_events), 
                                 f'Ya existe un evento con id **{id}**.')       

        message = await interaction.channel.send('Creando evento...')           
        event.set_link(message.jump_url)
        await message.edit(content=event.summarize(), 
                           embed=event.to_embed(interaction.user.display_avatar.url), 
                           view=EventsButton(database=self.database))
        await message.pin()
        
        await interaction.followup.send(content='Evento creado con éxito.', ephemeral=True)
        self._log_event(event, status='CREATED', ongoing=True)   
        print(' <EVENTOS> Evento creado con exito...')

    @app_commands.command(name='anular',
                          description='Anula un evento que diriges.',
                          )
    async def anular(self, 
                     interaction: discord.Interaction,
                     id: str,
                     ):
        await interaction.response.defer()
        print(' <EVENTOS> Anulando evento...')
        
        author = interaction.user.name
                
        old_events = await self._retrieve_pinned(interaction)
        
        for event, message in old_events:
            if event.is_eq_id(id):
                await self._manage_check(interaction, 
                                         event.director != author, 
                                         f'No eres el director del evento **{id}**.')
                
                await message.unpin()
                await message.edit(view=None)
                await interaction.followup.send(content=f'Evento **{id}** anulado con éxito.', ephemeral=True)
                print(' <EVENTOS> Evento anulada con exito')        
                self._log_event(event, status='CANCELLED', ongoing=False)   
                return 
        
        await interaction.followup.send(content=f'No se ha encontrado la evento **{id}**.', ephemeral=True)

    @app_commands.command(name='apuntar',
                            description='Apuntate a un evento.',
                            )
    async def apuntar(self,
                      interaction: discord.Interaction,
                      id: str,
                      jugador: str = None,   
                      ):
        await interaction.response.defer()
        print(' <EVENTOS> Apuntando al evento...')
            
        author = interaction.user.name if jugador is None else jugador
            
        old_events = await self._retrieve_pinned(interaction)
            
        for event, message in old_events:
            if event.is_eq_id(id):
                check, msg = event.add_player(author)
                
                await self._manage_check(interaction, not check, msg)
                    
                await message.edit(content=event.summarize(), embed=event.to_embed(interaction.user.display_avatar.url))
                await interaction.followup.send(content=f'{author} se ha apuntado a **{id}**.', ephemeral=True)
                self._log_event(event, status='ACTIVE', ongoing=True)   

                print(' <EVENTOS> Apuntado con exito')
                return 
            
        await interaction.followup.send(content=f'No se ha encontrado el evento **{id}**.', ephemeral=True)

    @app_commands.command(name='quitar',
                          description='Desapuntate de un evento.',
                            )
    async def quitar(self,
                     interaction: discord.Interaction,
                     id: str,
                     jugador: str = None,
                     ):
            await interaction.response.defer()
            print(' <EVENTOS> Quitando de la evento...')
                
            author = interaction.user.name if jugador is None else jugador
                
            old_events = await self._retrieve_pinned(interaction)
                
            for event, message in old_events:
                if event.is_eq_id(id):
                    check, msg = event.remove_player(author)
                    
                    await self._manage_check(interaction, not check, msg)
                        
                    await message.edit(content=event.summarize(), embed=event.to_embed(interaction.user.display_avatar.url))
                    await interaction.followup.send(content=f'{author} ha salido de **{id}**.', ephemeral=True)
                    self._log_event(event, status='ACTIVE', ongoing=True)   
                    print(' <EVENTOS> Quitado con exito')
                    return 
                
            await interaction.followup.send(content=f'No se ha encontrado el evento **{id}**.', ephemeral=True)

    @app_commands.command(name='modificar',
                            description='Modifica un evento que diriges.',
                            )
    async def modificar(self,
                        interaction: discord.Interaction,
                        id: str,
                        nueva_id: str = None,
                        nombre: str = None,
                        dia: str = None,
                        inicio: str = None,
                        fin: str = None,
                        maximo: int = None,
                        notas: str = None,
                        tipo: str = None,
                        ):
        await interaction.response.defer()
        print(' <EVENTOS> Modificando evento...')
        
        author = interaction.user.name
        
        old_events = await self._retrieve_pinned(interaction)
        
        for event, message in old_events:
            if event.is_eq_id(id):
                await self._manage_check(interaction, 
                                         event.director != author, 
                                         f'No eres el director de la evento **{id}**.')
                
                try:
                    event.update_field(id=nueva_id, 
                                       nombre=nombre, 
                                       dia=dia, 
                                       inicio=inicio, 
                                       fin=fin, 
                                       maximo=maximo, 
                                       notas=notas, 
                                       tipo=tipo)
                except Exception as e:
                    await interaction.followup.send(content=f'Error al modificar la evento: {e}', ephemeral=True)
                    return
                
                await message.edit(content=event.summarize(), embed=event.to_embed(interaction.user.display_avatar.url))
                await interaction.followup.send(content=f'Evento **{id}** modificado con éxito.', ephemeral=True)
                self._log_event(event, status='ACTIVE', ongoing=True)
                print(' <EVENTOS> Evento modificado con exito')   
                return
        
        await interaction.followup.send(content=f'No se ha encontrado el evento **{id}**.', ephemeral=True)
    
    @app_commands.command(name='mover',
                            description='Mueve un jugador a otro evento.',
                            )
    async def mover(self,
                    interaction: discord.Interaction,
                    id: str,
                    nueva_id: str,
                    jugador: str = None,
                    ):
        await interaction.response.defer()
        print(' <EVENTOS> Moviendo jugador...')
        
        author = interaction.user.name if jugador is None else jugador
        
        old_events = await self._retrieve_pinned(interaction)
        
        check_event = False
        for event, message in old_events:
            if event.is_eq_id(id):                
                check, msg = event.remove_player(author)
                
                await self._manage_check(interaction, not check, msg)
                
                await message.edit(content=event.summarize(), 
                                   embed=event.to_embed(interaction.user.display_avatar.url))
                
                check_event = True
        
        await self._manage_check(interaction, not check_event, f'No se ha encontrado el evento de origen **{id}**.')
        
        for event, message in old_events:
            if event.id == nueva_id:
                check, msg = event.add_player(author)
                
                await self._manage_check(interaction, not check, msg)
                
                await message.edit(content=event.summarize(), 
                                   embed=event.to_embed(interaction.user.display_avatar.url))
                await interaction.followup.send(content=f'{author} se ha movido de **{id}** a **{nueva_id}**.', ephemeral=True)
                self._log_event(event, status='ACTIVE', ongoing=True)  
                print(' <EVENTOS> Movido con exito')
                return
            
        await interaction.followup.send(content=f'No se ha encontrado el evento de destino **{nueva_id}**.', ephemeral=True)
        
    @app_commands.command(name='listar',
                            description='Muestra las partidas en curso.',
                            )
    async def listar(self, interaction: discord.Interaction):
        await interaction.response.defer()
                
        to_check = []
        retrieved_events = self.database.find({'ongoing': True})
                        
        games = pd.DataFrame(retrieved_events)
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
            jugadores = row['Jugadores']
            _, m = jugadores.split('-')
            link = row['Link']
            message += f'# {idx}\n* {nombre}, Dirige **{director}** a las **{inicio}**\n* Quedan {m} huecos.\n* Apúntante en {link}\n'
        
        if len(message) > 2000:
            message = 'Hay demasiados eventos en curso. Consulta el archivo con información.'

        await interaction.followup.send(content='Los eventos en curso están en tus mensajes privados...', ephemeral=True)
        await interaction.user.send(content=message, file=file_games)
        #await interaction.followup.send(content=message, file=file_games, ephemeral=True)

    @app_commands.command(name='recoger',
                          description='Recoge los eventos finalizados.',
                          )
    @app_commands.choices(margen=[
        app_commands.Choice(name="Mes", value="m"),
        app_commands.Choice(name="Trimestre", value="t"),
        app_commands.Choice(name="Año", value="y"),
        app_commands.Choice(name="Todo", value="a"),
        ])
    @commands.has_role(ADMIN_TAG)
    async def recoger(self, interaction: discord.Interaction, margen: app_commands.Choice[str]):
        await interaction.response.defer()

        day = datetime.now()
        if margen.value == 'm':
            start_date = day - relativedelta(months=1)
        elif margen.value == 't':
            start_date = day - relativedelta(months=3)
        elif margen.value == 'y':
            start_date = day - relativedelta(years=1)
        elif margen.value == 'a':
            start_date = date(1992, 1, 1)
        
        retrieved_events = self.database.find({'timestamp': {'$gt': start_date}, 'status': 'FINALIZED'})
        
        await interaction.followup.send(content='Los eventos finalizados están en tus mensajes privados...', ephemeral=True)
        
        df_events = pd.DataFrame(retrieved_events)
        csv_data = df_events.to_csv().encode()
        csv_file = io.BytesIO(csv_data)
        discord_file = discord.File(csv_file, filename='eventos.csv')
        
        await interaction.user.send(content='Eventos finalizados:', file=discord_file)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        await asyncio.sleep(15)
        
        day = date.today()
        
        old_events = await self._retrieve_pinned(message)
        for event, msg in old_events:
            if event.dia.date < day:
                await msg.unpin()
                await msg.edit(view=None)
                self._log_event(event, status='FINALIZED', ongoing=False)
            else:
                await msg.edit(view=EventsButton(database=self.database))
                self._log_event(event, status='ACTIVE', ongoing=True)
        
        return True
    
async def setup(client):
    await client.add_cog(Events(client))