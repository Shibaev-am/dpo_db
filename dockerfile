FROM python:3.12.3

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt
COPY requirements.dev.txt /app
ARG MODE
RUN if [ "$MODE" = "development" ]; then pip3 install -r requirements.dev.txt; fi

COPY . /app

CMD ["fastapi", "run", "src/main.py", "--port", "9000"]
