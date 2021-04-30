### How to run the application
___

To launch the stack, run this command:

```
docker compose up -d
docker compose exec app pipenv run ./manage.py migrate 
```

### How to test the application
___

To test the application, there are 2 options:

1) If the containers are already running locally, run this command:

```
docker compose exec app pipenv run pytest
```

2) If no containers are running locally, run this command:
```
docker compose run --rm app pipenv run pytest
```

### To try out the API

1) Launch the application

```
docker compose up -d
docker compose exec app pipenv run ./manage.py migrate 
```

2) Import the Postman Collection using these [instructions](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-data-into-postman)

