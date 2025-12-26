# stripe-payment-service
Платёжный сервис на Django + Stripe API

Решение можно посмотреть на ..

## Что реализовано?
- `GET /buy/{id}` получение stripe сессии на покупку товара
- `GET /item/{id}` получение html страницы товара с возможностью приопрести товар
- Админка для управление товарами (password: ... ; login: ...)
- Инкримент/Дикремент товара на стороне JS
- Запуск и деплой через Docker
- environment variables

## Запуск локально

1) Создайте `.env` файл в корне проекта

```.env
DJANGO_SECRET_KEY=secret_key
DJANGO_ALLOWED_HOSTS=*
DJANGO_DEBUG=0

POSTGRES_NAME=payment_service_db
POSTGRES_USER=user
POSTGRES_PASSWORD=12345678
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

ADMIN_EMAIL=test@gmail.com # Нужно только для ssl сертификатов в prod режиме
```

2) Запуск и сборка через docker

`compose.dev.yml` - локальный запуск
`compose.dev.yml` - запуск на сервере

```bash
docker-compose -f compose.dev.yml --build -d
```
