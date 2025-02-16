FROM python:3.10-bullseye
WORKDIR /app
COPY bot .
RUN pip3 install -r requirements.txt
CMD ["python3", "bot.py", "--mode", "deploy", "--remote"]