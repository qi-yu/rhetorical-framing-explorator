FROM python:3.8-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="./src:$PYTHONPATH"
ENV FLASK_APP=./src/main.py

WORKDIR /usr/src/app

# Install PostgreSQL development packages and build essentials
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv && pipenv install --system --deploy

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
