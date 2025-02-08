FROM python:3.12
RUN useradd -m bot
WORKDIR /home/bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN chown -R bot:bot .
USER bot