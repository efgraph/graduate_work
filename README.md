# Проектная работа: диплом

![Схема API](./architecture/architecture-Billing_API.png?raw=true)


##### Запуск проекта:

```
docker-compose up
```

###### сервис авторизации  http://localhost/swagger

###### тестовая карта 4242 4242 4242 4242

###### биллинг-сервис  http://localhost/admin   # admin/admin

- в биллинг-сервисе очень долго происходит синхронизация с dj-stripe, при запуске проект закоментил, но можно выполнить отдельно
```
docker exec -it billing sh -c "./manage.py djstripe_sync_models"
```

1. Создаем аккаунт admin/admin и логинимся для получения токена:
```
curl -X 'POST' \
  'http://localhost/v1/auth/register?login=foo&password=bar&email=foo%40bar.com' \
  -H 'accept: application/json' 

curl -X 'POST' \
  'http://localhost/v1/auth/login?login=foo&password=bar' \
  -H 'accept: application/json'
```

2. Создаем юзера в биллинге, подставляем access_token из прошлого шага
```
curl --location --request POST 'http://localhost/api/v1/customer' \
--header 'Authorization: Bearer $access_token' \
--header 'Content-Type: application/x-www-form-urlencoded' 
```

3. После этого становится возможна для юзера оплата покупки и подписки

- список подписок
```
curl --location --request POST 'http://localhost/api/v1/products' \
--header 'Authorization: Bearer $access_token' \
--header 'Content-Type: application/x-www-form-urlencoded' 
```
- после выбора нужного продукта, запрашиваем его оплату с параметром price_id
``` 
curl --location --request GET 'http://localhost/api/v1/checkout?price_id=' \
--header 'Authorization: Bearer $access_token' \
--header 'Content-Type: application/x-www-form-urlencoded' 
```
- в ответе приходит ссылка на окно оплаты
  
![Схема API](./architecture/checkout.png?raw=true)

4. После оплаты подписки приходит редирект на экран с успешной оплатой либо ошибкой
```
http://localhost/api/v1/success|cancel
```

5. Пользователь имеет возможность отменить подписку
```
curl --location --request POST 'http://localhost/api/v1/subscription' \
--header 'Authorization: Bearer $access_token' \
--header 'Content-Type: application/x-www-form-urlencoded' 
```

6. Пользователь имеет возможность возобновить подписку
```
curl --location --request POST 'http://localhost/api/v1/subscription' \
--header 'Authorization: Bearer $access_token' \
--header 'Content-Type: application/x-www-form-urlencoded' 
```

7. Проверить роль юзера после действий с подпиской
```
curl -X 'GET' \
  'http://localhost/v1/role/user?jwt=$access_token&login=foo' \
  -H 'accept: application/json'
```

>ссылка на проект https://github.com/efgraph/graduate_work