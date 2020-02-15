from collections import namedtuple
from datetime import datetime
import re

Argumento = namedtuple('Argumento', 'alias name default finder dtype')
Horario = namedtuple('Horario', 'hour minute')

class Campo(Argumento):
    def __init__(self, *args, **kwargs):
        super(Campo, self).__init__(*args, **kwargs)

    def find_value(self, text):
        value = self.finder.findall(text)[0]
        casted_value = self.dtype(value)
        return casted_value

ARGUMENT_TYPES = {'EventoBukanero': Campo(alias='t', name='tipo', default='Partida de rol', format='[EventoBukanero] %s.',
                                          regex=re.compile(r'\[EventoBukanero\]([a-zA-Z| ]+)', re.IGNORECASE),
                                          dtype=str),
                  'Juego': Campo(alias='a', name='id', default=None,
                                 finder=re.compile(r'Juego: ([^\s]+) -', re.IGNORECASE),
                                 dtype=str),
                  'Nombre': Campo(alias='n', name='nombre', default=None,
                                  finder=re.compile(r'Nombre: ([^\-]+) -', re.IGNORECASE)),
                  'Dia': Campo(alias='d', name='dia', default='auto',
                               finder=re.compile(r'Dia: [a-zA-Z]+ (\d+/\d+/\d+) -', re.IGNORECASE),
                               dtype=datetime), #ATENCION, TIPO DE DATOS MIXTO
                  'Inicio': Campo(alias='i', name='inicio', default=Horario(hour=17, minute=0),
                                  finder=re.compile(r'Inicio: (\d+:\d+) -', re.IGNORECASE),
                                  dtype=datetime), #ATENCION, TIPO MIXTO
                  'Fin': Campo(alias='f', name='fin', default=Horario(hour=21, minute=0),
                               finder=re.compile(r'Fin: (\d+:\d+) -', re.IGNORECASE),
                               dtype=datetime),
                  'Director': Campo(alias='D', name='director', default='auto',
                                    finder=re.compile(r'Fin: ([^\-]+) ?-', re.IGNORECASE),
                                    dtype=str),
                  'Jugador': Campo(alias='j', name='jugador', default='auto',
                                   finder=re.compile(r'- ?([^\n]+)\n', re.IGNORECASE),
                                   dtype=str),
                  'Maximo': Campo(alias='m', name='director', default=6,
                                  finder = re.compile(r'Maximo: (d+) [\-|\n]', re.IGNORECASE),
                                  dtype=int),
                  'Otros': Campo(alias='o', name='otros', default='nothing',
                                 finder=re.compile(r'Otros: ([^\-]+) \n', re.IGNORECASE),
                                 dtype=str)}

#if tp not in ARGUMENT_TYPES.keys():
#    raise Exception('Nombre del argumento no existe:\t{}'.format(tp))

#arg_type = ARGUMENT_TYPES[tp]

#if arg_type.default is None and value is None:
#    raise Exception('Hace falta un valor para el campo {}'.format(tp))
#elif value is None:
#    self.val = deepcopy(arg_type.default)
#else:
#    self.val = value

#self.arg = arg_type
#self.type = tp


class Evento:
    event_dict = None

    # [EventoBukanero] Partida de rol. Nombre: id - Partida: name - Dia: date - Inicio: start - Fin: end - Dirige: director - Maximo: max - other /n
    # [Jugadores] /n
    # - players[0]/n
    # - players[1]/n
    # - players[2]/n

    def __init__(self, raw_string=None, *args, **kwargs):
        if raw_string is not None:
            self.event_dict = self.parse(raw_string)
        else:
        self.id = kwargs['Juego']
        self.name = kwargs['Nombre']
        self.date = kwargs['Dia']
        self.start = kwargs['Inicio']
        self.end = kwargs['Fin']
        self.director = kwargs['Director']
        #self.players = kwargs['Jugadores']
        self.type = kwargs['EventoBukanero']
        self.max = kwargs['Maximo']
        self.other = kwargs['Otros']

    def __str__(self):
        pass

    def parse(self, raw_string):
        parsed_dict = dict()

        parsed_dict['EventoBukanero'] = Campo(tp= 'EventoBukanero', value=)
        return parsed_dict
