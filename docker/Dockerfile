FROM python:3.14-slim

WORKDIR /usr/src

COPY . .

WORKDIR /usr/src

RUN pip install -e .

CMD [ "fastapi", "run", "mkk/main.py"]
