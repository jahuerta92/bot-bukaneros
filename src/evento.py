from collections import namedtuple
from datetime import date, timedelta
from copy import copy

import unidecode
import re

Argumento = namedtuple('Argumento', 'alias name default finder dtype')

LEGAL_DAYS = [['lunes', 'l', 'lun', 'Lunes'],
              ['martes', 'm', 'mar', 'Martes'],
              ['miercoles', 'x', 'mie', 'Miércoles'],
              ['jueves', 'j', 'jue', 'Jueves'],
              ['viernes', 'v', 'vie', 'Viernes'],
              ['sabado', 's', 'sab', 'sábados', 'Sábado'],
              ['domingo', 'd', 'dom', 'Domingo']]

LEGAL_DAYS_SET = set([item for sublist in LEGAL_DAYS for item in sublist])


class Campo:
    """Clase Campo para la gestion de busqueda de elemntos en un string

    Parameters
    ----------
    alias : str
        Letra que define el campo
    name : str
        Nombre extendido del campo
    default: object
        Valor por defecto que puede tomar el campo
    finder: re
        Expresion regular de busqueda en un string
    dtype: object
        Clase a la que pertenece el campo

    Attributes
    ----------
    alias : str
        Letra que define el campo
    name : str
        Nombre extendido del campo
    default:
        Valor por defecto que puede tomar el campo
    finder: re
        Expresion regular de busqueda en un string
    dtype:
        Clase a la que pertenece el campo
    """


    alias = None
    name = None
    default = None
    finder = None
    dtype = None

    def __init__(self, *args, **kwargs):
        """Generador de un campo

        Parameters
        ----------
        alias : str
            Letra que define el campo
        name : str
            Nombre extendido del campo
        default: object
            Valor por defecto que puede tomar el campo
        finder: re
            Expresion regular de busqueda en un string
        dtype: object
            Clase a la que pertenece el campo

        Returns
        -------
        None
        """
        self.alias = kwargs['alias']
        self.name = kwargs['name']
        self.default = kwargs['default']
        self.finder = kwargs['finder']
        self.dtype = kwargs['dtype']

    def __call__(self, *args, **kwargs):
        return self.dtype(args[0])

    def find_value(self, text):
        """Usa el buscador particular de self.finder para encontrar el valor
        en el string dado

        Parameters
        ----------
        text : str
            Cadena de texto donde buscar el campo actual

        Returns
        -------
        casted_value:
            Valor encontrado con el dtype indicado del campo
        """
        values = self.finder.findall(text)
        if len(values) is 0:
            return None
        casted_value = self.dtype(values[0])
        return casted_value

    def find_all(self, text):
        """Usa el buscador particular de self.finder para encontrar el valor
        en el string dado

        Parameters
        ----------
        text : str
            Cadena de texto donde buscar el campo actual

        Returns
        -------
        casted_value:
            Lista de valores encontrados, siempre en string
        """
        return self.finder.findall(text)


class Hora:
    """Clase Hora para la gestion de hora-minuto y su lectura

    Parameters
    ----------
    args:
        Una de dos opciones, una hora y un minuto o un string de formato 'MM' / 'HH:MM'

    Attributes
    ----------
    hour : int
        Letra que define el campo
    minute : int
        Nombre extendido del campo

    """
    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            self.hour = kwargs['hour']
            self.minute = kwargs['minute']
        elif isinstance(args[0], str):
            tmp = args[0].split(':')
            self.hour = int(tmp[0])
            self.minute = 0 if len(tmp) == 1 else int(tmp[1])

    def __str__(self):
        return '{:02}:{:02}'.format(self.hour, self.minute)


class Dia:
    """Clase Hora para la gestion de la fecha y su lectira

    Parameters
    ----------
    args:
        Una de dos opciones, un objeto Dia, un objeto date o un string de formato DD/MM / DD/MM/YY / Jueves.
        Se intentará encontrar una fecha adecuada automáticamente.

    Attributes
    ----------
    hour : int
        Letra que define el campo
    minute : int
        Nombre extendido del campo

    """
    def __init__(self, *args, **kwargs):
        if isinstance(args[0], Dia):
            self.date = copy(args[0].date)

        elif isinstance(args[0], date):
            self.date = copy(args[0])

        elif isinstance(args[0], str):
            today = date.today()

            if unidecode.unidecode(args[0]).lower() in [item for sublist in LEGAL_DAYS for item in sublist]:
                for idx, days in enumerate(LEGAL_DAYS):
                    if unidecode.unidecode(args[0]).lower() in days:
                        weekday_idx = idx

                time_diff = weekday_idx - today.weekday()
                increment = timedelta(days=time_diff) if time_diff > 0 else timedelta(days=7 + time_diff)
                target_date = today + increment

                kwargs['day'] = target_date.day
                kwargs['month'] = target_date.month
                kwargs['year'] = target_date.year

            elif len(args[0].split('/')) > 1:
                try:
                    tmp = args[0].split('/')
                    kwargs['day'] = int(tmp[0])
                    kwargs['month'] = int(tmp[1])
                except:
                    raise Exception('Dia y Mes requeridos')

                if len(tmp) == 3:
                    kwargs['year'] = int(tmp[2])
                else:
                    if today.month > int(tmp[1]):
                        kwargs['year'] = today.year + 1
                    else:
                        kwargs['year'] = today.year
            else:
                raise Exception('No se puede reconocer el string como fecha')
            self.date = date(day=kwargs['day'], month=kwargs['month'], year=kwargs['year'])

    def __str__(self):
        i = self.date.weekday()
        weekday = LEGAL_DAYS[i][-1]
        return '{} {:02}/{:02}/{:04}'.format(weekday, self.date.day, self.date.month, self.date.year)


ARGUMENT_TYPES = {
    'EventoBukanero': Campo(alias='t', name='tipo', default='Partida de rol',
                            finder=re.compile(r'\[EventoBukanero\] *([\w| ]+).', re.IGNORECASE),
                            dtype=str),
    'Id': Campo(alias='a', name='id', default=None,
                finder=re.compile(r'Id: ([^\s]+) [·|\n]', re.IGNORECASE),
                dtype=str),
    'Nombre': Campo(alias='n', name='nombre', default=None,
                    finder=re.compile(r'Nombre: ([^·]+) [·|\n]', re.IGNORECASE),
                    dtype=str),
    'Dia': Campo(alias='d', name='dia', default=None,
                 finder=re.compile(r'Dia: *[^\s]+ (\d+/\d+/\d+) *[·|\n]', re.IGNORECASE),
                 dtype=Dia),  # ATENCION, TIPO DE DATOS MIXTO
    'Inicio': Campo(alias='i', name='inicio', default=Hora(hour=17, minute=0),
                    finder=re.compile(r'Inicio: *(\d+:\d+) *[·|\n]', re.IGNORECASE),
                    dtype=Hora),  # ATENCION, TIPO MIXTO
    'Fin': Campo(alias='f', name='fin', default=Hora(hour=21, minute=0),
                 finder=re.compile(r'Fin: *(\d+:\d+) *[·|\n]', re.IGNORECASE),
                 dtype=Hora),  # ATENCION, TIPO MIXTO
    'Director': Campo(alias='D', name='director', default=None,
                      finder=re.compile(r'Director: ([^·]+) [·|\n]', re.IGNORECASE),
                      dtype=str),
    'Jugadores': Campo(alias='j', name='jugador', default=[],
                       finder=re.compile(r'\n- *([^\n]+) *\n', re.IGNORECASE),
                       dtype=str),
    'Maximo': Campo(alias='m', name='maximo', default=6,
                    finder=re.compile(r'Maximo: *(\d+) *[·|\n]', re.IGNORECASE),
                    dtype=int),
    'Notas': Campo(alias='N', name='notas', default='nothing',
                   finder=re.compile(r'Notas: ([^·|\n]+) [·|\n]', re.IGNORECASE),
                   dtype=str)}


# -t Juego de Rol --id D&D -n Strahd in da hous -i 18:00 --fin 17:15 -D Javi --maximo 666

class Evento:
    """Clase Evento para la gestion de cada evento, su reconocimiento, replicación, etc

    Parameters
    ----------
    args:
        Una de dos opciones, un String en el formato de una partida, Como el indicado a
        continuación:
            [EventoBukanero] Partida de rol. Id: D&D · Nombre: La Maldición de Strahd ·
             Dia: Miércoles 12/02/2020 · Inicio: 15:30 · Fin: 19:30 · Director: Javi ·
             Maximo: 5 · Notas: Hola caracola
            [Jugadores]
            - John
            - Cesar
            - Jolimbo
            -
            -
        O un diccionario con los campos requeridos: Id, Nombre, Dia, Inicio, Fin, Director, Maximo, Notas

    Attributes
    ----------
    event_dict : dict
        Diccionario conteniendo todos los elementos del evento. Id, Nombre, Dia, Inicio, Fin, Director, Maximo,
        Notas y Jugadores

    """
    event_dict = None
    original_msg = None

    def __init__(self, message=None, *args, **kwargs):
        if message is not None:
            self.event_dict = self.parse(message.content)
            self.original_msg = message
            if self.event_dict['Notas'] is None:
                del self.event_dict['Notas']
            self.event_dict['Jugadores'] = [item for item in self.event_dict['Jugadores'] if len(item) > 1]
        else:
            ids, inputs = ARGUMENT_TYPES.keys(), kwargs.keys()
            defaults = [key for key in ids if kwargs[key] is None]
            if any(ARGUMENT_TYPES[k].default for k in defaults) is None:
                raise Exception('Faltan argumentos sin default')

            self.event_dict = dict()
            for k in ids:
                self.event_dict[k] = copy(ARGUMENT_TYPES[k].default) if k in defaults else ARGUMENT_TYPES[k](kwargs[k])

            if self.event_dict['Notas'] == 'nothing':
                del self.event_dict['Notas']

    def __eq__(self, other):
        """Función identidad Evento1 == Evento2 si sus ids son similares

        Parameters
        ----------
        other : Evento
            Evento con el que comparar

        Returns
        -------
        is_equal: bool
            Booleano que indica si los eventos se pueden considerar iguales
        """
        simple_this = unidecode.unidecode(self.event_dict['Id']).lower()
        simple_other = unidecode.unidecode(other.event_dict['Id']).lower()
        is_equal = simple_this == simple_other
        return is_equal

    def __str__(self):
        """Función para representar un Evento como string

        -------
        str_event: str
            El evento transformado a string con el formato estandar:
                [EventoBukanero] Partida de rol. Id: D&D · Nombre: La Maldición de Strahd ·
                 Dia: Miércoles 12/02/2020 · Inicio: 15:30 · Fin: 19:30 · Director: Javi ·
                 Maximo: 5 · Notas: Hola caracola
                [Jugadores]
                - John
                - Cesar
                - Jolimbo
                -
                -
        """
        if 'Notas' not in self.event_dict.keys():
            str_otros = ''
            str_maximo = 'Maximo: %d \n' % self.event_dict['Maximo']
        else:
            str_otros = ' Notas: %s \n' % self.event_dict['Notas']
            str_maximo = 'Maximo: %d ·' % self.event_dict['Maximo']

        players_list = ['- {}'.format(player) for player in self.event_dict['Jugadores']]
        if len(players_list) < self.event_dict['Maximo']:
            ending = ['-'] * (self.event_dict['Maximo'] - len(players_list))
        else:
            ending = []
        str_jugadores = '\n'.join(players_list + ending) + '\nApuntados: {}'.format(len(self.event_dict['Jugadores']))


        fmt = '''
[EventoBukanero] {}. Id: {} · Nombre: {} · Dia: {} · Inicio: {} · Fin: {} · Director: {} · {}{}[Jugadores]
{}
        '''
        return fmt.format(self.event_dict['EventoBukanero'],
                          self.event_dict['Id'],
                          self.event_dict['Nombre'],
                          self.event_dict['Dia'],
                          self.event_dict['Inicio'],
                          self.event_dict['Fin'],
                          self.event_dict['Director'],
                          str_maximo,
                          str_otros,
                          str_jugadores)

    def parse(self, raw_string):
        """Función para transformar un string a Evento, hace uso de ARGUMENT_TYPES y sus objetos
        tipo Campo.

        Parameters
        ----------
        raw_string : str
            String que transformar a evento

        Returns
        -------
        parsed_dict: dict
            Diccionario con todos loas campos de un evento
        """
        parsed_dict = dict()

        parsed_dict['EventoBukanero'] = ARGUMENT_TYPES['EventoBukanero'].find_value(raw_string)
        parsed_dict['Id'] = ARGUMENT_TYPES['Id'].find_value(raw_string)
        parsed_dict['Nombre'] = ARGUMENT_TYPES['Nombre'].find_value(raw_string)
        parsed_dict['Dia'] = ARGUMENT_TYPES['Dia'].find_value(raw_string)
        parsed_dict['Inicio'] = ARGUMENT_TYPES['Inicio'].find_value(raw_string)
        parsed_dict['Fin'] = ARGUMENT_TYPES['Fin'].find_value(raw_string)
        parsed_dict['Director'] = ARGUMENT_TYPES['Director'].find_value(raw_string)
        parsed_dict['Jugadores'] = ARGUMENT_TYPES['Jugadores'].find_all(raw_string)
        parsed_dict['Maximo'] = ARGUMENT_TYPES['Maximo'].find_value(raw_string)
        parsed_dict['Notas'] = ARGUMENT_TYPES['Notas'].find_value(raw_string)

        return parsed_dict

    def new_player(self, player):
        """Añade un jugador al evento si no ha sido añadido ya y si la partida aun tiene huecos.

        Parameters
        ----------
        player : str
            Nombre del jugador a añadir

        Returns
        -------
        check: bool
            Chequedo de si la operacion ha sido completada con exito.
        error: str
            Mensaje de error que enviar si la operacion no se completa

        """
        simple_players = [unidecode.unidecode(item).lower() for item in self.event_dict['Jugadores']]
        simple_player = unidecode.unidecode(player).lower()
        if self.event_dict['Maximo'] <= len(self.event_dict['Jugadores']):
            return False,  'No se pudo añadir a {}, la lista de {} ya está llena, consulta al director.'
        elif simple_player in simple_players:
            return False, 'El jugador {} ya está apuntado a la lista de {}'
        else:
            self.event_dict['Jugadores'].append(player)
            return True, None

    def remove_player(self, player):
        """Retira a un jugador de la partida

        Parameters
        ----------
        player : str
            Nombre del jugador a retirar

        Returns
        -------
        check: bool
            Chequedo de si la operacion ha sido completada con exito.
        error: str
            Mensaje de error que enviar si la operacion no se completa

        """
        simple_players = [unidecode.unidecode(item).lower() for item in self.event_dict['Jugadores']]
        simple_player = unidecode.unidecode(player).lower()
        if simple_player not in simple_players:
            return False, 'El jugador {} no está apuntado a la lista de {}'
        else:
            idx = simple_players.index(simple_player)
            self.event_dict['Jugadores'].remove(self.event_dict['Jugadores'][idx])
            return True, None

    def summary(self):
        return self.event_dict['Id'], str(self.event_dict['Dia']), ' · '.join(self.event_dict['Jugadores'])

    def unpin(self):
        return self.original_msg.unpin()

# str_event = '[EventoBukanero] Partida de rol. Id: D&D · Nombre: La Maldición de Strahd · Dia: Miércoles 12/02/2020 · Inicio: 15:30 · Fin: 19:30 · Director: Javi · Maximo: 5 · Notas: Hola caracola \n [Jugadores] \n- John \n - '
# parsed_event = Evento(str_event)

# str_event_rep = str(parsed_event)
# parsed_event_rep = Evento(str_event_rep)

# raw_event = Evento(Id='Flipas',
#                   Nombre='La muerte de dios',
#                   Dia='27/02',
#                   Director='Joseramon',
#                   Notas='Viva españa')

# print(raw_event)
