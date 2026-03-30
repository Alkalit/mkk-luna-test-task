FROM python:3.14-slim as builder

WORKDIR /usr/src

COPY . .

# I'm way too lazy to create a separate Dockerfile for tests
#  or write multistage image
RUN pip install -e .[test]

FROM builder

CMD ["fastapi", "run", "src/mkk/main.py"]
