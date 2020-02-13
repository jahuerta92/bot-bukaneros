import datetime

def class Partida:
	
	id, name, date, start, end, director, players, type, max, other = [None] * 10
	raw_args = None
	
	#[EventoBukanero] Partida de rol. Juego: id - Partida: name - Dia: date - Inicio: start - Fin: end - Dirige: director - Maximo: max - other /n
	#[Jugadores] /n
	# - players[0]
	# - players[1]
	# - players[2]
	
	def __init__(self, raw_string, *args, **kwargs):
		
		my_args = self.parse(raw_string)
		
		self.id = my_args['id']
		self.name = my_args['name']
		self.date = my_args['date']
		self.start = my_args['start']
		self.end = my_args['end']
		self.director = my_args['director']
		self.players = my_args['players']
		self.type = my_args['type']
		self.max = my_args['max']
		self.other = my_args['other']

	def __str__(self):
		pass
	
	def parse(raw_string):
		pass
	