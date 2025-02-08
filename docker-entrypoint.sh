#!/bin/sh
chown -R bot:bot /home/bot/volume
exec runuser -u bot -- "$@"