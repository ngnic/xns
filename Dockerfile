From python:3.7-slim

RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev postgresql
RUN pip install pipenv

WORKDIR /opt/app

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv sync -d

COPY . .

EXPOSE 8000
ENTRYPOINT ["./scripts/wait-for-it.sh"]
CMD ["pipenv run ./manage.py runserver 0:8000"]
