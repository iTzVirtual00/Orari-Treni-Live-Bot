FROM python:3.12
RUN useradd -m bot
WORKDIR /home/bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN mv ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
RUN chown -R bot:bot .

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "main.py"]