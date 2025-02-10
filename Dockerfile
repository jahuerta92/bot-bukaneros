FROM python:3.10-bullseye
RUN mkdir /app/bot
WORKDIR /bot
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3", "bot.py", "--mode", "beta"]