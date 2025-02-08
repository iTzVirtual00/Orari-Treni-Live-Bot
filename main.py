#!/usr/bin/env python
# pylint: disable=unused-argument
import logging
import os

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio
from asyncio import CancelledError
from sqlalchemy.orm import Session
from secrets import BOT_TOKEN
from util.rate_limiting import TelegramRateLimiter
from util.stations import StationUtil

from db import User, session_manager


logging.basicConfig(
	format="%(asctime)s - %(name)s - %(module)s0:%(lineno)d - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger('livetrenibot')
logger.setLevel(logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG")))

MAX_BUTTONS = 4
limiter = TelegramRateLimiter()

def check_migrations():
	import os
	os.system('python run_migrations.py')

def convert_to_keyboard(input_list, cols):
	return [input_list[i:i + cols] for i in range(0, len(input_list), cols)]

async def fetch_schedule(sid):
	pass


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session) -> None:
	await update.message.reply_text("Help!")

@limiter('query_station', 1)
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	if len(context.args) == 0:
		stations = StationUtil.get_id2stations().items()
	else:
		stations = StationUtil.search_station_by_name(' '.join(context.args[:]))
		if not stations:
			await update.message.reply_text("Nessuna stazione non trovata")
			return
	response = ''
	for i, el in enumerate(stations):
		sid, sname = el
		response += f'\n{sname} - {sid}'
		if i > 20:
			response += '...'
			break
	await update.message.reply_text(response)

@limiter('query_station', 1)
@session_manager
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session) -> None:
	message_text = update.message.text
	ephemeral = False
	if message_text.startswith('.'):
		message_text = message_text[1:]
		ephemeral = True
	if (sid := message_text[:message_text.find(' ')]).isdigit():
		station = StationUtil.get_station_by_id(sid)
		if not station:
			await update.message.reply_text(f'Stazione \'{sid}\' non trovata')
			return
	else:
		station = StationUtil.get_station_by_name(message_text)
		if not station:
			await update.message.reply_text(f'Stazione \'{message_text}\' non trovata')
			return
	logger.debug(f'got station {station}')
	sid, sname = station # station id, station name

	reply_markup = None
	if not ephemeral:
		user = User.get_user(db, update.effective_user.id)
		user.insert_button(db, f'{sid} {sname}')
		buttons = convert_to_keyboard(list(map(lambda a: KeyboardButton(text=a.label, web_app=WebAppInfo(url=f'https://iechub.rfi.it/ArriviPartenze/ArrivalsDepartures/Monitor?placeId={a.label.split(' ')[0]}&arrivals=False')), user.buttons)), 2)
		# buttons = convert_to_keyboard(list(map(lambda a: a.label, user.buttons)), 2)
		reply_markup = ReplyKeyboardMarkup(buttons)

	await update.message.reply_text(f'Stazione di {sname} aggiunta', reply_markup=reply_markup)

@limiter('clear', 1)
@session_manager
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE, db:Session) -> None:
	user = User.get_user(db, update.effective_user.id)
	user.buttons.clear()
	db.commit()
	await update.message.reply_text("Tastiera resettata ✅", reply_markup=ReplyKeyboardRemove())

async def run_bot(application):
	await application.initialize()
	await application.start()
	await application.updater.start_polling()


async def stop_bot(application):
	await application.updater.stop()
	await application.stop()
	await application.shutdown()


async def run_bot_forever(application):
	stop_event = asyncio.Event()
	bot_task = asyncio.create_task(run_bot(application))
	try:
		await stop_event.wait()  # Block here until stop_event.set() is called (manually or Ctrl+C)
	except CancelledError:
		pass

	await stop_bot(application)
	bot_task.cancel()


# noinspection PyTypeChecker
async def main() -> None:
	check_migrations()
	application = Application.builder().token(BOT_TOKEN).build()
	# application.add_handler(CommandHandler("start", help_command))
	# application.add_handler(CommandHandler("help", help_command))
	application.add_handler(CommandHandler("search", search))
	application.add_handler(CommandHandler("clear", clear))
	application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

	StationUtil()
	await StationUtil.refresh_stations()
	await run_bot_forever(application)


if __name__ == "__main__":
	StationUtil()
	asyncio.run(main())
