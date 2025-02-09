import discord
import unidecode
from copy import copy, deepcopy

from datetime import date
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

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
            if not is_date_format and unidecode.unidecode(fecha).lower() in self.LEGAL_DAYS_SET:
                # Se busca el índice del día de la semana
                for idx, days in enumerate(self.LEGAL_DAYS):
                    if unidecode.unidecode(fecha).lower() in days:
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
            m, p = players.split('|')
            clean = p.split(';')
            
            _, str_max = m.split('/')
            self.maximo = int(str_max)
            
            if len(clean) > self.maximo:
                raise ValueError('Demasiados jugadores.')

            self.players = [x.strip() for x in clean]

        elif isinstance(players, players):
            self.players = copy(players.players)
        else:
            raise ValueError('Jugadores no es una lista.')

        if self.maximo is None:
            self.maximo = 5


        
    def add_player(self, player):
        if len(self.players) >= self.maximo:
            return (False, 'Demasiados jugadores.')
        
        self.players.append(player)
        return (True, 'Jugador añadido.')
    
    def remove_player(self, player):
        if player not in self.players:
            return (False, 'El jugador no está en la lista.')
        elif len(self.players) == 1:
            return (False, 'No se puede quedar sin jugadores.')
        
        self.players.remove(player)
        return (True, 'Jugador eliminado.')
    
    def sort_players(self):
        self.players.sort()
    
    def __str__(self):
        players = '; '.join(self.players)
        n_players = len(self.players)
        return f'{n_players}/{self.maximo} | {players}'
            
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
                 *args,
                 **kwargs):
        
        self.tipo = tipo if tipo is not None else 'Partida de rol' 
        self.id = id
        self.nombre = nombre
        
        self.dia = Dia(dia)
        self.inicio = Hora(inicio)
        self.fin = Hora(fin)
        
        self.director = director
        self.jugadores = Jugadores(jugadores, maximo)
        self.notas = notas if notas is not None else '-'
    
    def __str__(self):
        # Se devuelve una cadena con los campos del evento
        return f'{self.tipo} | {self.nombre} | {self.dia} | {self.inicio} | {self.fin} | {self.director} | {self.jugadores} | {self.notas}'
        
    # Métodos de clase    
    @staticmethod
    def from_embed(embed):
        embd_dct = {dct['name'].lower(): dct['value']  for dct in embed.to_dict()['fields']}
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

    
    def copy(self):
        return deepcopy(self)
    
    # Métodos de instancia
    def update_field(self, **kwargs):
        # Se actualizan los campos del evento
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def add_player(self, player):
        return self.players.add_player(player)
    
    def remove_player(self, player):
        return self.players.remove_player(player)
    
    def sort_players(self):
        self.players.sort_players()
    
    def to_embed(self):
        # Se crea un embed con los campos del evento
        embed = discord.Embed(title=self.tipo)
        embed.set_footer(text=self.EVENT_TAG)
        embed.set_author(name=self.director)
        
        for key, value in self.__dict__.items():
            key = key.capitalize()
            inline = key in {'Jugadores', 'Notas', 'Nombre'}
            embed.add_field(name=key, value=str(value)[:1024], inline=inline)
        return embed

    def to_dict(self):
        # Se devuelve un diccionario con los campos del evento
        dict_event = {key: str(value) for key, value in self.__dict__.items()}
        return dict_event
    
    def summarize(self):
        # Se devuelve una cadena con los campos del evento
        return f'{self.tipo} \n **{self.nombre}** el dia **{self.dia}** de **{self.inicio}** a **{self.fin}**'
    
    def is_eq(self, evento):
        return self.id == evento.id
        
