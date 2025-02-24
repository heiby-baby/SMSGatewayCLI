# SMS Gateway CLI

CLI-приложение для отправки запросов через HTTP шлюз c использанием сокетов

## Особенности

- Конфигурация через TOML-файл
- Логирование операций
- Интеграционные тесты с использованием Prism CLI и Модульное тестирование с использованием Pytest

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/heiby-baby/SMSGatewayCLI
cd SMSGatewayCLI
```

2. Скачайте и запустите mock-сервер
Убедитесь что у вас установлен node.js
```bash
npm install -g @stoplight/prism-cli
prism-cli mock sms-platform.yaml
```

3. Запустите программу
```
python main.py <sender> <receiver> <message>
```

4. Для запуска тестов
```
python -m pytest test_SMSGateway.py
```
   
   
