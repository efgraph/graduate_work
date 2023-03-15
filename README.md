# Проектная работа: диплом

Здравствуйте, проект еще не готов (еще пару дней наверно нужно), но решил все таки узнать на правильном ли я пути.

Идея всего проекта такая, что по jwt токену billing_service понимает, что это за юзер, делает действие по биллингу и кидает событие в кафку.
В свою очередь auth_service слушает события из кафки и меняет юзеру роли в зависимости от того, за что заплачено.

Поресерчил и решил использовать все таки django, потому что там есть dj-stripe. Он сразу все модели предоставляет и возможность синхронизации с аккаунтом.

#### Планирую в итоге:
- постоить схему
- добавить кафку и обработку ролей
- написать тесты для биллинга
- добавить nginx
- закинуть в докер billing_service

#### Запуск проекта:

```
docker-compose up

billing_service пока вручную запускаю:

cd billing_service

./manage.py migrate

./manage.py createsuperuser

./manage.py djstripe_sync_models # синхронизация с аккаунтом stripe

./manage.py runserver
```

тестовая карта 4242 4242 4242 4242 

биллинг  http://localhost:8000/admin

авторизация http://localhost:5000

1. Создаем аккаунт admin/admin и логинимся для получения токена:
```
curl -X 'POST' \
  'http://localhost:5000/v1/auth/register?login=admin&password=admin&email=admin%40admin.com' \
  -H 'accept: application/json' 

curl -X 'POST' \
  'http://localhost:5000/v1/auth/login?login=admin&password=admin' \
  -H 'accept: application/json'
```

2. Создаем юзера в биллинге, подставляем access_token из прошлого шага
```
curl --location --request POST 'http://localhost:8000/api/v1/customer' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1=' \
--header 'Content-Type: application/x-www-form-urlencoded' 
```

3. После этого становится возможна для юзера оплата покупки и подписки


>ссылка на проект https://github.com/efgraph/graduate_work