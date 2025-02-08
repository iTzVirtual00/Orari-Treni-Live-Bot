import logging
import os
import time
from collections import defaultdict
from functools import wraps

from telegram import Update

logger = logging.getLogger('TelegramRateLimiter')
logger.setLevel(logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG")))

class TelegramRateLimiter:
	def __init__(self):
		self.rate_groups: dict[str: dict[int:int]] = defaultdict(lambda: defaultdict(int))
		# {
		# 	'search': {
		# 			12345: 1739033476 # telegram_id: last_time
		# 		}
		# }

	def __call__(self, group_name, delta):
		def wrapper(func):
			@wraps(func)
			async def wrapped(update: Update, *args, **kwargs):
				# Some fancy foo stuff
				if  (t := time.time() - self.rate_groups[group_name][update.effective_user.id]) < delta:
					logger.debug(f'{update.effective_user.id} got rate limited ({t})')
					return None
				self.rate_groups[group_name][update.effective_user.id] = int(time.time())
				return await func(update, *args, **kwargs)
			return wrapped
		return wrapper
