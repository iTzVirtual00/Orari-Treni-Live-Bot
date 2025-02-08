FROM python:3.12
RUN useradd -m bot
USER bot
WORKDIR /home/bot
COPY requirements.txt .
RUN pip install -r requirements.txt
