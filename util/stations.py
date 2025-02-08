from functools import wraps

import aiohttp
from bs4 import BeautifulSoup

def singleton_method(f):
	@wraps(f)
	def inner(cls, *args, **kwds):
		return f(cls._instance, *args, **kwds)
	return inner

class StationUtil:
	_instance = None

	def __init__(self):
		StationUtil._instance = self
		self.stations2id = dict()
		self.id2stations = dict()
		pass

	@classmethod
	@singleton_method
	async def refresh_stations(cls: 'StationUtil') -> None:
		url = "https://iechub.rfi.it/ArriviPartenze/"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				response.raise_for_status()
				soup = BeautifulSoup(await response.text(), "html.parser")
				data = soup.select("#ElencoLocalita option")
				cls._instance.stations2id = {station.text.upper(): station["value"] for station in data}
				cls._instance.id2stations = {station["value"]: station.text.upper() for station in data}

	@classmethod
	@singleton_method
	def get_station_by_name_exact(cls: 'StationUtil', name):
		sid = cls.stations2id.get(name.upper())
		return (sid,name.upper()) if sid else None

	@classmethod
	@singleton_method
	def get_station_by_id(cls: 'StationUtil', sid):
		sname = cls.id2stations.get(sid)
		return (sid, sname) if sname else None

	@classmethod
	@singleton_method
	def get_station_by_name(cls: 'StationUtil', name):
		res = cls.get_station_by_name_exact(name)
		if not res:
			for sname in cls.stations2id.keys():
				if name.upper() in sname:
					sid = cls.stations2id[sname]
					return sid, sname
		return res
	@classmethod
	@singleton_method
	def search_station_by_name(cls: 'StationUtil', name):
		return [(sid,sname) for sname, sid in cls.stations2id.items() if name.upper() in sname]

	@classmethod
	@singleton_method
	def get_stations2id(cls: 'StationUtil'):
		return cls.stations2id

	@classmethod
	@singleton_method
	def get_id2stations(cls: 'StationUtil'):
		return cls.id2stations

	@classmethod
	@singleton_method
	async def get_station_schedule(cls: 'StationUtil', sid):
		url = "https://iechub.rfi.it/ArriviPartenze/ArrivalsDepartures/Monitor?placeId={sid}&arrivals=False"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				response.raise_for_status()
				soup = BeautifulSoup(await response.text(), "html.parser")
				data = soup.select("#ElencoLocalita option")
				cls._instance.stations2id = {station.text.upper(): station["value"] for station in data}
				cls._instance.id2stations = {station["value"]: station.text.upper() for station in data}


