# session_decorator.py
from functools import wraps
from . import SessionFactory

def session_manager(func):
	@wraps(func)
	async def wrapper(update, context, *args, **kwargs):
		session = SessionFactory()

		try:
			return await func(update, context, session, *args, **kwargs)

		except Exception as e:
			session.rollback()
			raise e
		finally:
			session.close()

	return wrapper
