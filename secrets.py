import os

BOT_TOKEN = ''
if os.environ.get('DOCKER_MODE'):
	with open('/run/secrets/bot_token', 'r') as f:
		BOT_TOKEN = f.read().strip()
else:
	BOT_TOKEN = os.environ.get('BOT_TOKEN')
